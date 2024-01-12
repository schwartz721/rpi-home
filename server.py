from flask import Flask
from gpiozero import Servo

app = Flask(__name__)
app.servo = Servo(25)

# Routes
@app.route("/")
def ping():
    return "pong"

@app.route("/furnace")
def get_furnace():
    # Convert from servo position (from -1 and 1) to furnace setting (from 0 and 10)
    temp = (app.servo.value + 1) * 5
    # Return the current furnace setting
    return f"Furnace is set to {temp}"

@app.route("/furnace/<temp>", methods=["POST"])
def post_furnace(temp):
    try:
        # Convert from furnace setting (from 0 to 10) to servo position (from -1 to 1)
        temp = int(temp)
        app.servo.value = min(1, max(-1, temp / 5 - 1))
        return f"Setting furnace to {(app.servo.value + 1) * 5}"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(host='0.0.0.0')