from flask import Flask
import pigpio
from time import sleep

app = Flask(__name__)
app.servo_pin = 25

def percent_to_pwm(percent):
    return max(700, min(2500, (percent - 100) * -18 + 700))

def pwm_to_percent(pwm):
    return round((pwm - 700) / -18 + 100)

# Routes
@app.route("/")
def ping():
    return "Pong"

@app.route("/furnace")
def get_furnace():
    servo = pigpio.pi()
    pwm = servo.get_servo_pulsewidth(app.servo_pin)
    # Convert from servo position (from 2500 to 700) to furnace setting (from 0 to 100)
    furnace = pwm_to_percent(pwm)
    return f"Furnace is set to {furnace}"

@app.route("/furnace/<furnace>", methods=["POST"])
def post_furnace(furnace):
    try:
        furnace = int(furnace)
        # Convert from furnace setting (from 0 to 100) to servo position (from 2500 to 700)
        pwm = max(700, min(2500, furnace * 180 + 700))
        servo = pigpio.pi()
        servo.set_servo_pulsewidth(app.servo_pin, pwm)
        sleep(1)
        servo.set_servo_pulsewidth(app.servo_pin, None)
        return f"Setting furnace to {pwm_to_percent(pwm)}"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(host='0.0.0.0')