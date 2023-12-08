import os
import random

from faker import Faker
from faker.providers import BaseProvider

from logger import logger
from models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


class GenreProvider(BaseProvider):
    """
    Custom provider for generating random film genres.

    """
    original_genres = [
        "Action", "Comedy", "Drama", "Fantasy", "Horror", "Mystery",
        "Romance", "Thriller", "Western", "Crime", "Detective",
        "Science Fiction", "Biography", "Historical", "War",
        "Musical", "Adventure", "Family", "Sport", "Animation",
        "Documentary", "Experimental", "Music", "Short Film",
        "Art House", "Author Cinema", "Disaster", "Cyberpunk", "Noir", "Post-Apocalyptic",
        "Psychological", "Romantic Comedy", "Superhero", "Teen", "Supernatural",
        "Political", "Legal", "Medical", "Mockumentary", "Nature",
        "News", "Reality TV", "Road Movie", "Social", "Urban",
        "Vampire", "Zombie", "Time Travel", "Epic", "Found Footage"
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.genres = self.original_genres.copy()
        random.shuffle(self.genres)

    def genre(self):
        """
        Pop a random genre from the available list.

        :return: A random genre.
        """
        if self.genres:
            return self.genres.pop()
        else:
            raise IndexError("No more genres available.")

    def max_genres(self):
        """
        Get the maximum number of genres available.

        :return: Number of genres.
        """
        return len(self.original_genres)


fake = Faker("en_US")
fake.add_provider(GenreProvider)


def generate_film_work() -> FilmWork:
    """
    Generate a random film work.

    :return: A FilmWork object populated with random data.
    """
    certificate = random.choices([fake.bothify(text="??-###"), None], weights=[70, 30])[0]
    file_path = random.choices([fake.file_path(), None], weights=[70, 30])[0]

    return FilmWork(
        title=fake.catch_phrase(),
        description=fake.text(),
        creation_date=fake.date_between(start_date='-80y', end_date='today'),
        certificate=certificate,
        file_path=file_path,
        rating=random.uniform(0, 10),
        type=random.choice(['movie', 'tv_show'])
    )


def generate_person() -> Person:
    """
    Generate a random person.

    :return: A Person object populated with random data.
    """
    gender = random.choice(['M', 'F'])
    full_name = fake.name_male() if gender == 'M' else fake.name_female()
    return Person(
        full_name=full_name,
        gender=gender
    )


def generate_genre() -> Genre:
    """
    Generate a random genre.

    :return: A Genre object populated with random data.
    """
    return Genre(
        name=fake.genre(),
        description=fake.sentence()
    )


def generate_data():
    """
    Generate random data for films, persons, and genres.

    :return: A dictionary containing lists of generated data for each table.
    """
    films_count = int(os.environ.get('FILMS_COUNT'))
    persons_count = int(os.environ.get('PERSONS_COUNT'))
    genres_count = min(fake.max_genres(), int(os.environ.get('GENRES_COUNT')))

    logger.info(f"Generate {films_count} films.")
    film_works = [generate_film_work() for _ in range(films_count)]
    logger.info("Finished")
    logger.info(f"Generate {persons_count} persons.")
    persons = [generate_person() for _ in range(persons_count)]
    logger.info("Finished")
    logger.info(f"Generate {genres_count} genres.")
    genres = [generate_genre() for _ in range(genres_count)]
    logger.info("Finished")
    genre_film_works = []
    for film_work in film_works:
        selected_genres = random.sample(genres, k=random.randint(2, 5))
        for genre in selected_genres:
            genre_film_works.append(GenreFilmWork(film_work_id=film_work.id, genre_id=genre.id))

    person_film_works = []
    persons_role = [(person, role) for person in persons for role in ['actor', 'director', 'writer']]
    for film_work in film_works:
        selected_persons_roles = random.sample(persons_role, k=random.randint(5, 15))
        for person, role in selected_persons_roles:
            person_film_works.append(
                PersonFilmWork(film_work_id=film_work.id, person_id=person.id, role=role)
            )

    return {
        'film_work': film_works,
        'person': persons,
        'genre': genres,
        'genre_film_work': genre_film_works,
        'person_film_work': person_film_works
    }


class FakeDataGenerator:
    """
    Class for generating and batching fake data.

    :param data: Dictionary containing lists of data for each table.
    :param batch_size: Size of each data batch to be generated.
    """
    def __init__(self, data: dict, batch_size: int):
        self.data = data
        self.batch_size = batch_size

    def get_generator(self, table):
        """
        Generate data in batches for a specific table.

        :param table: The name of the table for which to generate data.
        :yield: A batch of data for the specified table.
        """
        data = self.data[table]
        for i in range(0, len(data), self.batch_size):
            yield data[i: i + self.batch_size]
