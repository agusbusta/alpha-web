from flask import Flask, request
from pathlib import Path
from db import session

THIS_FOLDER = Path(__file__).parent.resolve() # takes the parent path

app = Flask(__name__)

if __name__ == "__main__":
    app.run(port=4000, debug=True, threaded=True)