from flask import Flask
import pigpio

app = Flask(__name__)
app.servo_pin = 25

# Routes
@app.route("/")
def ping():
    return "pong"

@app.route("/furnace")
def get_furnace():
    servo = pigpio.pi()
    pwm = servo.get_servo_pulsewidth(app.servo_pin)
    # Convert from servo position (from 700 to 2500) to furnace setting (from 0 to 10)
    furnace = round((pwm - 700) / 180)
    return f"Furnace is set to {furnace}"

@app.route("/furnace/<furnace>", methods=["POST"])
def post_furnace(furnace):
    try:
        furnace = int(furnace)
        # Convert from furnace setting (from 0 to 10) to servo position (from 700 to 2500)
        pwm = max(700, min(2500, furnace * 180 + 700))
        servo = pigpio.pi()
        servo.set_servo_pulsewidth(app.servo_pin, pwm)
        return f"Setting furnace to {round((pwm - 700) / 180)}"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(host='0.0.0.0')