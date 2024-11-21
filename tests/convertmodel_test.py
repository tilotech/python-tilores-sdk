import unittest
from pydantic import create_model
from graphql_query import Field
from tilores.conversion import *

class ConvertModelTest(unittest.TestCase):
  def test_pydantic_record_model_conversion(self):
    graphqlModel = create_model(
      "Record",
      id=(str, ...),
      firstName=(str, ...),
      lastName=(str, ...),
      age=(int, ...),
      addr=(create_model(
        "Address",
        street=(str, ...),
        house=(str, ...),
        city=(str, ...)
      ), ...)
    )
    actual = pydantic_model_to_option_model(graphqlModel)
    expected = create_model(
      "Record",
      id=(bool, None),
      firstName=(bool, None),
      lastName=(bool, None),
      age=(bool, None),
      addr=(create_model(
        "Address",
        street=(bool, None),
        house=(bool, None),
        city=(bool, None)
      ), None)
    )

    self.assertEqual(expected.model_json_schema(), actual.model_json_schema())

  def test_option_model_to_graphql_fields(self):
    graphqlModel = create_model(
      "Record",
      id=(str, ...),
      firstName=(str, ...),
      lastName=(str, ...),
      age=(int, ...),
      addr=(create_model(
        "Address",
        street=(str, ...),
        house=(str, ...),
        city=(str, ...)
      ), ...)
    )
    optionModel = pydantic_model_to_option_model(graphqlModel)
    options = optionModel(
      id=True,
      firstName=False,
      lastName=True,
      age=False,
      addr={
        "street":True,
        "house":False,
        "city":True
      }
    )
    actual = option_model_to_graphql_fields(options)
    expected = [
      "id",
      "lastName",
      Field(name="addr", fields=["street", "city"])
    ]

    options = optionModel(
      id=True,
      firstName=True,
      age=True,
      addr={
        "street":False,
        "house":False,
      }
    )
    actual = option_model_to_graphql_fields(options)
    expected = [
      "id",
      "firstName",
      "age"
    ]

    self.assertEqual(expected, actual)