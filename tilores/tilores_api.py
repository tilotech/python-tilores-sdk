from graphql import get_introspection_query, build_client_schema, print_schema
from functools import cached_property
import requests
import time
import os

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
        self._fields = None

    @classmethod
    def from_environ(cls, **kwargs):
        return cls(
            api_url=os.environ['TILORES_API_URL'],
            token_url=os.environ['TILORES_TOKEN_URL'],
            client_id=os.environ['TILORES_CLIENT_ID'],
            client_secret=os.environ['TILORES_CLIENT_SECRET'],
            **kwargs
        )

    @property
    def access_token(self):
        """Get the access token, refreshing it if necessary."""
        now = int(time.time())
        if self._access_token_expires_at and self._access_token_expires_at < now:
            return self._access_token
        else:
            self._access_token_expires_at = None
            self._access_token = None
            response = requests.post(
                self.token_url,
                auth=(self.client_id, self.client_secret),
                data={'grant_type': 'client_credentials', 'scope': ' '.join(self.scope)},
            )
            response.raise_for_status()
            data = response.json()
            self._access_token = data['access_token']
            self._access_token_expires_at = now + data['expires_in']
            return self._access_token

    @cached_property
    def gql_schema(self):
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
        """Get a list of search parameter names and types for the search query."""
        if not refresh and self._search_params is not None:
            return self._search_params
        data = self.gql("""
            {
                __type(name: "SearchParams") {
                    name
                    kind
                    inputFields {
                        name
                        description
                        type {
                            name
                            kind
                        }
                    }
                }
            }
        """)
        fields = [(field['name'], field['type']['name']) for field in data['data']['__type']['inputFields']]
        self._search_params = fields
        return self._search_params

    @property
    def fields(self, refresh=False):
        """Get a list of field names and their type for the Record-type."""
        if not refresh and self._fields is not None:
            return self._fields
        data = self.gql("""
            {
                __type(name: "Record") {
                    name
                    kind
                    fields {
                        name
                        description
                        type {
                            name
                            kind
                        }
                    }
                }
            }
        """)
        fields = [(field['name'], field['type']['name']) for field in data['data']['__type']['fields']]
        self._fields = fields
        return self._fields

    def search(self, **params):
        """Perform a search query with the given parameters."""
        query = """
            query search($params: SearchParams!) {
                search(input: { parameters: $params }) {
                    entities {
                        id
                        hits
                        records {
                            id
                            $$fields$$
                        }
                    }
                }
            }
        """
        data = self.gql(query.replace('$$fields$$', '\n'.join(params.keys())), variables={"params": params})
        return data

if __name__ == "__main__":
    import os
    TILORES_API_URL = os.environ['TILORES_API_URL']
    TILORES_TOKEN_URL = os.environ['TILORES_TOKEN_URL']
    TILORES_CLIENT_ID = os.environ['TILORES_CLIENT_ID']
    TILORES_CLIENT_SECRET = os.environ['TILORES_CLIENT_SECRET']

    tilores = TiloresAPI(
        api_url=TILORES_API_URL,
        token_url=TILORES_TOKEN_URL,
        client_id=TILORES_CLIENT_ID,
        client_secret=TILORES_CLIENT_SECRET
    )
    print(f'searchParams: {tilores.search_params}')
    tilores.search({"first_name": "John"})
    import pdb; pdb.set_trace()
    print('okthxbye')

