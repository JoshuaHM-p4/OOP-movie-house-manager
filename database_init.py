'''
Execute this script to create a database file named movie.db
which will manually enter a database with 4 tables and 4 rooms.
'''

import sqlite3

conn = sqlite3.connect('movie.db')
cursor = conn.cursor()

# room Table
conn.execute(
    '''CREATE TABLE IF NOT EXISTS room (
        id INTEGER PRIMARY KEY,
        cost REAL
    )'''
)


room = [(1, 100), (2, 200), (3, 300), (4, 400)] # manually entering 4 rooms, change the values if needed
cursor.executemany(
    '''INSERT INTO room (id, cost) VALUES (?, ?)''',
    room
)


# movie Table
conn.execute(
    '''CREATE TABLE IF NOT EXISTS movie (
        id INTEGER PRIMARY KEY,
        title VARCHAR(255),
        genre varchar(255),
        is_deleted BOOLEAN default 0,
        cost REAL
    )'''
)

# room_record Table

conn.execute('PRAGMA foreign_keys = ON')
conn.execute(
    '''CREATE TABLE IF NOT EXISTS room_record (
        id INTEGER PRIMARY KEY,
        room_id INTEGER,
        total_cost REAL,
        is_finished BOOLEAN,

        FOREIGN KEY (room_id) REFERENCES room(id)
    )
    '''
)

# room_movie_record
conn.execute(
    '''CREATE TABLE IF NOT EXISTS room_movie_record (
        id INTEGER PRIMARY KEY,
        movie_id INTEGER,
        room_record_id INTEGER,

        FOREIGN KEY (movie_id) REFERENCES movie(id),
        FOREIGN KEY (room_record_id) REFERENCES room_record(id)
    )
    '''
)

conn.commit()

