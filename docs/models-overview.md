# Models Overview

Models are the fundamental building blocks of a `wiz`. Much like
a Kubernetes resource, a Nectar model represents an entity,
and exposes a customization API in the form of YAML.
 
As a publisher, the bulk of your `wiz` development
 work will be writing models. The subsections cover basic syntax and rules common
 across all models. 

## Registering Models

You have to tell `nectwiz` about your models in your `wiz`'s `main.py`
before calling `entrypoint.start()`. 

```python
import os

from nectwiz import entrypoint
from nectwiz.model.base.wiz_model import models_man
from nectwiz.core.core import utils

if __name__ == '__main__':
  yamls_root_dir = os.path.dirname(os.path.abspath(__file__))
  model_dicts = utils.yamls_in_dir_to_dicts(f'{yamls_root_dir}/configs')

  models_man.add_descriptors(model_dicts)
  models_man.add_classes([MyModelSubclass1, MyModelSubclass2])

  entrypoint.start()
```

Notice that `models_man.add_descriptors` takes in `dict`s rather 
than raw YAML. This gives you the flexibility of managing model 
definitions however you like, as long as they can be serialized to `dict`s.


## Models as YAML

When you add a model using the method above, it **must** have 
an `id` and a `kind` that identify it uniquely.

```yaml
kind: SomeKind
id: an.id
```
A model's `id` can have no uppercase letters or spaces. Nested
models are, for readability, encouraged to use dot notation, 
e.g `machine.automobile.scooter`.


### Children

Almost all model have child models. There are **three ways**
of expressing child relations:

#### Referencing Children by ID

```yaml
kind: Parent
id: parent
children:
	- "child"

---

kind: Child
id: child
title: Foo
info: Bar
```

In this hypothetical example, the `Parent` knows (at the source code level)
that its `children`'s `kind` must be `Child`; as such an ID is enough to uniquely 
identify a child.

> Note: order of parent versus child does not matter


#### Embeddeding Children Directly
```
kind: Parent
id: parent
children:
	- title: Foo
	  info: Bar
```

Once more, we can omit the child's `kind` because the parent 
knows it must be `Child`. We also omit the ID, but there are
cases where this is not legal.

#### Referencing Children by Kind

In some cases, an unconfigured instance of a child moddel is
enough. In these cases, you can pass a string designating
that child's kind; when the child is loaded, its default
configuration will be used.

```
kind: Parent
id: parent
children:
	- Child
```

Assuming there is a model called `Child`. Note that a reference name
that starts with a capital letter will be interpreted as a `kind`.


#### Mixing Children Declarations

A parent can mix all three types of children in a list:
```
kind: Parent
id: parent
children:
	- "child-1"
	- id: "child-2"
	  title: Car
	  info: Zar
    - "Child"

---

kind: Child
id: child-1
title: Foo
info: Bar
```

### Inheriting

YAML-based models can also borrow from each other using the 
`inherit_id` field:

```yaml
kind: Foo
id: foo
some_property: bar

---

kind: Foo
id: almost-foo
inherit_id: foo
```

When `wiz` inflates `almost-foo`, it will replace its configuration
with the contents of `foo`, except for `id`. Thus, when `almost-foo.some_property` 
is read, the result will be `"bar"`.

## Subclassing Models

There will be times when a model's configuration API doesn't have the expressive
power needed to do the thing you need it to. That's when you **subclass**
a model.

Taking a real example: you need a `Predicate` to decide whether a `string` is
valid based on rules ill suited for a regular expression. We can easily 
extend the `Predicate` class:

```
from nectwiz.models.predicate import Predicate

class MyCustomPredicate(Predicate):
	def evaluate(challenge) -> bool:
		if type(challenge) == str:
			# my custom decision logic
		return False

```
