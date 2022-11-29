DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS production_companies;
DROP TABLE IF EXISTS cast;
DROP TABLE IF EXISTS crew;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS keywords;
DROP TABLE IF EXISTS production_companies;

CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    budget INTEGER,
    original_language TEXT,
    popularity FLOAT,
    release_date TIMESTAMP,
    revenue INTEGER,
    runtime FLOAT,
    status TEXT,
    title TEXT,
    vote_average TEXT,
    vote_count INTEGER
);

CREATE TABLE production_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER,
    name TEXT,
    FOREIGN KEY(movie_id) REFERENCES movie(id)
);

CREATE TABLE cast (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER,
    character TEXT,
    gender INTEGER,
    name TEXT,
    appearance_order INTEGER,
    FOREIGN KEY(movie_id) REFERENCES movie(id)
);

CREATE TABLE crew (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER,
    department TEXT,
    gender INTEGER,
    job TEXT,
    name TEXT,
    FOREIGN KEY(movie_id) REFERENCES movie(id)
);

CREATE TABLE genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER,
    name TEXT,
    FOREIGN KEY(movie_id) REFERENCES movie(id)
);

CREATE TABLE keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER,
    name TEXT,
    FOREIGN KEY(movie_id) REFERENCES movie(id)
);