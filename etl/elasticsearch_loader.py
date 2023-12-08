from elasticsearch import Elasticsearch, helpers

from config import ElasticConf
from transform import Transform

elastic_conf = ElasticConf()


class ElasticsearchLoader:
    es: Elasticsearch
    ts: Transform

    def __init__(self, transform_object: Transform) -> None:
        self.es = Elasticsearch([f"http://{elastic_conf.hosts}:9200"])
        self.ts = transform_object

    def load_movies(self) -> None:
        """Uploading films data to elasticsearch."""
        actions = [
            {
                "_index": "movies",
                "_id": str(filmwork_id),
                "_source": es_film.model_dump()
            }
            for filmwork_id, es_film in self.ts.elastic_format.items()
        ]
        helpers.bulk(self.es, actions=actions)

    def load_genres(self) -> None:
        """Uploading genres data to elasticsearch."""
        actions = [
            {
                "_index": "genres",
                "_id": str(genre_id),
                "_source": es_genre.model_dump()
            }
            for genre_id, es_genre in self.ts.el_genres.items()
        ]
        helpers.bulk(self.es, actions=actions)

    def load_persons(self) -> None:
        """Uploading personalities data to elasticsearch."""
        actions = [
            {
                "_index": "persons",
                "_id": str(person_id),
                "_source": es_person.model_dump()
            }
            for person_id, es_person in self.ts.el_persons.items()
        ]
        helpers.bulk(self.es, actions=actions)
