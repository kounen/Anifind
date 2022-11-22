from flask import Flask, url_for, request, session, redirect, jsonify, json
import db
import bcrypt
from bson import json_util

app = Flask(__name__)

@app.route('/')
def flask_mongodb_atlas():
    return "flask mongodb atlas!"

@app.route('/index')
def index():
    if 'username' in session:
        return 'You are logged in as ' + session['username']

# POST '/login', login as username
# body: 
# 'username' 
# 'password'
@app.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    users = db.db.get_collection('users_collection')
    existing_user = users.find_one({'username': body['username']})
    
    if existing_user:
        if bcrypt.hashpw(body['password'].encode('utf-8'), existing_user['password']) == existing_user['password']:
            session['username'] = body['username']
            return redirect(url_for('index'))
        return 'Invalid', 400
    return 'Invalid', 400

# POST '/register', register an user
# body: 
# 'username' 
# 'password'
@app.route('/register', methods=['POST'])
def register():
    body = request.get_json()
    ratings = []

    if request.method == 'POST':
        users = db.db.get_collection('users_collection')
        existing_user = users.find_one({'username': body['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(body['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username': body['username'], 'password': hashpass, 'ratings': ratings})
            session['username'] = body['username']
            return redirect(url_for('index'))

    return 'Username already exists', 400

# POST '/ratings', add a rating to user
# body: 
# 'username'     
# "ratings": {
#       "anime": "pokemon",
#       "rating": "9"
# }
#
# GET '/ratings', get all ratings from user
# body: 
# 'username'     
@app.route('/ratings', methods=['GET', 'POST'])
def ratings():
    body = request.get_json()
    users = db.db.get_collection('users_collection')
    existing_user = users.find_one({'username': body['username']})
    if request.method == 'GET':
        resp = existing_user['ratings']
        if existing_user:
            return resp, 201

    if request.method == 'POST':
        if existing_user:
            users.update_one({'username': body['username']}, {'$push': {'ratings.0.anime': body['ratings']['anime']}}, upsert = True)
            users.update_one({'username': body['username']}, {'$push': {'ratings.0.rating': body['ratings']['rating']}}, upsert = True)
        return existing_user['ratings'], 201

    return 'Username unknown', 400

# GET '/animes', return all animes name and id
@app.route('/animes', methods=['GET', 'POST'])
def animes():
    animes = db.db.get_collection('animes_collection')
    if request.method == 'GET':
        cursor = animes.find({})
        data = list(cursor)
        json_data = json.loads(json_util.dumps(data))
        return json_data, 201

    return 'Username unknown', 400

if __name__ == '__main__':
    app.secret_key='mysecret'
    app.run(port=3000)