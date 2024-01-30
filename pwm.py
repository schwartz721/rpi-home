import pigpio
import time

class PWM:
    def __init__(self, gpio, ref_gpio=None, frequency=1000, restart_limit=10):
        self.gpio = gpio
        self.frequency = frequency
        self.ref_gpio = ref_gpio
        self.pi = pigpio.pi()
        self.restart_limit = restart_limit
        self.restart_count = 0
        self.setup()
    
    def setup(self):
        self.pwm = 0
        self.uptick = 0
        self.last_heartbeat = time.time()
        try:
            # Try cancelling an existing edge callback
            self.edge_callback.cancel()
        except Exception:
            pass
        self.edge_callback = self.pi.callback(self.gpio, pigpio.EITHER_EDGE, self.edge)
        self.watchdog = self.pi.set_watchdog(self.gpio, 1000)
    
    def teardown(self):
        try:
            self.edge_callback.cancel()
        except Exception:
            pass
        try:
            self.pi.set_watchdog(self.gpio, 0)
            self.pi.stop()
        except Exception:
            pass

    def edge(self, gpio, level, tick):
        self.last_heartbeat = time.time()
        if level == 1:
            self.uptick = tick
        elif level == 0:
            self.pwm = pigpio.tickDiff(self.uptick, tick)
        elif level == 2:
            # Watchdog timeout means there haven't been any edges detected for 1 second.
            # This means that:
            # - PWM is at 100% duty cycle
            # - PWM is at 0% duty cycle
            # - the microcontroller isn't sending any PWM signal
            if self.pi.read(self.gpio):
                # If the pin is high, the PWM is at 100% duty cycle
                self.pwm = self.frequency
            elif self.ref_gpio is not None and self.pi.read(self.ref_gpio):
                # If the reference pin is high that means that the microcontroller does have power,
                # so if the PWM pin is low that means that the PWM is at 0% duty cycle
                self.pwm = 0
            else:
                # If we can't confirm that the microcontroller is powered, set to 20% duty cycle for safety
                self.pwm = self.frequency * 0.2
    

def percent_to_pwm(percent):
    return max(700, min(2500, (percent - 100) * -18 + 700))

def pwm_to_percent(pwm):
    return round((pwm - 700) / -18 + 100)

pwm = PWM(27)
previous_pwm = 0
while True:
    try:
        if time.time() - pwm.last_heartbeat > 5:
            if pwm.restart_count >= pwm.restart_limit:
                print("Restart limit reached. Exiting.")
                pwm.teardown()
                break
            # The pigpio callback and/or watchdog has failed. Try restarting them.
            print("No heartbeat. Restarting.")
            pwm.setup()
            pwm.restart_count += 1
        
        if abs(pwm.pwm - previous_pwm) / pwm.frequency >= 0.01:
            percent = pwm.pwm / pwm.frequency * 100
            print(f"Input PWM: {pwm.pwm} ({percent}%). Output PWM: {percent_to_pwm(percent)} ({pwm_to_percent(pwm.pwm)}%)")
            previous_pwm = pwm.pwm

        time.sleep(1)
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        pwm.teardown()
        raise