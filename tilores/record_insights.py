from graphql_query import Operation, Query, Argument, Variable, Field

DESC = 'DESC'
ASC = 'ASC'

class RecordInsights(Field):
    """
    This class implements a GraphQL query builder for RecordInsights queries on entities.

    See also: https://docs.tilotech.io/tilores/api/#record-insights
    """

    def __init__(self, alias=None):
        super().__init__(name='recordInsights', alias=alias)

    def frequency_distribution(self, field_name, alias=None, top=1, direction=DESC):
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

    def newest(self, sort_by_field_name, alias, values):
        field = Field(
            name='newest',
            alias=alias,
            arguments=[ Argument(name='field', value=f'"{sort_by_field_name}"') ],
            fields=values
        )
        self.fields.append(field)
        return self

    def oldest(self, sort_by_field_name, alias, values):
        field = Field(
            name='oldest',
            alias=alias,
            arguments=[ Argument(name='field', value=f'"{sort_by_field_name}"') ],
            fields=values
        )
        self.fields.append(field)
        return self

    def values(self, field_name, alias=None):
        alias = alias or field_name
        field = Field(
            name='values',
            alias=alias,
            arguments=[ Argument(name='field', value=f'"{field_name}"')]
        )
        self.fields.append(field)
        return self

    def values_distinct(self, field_name, alias=None):
        alias = alias or field_name
        field = Field(
            name='valuesDistinct',
            alias=alias,
            arguments=[ Argument(name='field', value=f'"{field_name}"')]
        )
        self.fields.append(field)
        return self

