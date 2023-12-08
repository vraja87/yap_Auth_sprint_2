from http import HTTPStatus

import functional.testdata.es_backup as es_mapping
import pytest
from functional.settings import test_settings


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
                {'uuid': es_mapping.data[test_settings.es_index_persons][10]['uuid']},
                {'body': {"uuid": es_mapping.data[test_settings.es_index_persons][10]['uuid'],
                          "full_name": "Jason Lane",
                          "films": [
                              {
                                  "uuid": "e897a004-b576-42e3-8cf0-02b4963ee9b1",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "d76f9ca5-fabd-4d33-a9d8-2812bab218b7",
                                  "roles": ["director"]
                              },
                              {
                                  "uuid": "f91b8cd9-2e8e-48b4-8136-485678131caf",
                                  "roles": ["writer"]
                              },
                              {
                                  "uuid": "181f2372-d160-4960-8ec5-9375b04b4588",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "5f99506a-17d8-4393-843b-a00342f11563",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "db473128-347e-4412-a813-e36c4ac44fd4",
                                  "roles": ["writer"]
                              },
                              {
                                  "uuid": "ee5d3e77-ba62-437e-9eab-7d323ad26a72",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "28f3b5eb-6e42-44ef-8306-70548c2ffa9d",
                                  "roles": ["director"]
                              },
                              {
                                  "uuid": "2a751397-946a-4ffa-b149-b13cf2924ac9",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "d2470ff5-7528-4348-bfdb-29a31548cb30",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "5c06e32a-9bcc-4460-9ba8-624709d8b417",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "0fee69ac-c996-42a9-b774-e03e33fcbd63",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "5b25bffd-45aa-4d45-8884-ba60404cd373",
                                  "roles": ["director"]
                              },
                              {
                                  "uuid": "9e2c1364-ceb5-4933-b9dc-fa196847b373",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "a8c8f473-7f97-4708-b1b6-efbd904c15d0",
                                  "roles": ["director"]
                              },
                              {
                                  "uuid": "ee1be739-3f7e-4c07-ab98-288dbf6a7f48",
                                  "roles": ["writer"]
                              },
                              {
                                  "uuid": "a72e9a4e-1e1d-40ef-94e0-555030d6ac24",
                                  "roles": ["writer"]
                              },
                              {
                                  "uuid": "802b0508-c926-4a81-8325-ef73bd5919a0",
                                  "roles": ["writer", "director"]
                              },
                              {
                                  "uuid": "21bdb3ab-fc59-4486-a867-281347183c9b",
                                  "roles": ["writer"]
                              },
                              {
                                  "uuid": "573d8c76-7a77-404b-94f8-2520476c8be9",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "5b65c46f-4d2f-4c59-b195-ee8b90b15678",
                                  "roles": ["writer"]
                              },
                              {
                                  "uuid": "2b3a5bb7-6e3c-420e-9354-57d8c59498e6",
                                  "roles": ["writer"]
                              },
                              {
                                  "uuid": "92774ab7-5454-433e-bf19-82003d68764f",
                                  "roles": ["writer"]
                              },
                              {
                                  "uuid": "82c89f45-a3f9-45ac-ae2c-be35e64d3fe6",
                                  "roles": ["writer"]
                              },
                              {
                                  "uuid": "4c93f3f1-20f4-46ad-b301-8b1e3174f4f0",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "81aa39da-4f48-476a-b39e-dc348f04b8fc",
                                  "roles": ["actor"]
                              },
                              {
                                  "uuid": "594b85af-c5a0-4a64-b425-49a9dedc29ba",
                                  "roles": ["director"]
                              },
                              {
                                  "uuid": "3bbc3bd5-83a2-41f1-98e5-f9aafbd7b65e",
                                  "roles": ["writer"]
                              }
                          ]
                          },
                 'status': HTTPStatus.OK}
        ),
        (
                {'uuid': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'},
                {'body': {'detail': 'person not found'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
        (
                {'uuid': 'xxxxxxxx'},
                {'body': {'detail': 'person not found'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
        (
                {'uuid': 327},
                {'body': {'detail': 'person not found'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
    ]
)
async def test_person_details(make_get_request, test_data, expected_answer):
    """
    Tests the details of a person based on their UUID.

    :param make_get_request: Fixture for making GET requests.
    :param test_data: Dictionary containing test parameters like 'uuid'.
    :param expected_answer: Expected API response.
    """
    response = await make_get_request(f'/api/v1/persons/{test_data["uuid"]}', None)

    assert response.status == expected_answer['status']
    assert response.body == expected_answer['body']


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
                {'uuid': es_mapping.data[test_settings.es_index_persons][10]['uuid']},
                {'body': [{"uuid": "e897a004-b576-42e3-8cf0-02b4963ee9b1", "title": "Operative homogeneous toolset",
                           "imdb_rating": 2.5716885276084103},
                          {"uuid": "d76f9ca5-fabd-4d33-a9d8-2812bab218b7", "title": "Digitized responsive interface",
                           "imdb_rating": 8.328118331017633},
                          {"uuid": "f91b8cd9-2e8e-48b4-8136-485678131caf", "title": "Devolved multi-state monitoring",
                           "imdb_rating": 2.883561358345278},
                          {"uuid": "181f2372-d160-4960-8ec5-9375b04b4588", "title": "Streamlined hybrid alliance",
                           "imdb_rating": 6.39872809973523},
                          {"uuid": "5f99506a-17d8-4393-843b-a00342f11563", "title": "Sharable zero-defect emulation",
                           "imdb_rating": 5.878716859989577},
                          {"uuid": "db473128-347e-4412-a813-e36c4ac44fd4", "title": "Team-oriented heuristic benchmark",
                           "imdb_rating": 7.4612853173019955},
                          {"uuid": "ee5d3e77-ba62-437e-9eab-7d323ad26a72", "title": "Profound uniform superstructure",
                           "imdb_rating": 2.351567465694723}, {"uuid": "28f3b5eb-6e42-44ef-8306-70548c2ffa9d",
                                                               "title": "Polarized high-level customer loyalty",
                                                               "imdb_rating": 6.1188162500880345},
                          {"uuid": "2a751397-946a-4ffa-b149-b13cf2924ac9", "title": "Implemented systemic hierarchy",
                           "imdb_rating": 4.877213144626767}, {"uuid": "d2470ff5-7528-4348-bfdb-29a31548cb30",
                                                               "title": "Triple-buffered zero tolerance encryption",
                                                               "imdb_rating": 0.24642149869188779},
                          {"uuid": "5c06e32a-9bcc-4460-9ba8-624709d8b417",
                           "title": "Enterprise-wide 5thgeneration array", "imdb_rating": 0.9483161219364167},
                          {"uuid": "0fee69ac-c996-42a9-b774-e03e33fcbd63", "title": "Customizable explicit access",
                           "imdb_rating": 7.8594702704140795}, {"uuid": "5b25bffd-45aa-4d45-8884-ba60404cd373",
                                                                "title": "Virtual eco-centric Graphic Interface",
                                                                "imdb_rating": 9.523566900398498},
                          {"uuid": "9e2c1364-ceb5-4933-b9dc-fa196847b373",
                           "title": "Diverse regional Local Area Network", "imdb_rating": 0.5075077873476508},
                          {"uuid": "a8c8f473-7f97-4708-b1b6-efbd904c15d0", "title": "Extended eco-centric matrices",
                           "imdb_rating": 6.267019267075766},
                          {"uuid": "ee1be739-3f7e-4c07-ab98-288dbf6a7f48", "title": "Multi-layered didactic matrix",
                           "imdb_rating": 7.035200513708669}, {"uuid": "a72e9a4e-1e1d-40ef-94e0-555030d6ac24",
                                                               "title": "Devolved radical Graphic Interface",
                                                               "imdb_rating": 1.2713687645812888},
                          {"uuid": "802b0508-c926-4a81-8325-ef73bd5919a0",
                           "title": "Multi-channeled bandwidth-monitored database", "imdb_rating": 2.521904836164067},
                          {"uuid": "21bdb3ab-fc59-4486-a867-281347183c9b",
                           "title": "Fundamental multi-tasking neural-net", "imdb_rating": 3.592966735127167},
                          {"uuid": "573d8c76-7a77-404b-94f8-2520476c8be9", "title": "Exclusive tangible secured line",
                           "imdb_rating": 8.77809677596311}, {"uuid": "5b65c46f-4d2f-4c59-b195-ee8b90b15678",
                                                              "title": "Exclusive directional instruction set",
                                                              "imdb_rating": 4.5716004610676535},
                          {"uuid": "2b3a5bb7-6e3c-420e-9354-57d8c59498e6",
                           "title": "Devolved attitude-oriented throughput", "imdb_rating": 2.888865758958029},
                          {"uuid": "92774ab7-5454-433e-bf19-82003d68764f", "title": "Balanced responsive throughput",
                           "imdb_rating": 7.194262263177017}, {"uuid": "82c89f45-a3f9-45ac-ae2c-be35e64d3fe6",
                                                               "title": "Focused web-enabled open architecture",
                                                               "imdb_rating": 2.3155789320129374},
                          {"uuid": "4c93f3f1-20f4-46ad-b301-8b1e3174f4f0", "title": "Progressive web-enabled attitude",
                           "imdb_rating": 9.707702047358815},
                          {"uuid": "81aa39da-4f48-476a-b39e-dc348f04b8fc", "title": "Public-key 3rdgeneration adapter",
                           "imdb_rating": 0.31084735750935844}, {"uuid": "594b85af-c5a0-4a64-b425-49a9dedc29ba",
                                                                 "title": "Profit-focused client-driven matrices",
                                                                 "imdb_rating": 9.71734474867197},
                          {"uuid": "3bbc3bd5-83a2-41f1-98e5-f9aafbd7b65e",
                           "title": "Triple-buffered bandwidth-monitored challenge", "imdb_rating": 7.126311002024362}],
                 'status': HTTPStatus.OK}
        ),
        (
                {'uuid': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'},
                {'body': {'detail': 'person not found'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
        (
                {'uuid': "9135cc2b-1ed0-465b-a976-34e021b80fd5"},
                {'body': {'detail': 'films with person were not found'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
        (
                {'uuid': 327},
                {'body': {'detail': 'person not found'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
    ]
)
async def test_person_films(make_get_request, test_data, expected_answer):
    """
    Tests the list of films associated with a person based on their UUID.

    :param make_get_request: Fixture for making GET requests.
    :param test_data: Dictionary containing test parameters like 'uuid'.
    :param expected_answer: Expected API response.
    """
    response = await make_get_request(f'/api/v1/persons/{test_data["uuid"]}/film', None)

    assert response.status == expected_answer['status']
    assert response.body == expected_answer['body']


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
                {'query': 'Ryan Hunt',
                 'fuzzy': 0,
                 'page_number': 0,
                 'page_size': 5},
                {'body': [{"uuid": "92e55088-5117-42a0-839d-6a1666348d00", "full_name": "Ryan Hunt",
                           "films": [{"uuid": "bdb149a2-24d6-46eb-8d15-39ad3f4cd9f8", "roles": ["actor"]},
                                     {"uuid": "9966786a-6c6f-4b2a-b93b-92f3fa92410b", "roles": ["writer"]},
                                     {"uuid": "76751d43-bc32-4ee6-b6a9-fe3c23afa2b6", "roles": ["director"]},
                                     {"uuid": "5349fcf6-bdd2-46b7-a7dc-00d710f5b6be", "roles": ["actor"]},
                                     {"uuid": "181f2372-d160-4960-8ec5-9375b04b4588", "roles": ["writer"]},
                                     {"uuid": "08386c8d-54a1-442a-b6a4-deb78e7c2cbc", "roles": ["actor"]},
                                     {"uuid": "5f99506a-17d8-4393-843b-a00342f11563", "roles": ["writer"]},
                                     {"uuid": "d88bf4db-cdf6-4e64-842c-34c1e2ef1abf", "roles": ["actor"]},
                                     {"uuid": "4c0724d8-ce1a-488b-8638-9013629f46b3", "roles": ["actor", "writer"]},
                                     {"uuid": "ee5d3e77-ba62-437e-9eab-7d323ad26a72", "roles": ["actor"]},
                                     {"uuid": "28f3b5eb-6e42-44ef-8306-70548c2ffa9d", "roles": ["writer"]},
                                     {"uuid": "c3021c0b-c927-40d7-b10f-7e665cacb63d", "roles": ["writer"]},
                                     {"uuid": "e1a8af0e-2166-4c34-a5db-8bbfa6483ad3", "roles": ["director"]},
                                     {"uuid": "aacd497f-7546-41d9-a886-b438f80d8d42", "roles": ["actor"]},
                                     {"uuid": "1476d13c-bd0f-41d9-b327-01d28f7d0fe8", "roles": ["writer"]},
                                     {"uuid": "b3bef334-ffbc-45e2-b498-7b6ff8b9f27a", "roles": ["actor"]},
                                     {"uuid": "a8c8f473-7f97-4708-b1b6-efbd904c15d0", "roles": ["writer"]},
                                     {"uuid": "ee1be739-3f7e-4c07-ab98-288dbf6a7f48", "roles": ["actor"]},
                                     {"uuid": "8afa43ae-2478-4ecf-a576-f3a756168e24", "roles": ["director"]},
                                     {"uuid": "d3fc1b01-2157-4647-a9ae-b84f25bc6256", "roles": ["director"]},
                                     {"uuid": "a72e9a4e-1e1d-40ef-94e0-555030d6ac24", "roles": ["actor"]},
                                     {"uuid": "9237cbfc-a093-4492-a09d-a695937b58af", "roles": ["actor"]},
                                     {"uuid": "92774ab7-5454-433e-bf19-82003d68764f", "roles": ["actor"]},
                                     {"uuid": "998e898c-bf0f-4e53-862d-15f90fd3892c", "roles": ["writer"]},
                                     {"uuid": "4c93f3f1-20f4-46ad-b301-8b1e3174f4f0", "roles": ["director"]},
                                     {"uuid": "0f925154-2a24-445e-9f57-6480ee1a73fd", "roles": ["actor"]}]}],
                 'status': HTTPStatus.OK}
        ),
        (
                {'query': 'Thomas',
                 'fuzzy': 0,
                 'page_number': 0,
                 'page_size': 5},
                {'body': [{"uuid": "223188e3-c168-44d4-ba0e-26c93a4da0fd", "full_name": "Thomas Frazier",
                           "films": [{"uuid": "d2470ff5-7528-4348-bfdb-29a31548cb30", "roles": ["actor"]},
                                     {"uuid": "d76f9ca5-fabd-4d33-a9d8-2812bab218b7", "roles": ["director"]},
                                     {"uuid": "c0b5b68e-9e1f-4b86-b89d-ad8ad9451146", "roles": ["director"]},
                                     {"uuid": "b4b6f7cb-de49-4887-b0ac-69b31d400c43", "roles": ["actor"]},
                                     {"uuid": "82c89f45-a3f9-45ac-ae2c-be35e64d3fe6", "roles": ["actor", "writer"]},
                                     {"uuid": "802b0508-c926-4a81-8325-ef73bd5919a0", "roles": ["director"]},
                                     {"uuid": "181f2372-d160-4960-8ec5-9375b04b4588", "roles": ["writer"]},
                                     {"uuid": "bed8af23-1e18-4a38-b330-aa965dfcd71e", "roles": ["director"]},
                                     {"uuid": "0fee69ac-c996-42a9-b774-e03e33fcbd63", "roles": ["writer"]},
                                     {"uuid": "594b85af-c5a0-4a64-b425-49a9dedc29ba", "roles": ["director"]},
                                     {"uuid": "1476d13c-bd0f-41d9-b327-01d28f7d0fe8", "roles": ["writer"]},
                                     {"uuid": "2ae8f731-e45c-487a-893a-40df0421c57b", "roles": ["writer"]},
                                     {"uuid": "cdc9ba1b-3973-435b-8b09-e400fe5c314c", "roles": ["director"]},
                                     {"uuid": "27f96ae0-ed22-4b91-b1ba-053e8be9ba67", "roles": ["director"]},
                                     {"uuid": "a8c8f473-7f97-4708-b1b6-efbd904c15d0", "roles": ["writer"]}]},
                          {"uuid": "d5220d2e-0029-4bd2-8d08-559319e56dec", "full_name": "Bryan Thomas",
                           "films": [{"uuid": "ee1be739-3f7e-4c07-ab98-288dbf6a7f48", "roles": ["director"]},
                                     {"uuid": "572113da-8dad-4277-ab5f-56861add8e6e", "roles": ["director"]},
                                     {"uuid": "70fc3d13-bfc8-4c3e-a37b-9d0ec89da251", "roles": ["writer"]},
                                     {"uuid": "28f3b5eb-6e42-44ef-8306-70548c2ffa9d",
                                      "roles": ["actor", "writer", "director"]},
                                     {"uuid": "76751d43-bc32-4ee6-b6a9-fe3c23afa2b6", "roles": ["director"]},
                                     {"uuid": "2a751397-946a-4ffa-b149-b13cf2924ac9", "roles": ["writer"]},
                                     {"uuid": "c0b5b68e-9e1f-4b86-b89d-ad8ad9451146", "roles": ["writer"]},
                                     {"uuid": "27f96ae0-ed22-4b91-b1ba-053e8be9ba67", "roles": ["writer"]},
                                     {"uuid": "48eb861b-1920-4c84-b2f8-1f014bc4a6f7", "roles": ["actor"]},
                                     {"uuid": "0a65a826-2f52-4810-9da1-c62aa6d92c0b", "roles": ["actor"]},
                                     {"uuid": "5b25bffd-45aa-4d45-8884-ba60404cd373", "roles": ["actor"]},
                                     {"uuid": "21bdb3ab-fc59-4486-a867-281347183c9b", "roles": ["writer"]},
                                     {"uuid": "d88bf4db-cdf6-4e64-842c-34c1e2ef1abf", "roles": ["director"]},
                                     {"uuid": "b25d907e-bb04-4ebd-9495-d55d1b832485", "roles": ["writer"]}]},
                          {"uuid": "66287fc8-fd6e-492e-a91f-a2ea3299bc2a", "full_name": "Thomas Small",
                           "films": [{"uuid": "7742844d-fca9-4f98-9887-ff806fd5c31f", "roles": ["writer"]},
                                     {"uuid": "70fc3d13-bfc8-4c3e-a37b-9d0ec89da251", "roles": ["writer"]},
                                     {"uuid": "9e2c1364-ceb5-4933-b9dc-fa196847b373", "roles": ["writer"]},
                                     {"uuid": "9966786a-6c6f-4b2a-b93b-92f3fa92410b", "roles": ["actor"]},
                                     {"uuid": "76751d43-bc32-4ee6-b6a9-fe3c23afa2b6", "roles": ["director"]},
                                     {"uuid": "c0b5b68e-9e1f-4b86-b89d-ad8ad9451146", "roles": ["actor", "director"]},
                                     {"uuid": "2f916e1a-9302-4c57-b2aa-98f8f31f18e4", "roles": ["actor"]},
                                     {"uuid": "998e898c-bf0f-4e53-862d-15f90fd3892c", "roles": ["director"]},
                                     {"uuid": "5349fcf6-bdd2-46b7-a7dc-00d710f5b6be", "roles": ["actor", "writer"]},
                                     {"uuid": "0a65a826-2f52-4810-9da1-c62aa6d92c0b", "roles": ["actor"]},
                                     {"uuid": "26b9530b-5f6d-45c2-a991-e7e12889d5b5", "roles": ["director"]},
                                     {"uuid": "21bdb3ab-fc59-4486-a867-281347183c9b", "roles": ["writer"]},
                                     {"uuid": "d88bf4db-cdf6-4e64-842c-34c1e2ef1abf", "roles": ["actor"]},
                                     {"uuid": "b3bef334-ffbc-45e2-b498-7b6ff8b9f27a", "roles": ["actor"]},
                                     {"uuid": "2c1c826b-f66a-48ec-a68e-5cf7fc3c042c", "roles": ["director"]},
                                     {"uuid": "25bffeee-4b71-45ab-96c2-14a28a16a718", "roles": ["actor"]},
                                     {"uuid": "27f96ae0-ed22-4b91-b1ba-053e8be9ba67", "roles": ["director"]}]}],
                 'status': HTTPStatus.OK}
        ),
        (
                {'query': '',
                 'fuzzy': 0,
                 'page_number': 0,
                 'page_size': 10},
                {'body': {'detail': 'persons not found'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
        (
                {'query': ' ',
                 'fuzzy': 0,
                 'page_number': 0,
                 'page_size': 10},
                {'body': {'detail': 'persons not found'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
        (
                {'query': 'Stephen Hawking',  # no one
                 'fuzzy': 3,
                 'page_number': 0,
                 'page_size': 10},
                {'body': {'detail': 'persons not found'},
                 'status': HTTPStatus.NOT_FOUND}
        ),
    ]
)
async def test_persons_search(make_get_request, test_data, expected_answer):
    """
    Tests the search functionality for persons.

    :param make_get_request: Fixture for making GET requests.
    :param test_data: Dictionary containing test parameters like 'query', 'fuzzy', etc.
    :param expected_answer: Expected API response.
    """
    response = await make_get_request('/api/v1/persons/search/', test_data)

    assert response.status == expected_answer['status']
    assert response.body == expected_answer['body']


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
                {'query': 'Anderson',
                 'fuzzy': 3,
                 'page_number': 0,
                 'page_size': 10},
                {'length': 2,
                 'status': HTTPStatus.OK}
        ),
        (
                {'query': 'Anderson',
                 'fuzzy': 3,
                 'page_number': 1,
                 'page_size': 10},
                {'length': 1,
                 'status': HTTPStatus.NOT_FOUND}
        ),
        (
                {'query': 'Anderson',
                 'fuzzy': 3,
                 'page_number': -1,
                 'page_size': 10},
                {'length': 1,
                 'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
                {'query': 'Anderson',
                 'fuzzy': 3,
                 'page_number': 100,
                 'page_size': 10},
                {'length': 1,
                 'status': HTTPStatus.NOT_FOUND}
        ),
        (
                {'query': 'Anderson',
                 'fuzzy': 3,
                 'page_number': 0,
                 'page_size': 0},
                {'length': 1,
                 'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
                {'query': 'Anderson',
                 'fuzzy': 3,
                 'page_number': 0,
                 'page_size': -1},
                {'length': 1,
                 'status': HTTPStatus.UNPROCESSABLE_ENTITY}
        ),
        (
                {'query': 'Anderson',
                 'fuzzy': 3,
                 'page_number': 0,
                 'page_size': 1000},
                {'length': 2,
                 'status': HTTPStatus.OK}
        ),
    ]
)
async def test_persons_page_num_size(make_get_request, test_data, expected_answer):
    """
    Tests the pagination functionality for searching persons.

    :param make_get_request: Fixture for making GET requests.
    :param test_data: Dictionary containing test parameters like 'query', 'fuzzy', 'page_number', and 'page_size'.
    :param expected_answer: Expected API response with status code and the number of results.
    """
    response = await make_get_request('/api/v1/persons/search/', test_data)
    assert response.status == expected_answer['status']
    assert len(response.body) == expected_answer['length']


@pytest.mark.parametrize(
    'test_data, expected_answer',
    [
        (
                {'uuid': es_mapping.data[test_settings.es_index_persons][20]['uuid']},
                {'status': HTTPStatus.OK}
        ),
    ]
)
async def test_person_redis(make_get_request, redis_cleanup, test_data, expected_answer):
    """
    Tests the caching behavior of the genre-related API endpoint using Redis.

    :param make_get_request: Fixture for making GET requests.
    :param test_data: Dictionary containing test parameters like 'uuid'.
    :param expected_answer: Expected API response with status code.
    """
    await redis_cleanup()
    response1 = await make_get_request(f'/api/v1/persons/{test_data["uuid"]}', None)
    response2 = await make_get_request(f'/api/v1/persons/{test_data["uuid"]}', None)
    assert response1.status == expected_answer['status']
    assert response2.status == expected_answer['status']
    assert response1.body == response2.body
    assert response2.response_time < response1.response_time
