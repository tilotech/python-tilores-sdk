import unittest
from tilores import TiloresAPI
import time
import graphql

class IntegrationTest(unittest.TestCase):
    """
    This is a set of tests run against a specific Tilores instance,
    pre-configured with a fixed schema and fixed test data.

    Before running these tests, obtain a set of API credentials and
    provide them in your environemnt. See also: .envrc.example

    You can find the schema in:    tests/fixtures/integration.graphql
    You can find the test data in: tests/fixtures/integration.jsonl
    """
    @classmethod
    def setUpClass(cls):
        cls.tilores = TiloresAPI.from_environ()

    def test_access_token(self):
        now = int(time.time())
        access_token = self.tilores.access_token
        self.assertIsNotNone(access_token)
        self.assertEqual(self.tilores.access_token, access_token)
        self.assertGreaterEqual(self.tilores._access_token_expires_at, now + 3600)
        new_access_token, _expires_in = self.tilores.fetch_access_token()
        self.assertNotEqual(new_access_token, self.tilores.access_token)

    def test_schema(self):
        schema = self.tilores.schema
        self.assertEqual(schema, self.tilores.schema)
        self.assertIsInstance(schema, graphql.type.schema.GraphQLSchema)
        self.assertIsInstance(schema.get_type('SearchParams'), graphql.type.schema.GraphQLInputObjectType)
        self.assertIsInstance(schema.get_type('RecordInput'), graphql.type.schema.GraphQLInputObjectType)
        self.assertIsInstance(schema.get_type('Record'), graphql.type.schema.GraphQLObjectType)

    def test_search_params(self):
        field_names = [x for (x, _) in self.tilores.search_params]
        self.assertEqual(field_names, [
            'first_name',
            'last_name',
            'name',
            'dob',
            'birthday',
            'address_line',
            'street',
            'housenumber',
            'postal_code',
            'zip',
            'city',
            'phone',
            'email',
            'lat',
            'lng',
            'receivedDate',
        ])

    def test_record_fields(self):
        field_names = [x for (x, _) in self.tilores.record_fields]
        self.assertEqual(field_names, [
            'id',
            'source',
            'first_name',
            'last_name',
            'name',
            'dob',
            'birthday',
            'address_line',
            'street',
            'housenumber',
            'postal_code',
            'zip',
            'city',
            'phone',
            'email',
            'lat',
            'lng',
            'receivedDate',
        ])

    def test_record_params(self):
        field_names = [x for (x, _) in self.tilores.record_params]
        self.assertEqual(field_names, [
            'id',
            'source',
            'first_name',
            'last_name',
            'name',
            'dob',
            'birthday',
            'address_line',
            'street',
            'housenumber',
            'postal_code',
            # 'zip',
            'city',
            'phone',
            'email',
            'lat',
            'lng',
            'receivedDate',
        ])

    def test_search(self):
        result = self.tilores.search(first_name='Sophia', last_name='Müller', dob='1990-04-15')
        entities = result['data']['search']['entities']
        self.assertEqual(len(entities), 1)
        # Test that search params are validated against the Record type
        with self.assertRaises(AssertionError):
            self.tilores.search(field_does_not_exist='Sophia')

if __name__ == '__main__':
    unittest.main()

