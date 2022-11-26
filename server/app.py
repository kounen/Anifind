from flask import Flask, url_for, request, session, redirect, jsonify, json
import db
import bcrypt
from bson import json_util
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"*"
    }
})

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

# POST '/ratings', add a rating to user, must provide an existing anime name !!
# body: 
# 'username'     
# "ratings": {
#       "anime": "Cowboy Bebop",
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
        animes = db.db.get_collection('animes_collection')
        ratings = db.db.get_collection('ratings_collection')
        existing_anime = animes.find_one({'Name': body['ratings']['anime']})
        if existing_user:
            if existing_anime:
                anime_id = existing_anime['anime_id']
                users.update_one({'username': body['username']}, {'$push': {'ratings.0.anime': body['ratings']['anime']}}, upsert = True)
                users.update_one({'username': body['username']}, {'$push': {'ratings.0.rating': body['ratings']['rating']}}, upsert = True)
                users.update_one({'username': body['username']}, {'$push': {'ratings.0.anime_id': anime_id}}, upsert = True)
                ratings.insert_one({'user_id': str(existing_user['_id']), 'anime_id': anime_id, 'rating':  body['ratings']['rating']})
                return existing_user['ratings'], 201
            return 'Anime unknow', 400
        return 'Usern unknow', 400

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
    app.run(host='0.0.0.0', port=5000, debug=True)