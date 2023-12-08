from http import HTTPStatus

import functional.testdata.es_backup as es_mapping
import pytest
from functional.settings import test_settings


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
                {'uuid': "572113da-8dad-4277-ab5f-56861add8e6e"},
                {'body': {"uuid": "572113da-8dad-4277-ab5f-56861add8e6e", "title": "Profit-focused hybrid success",
                          "imdb_rating": 3.950701307316523,
                          "description": "Then bit TV seven easy. Treat consider generation them station four.\nNo "
                                         "relate anyone bag American.\nDrop after though career financial.",
                          "genre": [{"uuid": "4883c1d5-9e51-4ab5-8776-d40df1e93894", "name": "Short Film"},
                                    {"uuid": "97e69bb0-c2d8-46b4-8dd1-a123b34f6518", "name": "Musical"},
                                    {"uuid": "48ee2c80-4c8b-42e3-9b95-70635c3097c9", "name": "Disaster"},
                                    {"uuid": "e1ba3b73-5864-4a50-853b-030f4e137337", "name": "Romantic Comedy"},
                                    {"uuid": "4b1a523e-c1b3-4290-96da-d27de20b1553", "name": "Superhero"}],
                          "actors": [{"uuid": "0234c9d1-32a3-4f39-826e-313f9334d979", "full_name": "Peggy Johnson"},
                                     {"uuid": "b688c1fb-e8af-4132-8816-8121c8d592e6", "full_name": "Dustin Richmond"},
                                     {"uuid": "f49dc9af-6f96-4e7a-b18b-3db3238731c5", "full_name": "Randy Mullins"},
                                     {"uuid": "b4589532-21aa-4bed-a6b7-7a6a6e0876fb", "full_name": "Richard Willis"},
                                     {"uuid": "a506fc2b-3ec5-44e1-8af6-8f29de2d8d8a", "full_name": "John Burke"}],
                          "writers": [],
                          "directors": [{"uuid": "68b88239-4140-4d14-bc51-50cd02a8d69e", "full_name": "Michael Tucker"},
                                        {"uuid": "b845cde2-6082-47ca-b47f-5b3aea474d61", "full_name": "Linda Weaver"},
                                        {"uuid": "d5220d2e-0029-4bd2-8d08-559319e56dec", "full_name": "Bryan Thomas"},
                                        {"uuid": "9ace0dfa-aac5-4c9d-8be0-0b8d2b795b7e", "full_name": "Andrew Potter"},
                                        {"uuid": "47544eac-9e82-4bea-a678-1344270aeec2",
                                         "full_name": "Gabrielle Anderson"}]},
                 'status': HTTPStatus.OK}
        ),
        (
                {'uuid': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'},
                {'body': {'detail': 'Film not found.'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
        (
                {'uuid': 'xxxxxxxx'},
                {'body': {'detail': 'Film not found.'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
        (
                {'uuid': 327},
                {'body': {'detail': 'Film not found.'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
    ]
)
async def test_film_details(make_get_request, test_data, expected_answer):
    """
    Asynchronously test the details of a specific film by UUID.

    :param make_get_request: Async fixture for making GET requests.
    :param test_data: Data for the test case.
    :param expected_answer: Expected response data and status code.
    """
    response = await make_get_request(f'/api/v1/films/{test_data["uuid"]}', None)

    assert response.status == expected_answer['status']
    assert response.body == expected_answer['body']


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
                {'page_number': 2,
                 'page_size': 5},
                {'status': HTTPStatus.OK}
        ),
        (
                {'page_number': 2,
                 'page_size': 5,
                 'rating_max': 7.5,
                 'sort': ['-imdb_rating']
                 },
                {'status': HTTPStatus.OK}
        ),
        (
                {'page_number': 2,
                 'page_size': 5,
                 'rating_max': 7.5,
                 'sort': ['imdb_rating']
                 },
                {'status': HTTPStatus.OK}
        ),
    ]
)
async def test_film_list_sort_filter(make_get_request, test_data, expected_answer):
    """
    Asynchronously test the film listing with sorting and filtering options.

    :param make_get_request: Async fixture for making GET requests.
    :param test_data: Data for the test case.
    :param expected_answer: Expected status code.
    """
    start_idx = test_data['page_number'] * test_data['page_size']
    end_idx = start_idx + test_data['page_size']
    rating_max = float(test_data['rating_max']) if 'rating_max' in test_data else 10
    order = test_data['sort'][0] if 'sort' in test_data else '-imdb_rating'
    if not order.startswith('-'):
        order = False
    else:
        order = True
    genres_slice = sorted([y for y in es_mapping.data[test_settings.es_index_movies] if y['imdb_rating'] < rating_max],
                          key=lambda x: x['imdb_rating'], reverse=order)[start_idx: end_idx]
    genres_slice = [{'uuid': x['uuid'], 'title': x['title'], 'imdb_rating': x['imdb_rating']} for x in genres_slice]

    response = await make_get_request('/api/v1/films/', test_data)

    assert response.status == expected_answer['status']
    assert len(response.body) == len(genres_slice)
    assert response.body == genres_slice
    if order:
        assert response.body[0]['imdb_rating'] > response.body[1]['imdb_rating']
    else:
        assert response.body[0]['imdb_rating'] < response.body[1]['imdb_rating']


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
                {'page_number': -1,
                 'page_size': 5},
                {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
                {'page_number': 2,
                 'page_size': 0,
                 'sort_by': '+imdb_rating'
                 },
                {'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
                {'page_number': 10,
                 'page_size': 100,
                 'rating_max': 7.5,
                 'sort_by': 'imdb_rating'
                 },
                {'body': {'detail': 'Films not found.'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
    ]
)
async def test_film_page_border_cases(make_get_request, test_data, expected_answer):
    """
    Asynchronously test the border cases for film pagination.

    :param make_get_request: Async fixture for making GET requests.
    :param test_data: Data for the test case.
    :param expected_answer: Expected response data and status code.
    """
    response = await make_get_request('/api/v1/films/', test_data)

    assert response.status == expected_answer['status']
    if expected_answer['status'] == HTTPStatus.NOT_FOUND:
        assert response.body == expected_answer['body']


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
                {
                    'query': 'start',
                    'page_number': 0,
                    'page_size': 10,
                    'rating_max': 7.5,
                },
                {'body': [{"uuid": "1476d13c-bd0f-41d9-b327-01d28f7d0fe8", "title": "Up-sized client-server complexity",
                           "imdb_rating": 5.806447587631739},
                          {"uuid": "d3fc1b01-2157-4647-a9ae-b84f25bc6256", "title": "Synergized impactful neural-net",
                           "imdb_rating": 5.411727422322415}, {"uuid": "0f925154-2a24-445e-9f57-6480ee1a73fd",
                                                               "title": "Versatile fresh-thinking encryption",
                                                               "imdb_rating": 4.654242631163772},
                          {"uuid": "2b3a5bb7-6e3c-420e-9354-57d8c59498e6",
                           "title": "Devolved attitude-oriented throughput", "imdb_rating": 2.888865758958029},
                          {"uuid": "bdb149a2-24d6-46eb-8d15-39ad3f4cd9f8", "title": "Sharable transitional protocol",
                           "imdb_rating": 2.5830342106708857}],
                 'status': HTTPStatus.OK}
        ),
        (
                {
                    'query': 'structure',
                    'page_number': 0,
                    'page_size': 10,
                    'fuzzy': 3,
                },
                {'body': [{"uuid": "d76f9ca5-fabd-4d33-a9d8-2812bab218b7", "title": "Digitized responsive interface",
                           "imdb_rating": 8.328118331017633}, {"uuid": "b25d907e-bb04-4ebd-9495-d55d1b832485",
                                                               "title": "Progressive intermediate structure",
                                                               "imdb_rating": 7.118053190956019},
                          {"uuid": "f4d93ee3-9c10-4ff2-808e-d98f9da4cb46", "title": "Adaptive heuristic database",
                           "imdb_rating": 0.7585282914865377}],
                 'status': HTTPStatus.OK}
        ),
    ]
)
async def test_film_search(make_get_request, test_data, expected_answer):
    """
    Asynchronously test the film search functionality.

    :param make_get_request: Async fixture for making GET requests.
    :param test_data: Data for the test case.
    :param expected_answer: Expected response data and status code.
    """
    response = await make_get_request('/api/v1/films/search/', test_data)

    assert response.status == expected_answer['status']
    assert len(response.body) == len(expected_answer['body'])
    assert response.body == expected_answer['body']


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
                {'uuid': es_mapping.data[test_settings.es_index_movies][20]['uuid']},
                {'status': HTTPStatus.OK}
        ),
    ]
)
async def test_film_redis(make_get_request, redis_cleanup, test_data, expected_answer):
    """
    Asynchronously test the film details cached in Redis.

    :param make_get_request: Async fixture for making GET requests.
    :param test_data: Data for the test case, specifically the film UUID.
    :param expected_answer: Expected status code.
    """
    await redis_cleanup()

    response1 = await make_get_request(f'/api/v1/films/{test_data["uuid"]}', None)
    response2 = await make_get_request(f'/api/v1/films/{test_data["uuid"]}', None)

    assert response1.status == expected_answer['status']
    assert response2.status == expected_answer['status']
    assert response1.body == response2.body
    assert response2.response_time < response1.response_time
