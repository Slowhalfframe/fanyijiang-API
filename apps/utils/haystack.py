from haystack.backends.elasticsearch_backend import ElasticsearchSearchEngine
from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend
from haystack.constants import DJANGO_CT, DJANGO_ID

DEFAULT_FIELD_MAPPING = {'type': 'string', 'analyzer': 'snowball'}

FIELD_MAPPINGS = {
    'edge_ngram': {'type': 'string', 'analyzer': 'edgengram_analyzer'},
    'ngram':      {'type': 'string', 'analyzer': 'ngram_analyzer'},
    'date':       {'type': 'date'},
    'datetime':   {'type': 'date'},

    'location':   {'type': 'geo_point'},
    'boolean':    {'type': 'boolean'},
    'float':      {'type': 'float'},
    'long':       {'type': 'long'},
    'integer':    {'type': 'string'},
}


class CustomElasticsearchSearchBackend(ElasticsearchSearchBackend):
    def build_schema(self, fields):
        content_field_name = ''
        mapping = {
            DJANGO_CT: {'type': 'string', 'index': 'not_analyzed', 'include_in_all': False},
            DJANGO_ID: {'type': 'string', 'index': 'not_analyzed', 'include_in_all': False},
        }

        for field_name, field_class in fields.items():
            field_mapping = FIELD_MAPPINGS.get(field_class.field_type, DEFAULT_FIELD_MAPPING).copy()
            if field_class.boost != 1.0:
                field_mapping['boost'] = field_class.boost

            if field_class.document is True:
                content_field_name = field_class.index_fieldname

            # Do this last to override `text` fields.
            if field_mapping['type'] == 'string':
                if field_class.indexed is False or hasattr(field_class, 'facet_for'):
                    field_mapping['index'] = 'not_analyzed'
                    del field_mapping['analyzer']

            mapping[field_class.index_fieldname] = field_mapping

        return (content_field_name, mapping)


class CustomElasticsearchSearchEngine(ElasticsearchSearchEngine):
    backend = CustomElasticsearchSearchBackend

