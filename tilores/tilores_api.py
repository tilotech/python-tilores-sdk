from graphql import get_introspection_query, build_client_schema, print_schema
from graphql_query import Operation, Query, Argument, Variable, Field
from functools import cached_property
from contextlib import contextmanager
import requests
import time
import os
from .record_insights import RecordInsights

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
        self._search_params = None
        self._record_fields = None
        self._record_params = None
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
            data['variables'] = variables
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

    @property
    def search_params(self, refresh=False):
        """Get a list of tuples of search parameter names and types for the search query."""
        if not refresh and self._search_params is not None:
            return self._search_params
        self._search_params = []
        for name, graphql_input_field in self.schema.get_type('SearchParams').fields.items():
            self._search_params.append((name, graphql_input_field.type))
        return self._search_params

    @property
    def record_fields(self, refresh=False):
        """Get a list of tuples of field names and their type for the Record-type."""
        if not refresh and self._record_fields is not None:
            return self._record_fields
        self._record_fields = []
        for name, graphql_field in self.schema.get_type('Record').fields.items():
            self._record_fields.append((name, graphql_field.type))
        return self._record_fields

    @property
    def record_params(self, refresh=False):
        """Get a list of tuples of field names and their type for the RecordInput-type."""
        if not refresh and self._record_params is not None:
            return self._record_params
        self._record_params = []
        for name, graphql_input_field in self.schema.get_type('RecordInput').fields.items():
            self._record_params.append((name, graphql_input_field.type))
        return self._record_params

    def search(self, **params):
        """
        Perform a search query with the given parameters.

        See also: https://docs.tilotech.io/tilores/api/#query-search
        """
        actual_record_field_names = [x for (x, _) in self.record_fields]
        record_fields = []
        for key in params.keys():
            if key == 'id':
                continue
            assert key in actual_record_field_names, f'Invalid record field name: "{key}", not found in Record field names.'
            record_fields.append(key)
        [key for key in params.keys() if key != 'id']
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
                            Field(name='records', fields=[
                                'id',
                                *record_fields
                            ])
                        ])
                    ]
                )
            ]
        )
        return self.gql(operation.render(), variables={'params': params})

    @contextmanager
    def build_golden_record(self, query_alias):
        record_insights = RecordInsights(alias=query_alias)
        yield record_insights
        self._golden_records[query_alias] = record_insights
        return record_insights

    def fetch_golden_record(self, query_alias:str, id:str):
        """
        Retrieve a unified and aggregated version of a single entity using recordInsights.

        See also:

        * https://docs.tilotech.io/tilores/golden-record
        * https://docs.tilotech.io/tilores/api/#record-insights
        """
        record_insights = self._golden_records[query_alias]
        operation = Operation(
            type='query',
            queries=[
                Query(
                    name='entity',
                    arguments=[
                        Argument(name='input', value=Argument(name='id', value=f'"{id}"'))
                    ],
                    fields=[
                        Field(
                            name='entity',
                            fields=[record_insights]
                        )
                    ]
                )
            ]
        )
        return self.gql(operation.render())

