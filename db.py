from flask import Flask
from flask_pymongo import pymongo
from main import app

client = pymongo.MongoClient("mongodb+srv://Kiran:kiran$2000@cluster0.mfqoj.mongodb.net/edge-backend?retryWrites=true&w=majority")

db = client.get_database('flask_mongodb_atlas')
user_collection = pymongo.collection.Collection(db, 'user_collection')
