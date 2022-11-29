import sqlite3
import pandas as pd
import json


def create_df(row, field_name, pk_name, fk_name):
    df = pd.json_normalize(json.loads(row[field_name]))
    if df.size:
        df.insert(0, fk_name, row[pk_name])
    return df


credits = pd.read_csv('../db/tmdb_5000_credits.csv')
movies = pd.read_csv('../db/tmdb_5000_movies.csv')
cast = pd.concat(credits.apply(lambda x: create_df(
    x, 'cast', 'movie_id', 'movie_id'), axis=1).tolist())
crew = pd.concat(credits.apply(lambda x: create_df(
    x, 'crew', 'movie_id', 'movie_id'), axis=1).tolist())
genres = pd.concat(movies.apply(
    lambda x: create_df(x, 'genres', 'id', 'movie_id'), axis=1).tolist())
keywords = pd.concat(movies.apply(
    lambda x: create_df(x, 'keywords', 'id', 'movie_id'), axis=1).tolist())
production_companies = pd.concat(movies.apply(
    lambda x: create_df(x, 'production_companies', 'id', 'movie_id'), axis=1).tolist())
spoken_languages = pd.concat(movies.apply(
    lambda x: create_df(x, 'spoken_languages', 'id', 'movie_id'), axis=1).tolist())
production_countries = pd.concat(movies.apply(
    lambda x: create_df(x, 'production_countries', 'id', 'movie_id'), axis=1).tolist())
del credits
cast['appearance_order'] = cast['order']
cast = cast.drop(['cast_id', 'credit_id', 'id', 'order'], axis=1)
crew = crew.drop(['credit_id', 'id'], axis=1)
genres = genres.drop(['id'], axis=1)
keywords = keywords.drop(['id'], axis=1)
production_companies = production_companies.drop(['id'], axis=1)
movies = movies.drop(['genres', 'keywords', 'production_companies',
                      'spoken_languages', 'production_countries', 'overview', 'tagline', 'homepage', 'original_title'], axis=1)

connection = sqlite3.connect('../db/movies.db')
with open('../db/schema.sql') as f:
    connection.executescript(f.read())

movies.to_sql("movies", connection, if_exists='replace', index=False)
production_companies.to_sql("production_companies",
                            connection, if_exists='replace', index=False)
cast.to_sql("cast", connection, if_exists='replace', index=False)
crew.to_sql("crew", connection, if_exists='replace', index=False)
genres.to_sql("genres", connection, if_exists='replace', index=False)
keywords.to_sql("keywords", connection, if_exists='replace', index=False)

connection.commit()
connection.close()
