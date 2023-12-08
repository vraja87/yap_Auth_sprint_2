
person_id = {
    200: {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "examples": {
                    "Single Film Example": {
                        "value": {
                            "uuid": "12345678-1234-5678-1234-567812345678",
                            "full_name": "Leonardo DiCaprio",
                            "films": [
                                {
                                    "uuid": "8cf5ae36-b0e9-4b2b-8d6d-659a5cdfe5c5",
                                    "roles": ["Actor"]
                                }
                            ]
                        }
                    },
                    "Multiple Films Example": {
                        "value": {
                            "uuid": "12345678-1234-5678-1234-567812345678",
                            "full_name": "Christopher Nolan",
                            "films": [
                                {
                                    "uuid": "8cf5ae36-b0e9-4b2b-8d6d-659a5cdfe5c5",
                                    "roles": ["Director", "Writer"]
                                },
                                {
                                    "uuid": "50998400-cb08-4cd1-bf07-4c7032560533",
                                    "roles": ["Director"]
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
}


person_film = {
    200: {
        "description": "Successful Response",
        "content": {
            "application/json": {
                "examples": {
                    "Blockbusters": {
                        "value": [
                            {
                                "uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                                "title": "Inception",
                                "imdb_rating": 8.8
                            },
                            {
                                "uuid": "550e8400-e29b-41d4-a716-446655440000",
                                "title": "The Dark Knight",
                                "imdb_rating": 9.0
                            },
                            {
                                "uuid": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                                "title": "The Matrix",
                                "imdb_rating": 8.7
                            }
                        ]
                    },
                    "No IMDb Rating": {
                        "value": [
                            {
                                "uuid": "6ba7b814-9dad-11d1-80b4-00c04fd430c1",
                                "title": "Indie Film No One Has Seen",
                                "imdb_rating": None
                            }
                        ]
                    }
                }
            }
        }
    }
}


person_search = {
    200: {
        "description": "Successful Search Response",
        "content": {
            "application/json": {
                "examples": {
                    "Multiple Results": {
                        "value": [
                            {
                                "uuid": "1d490d10-5c46-4c45-9a4a-36f10d7b172b",
                                "full_name": "Robert De Niro",
                                "films": [
                                    {
                                        "uuid": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                                        "roles": ["Actor"]
                                    },
                                    {
                                        "uuid": "550e8400-e29b-41d4-a716-446655440000",
                                        "roles": ["Actor"]
                                    }
                                ]
                            },
                            {
                                "uuid": "c3d8d6a1-7ce9-4499-a865-8d8dcd0dbf66",
                                "full_name": "Robert Downey Jr.",
                                "films": [
                                    {
                                        "uuid": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                                        "roles": ["Actor"]
                                    },
                                    {
                                        "uuid": "6ba7b811-9dad-11d1-80b4-00c04fd430c9",
                                        "roles": ["Actor"]
                                    }
                                ]
                            }
                        ]
                    },
                    "Single Result": {
                        "value": [
                            {
                                "uuid": "c8a0c82d-0647-4508-8d11-4dd9c3a4ed20",
                                "full_name": "Roberto Benigni",
                                "films": [
                                    {
                                        "uuid": "6ba7b812-9dad-11d1-80b4-00c04fd430c0",
                                        "roles": ["Actor", "Director"]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
    }
}


genres = {
    200: {
        "description": "Successful Retrieval of Genres",
        "content": {
            "application/json": {
                "examples": {
                    "List genres": {
                        "value": [
                            {
                                "uuid": "550e8400-e29b-41d4-a716-446655440001",
                                "name": "Action"
                            },
                            {
                                "uuid": "550e8400-e29b-41d4-a716-446655440002",
                                "name": "Comedy"
                            }
                        ]
                    }
                }
            }
        }
    }
}


genre = {
    200: {
        "description": "Successful Retrieval of a Single Genre",
        "content": {
            "application/json": {
                "examples": {
                    "Genre": {
                        "value": {
                            "uuid": "550e8400-e29b-41d4-a716-446655440001",
                            "name": "Action"
                        }
                    }
                }
            }
        }
    }
}

film_details = {
    200: {
        "description": "Successful Retrieval of Film Details",
        "content": {
            "application/json": {
                "examples": {
                    "Blockbuster Film": {
                        "value": {
                            "uuid": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "The Matrix",
                            "imdb_rating": 8.7,
                            "description": "A computer hacker learns from mysterious rebels about the true nature"
                                           " of his reality and his role in the war against its controllers.",
                            "genre": [
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440001",
                                    "name": "Action"
                                },
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440002",
                                    "name": "Sci-Fi"
                                }
                            ],
                            "actors": [
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440003",
                                    "full_name": "Keanu Reeves"
                                }
                            ],
                            "writers": [
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440004",
                                    "full_name": "Lana Wachowski"
                                },
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440005",
                                    "full_name": "Lilly Wachowski"
                                }
                            ],
                            "directors": [
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440004",
                                    "full_name": "Lana Wachowski"
                                },
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440005",
                                    "full_name": "Lilly Wachowski"
                                }
                            ]
                        }
                    },
                    "Classic Drama": {
                        "value": {
                            "uuid": "550e8400-e29b-41d4-a716-446655440017",
                            "title": "The Godfather",
                            "imdb_rating": 9.2,
                            "description": "The aging patriarch of an organized crime "
                                           "dynasty transfers control of his clandestine empire to his reluctant son.",
                            "genre": [
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440018",
                                    "name": "Drama"
                                },
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440019",
                                    "name": "Crime"
                                }
                            ],
                            "actors": [
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440020",
                                    "full_name": "Marlon Brando"
                                },
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440021",
                                    "full_name": "Al Pacino"
                                }
                            ],
                            "writers": [
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440022",
                                    "full_name": "Mario Puzo"
                                }
                            ],
                            "directors": [
                                {
                                    "uuid": "550e8400-e29b-41d4-a716-446655440023",
                                    "full_name": "Francis Ford Coppola"
                                }
                            ]
                        }
                    }
                }
            }
        }
    }
}


films = {
    200: {
        "description": "Successful Retrieval of Films",
        "content": {
            "application/json": {
                "examples": {
                    "Films": {
                        "value": [
                            {
                                "uuid": "550e8400-e29b-41d4-a716-446655440010",
                                "title": "Inception",
                                "imdb_rating": 8.8
                            },
                            {
                                "uuid": "550e8400-e29b-41d4-a716-446655440011",
                                "title": "Forrest Gump",
                                "imdb_rating": 8.8
                            },
                            {
                                "uuid": "550e8400-e29b-41d4-a716-446655440012",
                                "title": "The Big Lebowski",
                                "imdb_rating": 8.1
                            },
                            {
                                "uuid": "550e8400-e29b-41d4-a716-446655440013",
                                "title": "Fight Club",
                                "imdb_rating": 8.8
                            }
                        ]
                    }
                }
            }
        }
    }
}


film_search = {
    200: {
        "description": "Successful Film Search",
        "content": {
            "application/json": {
                "examples": {
                    "Multiple Matches": {
                        "value": [
                            {
                                "uuid": "550e8400-e29b-41d4-a716-446655440013",
                                "title": "Star Wars: A New Hope",
                                "imdb_rating": 8.6
                            },
                            {
                                "uuid": "550e8400-e29b-41d4-a716-446655440014",
                                "title": "Star Trek: First Contact",
                                "imdb_rating": 7.6
                            },
                            {
                                "uuid": "550e8400-e29b-41d4-a716-446655440015",
                                "title": "Stargate",
                                "imdb_rating": 7.1
                            }
                        ]
                    },
                    "Single Match": {
                        "value": [
                            {
                                "uuid": "550e8400-e29b-41d4-a716-446655440016",
                                "title": "The Intouchables",
                                "imdb_rating": 8.5
                            }
                        ]
                    },
                    "No Match": {
                        "value": []
                    }
                }
            }
        }
    }
}
