from pydantic import BaseModel
from pydantic import create_model
from graphql_query import Field

def pydantic_model_to_option_model(model: type[BaseModel]):
  fields = {}

  for name, field in model.model_fields.items():
    if isinstance(field.annotation, type) and issubclass(field.annotation, BaseModel):
      fields[name] = (pydantic_model_to_option_model(field.annotation), None)
    else:
      fields[name] = (bool, None)

  return create_model(model.__name__, **fields)

def option_model_to_graphql_fields(model: BaseModel):
  fields = []

  for name, field in model.model_fields.items():
    if isinstance(field.annotation, type) and issubclass(field.annotation, BaseModel):
      subfields = option_model_to_graphql_fields(getattr(model, name))
      if len(subfields) > 0:
        fields.append(Field(name=name, fields=subfields))
    elif getattr(model, name):
      fields.append(name)

  return fields