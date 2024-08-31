# Tilores Python SDK

The `tilores-sdk` Python package is a small SDK to develop with the [Tilores entity resolution system](https://docs.tilotech.io/tilores/).

## What is entity resolution?

Entity resolution is the connecting of non-identitcal, related data from disparate sources to "entities".
Entities can be anything from people, to companies to financial transactions.

Tilores is a highly-scalable, “entity-resolution” technology that was originally developed to connect internal data together. The technology was developed because we found that no other technology on the market could deliver the speed, scalability or cost performance we demanded.

Common use cases of entity resolution are:

* Deduplication of records from different sources
* Matching of financial transaction records
* Data cleaning and transformation
* Frequency analysis of individual attributes
* Retrieval Augmented Generation

## Example usage

### Installation

```console
$ pip install tilores-sdk
```

### Usage

* Given you have a Tilores instance setup
* Given you have a set of Tilores instance API credentials.

    Obtain your credentials from your Tilores instance in [Manage Instance > Integration > GraphQL API](https://app.tilores.io/).

* Given you have data loaded, and a schema configured that supports searching for the fields specified in this example.

```python
import os
from tilores import TiloresAPI

# Initialize the TiloresAPI (or use `TiloresAPI.from_environ()`)
tilores = TiloresAPI(
    api_url=os.environ['TILORES_API_URL'],
    token_url=os.environ['TILORES_TOKEN_URL'],
    client_id=os.environ['TILORES_CLIENT_ID'],
    client_secret=os.environ['TILORES_CLIENT_SECRET']
)
tilores.search({'name': 'Müller, Sophia'})
```

## Features

The Tilores SDK supports the following features of the Tilores API:

* Tilores instance authentication
* Tilores database schema and introspection
* Tilores database GraphQL queries
* Tilores entity resolution search
* Tilores golden record retrieval

In addition to that, it provides various convenience helpers to integrate with the Python ecosystem:

* Create pydantic base classes from the Tilores schema

