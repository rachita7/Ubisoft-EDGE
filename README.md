# Video Credits Extractor - Backend Repository

This repository contains the codebase for the backend repository of the Video Credits Extractor. 

# Setup
## Database - MongoDB
Make sure you have the latest version of MongoDB installed. Visit https://www.mongodb.com/try/download/community to download it.

To set up database locally, edit `db.py` to add the following line:
``` 
client = MongoClient('mongodb://localhost:27017/') 
```
If you want to use a shared cloud server, create a cluster in MongoDB Atlas, and paste the code SVN in the client variable in `db.py`

## Repository
In a virtual environment, run:
```
pip install requirements.txt
```

# Executing the code

 Export the Flask app using:
 ```
 export FLASK_APP=main.py
 ```
 Start the flask app using
 ``` flask run ``` or
 ``` python3 main.py``` in the terminal
