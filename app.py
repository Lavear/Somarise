from flask import Flask, jsonify, render_template
import websocket
import json
import threading

app = Flask(__name__)
WEMOS_WS_URL = "ws://10.150.180.45:81"  # ESP's IP (Wemos)

# Holds the latest readings
val = {
    "bpm": 0,
    "spo2": 0,
    "motion": 0,
    "state": "UNKNOWN",
    "sleep_score": 0,
    "deep_sleep_time": 0,
    "light_sleep_time": 0,
    "avg_bpm": 0,
    "avg_spo2": 0,
    "avg_motion": 0
}

def on_message(ws, message):
    global val
    try:
        data = json.loads(message)
        print("Received:", data)
        # Update val based on message type
        if data.get("type") == "report":
            val.update({
                "sleep_score": data.get("sleep_score", val["sleep_score"]),
                "deep_sleep_time": data.get("deep_sleep_time", val["deep_sleep_time"]),
                "light_sleep_time": data.get("light_sleep_time", val["light_sleep_time"]),
                "avg_bpm": data.get("avg_bpm", val["avg_bpm"]),
                "avg_spo2": data.get("avg_spo2", val["avg_spo2"]),
                "avg_motion": data.get("avg_motion", val["avg_motion"])
            })
        else:
            val.update({
                "bpm": data.get("bpm", val["bpm"]),
                "spo2": data.get("spo2", val["spo2"]),
                "motion": data.get("motion", val["motion"]),
                "state": data.get("state", val["state"])
            })
    except Exception as e:
        print("Error parsing message:", e)

def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket closed (code={close_status_code})")
    threading.Timer(5, start_wemos_websocket).start()

def on_open(ws):
    print("Connected to Wemos")

def start_wemos_websocket():
    ws = websocket.WebSocketApp(
        WEMOS_WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    return jsonify(val)

if __name__ == "__main__":
    threading.Thread(target=start_wemos_websocket, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)