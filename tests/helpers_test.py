import unittest
from tilores.helpers import PydanticFactory
import graphql

class GraphQLModelFactoryTest(unittest.TestCase):
    def test_generate(self):
        """
        Test converting a GraphQL schema to pydantic base classes.
        """
        schema = None
        with open('tests/fixtures/schema.graphql') as f:
            schema = graphql.build_schema(f.read())
        references = PydanticFactory(schema).generate()
        assert 'Record' in references
        assert 'RecordInput' in references
        assert 'SearchParams' in references

    def test_generate_complex_schema(self):
        """
        Test converting a complex GraphQL schema to pydantic base classes.
        """
        schema = None
        with open('tests/fixtures/complex_schema.graphql') as f:
            schema = graphql.build_schema(f.read())
        references = PydanticFactory(schema).generate()
        assert 'Record' in references
        assert references['Record'].__doc__ is not None
        assert 'RecordInput' in references
        assert 'SearchParams' in references
        # Custom object type
        assert 'Address' in references
        # Enum
        assert 'SeasonEnum' in references
        assert references['SeasonEnum'].__doc__ is not None
        # Unions
        assert 'Discount' in references
        assert 'Coupon' in references
        # Interfaces
        assert 'Animal' in references

if __name__ == '__main__':
    unittest.main()

