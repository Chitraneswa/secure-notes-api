from pymongo import MongoClient
import certifi
import os

client = MongoClient(
    os.getenv("MONGO_URI"),
    tls=True,
    tlsCAFile=certifi.where()
)
db = client["notes_db"]
