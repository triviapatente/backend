from setup import database, structure
from flask import Flask
def bootstrap():
    app = Flask(__file__)
    structure.initialize()
    database.initialize()

if __name__ == "__main__":
    bootstrap()
