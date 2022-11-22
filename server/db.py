from flask import Flask
from flask_pymongo import pymongo

CONNECTION_STRING = "mongodb+srv://ani:tf4xJe4ngEBwUUzK@cluster0.lenfml0.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(CONNECTION_STRING)

db = client.users
