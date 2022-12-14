---
title: readme
author: Max Ludden
email: dev@maxludden.com
version: 0.1.0
---

# maxludden/supergene_classes

### Purpose

This module facilitates the retrieval, editing, and saving of data pertaining to the webnovel ["Super Gene"](https://bestlightnovel.com/novel_888112448) to [Mongodb](https://www.mongodb.com/) using [MongoEngine](https://github.com/MongoEngine/mongoengine).

### Instillation

`supergene_classes` is available on PyPi and can be installed using your favorite package manager:

#### Pipx (recommended)

```shell
pipx install supergene_classes
```

#### Pip

```shell
pip install supergene_classes
```

#### Poetry

```shell
poetry add supergene_classes
```

### Usage

`supergene_classes` contains custom classes for MongoEngine Documents and a number of helper functions to access them.

#### Classes

##### Chapter

```python
from mongoengine import connect, Document
from mongoengine.fields import (
    StringField,
    IntField,
    URLField,

)
Chapter(Document):
```
