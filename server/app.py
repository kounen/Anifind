from flask import Flask, url_for, request, session, redirect, jsonify, json
import db
import bcrypt
from bson import json_util
from flask_cors import CORS, cross_origin
import numpy as np # linear algebra
import pandas as pd
from mal import generate_code_challenge, get_request_authentication_url, generate_access_token, get_user_anime_list
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix

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

@app.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    users = db.db.get_collection('users_collection')
    existing_user = users.find_one({'username': body['username']})
    
    if existing_user:
        if bcrypt.hashpw(body['password'].encode('utf-8'), existing_user['password']) == existing_user['password']:
            return 'Success', 200
        return 'Wrong password', 400
    return 'No user', 400

@app.route('/register', methods=['POST'])
def register():
    body = request.get_json()
    ratings = [{}]

    if request.method == 'POST':
        users = db.db.get_collection('users_collection')
        existing_user = users.find_one({'username': body['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(body['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username': body['username'], 'password': hashpass, 'ratings': []})
            return 'Success', 200
        return 'Username already exists', 400
  
@app.route('/ratings', methods=['GET', 'POST'])
def ratings():
    users = db.db.get_collection('users_collection')
    
    if request.method == 'GET':
        arg = request.args.get('username')
        existing_user = users.find_one({'username': arg})
        resp = existing_user['ratings']
        if existing_user:
            return resp, 200

    if request.method == 'POST':
        body = request.get_json()
        existing_user = users.find_one({'username': body['username']})
        animes = db.db.get_collection('animes_collection')
        ratings = db.db.get_collection('ratings_collection')
        existing_anime = animes.find_one({'Name': body['ratings']['anime']})
        if existing_user:
            if existing_anime:
                anime_id = existing_anime['anime_id']
                for result in existing_user['ratings']:
                    #is anime already rated ?
                    if result.get('anime') == body['ratings']['anime']:
                        users.update_one({ 'username': body['username'], 'ratings.anime':body['ratings']['anime'] }, { '$set' : { "ratings.$.rating": body['ratings']['rating']} })
                        ratings.update_one( { 'user_id': str(existing_user['_id']), 'anime_id':anime_id }, { '$set' : { "rating": body['ratings']['rating']} })
                        return existing_user['ratings'], 200

                #adding new rating
                users.update_one({'username': body['username'] }, { '$addToSet': { "ratings": { "anime": body['ratings']['anime'], "rating": body['ratings']['rating'], "anime_id": anime_id} } }, upsert=True)
                ratings.insert_one({'user_id': str(existing_user['_id']), 'anime_id': anime_id, 'rating':  body['ratings']['rating']})
                return existing_user['ratings'], 200    
            return 'Anime unknow', 400

@app.route('/animes', methods=['GET', 'POST'])
def animes():
    animes = db.db.get_collection('animes_collection')
    if request.method == 'GET':
        cursor = animes.find({})
        data = list(cursor)
        json_data = json.loads(json_util.dumps(data))
        return json_data, 201
    return 'Username unknown', 400

# GET '/mal-auth-url', return the OAuth 2.0 authentication URL to call myanimelist's API
# params: 
# 'env': can be 'prod' or 'env' (will update the redirect url according to this value)
@app.route('/mal-auth-url', methods=['GET'])
def mal_auth_url():
    env = request.args.get('env')
    if request.method == 'GET' and (env == 'dev' or env == 'prod'):
        code_challenge = generate_code_challenge()
        auth_url = get_request_authentication_url(env, code_challenge)
        return auth_url, 200
    return 'Bad method or env', 400

# POST '/mal-anime-list', load in DB the user MAL anime list ratings
# (Title and respective score are collected for each anime)
# body:
# 'env': can be 'prod' or 'env' (will update the redirect url according to this value)
# 'code_verifier': send the same code_challenge present in the MAL authentication URL
# 'code': code present in the redirected URL as a param
# 'username': to add the ratings to the specific user
@app.route('/mal-anime-list', methods=['POST'])
def mal_anime_list():
    if request.method == 'POST':
        body = request.get_json()
        access_token = generate_access_token(body['env'], body['code_verifier'],  body['code'])
        anime_list = []
        if access_token:
            anime_list = get_user_anime_list(access_token)
        if anime_list:
            users = db.db.get_collection('users_collection')
            existing_user = users.find_one({'username': body['username']})
            if existing_user:
                animes = db.db.get_collection('animes_collection')
                ratings = db.db.get_collection('ratings_collection')
                for anime in anime_list:
                    existing_anime = animes.find_one({'Name': anime['Title']})
                    if existing_anime:
                        anime_id = existing_anime['anime_id']
                        isPresent = False
                        for rating in existing_user['ratings']:
                            # Is anime already rated?
                            if rating.get('anime') == anime['Title']:
                                users.update_one(
                                    {
                                        'username': body['username'],
                                        'ratings.anime': anime['Title'],
                                        'ratings.anime_id': anime_id
                                    },
                                    {
                                        # Replace the value of a field with the specified value
                                        '$set': {
                                            'ratings.$.rating': anime['Score']
                                        }
                                    },
                                    upsert = False
                                )
                                ratings.update_one(
                                    {
                                        'user_id': str(existing_user['_id']),
                                        'anime_id': anime_id
                                    },
                                    {
                                        '$set': {
                                            'rating': anime['Score']
                                        }
                                    },
                                    upsert = False
                                )
                                isPresent = True
                        # Adding new rating
                        if not isPresent:
                            users.update_one(
                                {
                                    'username': body['username']
                                },
                                {
                                    # Add a value to an array unless the value is already present
                                    '$addToSet': {
                                        'ratings': {
                                            'anime': anime['Title'],
                                            'rating': anime['Score'],
                                            'anime_id': anime_id
                                        }
                                    }
                                },
                                upsert = True
                            )
                            ratings.insert_one(
                                {
                                    'user_id': str(existing_user['_id']),
                                    'anime_id': anime_id,
                                    'rating': anime['Score']
                                }
                            )
                return existing_user['ratings'], 200
            else:
                return 'User unknown', 400
        else:
            return 'No anime found in MAL account', 400
    return 'Bad method', 400

# GET '/animes', return all animes with the given genre
# params: 
# 'Genre' 
@app.route('/animesGenre', methods=['GET'])
def animesGenre():
    animes = db.db.get_collection('animes_collection')

    if request.method == 'GET':
        arg = request.args.get('Genre')
        cursor = animes.find({"Genres": {'$regex' : '.*' + arg + '.*'}})
        data = list(cursor)
        json_data = json.loads(json_util.dumps(data))
        return json_data, 201
    return 'Username unknown', 400

# GET '/rs', do rs
@app.route('/rs', methods=['GET'])
def rs():
    body = request.get_json()
    rating_data = db.db.get_collection('ratings_collection')
    if request.method == 'GET':
        cursor = rating_data.find({})
        df =  pd.DataFrame(list(cursor))
        if '_id' in df:
            del df['_id']
        df.to_csv('database/ratings_rs.csv', index=False)

        anime_df = pd.read_csv('database/anime_mini.csv')

        anime_df = anime_df.rename(columns={"MAL_ID": "anime_id"})
        anime_df = anime_df[["anime_id", "Name"]]
        rating_df = pd.read_csv('database/ratings_rs.csv', 
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

        combine_movie_rating = rating_data.dropna(axis = 0, subset = ['Name'])
        movie_ratingCount = (combine_movie_rating.
            groupby(by = ['Name'])['rating'].
            count().
            reset_index()
            [['Name', 'rating']]
        )
        rating_data = combine_movie_rating.merge(movie_ratingCount, left_on = 'Name', right_on = 'Name', how = 'left')
        rating_data = rating_data.drop(columns = "rating_x")
        rating_data = rating_data.rename(columns={"rating_y": "rating"})

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

        g = rating_data.groupby('user_id')['rating'].count()
        top_users = g.dropna().sort_values(ascending=False)[:20]
        top_r = rating_data.join(top_users, rsuffix='_r', how='inner', on='user_id')

        g = rating_data.groupby('anime_id')['rating'].count()
        top_animes = g.dropna().sort_values(ascending=False)[:20]
        top_r = top_r.join(top_animes, rsuffix='_r', how='inner', on='anime_id')

        pivot = pd.crosstab(top_r.user_id, top_r.anime_id, top_r.rating, aggfunc=np.sum)
        pivot.fillna(0, inplace=True)

        piviot_table = rating_data.pivot_table(index="Name",columns="user_id", values="rating").fillna(0)
        piviot_table_matrix = csr_matrix(piviot_table.values)
        model = NearestNeighbors(metric="cosine", algorithm="brute")
        model.fit(piviot_table_matrix)
        recommended_anime = []

        def predict(recommended_anime):
            random_anime = np.random.choice(piviot_table.shape[0]) # This will choose a random anime name and our model will predict on it.

            recommended_anime = []
            query = piviot_table.iloc[random_anime, :].values.reshape(1, -1)
            distance, suggestions = model.kneighbors(query, n_neighbors=6)
            
            for i in range(0, len(distance.flatten())):
                if i == 0:
                    print('Recommendations for {0}:\n'.format(piviot_table.index[random_anime]))
                else:
                    recommended_anime.append(piviot_table.index[suggestions.flatten()[i]])
                    print('{0}: {1}, with distance of {2}:'.format(i, piviot_table.index[suggestions.flatten()[i]], distance.flatten()[i]))
            return recommended_anime

        recommended_anime = predict(recommended_anime)
        animes = db.db.get_collection('animes_collection')
        result = []
        for anime in recommended_anime:
            existing_anime = animes.find_one({'Name': anime})
            result.append(json.loads(json_util.dumps(existing_anime)))
        return result, 200


if __name__ == '__main__':
    app.secret_key='mysecret'
    app.run(host='0.0.0.0', port=5000, debug=True)