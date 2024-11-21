from graphql import get_introspection_query, build_client_schema, GraphQLObjectType
from graphql_query import Operation, Query, Argument, Variable, Field
from functools import cached_property
from contextlib import contextmanager
import requests
import time
import os
from .record_insights import RecordInsights
from pydantic import BaseModel
from tilores.conversion import option_model_to_graphql_fields

class TiloresAPI:
    """A simple API client to interact with a Tilores instance."""

    def __init__(self,
        *,
        api_url: str,
        token_url: str,
        client_id: str,
        client_secret: str,
        scope: list[str] = None
        ):
        self.api_url = api_url
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope or ["tilores/mutation.submit", "tilores/query.search", "tilores/query.entity"]
        self._access_token = None
        self._access_token_expires_at = None
        self._golden_records = {}

    @classmethod
    def from_environ(cls, **kwargs):
        return cls(
            api_url=os.environ['TILORES_API_URL'],
            token_url=os.environ['TILORES_TOKEN_URL'],
            client_id=os.environ['TILORES_CLIENT_ID'],
            client_secret=os.environ['TILORES_CLIENT_SECRET'],
            **kwargs
        )

    def fetch_access_token(self):
        response = requests.post(
            self.token_url,
            auth=(self.client_id, self.client_secret),
            data={'grant_type': 'client_credentials', 'scope': ' '.join(self.scope)},
        )
        response.raise_for_status()
        data = response.json()
        return (data['access_token'], data['expires_in'])

    @property
    def access_token(self):
        """Get the access token, refreshing it if necessary."""
        now = int(time.time())
        if self._access_token_expires_at and self._access_token_expires_at > now:
            return self._access_token
        else:
            access_token, expires_in = self.fetch_access_token()
            self._access_token = access_token
            self._access_token_expires_at = now + expires_in
            return self._access_token

    @cached_property
    def schema(self):
        result = self.gql(get_introspection_query(descriptions=True))
        return build_client_schema(result['data'])

    def gql(self, query, variables=None):
        """Perform a GraphQL query against the Tilores instance."""
        data = {'query': query}
        if variables is not None:
            def to_serializable(val):
                if isinstance(val, BaseModel):
                    return val.dict()  # Converts Pydantic model to dict
                elif isinstance(val, dict):
                    return {k: to_serializable(v) for k, v in val.items()}
                elif isinstance(val, list):
                    return [to_serializable(v) for v in val]
                return val
            data['variables'] = to_serializable(variables)
        response = requests.post(
            self.api_url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            },
            json=data
        )
        response.raise_for_status()
        return response.json()

    @cached_property
    def search_params(self):
        """Get a list of tuples of search parameter names and types for the search query."""
        search_params = []
        for name, graphql_input_field in self.schema.get_type('SearchParams').fields.items():
            search_params.append((name, graphql_input_field.type))
        return search_params

    @cached_property
    def search_param_names(self):
        """Get a list of search parameter names for the search query."""
        return [x for (x, _) in self.search_params]

    @cached_property
    def records_definition(self):
        """Returns the field definition for the records field."""
        def subfieldsOf(type):
            subfields = []
            for name, subfield in type.fields.items():
                if isinstance(subfield.type, GraphQLObjectType):
                    subfields.append(Field(name=name, fields=subfieldsOf(subfield.type)))
                else:
                    subfields.append(name)
            return subfields

        return Field(name='records', fields=subfieldsOf(self.schema.get_type('Record')))

    @cached_property
    def record_params(self, refresh=False):
        """Get a list of tuples of field names and their type for the RecordInput-type."""
        record_params = []
        for name, graphql_input_field in self.schema.get_type('RecordInput').fields.items():
            record_params.append((name, graphql_input_field.type))
        return record_params

    @cached_property
    def record_param_names(self):
        """Get a list of search parameter names for the search query."""
        return [x for (x, _) in self.record_params]

    def search(self, recordFieldsToQuery, searchParams):
        """
        Perform a search query with the given parameters.

        Args:
            recordFieldsToQuery: A nested dict[str,bool] of GraphQL fields to query on the record field, should be limited to relevant fields.
            searchParams: Search parameters to use in the query.

        See also: https://docs.tilotech.io/tilores/api/#query-search
        """
        recordFields=Field(name="records", fields = option_model_to_graphql_fields(recordFieldsToQuery))
        var_params = Variable(name='params', type='SearchParams!')
        operation = Operation(
            type='query',
            name='search',
            variables=[var_params],
            queries=[
                Query(
                    name='search',
                    arguments=[
                        Argument(name='input', value=Argument(name='parameters', value=var_params))
                    ],
                    fields=[
                        Field(name='entities', fields=[
                            'id',
                            'hits',
                            recordFields
                        ])
                    ]
                )
            ]
        )
        return self.gql(operation.render(), variables={'params': searchParams})

    def entity_edges(self, entityID):
        """
        Searches for the edges of a single entity.
        """
        var_entity_id = Variable(name='entityID', type='ID!')
        operation = Operation(
            type='query',
            name='get_edges',
            variables=[var_entity_id],
            queries=[
                Query(
                    name='entity',
                    arguments=[
                        Argument(name='input', value=Argument(name='id', value=var_entity_id))
                    ],
                    fields=[
                        Field(name='entity', fields=[
                            'edges'
                        ])
                    ]
                )
            ]
        )
        return self.gql(operation.render(), variables={'entityID': entityID})