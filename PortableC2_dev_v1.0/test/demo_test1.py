from flask import Flask
import threading

app = Flask("__main__")

def test():
    print("this is test")
    print(threading.current_thread())

@app.route("/")
def index():
    threading.Thread(target=test).start()
    return "hahahah"

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=9000)