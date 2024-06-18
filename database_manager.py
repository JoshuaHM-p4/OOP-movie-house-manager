import sqlite3
from typing import List, Any, Union, Tuple
from classes import Record, Movie, Room

class MovieHouseDatabaseManager:
    def __init__(self, database_file: str):
        self.database_file = database_file

    def get_connection(self):
        return sqlite3.connect(self.database_file)

    def register_movie(self, title: str, genre: str, cost: float) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
            '''INSERT INTO movie (title, genre, cost) VALUES (?, ?, ?)''',
            (title, genre, cost)
            )
            conn.commit()

            return True
        except Exception as e:
            print(f"Error registering movie: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def remove_movie(self, id: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''UPDATE movie SET is_deleted = 1 WHERE id = ?''',
            (id,)
        )
        conn.commit()
        conn.close()

    def retrieve_movies(self, movie_id: list[int] | None = None, genres: list[str] | None = None) -> list[Movie]:

        if movie_id is None:
            movie_id = []
        if genres is None:
            genres = []

        conn = self.get_connection()
        cursor = conn.cursor()

        if movie_id: # if id is provided, fetch movies by id
            placeholders = ','.join(['?']*len(movie_id))
            cursor.execute(
                f'''SELECT id, title, genre, cost FROM movie WHERE id IN ({placeholders}) AND is_deleted = 0''',
                movie_id
            )
        elif genres: # fetch movies by genre
            placeholders = ','.join(['?']*len(genres)) # returns ?,?,?..n times
            cursor.execute(
                f'''SELECT id, title, genre, cost FROM movie WHERE genre IN ({placeholders}) AND is_deleted = 0''',
                genres
            )
        else: # if no genres are provided, fetch all movies
            cursor.execute(
                '''SELECT id, title, genre, cost FROM movie WHERE is_deleted = 0'''
            )

        movies = cursor.fetchall()
        conn.close()

        # Convert fetched movies into a list of Movie objects
        movie_list = [Movie(*movie_data) for movie_data in movies]

        return movie_list

    def retrieve_rooms(self) -> list[Room]:
        # retrieves all rooms from the database, and returns a list of Movie

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''SELECT * FROM room'''
        )

        rooms = cursor.fetchall()
        conn.close()

        rooms_list = [Room(*room_data) for room_data in rooms]
        return rooms_list

    def retrieve_record(self, room_id) -> Record:
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Retrieve the LATEST ROOM RECORD that is NOT finished
            cursor.execute('''
                SELECT id, room_id, total_cost, is_finished
                FROM room_record
                WHERE room_id = ?
                AND is_finished = 0
                ORDER BY id DESC
                LIMIT 1
            ''', (room_id,))

            room_record_data = cursor.fetchone() # fetches the latest record

            if room_record_data:
                record_id, room_id, total_cost, is_finished = room_record_data # unpack the record data

                # Retrieve associated movies for the room record
                cursor.execute('''
                    SELECT m.id, m.title, m.genre, m.cost FROM movie m
                    JOIN room_movie_record r ON m.id = r.movie_id
                    WHERE r.room_record_id = ?
                ''', (record_id,)) # Join clause links the movie table to the room_movie_record table

                movies_data = cursor.fetchall()
                movies = [Movie(*movie_data) for movie_data in movies_data]

                # Close the cursor and connection
                cursor.close()
                conn.close()

                return Record(id=record_id, room_id=room_id, total_cost=total_cost, is_finished=bool(is_finished),  movies=movies)
            else:
                # No record found, return new empty Record object and empty list of movies
                cursor.close()
                conn.close()

                return Record(id=0, room_id=room_id, total_cost=0.0, is_finished=True, movies=[])

        except Exception as e:
            print(f"Error retrieving record: {e}")
            # Close the cursor and connection in case of error
            cursor.close()
            conn.close()
            return None

    def check_in(self, room_id: int, movies: list[Movie]) -> bool:
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Begin transaction
            cursor.execute('BEGIN TRANSACTION')

            # Get the room cost
            cursor.execute(
                '''SELECT cost FROM room WHERE id = ?''',
                (room_id,)
            )
            room_cost = cursor.fetchone()[0]

            # Insert into room_record
            cursor.execute(
                '''INSERT INTO room_record (room_id, total_cost, is_finished) VALUES (?, ?, ?)''',
                (room_id, sum([movie.cost for movie in movies])+room_cost, 0) # (id of movie, sum of all movie costs, is_finished = 0)
            )

            # Retrieve the auto-generated ID
            room_record_id = cursor.lastrowid

            # Insert into room_movie_record for each movie
            for movie in movies:
                cursor.execute(
                    '''INSERT INTO room_movie_record (movie_id, room_record_id) VALUES (?, ?)''',
                    (movie.id, room_record_id)
                )

            conn.commit() # commit the changes to the database

            return True
        except Exception as e:
            print(f"Error creating room record: {e}")
            conn.rollback()  # Rollback changes on error
            return False
        finally:
            cursor.close()
            conn.close()

    def check_out(self, id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                '''UPDATE room_record SET is_finished = 1 WHERE id = ?''',
                (id,)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error checking out: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()