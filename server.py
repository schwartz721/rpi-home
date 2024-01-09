from flask import Flask

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
    app.furnace_temp = temp
    return f"Setting furnace to {app.furnace_temp}"

if __name__ == "__main__":
    app.run(host='0.0.0.0')