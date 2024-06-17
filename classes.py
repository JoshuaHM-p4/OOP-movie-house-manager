class Movie:
    def __init__(self, id: int, title: str, genre: str, cost: float):
        self.__id = id
        self.__title = title
        self.__genre = genre
        self.__cost = cost

    @property  # getter for id
    def id(self) -> int:
        return self.__id

    @id.setter # setter for id
    def id(self, id: int):
        self.__id = id

    @property  # getter for title
    def title(self) -> str:
        return self.__title

    @title.setter # setter for title
    def title(self, title: str):
        self.__title = title

    @property  # getter for genre
    def genre(self) -> str:
        return self.__genre

    @genre.setter # setter for genre
    def genre(self, genre: str):
        self.__genre = genre

    @property  # getter for cost
    def cost(self) -> float:
        return self.__cost

    @cost.setter # setter for cost
    def cost(self, cost: float):
        self.__cost = cost

    def __str__(self) -> str:
        return f"{self.__id} - {self.__title}"

class Room:
    def __init__(self, id: int, cost: float):
        self.__id = id
        self.__cost = cost

    @property  # getter for id
    def id(self) -> IndentationError:
        return self.__id

    @id.setter # setter for id
    def id(self, id: int):
        self.__id = id

    @property  # getter for cost
    def cost(self) -> float:
        return self.__cost

    @cost.setter # setter for cost
    def cost(self, cost: float):
        self.__cost = cost

    def __str__(self) -> str:
        return f"{self.__id}"

class Record:
    def __init__(self, id: int, room_id: int, is_finished:bool, total_cost: float, movies: list[Movie]):
        self.__id = id
        self.__room_id = room_id
        self.__is_finished = is_finished
        self.__total_cost = total_cost
        self.__movies = movies

    @property  # getter for id
    def id(self):
        return self.__id

    @id.setter # setter for id
    def id(self, id: int):
        self.__id = id

    @property  # getter for room_id
    def room_id(self) -> int:
        return self.__room_id

    @room_id.setter # setter for room_id
    def room_id(self, room_id: int):
        self.__room_id = room_id

    @property  # getter for is_finished
    def is_finished(self):
        return self.__is_finished

    @is_finished.setter
    def is_finished(self, is_finished: bool):
        self.__is_finished = is_finished

    @property  # getter for total_cost
    def total_cost(self) -> float:
        return self.__total_cost

    @total_cost.setter # setter for total_cost
    def total_cost(self, total_cost: float):
        self.__total_cost = total_cost

    @property  # getter for movies
    def movies(self) -> list[Movie]:
        return self.__movies

    @movies.setter # setter for movies
    def movies(self, movies: list[Movie]):
        self.__movies = movies

    def __str__(self) -> str:
        return f"Record ID: {self.__id} - Room_id: {self.__room_id} - Total Cost: P{self.__total_cost} - Finished: {self.__is_finished}"



if __name__ == "__main__":
    movie1 = Movie(1, "The Shawshank Redemption", "Drama", 10)
    print(movie1)
    movie1.id = 2
    print(movie1)
