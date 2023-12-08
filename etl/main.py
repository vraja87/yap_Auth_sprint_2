import json
from datetime import datetime
from time import sleep

from dateutil.parser import parser
from elasticsearch import Elasticsearch

from config import CacheConf, ElasticConf, MainConf
from elasticsearch_loader import ElasticsearchLoader
from lib import CacheStates, JsonFileStorage, State, get_logger
from postgres_operations import (PostgresEnricher, PostgresMerger,
                                 PostgresProducer, PostgresEnricherPersonsOnly)
from postgres_saver import PostgresSaver, backoff
from transform import Transform

logger = get_logger('etl module')
main_conf, cache_conf, elastic_conf = MainConf(), CacheConf(), ElasticConf()


def max_date(last_date: datetime, new_date: datetime) -> datetime:
    if last_date is None:
        last_date = new_date
    last_date = new_date if new_date > last_date else last_date
    return last_date


@backoff()
def create_elastic_index() -> None:
    """Проверяем наличие индекса, создаём при необходимости."""
    indexes = [
        'movies',
        'genres',
        'persons',
    ]
    for idx in indexes:
        create_es_index(idx)


@backoff()
def create_es_index(idx: str) -> None:
    logger.info(f'Checking the presence of the index {idx}.')
    es = Elasticsearch([f"http://{elastic_conf.hosts}:9200"])
    if not es.indices.exists(index=idx):
        logger.info(f'Create index {idx}.')
        with open(f'create_schema/create_schema_{idx}.json') as file_:
            data = file_.read()
            data = json.loads(data)
            es.indices.create(index=idx,
                              settings=data['settings'],
                              mappings=data['mappings'],
                              )
        logger.info(f'Index {idx} created.')


def main() -> None:
    """Основной метод запуска синхронизации.

    Запускает остальной функционал в несколько прогонов,
    для обеспечения полноты копирования и распределения нагрузки.

    Имеется защита от повторного запуска скрипта.
    """
    create_elastic_index()
    logger.info('Synchronise of modified records.')

    limit_size = main_conf.limit_size

    n_run = 1  # номер прогона.
    # через парсер для избежания конфликта типов
    start_time = parser().parse('1970-01-01T00:00:00.000Z')
    last_max_modified = None
    storage = JsonFileStorage(cache_conf.main)
    state = State(storage)
    global_state = state.get_state('global_state')
    global_n_run = state.get_state('global_n_run')

    # Защита от повторного запуска, с записью лога уровня warning
    if global_state == CacheStates.START:
        logger.warning('Abort. Previous synch process has not been completed.')
        exit()
    cached_modified = state.get_state('modified_after')
    if cached_modified:
        modified_after = parser().parse(cached_modified)
    else:
        modified_after = start_time

    if global_state == CacheStates.ERROR:
        n_run = global_n_run
    try:
        postgres_saver = PostgresSaver()
        state.set_state('global_state', CacheStates.START)
        while True:
            state.set_state('global_state', CacheStates.START)
            state.set_state('global_n_run', n_run)
            pp = PostgresProducer(postgres_saver, limit_size,
                                  modified_after, n_run)
            pp.collect()

            if not pp.has_results:  # событие остановки
                state.set_state('global_state', CacheStates.FINISH)
                # дата с предыдущего прогона
                state.set_state('modified_after', last_max_modified)
                logger.info('Synchronization completed.')
                break

            last_max_modified = max_date(last_max_modified,
                                         pp.max_modified_after)

            n_run2 = 1
            while True:
                pe = PostgresEnricher(pp, limit_size, modified_after, n_run2)
                pe.collect()

                pe_persons = PostgresEnricherPersonsOnly(pp, modified_after)
                pe_persons.collect()

                if not pe.has_results:  # событие остановки
                    last_max_modified = max_date(last_max_modified,
                                                 pe.max_modified_after)
                    break

                # если изменить 1 жанр, то изменятся тысячи произведений...
                # поэтому сразу заливка, небольшими кусками.
                pm = PostgresMerger(
                    postgres_saver, modified_after,
                    pe.results['get_genre_links'],
                    pe.results['get_person_links'],
                )

                # additionally collect all films by person for person idx
                pm_persons = PostgresMerger(
                    postgres_saver, modified_after,
                    pe.results['get_genre_links'],
                    pe_persons.results['get_unlimited_person_links'],
                )

                pm.collect()
                pm_persons.collect()
                last_max_modified = max_date(last_max_modified,
                                             pm.max_modified_after)

                tr = Transform(
                    pm.results['get_films_linked'],
                    pp.results['get_genre'],
                    pm_persons.results['get_persons_linked'],
                )
                tr.reformat()
                tr.reformat_genres()
                tr.reformat_persons()

                es = ElasticsearchLoader(tr)
                es.load_movies()
                es.load_genres()
                es.load_persons()

                n_run2 += 1
            n_run += 1

    except Exception as e:
        state.set_state('global_state', CacheStates.ERROR)
        logger.error(f'{e}')
        raise e


if __name__ == '__main__':
    while True:
        main()
        sleep(main_conf.sleep_period)
