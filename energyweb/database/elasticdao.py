import logging

import elasticsearch as es

from tasks.database import dao
from tasks.ocpp16.protocol import ChargingStation


class ElasticSearchDAO(dao.DAO):

    def __init__(self, id_att_name: str, cls: dao.Model, *service_urls: str):
        """
        :param id_att_name: Class id attribute name
        :param cls: Class to instantiate
        :param service_urls: i.e. 'http://localhost:9200', 'https://remotehost:9000'
        """
        self._index = id_att_name
        self._cls = cls
        self._doc_type = cls.__name__
        self._db = es.Elasticsearch(service_urls)
        # suppress warnings
        es_logger = logging.getLogger('elasticsearch')
        es_logger.setLevel(logging.ERROR)

    def create(self, obj: dao.Model):
        res = self._db.index(index=self._index, doc_type=self._doc_type, body=obj.to_dict(), id=obj.reg_id,
                             refresh=True)
        if not res['result'] in ('created', 'updated'):
            raise es.ElasticsearchException('Fail creating or updating the object in the database')

    def retrieve(self, _id):
        self._db.indices.refresh(self._index)
        res = self._db.get(self._index, self._doc_type, id=_id)
        if not res['found']:
            raise es.ElasticsearchException('Object not found.')
        obj = self._cls.from_dict(res['_source'])
        obj.reg_id = res['_id']
        return obj

    def retrieve_all(self):
        self._db.indices.refresh(self._index)
        res = self._db.search(self._index, self._doc_type, body={"query": {"match_all": {}}})
        objs = []
        for hit in res['hits']['hits']:
            obj = self._cls.from_dict(hit['_source'])
            obj.reg_id = hit['_id']
            objs.append(obj)
        return objs

    def update(self, obj: dao.Model):
        self.create(obj)

    def delete(self, obj: dao.Model):
        response = self._db.delete(index=self._index, doc_type=self._doc_type, id=obj.reg_id)
        if not response['result'] == 'deleted':
            raise es.ElasticsearchException('Object not found.')

    def find_by(self, attributes: [dict]) -> [dict]:
        self._db.indices.refresh(self._index)
        query = {"query": {"bool": {"must": [{"match": {k: attributes[k]}} for k in attributes]}}}
        res = self._db.search(self._index, self._doc_type, body=query)
        objs = []
        for hit in res['hits']['hits']:
            obj = self._cls.from_dict(hit['_source'])
            obj.reg_id = hit['_id']
            objs.append(obj)
        return objs

    def delete_all(self):
        self._db.delete_by_query(self._index, doc_type=self._doc_type, body={"query": {"match_all": {}}})

    def delete_all_blank(self, field: str):
        self._db.delete_by_query(self._index, doc_type=self._doc_type, body={"bool": {"must_not": {"exists": {"field": field}}}})

    def query(self, query: dict) -> [dict]:
        """
        :param query: https://www.elastic.co/guide/en/elasticsearch/reference/5.6/query-filter-context.html
        :return: dict
        """
        self._db.indices.refresh(self._index)
        res = self._db.search(self._index, self._doc_type, body={"query": query})
        objs = []
        for hit in res['hits']['hits']:
            obj = self._cls.from_dict(hit['_source'])
            obj.reg_id = hit['_id']
            objs.append(obj)
        return objs


class ElasticSearchDAOFactory(dao.DAOFactory):

    def __init__(self, index_name: str, *service_urls: str):
        super().__init__()
        self._instances = {}
        self._service_urls = service_urls
        self._index = index_name

    def get_instance(self, cls) -> ElasticSearchDAO:
        if id(cls) in list(self._instances.keys()):
            return self._instances[id(cls)]
        self._instances[id(cls)] = ElasticSearchDAO(self._index, cls, *self._service_urls)
        return self._instances[id(cls)]
