from flask import Flask, url_for, request, session, redirect, jsonify, json
import db
import bcrypt
from bson import json_util
from flask_cors import CORS, cross_origin
import numpy as np # linear algebra
import pandas as pd
from scipy.stats import rankdata
from surprise import Reader, Dataset, SVD
from surprise.model_selection import cross_validate
import keras
from keras import layers 
import tensorflow as tf
from keras.models import Model
from tensorflow.keras.optimizers import Adam
from keras.layers import Add, Activation, Lambda, BatchNormalization, Concatenate, Dropout, Input, Embedding, Dot, Reshape, Dense, Flatten
from tensorflow.keras.callbacks import Callback, ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping, ReduceLROnPlateau
from scipy.sparse import csr_matrix
# from sklearn.neighbors import NearestNeighbors


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

        g = rating_data.groupby('user_id')['rating'].count()
        users = g.dropna().sort_values(ascending=False)
        r = rating_df.join(users, rsuffix='_r', how='inner', on='user_id')

        g = rating_data.groupby('anime_id')['rating'].count()
        animes = g.dropna().sort_values(ascending=False)
        r = r.join(animes, rsuffix='_r', how='inner', on='anime_id')

        piv_ = pd.crosstab(r.user_id, r.anime_id, r.rating, aggfunc=np.sum)
        piv_.fillna(0, inplace=True)
        piv_ = piv_.T

        data_array = np.array(piv_)
        columns = ["$X_{%d}$" % j for j in range(n_users)]
        x = data_array / np.linalg.norm(data_array)
        norm_data = pd.DataFrame(data=x, index=piv_.index, columns=columns)

        a_pos = np.zeros(n_users)
        a_neg = np.zeros(n_users)
        for j in range(n_users):
            column = x[:,j]
            max_val = np.max(column)
            min_val = np.min(column)
            
            # See if we want to maximize benefit or minimize cost (for PIS)
            if j in range(0, n_users):
                a_pos[j] = max_val
                a_neg[j] = min_val
            else:
                a_pos[j] = min_val
                a_neg[j] = max_val

        pd.DataFrame(data=[a_pos, a_neg], index=["$A^*$", "$A^-$"], columns=columns)
        m = len(data_array)
        sp = np.zeros(m)
        sn = np.zeros(m)
        cs = np.zeros(m)

        for i in range(m):
            diff_pos = x[i] - a_pos
            diff_neg = x[i] - a_neg
            sp[i] = np.sqrt(diff_pos @ diff_pos)
            sn[i] = np.sqrt(diff_neg @ diff_neg)
            cs[i] = sn[i] / (sp[i] + sn[i])

        pd.DataFrame(data=zip(sp, sn, cs), index=piv_.index, columns=["$S^*$", "$S^-$", "$C^*$"])
        def rank_according_to(data):
            ranks = rankdata(data).astype(int)
            ranks -= 1
            return piv_.index[ranks][::-1]
        
        cs_order = rank_according_to(cs)
        sp_order = rank_according_to(sp)
        sn_order = rank_according_to(sn)

        pd.DataFrame(data=zip(cs_order, sp_order, sn_order), index=range(1, m + 1), columns=["$C^*$", "$S^*$", "$S^-$"])
        print("The best candidate/alternative according to C* is ", cs_order[0])
        print("The preferences in descending order are ", np.array(cs_order))
        # rating = rating_data[['user_id', 'anime_id', 'rating']]
        # reader = Reader()
        # rating_df = Dataset.load_from_df(rating, reader)
        # svd = SVD()
        # trainset = rating_df.build_full_trainset()
        # svd.fit(trainset)
        # svd.predict(1, 356, 5)
        # rating_df = rating_data.sample(frac=1, random_state=73)

        # X = rating_df[['user_id', 'anime_id']].values
        # y = rating_df["rating"]

        # # Split
        # test_set_size = 1000#10k for test set
        # train_indices = rating_df.shape[0] - test_set_size 

        # X_train, X_test, y_train, y_test = (
        #     X[:train_indices],
        #     X[train_indices:],
        #     y[:train_indices],
        #     y[train_indices:],
        # )

        # print('> Train set ratings: {}'.format(len(y_train)))
        # print('> Test set ratings: {}'.format(len(y_test)))

        # X_train_array = [X_train[:, 0], X_train[:, 1]]
        # X_test_array = [X_test[:, 0], X_test[:, 1]]

        # def RecommenderNet():
        #     embedding_size = 128
            
        #     user = Input(name = 'user_id', shape = [1])
        #     user_embedding = Embedding(name = 'user_embedding',
        #                     input_dim = n_users, 
        #                     output_dim = embedding_size)(user)
            
        #     anime = Input(name = 'anime_id', shape = [1])
        #     anime_embedding = Embedding(name = 'anime_embedding',
        #                     input_dim = n_animes, 
        #                     output_dim = embedding_size)(anime)
            
        #     #x = Concatenate()([user_embedding, anime_embedding])
        #     x = Dot(name = 'dot_product', normalize = True, axes = 2)([user_embedding, anime_embedding])
        #     x = Flatten()(x)
 
        #     x = Dense(1, kernel_initializer='he_normal')(x)
        #     x = BatchNormalization()(x)
        #     x = Activation("sigmoid")(x)
            
        #     model = Model(inputs=[user, anime], outputs=x)
        #     model.compile(loss='binary_crossentropy', metrics=["mae", "mse"], optimizer='Adam')
            
        #     return model

        # model = RecommenderNet()
        # model.summary()

        # start_lr = 0.00001
        # min_lr = 0.00001
        # max_lr = 0.00005
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

        # checkpoint_filepath = './weights.h5'

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

        # ##fix
        # history = model.fit(
        #     x=X_train_array,
        #     y=y_train,
        #     batch_size=batch_size,
        #     epochs=20,
        #     verbose=1,
        #     validation_data=(X_test_array, y_test))

        # model.load_weights(checkpoint_filepath)

        # combine_movie_rating = rating_data.dropna(axis = 0, subset = ['Name'])
        # movie_ratingCount = (combine_movie_rating.
        #     groupby(by = ['Name'])['rating'].
        #     count().
        #     reset_index()
        #     [['Name', 'rating']]
        #     )
        # movie_ratingCount.head()

        # rating_data = combine_movie_rating.merge(movie_ratingCount, left_on = 'Name', right_on = 'Name', how = 'left')
        # rating_data = rating_data.drop(columns = "rating_x")
        # rating_data = rating_data.rename(columns={"rating_y": "rating"})

        # user_ids = rating_data["user_id"].unique().tolist()
        # user2user_encoded = {x: i for i, x in enumerate(user_ids)}
        # user_encoded2user = {i: x for i, x in enumerate(user_ids)}
        # rating_data["user"] = rating_data["user_id"].map(user2user_encoded)
        # n_users = len(user2user_encoded)

        # anime_ids = rating_data["anime_id"].unique().tolist()
        # anime2anime_encoded = {x: i for i, x in enumerate(anime_ids)}
        # anime_encoded2anime = {i: x for i, x in enumerate(anime_ids)}
        # rating_data["anime"] = rating_data["anime_id"].map(anime2anime_encoded)
        # n_animes = len(anime2anime_encoded)

        # print("Num of users: {}, Num of animes: {}".format(n_users, n_animes))
        # print("Min total rating: {}, Max total rating: {}".format(min(rating_data['rating']), max(rating_data['rating'])))

        # g = rating_data.groupby('user_id')['rating'].count()
        # top_users = g.dropna().sort_values(ascending=False)[:20]
        # top_r = rating_data.join(top_users, rsuffix='_r', how='inner', on='user_id')

        # g = rating_data.groupby('anime_id')['rating'].count()
        # top_animes = g.dropna().sort_values(ascending=False)[:20]
        # top_r = top_r.join(top_animes, rsuffix='_r', how='inner', on='anime_id')

        # pivot = pd.crosstab(top_r.user_id, top_r.anime_id, top_r.rating, aggfunc=np.sum)
        # pivot.fillna(0, inplace=True)
        # piviot_table = rating_data.pivot_table(index="Name",columns="user_id", values="rating").fillna(0)
        # piviot_table_matrix = csr_matrix(piviot_table.values)
        # model = NearestNeighbors(metric="cosine", algorithm="brute")
        # model.fit(piviot_table_matrix)

        # def predict():
        #     random_anime = np.random.choice(piviot_table.shape[0]) # This will choose a random anime name and our model will predict on it.

        #     query = piviot_table.iloc[random_anime, :].values.reshape(1, -1)
        #     distance, suggestions = model.kneighbors(query, n_neighbors=6)
            
        #     for i in range(0, len(distance.flatten())):
        #         if i == 0:
        #             print('Recommendations for {0}:\n'.format(piviot_table.index[random_anime]))
        #         else:
        #             print('{0}: {1}, with distance of {2}:'.format(i, piviot_table.index[suggestions.flatten()[i]], distance.flatten()[i]))
        # predict()
        return 'ok', 201


if __name__ == '__main__':
    app.secret_key='mysecret'
    app.run(host='0.0.0.0', port=5000, debug=True)