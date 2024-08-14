from typing import Optional, List
from graphql_query import Operation, Query, Argument, Variable, Field

DESC = 'DESC'
ASC = 'ASC'

class RecordInsights(Field):
    """
    This class implements a GraphQL query builder for RecordInsights queries on entities.

    See also: https://docs.tilotech.io/tilores/api/#record-insights
    """
    validate_field_names: Optional[List[str]] = None

    def __init__(self, alias=None, validate_field_names=None):
        super().__init__(name='recordInsights', alias=alias)
        self.validate_field_names = validate_field_names

    def assert_field_name(self, field_name):
        if self.validate_field_names is None:
            return
        assert field_name in self.validate_field_names, f'Field name {field_name} not present in field names: {self.validate_field_names!r}'

    def frequency_distribution(self, field_name, alias=None, top=1, direction=DESC):
        self.assert_field_name(field_name)
        alias = alias or field_name
        field = Field(
            name='frequencyDistribution',
            alias=alias,
            arguments=[
                Argument(name='field', value=f'"{field_name}"'),
                Argument(name='top', value=top),
                Argument(name='direction', value=direction),
            ],
            fields=[ 'value' ]
        )
        self.fields.append(field)
        return self

    def newest(self, sort_by_field_name, alias, fields):
        self.assert_field_name(sort_by_field_name)
        [self.assert_field_name(f) for f in fields if isinstance(f, str)]
        [self.assert_field_name(f.name) for f in fields if isinstance(f, Field)]
        field = Field(
            name='newest',
            alias=alias,
            arguments=[ Argument(name='field', value=f'"{sort_by_field_name}"') ],
            fields=fields
        )
        self.fields.append(field)
        return self

    def oldest(self, sort_by_field_name, alias, fields):
        self.assert_field_name(sort_by_field_name)
        [self.assert_field_name(f) for f in fields if isinstance(f, str)]
        [self.assert_field_name(f.name) for f in fields if isinstance(f, Field)]
        field = Field(
            name='oldest',
            alias=alias,
            arguments=[ Argument(name='field', value=f'"{sort_by_field_name}"') ],
            fields=fields
        )
        self.fields.append(field)
        return self

    def values(self, field_name, alias=None):
        self.assert_field_name(field_name)
        alias = alias or field_name
        field = Field(
            name='values',
            alias=alias,
            arguments=[ Argument(name='field', value=f'"{field_name}"')]
        )
        self.fields.append(field)
        return self

    def values_distinct(self, field_name, alias=None):
        self.assert_field_name(field_name)
        alias = alias or field_name
        field = Field(
            name='valuesDistinct',
            alias=alias,
            arguments=[ Argument(name='field', value=f'"{field_name}"')]
        )
        self.fields.append(field)
        return self

