from flask import Flask, url_for, request, session, redirect, jsonify, json
import db
import bcrypt
from bson import json_util
from flask_cors import CORS, cross_origin
import random

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from collections import defaultdict
import keras
from keras import layers 
import tensorflow as tf
from keras.models import Model
from tensorflow.python.keras.optimizer_v2.adam import Adam
from keras.layers import Add, Activation, Lambda, BatchNormalization, Concatenate, Dropout, Input, Embedding, Dot, Reshape, Dense, Flatten
from tensorflow.keras.callbacks import Callback, ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping, ReduceLROnPlateau

from mal import generate_code_challenge, get_request_authentication_url, generate_access_token, get_user_anime_list
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
from waitress import serve

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
        id = random.randint(200, 1000)

        if existing_user is None:
            while users.find_one({'id': id}):
                id = random.randint(200, 1000)
            hashpass = bcrypt.hashpw(body['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert_one({'username': body['username'], 'password': hashpass, 'id': id,'ratings': []})
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
        ratings = db.db.get_collection('anime_collection')
        existing_anime = animes.find_one({'Name': body['ratings']['anime']})
        if existing_user:
            if existing_anime:
                anime_id = existing_anime['anime_id']
                for result in existing_user['ratings']:
                    #is anime already rated ?
                    if result.get('anime') == body['ratings']['anime']:
                        users.update_one({ 'username': body['username'], 'ratings.anime':body['ratings']['anime'] }, { '$set' : { "ratings.$.rating": body['ratings']['rating']} })
                        ratings.update_one( { 'user_id': existing_user['id'], 'anime_id':anime_id }, { '$set' : { "rating": body['ratings']['rating']} })
                        return existing_user['ratings'], 200

                #adding new rating
                users.update_one({'username': body['username'] }, { '$addToSet': { "ratings": { "anime": body['ratings']['anime'], "rating": body['ratings']['rating'], "anime_id": anime_id} } }, upsert=True)
                ratings.insert_one({'user_id': existing_user['id'], 'anime_id': anime_id, 'rating':  body['ratings']['rating']})
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
                ratings = db.db.get_collection('anime_collection')
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
                                        'user_id': existing_user['id'],
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
                                    'user_id': existing_user['id'],
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

@app.route('/getId', methods=['POST'])
def getId():
    body = request.get_json()
    users = db.db.get_collection('users_collection')
    existing_user = users.find_one({'username': body['username']})
    
    if existing_user:
        id = existing_user['id']
        return str(id), 200
    return 'No user', 400

# GET '/rs', do rs
# params: 
# 'user_id' 
@app.route('/rs', methods=['GET'])
def rs():
    rating_data = db.db.get_collection('anime_collection')
    if request.method == 'GET':
        user = request.args.get('user_id')
        df1 = pd.DataFrame(list(rating_data.find()))
        df1.to_csv('database/ratings_rs.csv', index=False)

        anime_df = pd.read_csv('database/anime.csv')
        rating_df = pd.read_csv('database/ratings_rs.csv', 
                        low_memory=False, 
                        usecols=["user_id", "anime_id","rating"],
                        nrows=20000
                        )

        anime_df = anime_df.rename(columns={"MAL_ID": "anime_id"})
        anime_df = anime_df[["anime_id", "Name"]]
        n_ratings = rating_df['user_id'].value_counts()
        rating_df = rating_df[rating_df['user_id'].isin(n_ratings[n_ratings >= 1].index)].copy()

        duplicates = rating_df.duplicated()

        if duplicates.sum() > 0:
            rating_df = rating_df[~duplicates]
        
        g = rating_df.groupby('user_id')['rating'].count()
        top_users = g.dropna().sort_values(ascending=False)[:20]
        top_r = rating_df.join(top_users, rsuffix='_r', how='inner', on='user_id')

        g = rating_df.groupby('anime_id')['rating'].count()
        top_animes = g.dropna().sort_values(ascending=False)[:20]
        top_r = top_r.join(top_animes, rsuffix='_r', how='inner', on='anime_id')

        pd.crosstab(top_r.user_id, top_r.anime_id, top_r.rating, aggfunc=np.sum)
        user_ids = rating_df["user_id"].unique().tolist()
        user2user_encoded = {x: i for i, x in enumerate(user_ids)}
        user_encoded2user = {i: x for i, x in enumerate(user_ids)}
        rating_df["user"] = rating_df["user_id"].map(user2user_encoded)
        n_users = len(user2user_encoded)

        anime_ids = rating_df["anime_id"].unique().tolist()
        anime2anime_encoded = {x: i for i, x in enumerate(anime_ids)}
        anime_encoded2anime = {i: x for i, x in enumerate(anime_ids)}
        rating_df["anime"] = rating_df["anime_id"].map(anime2anime_encoded)
        n_animes = len(anime2anime_encoded)
        
        rating_df = rating_df.sample(frac=1, random_state=73)

        X = rating_df[['user', 'anime']].values
        y = rating_df["rating"]

        test_set_size = 5000 #5k for test set
        train_indices = rating_df.shape[0] - test_set_size 

        X_train, X_test, y_train, y_test = (
            X[:train_indices],
            X[train_indices:],
            y[:train_indices],
            y[train_indices:],
        )

        X_train_array = [X_train[:, 0], X_train[:, 1]]
        X_test_array = [X_test[:, 0], X_test[:, 1]]

        df = pd.read_csv('database/anime.csv', low_memory=True)

        df.sort_values(by=['Score'], 
                    inplace=True,
                    ascending=False, 
                    kind='quicksort',
                    na_position='last')

        df = df[['anime_id', "Name", "Score", "Genres", "Episodes"]]

        def RecommenderNet():
            embedding_size = 256
            
            user = Input(name = 'user', shape = [1])
            user_embedding = Embedding(name = 'user_embedding',
                            input_dim = n_users, 
                            output_dim = embedding_size)(user)
            
            anime = Input(name = 'anime', shape = [1])
            anime_embedding = Embedding(name = 'anime_embedding',
                            input_dim = n_animes, 
                            output_dim = embedding_size)(anime)
            
            #x = Concatenate()([user_embedding, anime_embedding])
            x = Dot(name = 'dot_product', normalize = True, axes = 2)([user_embedding, anime_embedding])
            x = Flatten()(x)
                
            x = Dense(1, kernel_initializer='he_normal')(x)
            x = BatchNormalization()(x)
            x = Activation("sigmoid")(x)
            
            model = Model(inputs=[user, anime], outputs=x)
            model.compile(loss='binary_crossentropy', metrics=["mae", "mse"], optimizer='Adam')
            
            return model

        model = RecommenderNet()
        # model.summary()

        # start_lr = 0.00001
        # min_lr = 0.00001
        # max_lr = 0.001
        # batch_size = 10000

        # rampup_epochs = 5
        # sustain_epochs = 0
        # exp_decay = .8

        # def lrfn(epoch):
        #     if epoch < rampup_epochs:
        #         return (max_lr - start_lr)/rampup_epochs * epoch + start_lr
        #     elif epoch < rampup_epochs + sustain_epochs:
        #         return max_lr
        #     else:
        #         return (max_lr - min_lr) * exp_decay**(epoch-rampup_epochs-sustain_epochs) + min_lr


        # lr_callback = LearningRateScheduler(lambda epoch: lrfn(epoch), verbose=0)

        checkpoint_filepath = './weights_callback'

        # model_checkpoints = ModelCheckpoint(filepath=checkpoint_filepath,
        #                                         save_weights_only=True,
        #                                         monitor='val_loss',
        #                                         mode='min',
        #                                         save_best_only=True)

        # early_stopping = EarlyStopping(patience = 3, monitor='val_loss', 
        #                             mode='min', restore_best_weights=True)

        # my_callbacks = [
        #     model_checkpoints,
        #     lr_callback,
        #     early_stopping,   
        # ]

        # # Model training
        # history = model.fit(
        #     x=X_train_array,
        #     y=y_train,
        #     batch_size=batch_size,
        #     epochs=15,
        #     verbose='auto',
        #     validation_data=(X_test_array, y_test),
        #     callbacks=my_callbacks
        # )

        model.load_weights(checkpoint_filepath)

        def extract_weights(name, model):
            weight_layer = model.get_layer(name)
            weights = weight_layer.get_weights()[0]
            weights = weights / np.linalg.norm(weights, axis = 1).reshape((-1, 1))
            return weights

        anime_weights = extract_weights('anime_embedding', model)
        user_weights = extract_weights('user_embedding', model)

        ratings_per_user = rating_df.groupby('user_id').size()
        random_user = int(user)

        pd.set_option("max_colwidth", None)

        def find_similar_users(item_input, n=10,return_dist=False, neg=False):
                index = item_input
                encoded_index = user2user_encoded.get(index)
                weights = user_weights
            
                dists = np.dot(weights, weights[encoded_index])
                sorted_dists = np.argsort(dists)
                
                n = n + 1
                
                if neg:
                    closest = sorted_dists[:n]
                else:
                    closest = sorted_dists[-n:]

                print('😱users similar to #{}'.format(item_input))

                if return_dist:
                    return dists, closest
                
                SimilarityArr = []
                
                for close in closest:
                    similarity = dists[close]

                    if isinstance(item_input, int):
                        decoded_id = user_encoded2user.get(close)
                        SimilarityArr.append({"similar_users": decoded_id, 
                                            "similarity": similarity})

                Frame = pd.DataFrame(SimilarityArr).sort_values(by="similarity", 
                                                                ascending=False)
                
                return Frame

        similar_users = find_similar_users(int(random_user), 
                                        n=5, 
                                        neg=False)

        similar_users = similar_users[similar_users.similarity > 0.005]
        similar_users = similar_users[similar_users.similar_users != random_user]

        def getFavGenre(frame, plot=False):
                frame.dropna(inplace=False)
                all_genres = defaultdict(int)
                
                genres_list = []
                for genres in frame["Genres"]:
                    if isinstance(genres, str):
                        for genre in genres.split(','):
                            genres_list.append(genre)
                            all_genres[genre.strip()] += 1
                return genres_list
            
        def get_user_preferences(user_id, plot=False, verbose=0):
            animes_watched_by_user = rating_df[rating_df.user_id==user_id]
            user_rating_percentile = np.percentile(animes_watched_by_user.rating, 75)
            # animes_watched_by_user = animes_watched_by_user[animes_watched_by_user.rating >= user_rating_percentile]
            top_animes_user = (
                animes_watched_by_user.sort_values(by="rating", ascending=False)#.head(10)
                .anime_id.values
            )
            

            anime_df_rows = df[df["anime_id"].isin(top_animes_user)]
            anime_df_rows = anime_df_rows[["Name", "Genres"]]
            
            if verbose != 0:
                print("🤑 User #{} has rated {} movies (avg. rating = {:.1f})".format(
                user_id, len(animes_watched_by_user),
                animes_watched_by_user['rating'].mean(),
                ))            
            if plot:
                getFavGenre(anime_df_rows, plot)
                
            return anime_df_rows

        user_pref = get_user_preferences(random_user, plot=True, verbose=1)

        print('👌 animes highly rated by this user')
        print(pd.DataFrame(user_pref).head(5))

        def getAnimeFrame(anime):
            if isinstance(anime, int):
                return df[df.anime_id == anime]
            if isinstance(anime, str):
                return df[df.Name == anime]

        def get_recommended_animes(similar_users, n=10):
            recommended_animes = []
            anime_list = []
            
            for user_id in similar_users.similar_users.values:
                pref_list = get_user_preferences(int(user_id), verbose=0)
                pref_list = pref_list[~ pref_list.Name.isin(user_pref.Name.values)]
                anime_list.append(pref_list.Name.values)
                
            anime_list = pd.DataFrame(anime_list)
            sorted_list = pd.DataFrame(pd.Series(anime_list.values.ravel()).value_counts()).head(n)
            
            for i, anime_name in enumerate(sorted_list.index):
                n_user_pref = sorted_list[sorted_list.index == anime_name].values[0][0]
                if isinstance(anime_name, str):
                    try:
                        frame = getAnimeFrame(anime_name)
                        anime_id = frame.anime_id.values[0]
                        genre = frame.Genres.values[0]
                        recommended_animes.append({#"anime_id": anime_id ,
                                                    "n": n_user_pref,
                                                    "anime_name": anime_name, 
                                                    "Genres": genre})
                    except:
                        pass
            
            return pd.DataFrame(recommended_animes)

        recommended_animes = get_recommended_animes(similar_users, n=10)
        getFavGenre(recommended_animes, plot=True)

        animes = db.db.get_collection('animes_collection')
        result = []
        test = json.loads(json.dumps(list(recommended_animes.T.to_dict().values())))
        for anime in test:
            existing_anime = animes.find_one({'Name': anime['anime_name']})
            result.append(json.loads(json_util.dumps(existing_anime)))
        return result, 200


if __name__ == '__main__':
    app.secret_key='mysecret'
    serve(app, host='0.0.0.0', port=5000)
    # app.run(host='0.0.0.0', port=5000, debug=True)