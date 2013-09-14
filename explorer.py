#!/usr/bin/env python
from flask import Flask
import chromelogger as console

app = Flask(__name__)
@app.route("/")
def hello():
    console.log('Hello console!')
    console.get_header()
    return "Hello World!"

if __name__ == "__main__":
    app.run()