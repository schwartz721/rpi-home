import pigpio
import time
import datetime
import logging

class PWM:
    def __init__(self, gpio, low=91, high=1000, restart_limit=10):
        self.gpio = gpio
        self.high = high
        self.low = low
        self.range = high - low
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
            # There's also the chance that the microcontroller lost power and isn't sending any signal,
            # but since the R Pi supplies power to the microcontroller, if the microcontroller doesn't
            # have power then the R Pi doesn't either, so this script won't be running.
            if self.pi.read(self.gpio):
                # If the pin is high, the PWM is at 100% duty cycle
                self.pwm = self.high
            else:
                # If the pin is low, the PWM is at 0% duty cycle
                self.pwm = 0
    
    def pwm_to_percent(self, pwm):
        return round(100 * max(0, min(1, (pwm - self.low) / self.range)))
    
    def pwm_change(self, previous_pwm):
        return abs(self.pwm - previous_pwm) / self.range >= 0.01
    
    @property
    def percent(self):
        return self.pwm_to_percent(self.pwm)


class Servo:
    def __init__(self, gpio, low=700, high=2500):
        self.gpio = gpio
        self.low = low
        self.high = high
        self.range = high - low
        self.pi = pigpio.pi()

    def percent_to_pwm(self, percent): # percent is 0 to 100
        return max(self.low, min(self.high, (percent - 100) / 100 * -self.range + self.low))
    
    def set_percent(self, percent):
        pwm = self.percent_to_pwm(percent)
        self.pi.set_servo_pulsewidth(self.gpio, pwm)
    
    def release(self):
        self.pi.set_servo_pulsewidth(self.gpio, 0)


logging.basicConfig(level=logging.INFO)

pwm = PWM(27)
servo = Servo(25)
previous_pwm = -100 # Set initial PWM at an unreachable value so that the first loop is guaranteed to update the value
while True:
    try:
        if time.time() - pwm.last_heartbeat > 5:
            if pwm.restart_count >= pwm.restart_limit:
                logging.info(f"{datetime.datetime.now()} - Restart limit reached. Exiting.")
                pwm.teardown()
                break
            # The pigpio callback and/or watchdog has failed. Try restarting them.
            logging.info(f"{datetime.datetime.now()} - No heartbeat. Restarting.")
            pwm.setup()
            pwm.restart_count += 1
        
        actual_pwm = pwm.pwm
        actual_percent = pwm.percent
        if pwm.pwm_change(previous_pwm):
            logging.info(f"{datetime.datetime.now()} - Input PWM: {actual_pwm} ({actual_percent}%).")
            previous_pwm = actual_pwm
            servo.set_percent(actual_percent)
        else:
            servo.release()

        time.sleep(1)
    except (KeyboardInterrupt, SystemExit, Exception) as e:
        pwm.teardown()
        logging.info(f"{datetime.datetime.now()} - Encountered error: {e}.")
        raise