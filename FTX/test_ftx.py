import websocket
import json

def on_open(ws):
    data = json.dumps({"op": "subscribe",
                       "channel": "markets"})
    ws.send(data)

    print("Connected")

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(close_msg):
    print(f"Connection close")

endpoint = "wss://ftx.com/ws/"
ws = websocket.WebSocketApp(endpoint,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

ws.run_forever()

