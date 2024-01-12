from flask import Flask
from gpiozero import Servo

app = Flask(__name__)
app.furnace_temp = 0

# Routes
@app.route("/")
def ping():
    return "pong"

@app.route("/furnace")
def get_furnace():
    return f"Furnace is set to {app.furnace_temp}"

@app.route("/furnace/<temp>", methods=["POST"])
def post_furnace(temp):
    servo = Servo(25)
    temp = int(temp)
    app.furnace_temp = temp
    pwm = temp / 5 - 1
    pwm = max(-1, pwm)
    pwm = min(1, pwm)
    servo.value(pwm)
    return f"Setting furnace to {temp}"

if __name__ == "__main__":
    app.run(host='0.0.0.0')