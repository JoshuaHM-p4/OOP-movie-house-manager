'''
CMPE 103 - Lab Activity 7-  Tkinter Application with DB Activity
    - Create a Tkinter application that allows the user to register movies and rooms
    - Project for the Completion of the CMPE 103 Course: Object-Oriented Programming
    - Initial work - Joshua Mistal - [JoshuaHM-p4]
    - Date Accomplished: 2024-6-17
'''

import tkinter as tk
from tkinter import messagebox
from database_manager import MovieHouseDatabaseManager
from classes import Movie, Record, Room
from typing import List
import os

class RecordWindow(tk.Toplevel):
    def __init__(self, room: Room, db_manager: MovieHouseDatabaseManager, record: Record):
        self.room: Room = room
        self.db_manager = db_manager
        self.record = record

        super().__init__()
        self.title(f"Room {self.room.id}")
        self.geometry("640x400")
        self.configure(padx=15, pady=15)

        for i in range(2): # Configure 2 rows and 2 columns to expand equally
            self.rowconfigure(i, weight=1)
            self.columnconfigure(i, weight=1)

        # Note: You don't need to use self in the following widgets since they are not being accessed outside of this class

        ################################################ MOVIES SECTION ################################################
        self.movies_frame = tk.Frame(self)
        self.movies_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)  # Add padx and pady for padding

        self.movies_label = tk.Label(self.movies_frame, text="Movies")
        self.movies_label.pack(side="top", fill="x", expand=True)

        self.movies_list = tk.Listbox(self.movies_frame)
        self.movies_list.pack(side="top", fill="both", expand=True)

        self.add_movie_button = tk.Button(self.movies_frame, text="Add Movie", command=self.add_movie, width = 25, state=tk.DISABLED)
        self.add_movie_button.pack(side="top")

        self.movies_list.bind("<<ListboxSelect>>", self.add_movie_button_state)

        ################################################ MOVIES TO WATCH SECTION ################################################
        self.movies_to_view_frame = tk.Frame(self)
        self.movies_to_view_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)  # Add padx and pady for padding

        self.movies_to_watch_label = tk.Label(self.movies_to_view_frame, text="Movies to Watch")
        self.movies_to_watch_label.pack(side="top", fill="x", expand=True)

        self.movies_to_view_list = tk.Listbox(self.movies_to_view_frame)
        self.movies_to_view_list.pack(side="top", fill="both", expand=True)

        self.remove_movie_button = tk.Button(self.movies_to_view_frame, text="Remove Movie", command=self.remove_movie, width = 25, state=tk.DISABLED)
        self.remove_movie_button.pack(side="top")

        self.movies_to_view_list.bind("<<ListboxSelect>>", self.remove_movie_button_state)

        ################################################ ROOM ACTION BUTTTONS ################################################
        self.room_action_frame = tk.Frame(self)
        self.room_action_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)  # Add padx and pady for padding
        self.room_action_frame.columnconfigure(0, weight=1)
        self.room_action_frame.rowconfigure(0, weight=1)

        self.total_cost = tk.StringVar()
        self.total_cost_label = tk.Label(self.room_action_frame, textvariable=self.total_cost)
        self.total_cost_label.pack(side="top", fill="both")

        self.check_frame = tk.Frame(self.room_action_frame)
        self.check_frame.pack(side="top", expand=True, pady=10)
        self.check_frame.columnconfigure(0, weight=1)
        self.check_frame.columnconfigure(1, weight=1)

        self.check_in_button = tk.Button(self.check_frame, text="Check In", command=self.check_in, width = 25)
        self.check_in_button.grid(row=0, column=0, padx=10)

        self.check_out_button = tk.Button(self.check_frame, text="Check Out", command=self.check_out, width = 25)
        self.check_out_button.grid(row=0, column=1, padx=10)

        ################################################################################################

        # Update Elements Upon Load
        self.load_listboxes()
        self.update_total_cost()
        self.check_buttons_state()

        print(self.db_manager.retrieve_record(self.room.id))


    def load_listboxes(self) -> None:
        '''Loads the listboxes with the movies and movies to view fetched from the database'''

        self.movies_list.delete(0, tk.END)
        self.movies_to_view_list.delete(0, tk.END)

        movies = self.db_manager.retrieve_movies()

        movie_titles = [movie.title for movie in self.record.movies]
        unchecked_movies = map(str, [movie for movie in movies if movie.title not in movie_titles])
        self.movies_list.insert(tk.END, *unchecked_movies)

        if self.record.movies:
            self.movies_to_view_list.insert(tk.END, *self.record.movies)

    def update_total_cost(self):
        # Update total cost label
        if self.record.total_cost:
            self.total_cost.set(f"Total Cost: P{self.record.total_cost:,.2f}")
        elif self.record.total_cost == 0 and self.record.is_finished:
            selected_movies_id = [movie_id.split("-")[0].strip() for movie_id in self.movies_to_view_list.get(0, tk.END)]
            movies = self.db_manager.retrieve_movies(movie_id=selected_movies_id)
            new_total_cost = self.room.cost
            if selected_movies_id:
                new_total_cost += sum([movie.cost for movie in movies])
            self.total_cost.set(f"Total Cost: P{new_total_cost:,.2f}")
        else:
            self.total_cost.set("Total Cost: P0.00")

    def check_buttons_state(self):
        # Update the check buttons state
        if self.record.is_finished and self.movies_to_view_list.size() > 0:
            self.check_out_button.config(state=tk.DISABLED)
            self.check_in_button.config(state=tk.NORMAL)
        elif not self.record.is_finished and self.movies_to_view_list.size() > 0:
            self.check_out_button.config(state=tk.NORMAL)
            self.check_in_button.config(state=tk.DISABLED)
        else:
            self.check_out_button.config(state=tk.DISABLED)
            self.check_in_button.config(state=tk.DISABLED)

    def check_in(self):
        selected_movies_id = [movie_id.split("-")[0].strip() for movie_id in self.movies_to_view_list.get(0, tk.END)]
        movies = self.db_manager.retrieve_movies(movie_id=selected_movies_id)

        if self.db_manager.check_in(self.room.id, movies):
            self.record = self.db_manager.retrieve_record(self.room.id)
            messagebox.showinfo("Success", "Check in successful")
        else:
            messagebox.showerror("Error", "Check in failed")

        self.update_total_cost()
        self.load_listboxes()
        self.check_buttons_state()

    def check_out(self):
        if self.db_manager.check_out(self.record.id):
            self.record = self.db_manager.retrieve_record(self.room.id)
            messagebox.showinfo("Success", "Check out successful")
        else:
            messagebox.showerror("Error", "Check out failed")
        self.update_total_cost()
        self.load_listboxes()
        self.check_buttons_state()

    def add_movie(self) -> None:
        selected_listbox = self.movies_list.curselection() # select the current movie selected from list

        if selected_listbox:
            selected_movie = self.movies_list.get(selected_listbox) # get the selected movie
            self.movies_to_view_list.insert(tk.END, selected_movie)
            self.movies_list.delete(selected_listbox)
            self.check_buttons_state()
            self.update_total_cost()
        else:
            messagebox.showerror("Error", "No movie selected")
            return

    def remove_movie(self):
        selected_listbox = self.movies_to_view_list.curselection()

        if selected_listbox:
            selected_movie = self.movies_to_view_list.get(selected_listbox)
            self.movies_list.insert(tk.END, selected_movie)
            self.movies_to_view_list.delete(selected_listbox)
            self.check_buttons_state()
            self.update_total_cost()
        else:
            messagebox.showerror("Error", "No movie selected")
            return

    def add_movie_button_state(self, event) -> None:
        selected_movie = self.movies_list.curselection()
        if selected_movie and self.check_out_button.cget("state") != tk.NORMAL:
            self.add_movie_button.config(state=tk.NORMAL)
        else:
            self.add_movie_button.config(state=tk.DISABLED)

    def remove_movie_button_state(self, event) -> None:
        selected_movie = self.movies_to_view_list.curselection()
        if selected_movie and self.record.is_finished:
            self.remove_movie_button.config(state=tk.NORMAL)
        else:
            self.remove_movie_button.config(state=tk.DISABLED)

class MovieHouseWindow(tk.Tk):
    def __init__(self, database_file_name: str):
        self._database_manager = MovieHouseDatabaseManager(database_file_name)

        super().__init__()

        self.title("Movie House")
        self.geometry("640x400")
        self.configure(padx=15, pady=15)

        # Frames
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side="left", fill="both", expand=True)

        ################################################ REGISTER SECTION ################################################
        self.register_lf = tk.LabelFrame(self.left_frame, text="Register")
        self.register_lf.pack(side="top", fill="both", expand=True)

        # Entry Frame (holds the entries and add movie button)
        self.register_input_frame = tk.Frame(self.register_lf)
        self.register_input_frame.pack(expand=True)


        # register entries
        self.title_label = tk.Label(self.register_input_frame, text="Movie Title")
        self.movie_title_entry = tk.Entry(self.register_input_frame)
        self.title_label.grid(row=0, column=0, sticky='w')
        self.movie_title_entry.grid(row=0, column=1, sticky='ew')

        self.genre_label = tk.Label(self.register_input_frame, text="Genre")
        self.genre_entry = tk.Entry(self.register_input_frame)
        self.genre_label.grid(row=1, column=0, sticky='w')
        self.genre_entry.grid(row=1, column=1, sticky='ew')

        self.cost_label = tk.Label(self.register_input_frame, text="Cost")
        self.cost_entry = tk.Entry(self.register_input_frame)
        self.cost_label.grid(row=2, column=0, sticky='w')
        self.cost_entry.grid(row=2, column=1, sticky='ew')

        # add movie button
        self.add_movie_button = tk.Button(self.register_input_frame, text="Add Movie", command=self.add_movie)
        self.add_movie_button.grid(row=3, column=0, columnspan=2, sticky='ew')

        ################################################ MOVIES SECTION ################################################
        self.movies_lf = tk.LabelFrame(self.left_frame, text="Movies", padx=15, pady=15)
        self.movies_lf.pack(side="bottom", fill="both", expand=True)
        self.movies_lf.columnconfigure(0, weight=1)
        self.movies_lf.columnconfigure(1, weight=1)
        self.movies_lf.rowconfigure(0, weight=1)
        self.movies_lf.rowconfigure(1, weight=1)

        # listboxes of movies
        self.movies_list = tk.Listbox(self.movies_lf, selectmode=tk.SINGLE)
        self.movies_list.grid(row=0, column=0, sticky='nsew')

        # bind the remove_movie_button to the selected movie in movies_listbox
        self.movies_list.bind("<<ListboxSelect>>", self.update_remove_button_state)

        # remove movie button
        self.remove_movie_button = tk.Button(self.movies_lf, text="Remove Movie", command=self.remove_movie, state=tk.DISABLED)
        self.remove_movie_button.grid(row=1, column=0, sticky='ew')

        # checkboxes for filteirng movies list
        self.filter_container = tk.Frame(self.movies_lf, padx=10, pady=10)
        self.filter_container.grid(row=0, column=1, sticky='nsew', rowspan=2)
        self.genre_filter_label = tk.Label(self.filter_container, text="Genres")
        self.genre_filter_label.pack(side="top", fill="both")

        self.adventure_checked = tk.BooleanVar()
        self.comedy_checked = tk.BooleanVar()
        self.fantasy_checked = tk.BooleanVar()
        self.romance_checked = tk.BooleanVar()
        self.tragedy_checked = tk.BooleanVar()

        self.checkbox_container = tk.Frame(self.filter_container)
        self.checkbox_container.pack(side='top', fill='both', expand=True)

        self.adventure_checkbox = tk.Checkbutton(self.checkbox_container, text="Adventure", command=self.filter_movies, variable=self.adventure_checked)
        self.adventure_checkbox.grid(row=0, column=0, sticky='w')

        self.comedy_checkbox = tk.Checkbutton(self.checkbox_container, text="Comedy", command=self.filter_movies, variable=self.comedy_checked)
        self.comedy_checkbox.grid(row=1, column=0, sticky='w')

        self.fantasy_checkbox = tk.Checkbutton(self.checkbox_container, text="Fantasy", command=self.filter_movies, variable=self.fantasy_checked)
        self.fantasy_checkbox.grid(row=2, column=0, sticky='w')

        self.romance_checkbox = tk.Checkbutton(self.checkbox_container, text="Romance", command=self.filter_movies, variable=self.romance_checked)
        self.romance_checkbox.grid(row=3, column=0, sticky='w')

        self.tragedy_checkbox = tk.Checkbutton(self.checkbox_container, text="Tragedy", command=self.filter_movies, variable=self.tragedy_checked)
        self.tragedy_checkbox.grid(row=4, column=0, sticky='w')

        ################################################ ROOMS SECTION ################################################
        self.rooms_lf = tk.LabelFrame(self, text="Rooms", padx=15, pady=15)
        self.rooms_lf.pack(side="right", fill="both", expand=True)
        # rooms button
        for i in range(1, 5):
            room_button = tk.Button(self.rooms_lf, text=f"Room {i}", command=lambda i=i: self.open_room(i))
            room_button.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.update_list() # update the movies list (saka mo na gawin ito)

    def update_remove_button_state(self, event):
        selected_movie = self.movies_list.curselection()
        if selected_movie:
            self.remove_movie_button.config(state=tk.NORMAL)
        else:
            self.remove_movie_button.config(state=tk.DISABLED)

    def add_movie(self):
        # adds movie with the given title, genre, and cost to the database
        title = self.movie_title_entry.get()
        genre = self.genre_entry.get()
        cost = self.cost_entry.get()

        # Check if any of the fields are empty then set to red
        if not title:
            self.title_label.config(fg="red")
            return
        if not genre:
            self.genre_label.config(fg="red")
            return
        if not cost:
            self.cost_label.config(fg="red")
            return

        # Check if the cost is a valid float
        try:
            cost = float(cost)
        except ValueError:
            # Set the cost label to red
            self.cost_label.config(fg="red")
            return

        # Check if the genre is valid
        valid_genres = ["Action", "Adventure", "Comedy", "Drama", "Fantasy", "Horror", "Romance", "Sci-Fi", "Thriller"]
        if genre not in valid_genres:
            self.genre_label.config(fg="red")
            return

        # Register the movie and update the list
        if self._database_manager.register_movie(title, genre, cost):
            self.update_list()
        else:
            self.movie_title_entry.delete(0, tk.END)
            self.genre_entry.delete(0, tk.END)
            self.cost_entry.delete(0, tk.END)
            messagebox.showerror("Error", "Failed to register movie")

        # Revert the labels to normal color
        self.title_label.config(fg="black")
        self.genre_label.config(fg="black")
        self.cost_label.config(fg="black")


    def remove_movie(self):
        selected_listbox = self.movies_list.curselection()

        if selected_listbox:
            listbox_index = selected_listbox[0]
            selected_movie_id = self.movies_list.get(listbox_index).split("-")[0].strip()

            # Remove the selected movie from the list
            self.movies_list.delete(listbox_index)

            # Delete movie from database
            self._database_manager.remove_movie(selected_movie_id)

            self.update_list()
        else:
            # No movie selected, display an error message or handle the case accordingly
            messagebox.showerror("Error", "No movie selected")

    def update_list(self):
        # update the movies list
        self.movies_list.delete(0, tk.END)
        movies = self._database_manager.retrieve_movies()
        for movie in movies:
            self.movies_list.insert(tk.END, movie)

    def open_room(self, room_id: int):
        # retrieve the room from where the button is clicked
        room = self._database_manager.retrieve_rooms()[room_id-1]
        record = self._database_manager.retrieve_record(room_id)
        record_window = RecordWindow(room, self._database_manager, record)
        record_window.mainloop()

    def filter_movies(self):
        # filter movies list based on the checkboxes

        genres = []
        if self.adventure_checked.get():
            genres.append("Adventure")
        if self.comedy_checked.get():
            genres.append("Comedy")
        if self.fantasy_checked.get():
            genres.append("Fantasy")
        if self.romance_checked.get():
            genres.append("Romance")
        if self.tragedy_checked.get():
            genres.append("Tragedy")


        movies = self._database_manager.retrieve_movies(genres=genres)
        self.movies_list.delete(0, tk.END)
        for movie in movies:
            self.movies_list.insert(tk.END, movie)

if __name__ == "__main__":
    if not os.path.exists("movie.db"):
        messagebox.showerror("Error", "Database file not found. Initialize the database first. Run database_init.py")
    else:
        window = MovieHouseWindow("movie.db")
        window.mainloop()
