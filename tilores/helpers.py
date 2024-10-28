import graphql
import typing
from enum import Enum
import datetime
from pydantic import create_model, Field

TILORES_ROOT_TYPES = ['Record', 'RecordInput', 'SearchParams']

class PydanticFactory():
    def __init__(self, schema):
        self.references = {}
        self.schema = schema

    def generate(self):
        [self.create_model(model_name) for model_name in TILORES_ROOT_TYPES]
        return self.references

    def create_model(self, model_name:str):
        if model_name in self.references:
            return self.references[model_name]
        graphql_type = self.schema.get_type(model_name)
        assert graphql_type is not None, f'Cannot get type in schema for: {model_name!r}'
        fields = {}
        for field_name, field_type in graphql_type.fields.items():
            default_value, python_type = self.type_of(field_type)
            field = (python_type, Field(default_value, description=f'A value for {field_name} of type {python_type!r}'))
            fields[field_name] = field
        model = create_model(model_name, **fields, __doc__=graphql_type.description)
        self.references[model_name] = model
        return model

    def type_of(self, graphql_type, default_value=None):
        python_type = None
        match graphql_type:
            case graphql.type.definition.GraphQLInputField() | graphql.type.definition.GraphQLField():
                default_value, python_type = self.type_of(graphql_type.type, default_value)
            case graphql.type.definition.GraphQLNonNull():
                default_value = ...
                _, python_type = self.type_of(graphql_type.of_type, default_value)
            case graphql.type.definition.GraphQLScalarType(name='String') | graphql.type.definition.GraphQLScalarType(name='ID'):
                python_type = str
            case graphql.type.definition.GraphQLScalarType(name='Int'):
                python_type = int
            case graphql.type.definition.GraphQLScalarType(name='Boolean'):
                python_type = bool
            case graphql.type.definition.GraphQLScalarType(name='Float'):
                python_type = float
            case graphql.type.definition.GraphQLScalarType(name='Time'):
                python_type = datetime.time
            case graphql.type.definition.GraphQLScalarType(name='Date'):
                python_type = datetime.date
            case graphql.type.definition.GraphQLScalarType(name='DateTime'):
                python_type = datetime.datetime
            case graphql.type.definition.GraphQLList():
                inner_default_value, inner_python_type = self.type_of(graphql_type.of_type)
                if inner_default_value is not ...:
                    inner_python_type = typing.Optional[inner_python_type]
                python_type = list[inner_python_type]
            case graphql.type.definition.GraphQLEnumType(name=enum_model_name):
                if enum_model_name in self.references:
                    python_type = self.references[enum_model_name]
                else:
                    python_type = Enum(enum_model_name, [enum_field.value for enum_field in graphql_type.values.values()])
                    python_type.__doc__ = graphql_type.description
                    self.references[enum_model_name] = python_type
            case graphql.type.definition.GraphQLUnionType(name=union_model_name):
                inner_python_types = []
                for inner_graphql_type in graphql_type.types:
                    inner_python_type = self.create_model(inner_graphql_type.name)
                    inner_python_types.append(inner_python_type)
                python_type = typing.Union[*inner_python_types]
            case graphql.type.definition.GraphQLObjectType(name=model_name) | graphql.type.definition.GraphQLInterfaceType(name=model_name) | graphql.type.definition.GraphQLInputObjectType(name=model_name):
                python_type = self.create_model(model_name)
            case _:
                raise NotImplementedError(f'Unmatched case for GraphQL type: {graphql_type!r}')
        if default_value is not ...:
            python_type = typing.Optional[python_type]
        return default_value, python_type

