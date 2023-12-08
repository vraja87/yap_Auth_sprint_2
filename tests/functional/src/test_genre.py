from http import HTTPStatus

import functional.testdata.es_backup as es_mapping
import pytest
from functional.settings import test_settings


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {},
            {'status': HTTPStatus.OK, 'length': 30}
        ),
        (
            {'page_number': 0},
            {'status': HTTPStatus.OK, 'length': 30}
        ),
        (
            {'page_number': 1},
            {'status': HTTPStatus.NOT_FOUND, 'length': 1}
        ),
        (
            {'page_number': -1},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {'page_number': 100},
            {'status': HTTPStatus.BAD_REQUEST, 'length': 1}
        ),
        (
            {'page_number': 'Mashed potato'},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {'page_size': 10},
            {'status': HTTPStatus.OK, 'length': 10}
        ),
        (
            {'page_size': 20},
            {'status': HTTPStatus.OK, 'length': 20}
        ),
        (
            {'page_size': 0},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {'page_size': -1},
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'length': 1}
        ),
        (
            {'page_size': 5000},
            {'status': HTTPStatus.OK, 'length': 30}
        ),
    ]
)
async def test_all_genres_page_num_size(make_get_request, query_data: dict, expected_answer: dict):
    """
    Asynchronously test various combinations of page_size and page_number for genre listing.

    :param make_get_request: Async fixture for making GET requests.
    :param query_data: Data for the test case.
    :param expected_answer: Expected status code and body length.
    """
    response = await make_get_request('/api/v1/genres/', query_data)

    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        (
            {'page_number': 2, 'page_size': 10},
            {'status': HTTPStatus.OK, 'length': 10}
        ),
    ]
)
async def test_all_genres_format_sorting_consistency(make_get_request, query_data: dict, expected_answer: dict):
    """
    Asynchronously test the consistency of genre data format and sorting by names.

    :param make_get_request: Async fixture for making GET requests.
    :param query_data: Data for the test case.
    :param expected_answer: Expected status code and body length.
    """
    genres_slice = sorted(es_mapping.data[test_settings.es_index_genres],
                          key=lambda x: x['name'])[query_data['page_number'] * query_data['page_size']:]

    response = await make_get_request('/api/v1/genres/', query_data)

    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']
    assert response.body == genres_slice
    assert response.body[0]['name'] < response.body[1]['name']


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
            {'uuid': es_mapping.data[test_settings.es_index_genres][4]['uuid']},
            {'body': es_mapping.data[test_settings.es_index_genres][4], 'status': HTTPStatus.OK}
        ),
        (
            {'uuid': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'},
            {'body': {'detail': 'Genre not found.'}, 'status': HTTPStatus.NOT_FOUND}
        ),
    ]
)
async def test_genre_details(make_get_request, test_data: dict, expected_answer: dict):
    """
    Asynchronously test the details of a specific genre by UUID.

    :param make_get_request: Async fixture for making GET requests.
    :param test_data: Data for the test case.
    :param expected_answer: Expected response data and status code.
    """
    response = await make_get_request(f'/api/v1/genres/{test_data["uuid"]}/', {})

    assert response.body == expected_answer['body']
    assert response.status == expected_answer['status']


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
                {'uuid': es_mapping.data[test_settings.es_index_genres][20]['uuid']},
                {'status': HTTPStatus.OK}
        ),
    ]
)
async def test_genre_redis(make_get_request, redis_cleanup, test_data, expected_answer):
    """
    Asynchronously test the genre details cached in Redis.

    :param make_get_request: Async fixture for making GET requests.
    :param test_data: Data for the test case, specifically the genre UUID.
    :param expected_answer: Expected status code.
    """
    await redis_cleanup()
    response1 = await make_get_request(f'/api/v1/genres/{test_data["uuid"]}', None)
    response2 = await make_get_request(f'/api/v1/genres/{test_data["uuid"]}', None)
    assert response1.status == expected_answer['status']
    assert response2.status == expected_answer['status']
    assert response1.body == response2.body
    assert response2.response_time < response1.response_time
