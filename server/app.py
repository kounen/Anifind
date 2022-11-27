from flask import Flask, url_for, request, session, redirect, jsonify, json
import db
import bcrypt
from bson import json_util
from flask_cors import CORS, cross_origin
import numpy as np # linear algebra
import pandas as pd

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
            return 'Success', 200
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
            return 'Success', 200

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

# GET '/rs', do rs
@app.route('/rs', methods=['GET'])
def rs():
    rating_data = db.db.get_collection('ratings_collection')
    if request.method == 'GET':
        cursor = rating_data.find({})
        df =  pd.DataFrame(list(cursor))
        if '_id' in df:
            del df['_id']
        df.to_csv('../database/ratings_rs.csv', index=False)

        anime_df = pd.read_csv('../database/anime.csv')
        anime_df = anime_df.rename(columns={"MAL_ID": "anime_id"})
        anime_df = anime_df[["anime_id", "Name"]]
        rating_df = pd.read_csv('../database/ratings_rs.csv', 
                        low_memory=False, 
                        usecols=["user_id", "anime_id","rating"],
                        nrows=1000000
                        )
        n_ratings = rating_df['user_id'].value_counts()
        rating_df = rating_df[rating_df['user_id'].isin(n_ratings[n_ratings >= 60].index)].copy()
        len(rating_df)

        duplicates = rating_df.duplicated()

        if duplicates.sum() > 0:
            rating_df = rating_df[~duplicates]
    
        rating_data = rating_df.merge(anime_df, left_on = 'anime_id', right_on = 'anime_id', how = 'left')
        rating_data = rating_data[["user_id", "Name", "anime_id","rating"]]

        user_ids = rating_data["user_id"].unique().tolist()
        user2user_encoded = {x: i for i, x in enumerate(user_ids)}
        user_encoded2user = {i: x for i, x in enumerate(user_ids)}
        rating_data["user"] = rating_data["user_id"].map(user2user_encoded)
        n_users = len(user2user_encoded)

        anime_ids = rating_data["anime_id"].unique().tolist()
        anime2anime_encoded = {x: i for i, x in enumerate(anime_ids)}
        anime_encoded2anime = {i: x for i, x in enumerate(anime_ids)}
        rating_data["anime"] = rating_data["anime_id"].map(anime2anime_encoded)
        n_animes = len(anime2anime_encoded)

        print("Num of users: {}, Num of animes: {}".format(n_users, n_animes))
        print("Min total rating: {}, Max total rating: {}".format(min(rating_data['rating']), max(rating_data['rating'])))

        return 'ok', 201


if __name__ == '__main__':
    app.secret_key='mysecret'
    app.run(host='0.0.0.0', port=5000, debug=True)