from flask import Flask
from systemd.journal import Reader

app = Flask(__name__)

# Routes
@app.route("/")
def ping():
    return "Pong"

@app.route("/journal")
def journal():
    reader = Reader()
    reader.add_match(_SYSTEMD_UNIT="pwm.service")
    reader.seek_tail()
    response = ""
    for _ in range(10):
        entry = reader.get_previous()
        if entry:
            timestamp = entry.__REALTIME_TIMESTAMP
            response += f"{timestamp.strftime('%b %d %H:%M:%S')} - {entry.MESSAGE}\n"

if __name__ == "__main__":
    app.run(host='0.0.0.0')