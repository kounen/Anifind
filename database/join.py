import pandas as pd

columns1 = ['anime_id', 'Name']
columns2 = ['user_id' ,'anime_id', 'rating']
columns3 = ["user_id" ,"Name", "rating"]

animefront = ["anime_id", "Name", "Score", "Genres", "English name", "Episodes"]

# # reading two csv files
anime = pd.read_csv('anime.csv', index_col=False)
anime_mini = anime[animefront]
anime_mini.to_csv("anime_front.csv", index=False)

# animelist = pd.read_csv('animelist.csv', index_col=False)
# animelist = animelist[columns2]
# animelist.to_csv("animelist_mini.csv", index=False)

# anime_data = pd.read_csv('anime_mini.csv', index_col=False)
animelist_data = pd.read_csv('animelist_mini.csv', index_col=False, nrows=999999)
animelist_data.to_csv("rs.csv", index=False)
  
# # using merge function by setting how='inner'
# data = pd.merge(animelist_data, anime_data,
#                    on='anime_id', 
#                    how='left',
#                    )

# data.insert(0, 'id', range(1, 1 + len(data)))
# data = data[['id', 'user_id', 'Name', 'rating']]
# data.to_csv("final.csv", index=False)

# final = pd.read_csv('final.csv', index_col=False, nrows=999999)
# final.to_csv("final_mini.csv", index=False)