# Models Overview

Models are the fundamental building blocks of a `wiz`. Much like
a Kubernetes resource, a Nectar model represents an entity,
and exposes a customization API in the form of YAML.
 
Practically speaking, models are a convenient way for publishers to customize the `wiz`'s behavior.
Instead of letting publishers directly write the HTTP controllers 
that ultimately provide Nectar's client-facing app with the necessary data,
the `wiz` controllers handle boilerplate I/O work and delegate the real 
work to relevant models.

 
As a publisher, the bulk of your `wiz` development work will be 
writing models. This page describes the basic mechanics of models without 
looking at one model in particular. 



## Anatomy of a Model 

Every model in a `wiz` is a subclass of `WizModel` and has the four
following properties definable in YAML:

```yaml
kind: SomeWizModelSubClassName
id: string-unique-in-its-subclass
title: Human Friendly Name If Displayed
info: Human Friendly Description if Displayed
```

Beyond these four, different models will have different properties. 

> **Every top level model needs an `id` and a `kind`**. A top level model is one that
is not an embedded child of another model. For children, `kind` is implied and `id` is
often optional. Read more in Children section. 

A model's `id` can have no uppercase letters or spaces. Nested
models are, for readability, encouraged to use dot notation, 
e.g `machine.automobile.scooter`, but this is not a requirement.

### Dynamic Property Values

The examples up to now have shown only static property-value assignments:
```yaml
kind: Foo
id: bar
title: This will not change
``` 

However, it's possible and often necessary to make values dynamic. There are
two mechanisms that can achieve this (although they are not interchangeable): 
**string interpolation** and **`ValueSupplier`s.

#### String Interpolation

When a `WizModel` loads a property, it will try to interpolate anything in the
form of `"don't interpolate {<do-interpolate>}"`. Depending on the model, different
tokens will be interpolated to different things. There is, however, one set
of tokens that will interpolatable anywhere regardless of context:  

| Token                      | Description                                                           |
|----------------------------|-----------------------------------------------------------------------|
| `app/ns`                   | Returns namespace where this application is installed                 |
| `app/install_uuid`         | Returns `install_uuid` to communicate with Nectar API                 |
| `tam_config/<key>`         | Returns `<key>` property of the `tam` e.g `tam_config/version`        |
| `manifest_variables/<key>` | Returns manifest var value e.g `manifest_variables/frontend.svc.type` |
| `prefs/<key>`              | Returns prefs var value e.g `prefs/telem-db.strategy`                 |


As such, the following Predicate would work correctly: 
```yaml
kind: Predicate
title: Check if the frontend is a LoadBalancer or a NodePort
challenge: "{manifest_variables/frontend.svc.type}"
operator: in
check_against: [NodePort, LoadBalancer]
```

#### Value Suppliers

In cases when string interpolation is not enough, you can use one of the pre-built `ValueSupplier` subclasses
or write your own. To use a `ValueSupplier`, embed it in your hierarchy or refer to it via id. For
example, the following Predicate uses a `ResourcesSupplier`, which is a subclass of `ValueSupplier`, 
to a list of strings (in this case it might be `['Running', 'Pending']`).

```yaml
kind: Predicate
title: Check if the frontend Deployment's pods are all running
challenge: 
  kind: ResourcesSupplier
  output: raw.status.phase
  selector: 
    res_kind: Pod
    label_selector:
      app: frontend
operator: only
check_against: Running
```



> When embedding a `ValueSupplier` subclass, **its `kind` must be explicitly set** for
`wiz` to interpret it as a special object.  


## The Model Hierarchy: Children

Almost all model have child models. There are **three ways**
of expressing child relations:

### Referencing by ID

If a parent model has a child with an id, and that child is defined at the top level, 
the following is valid:

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

> In this hypothetical example, the `Parent` knows (at the source code level)
that its `children`'s `kind` must be `Child`; as such, an ID is enough to uniquely 
identify a child.

> Parent-versus-child order has no effect. A child can be defined before its parent and vice-versa.


### Embedding Children Directly

When children are not re-used, it often makes sense to embed them
directly: 

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

> If the child is given an ID, models at the parent's level other 
than the parent itself will **not** be able to reference it.


#### Referencing Children by Kind

In some cases, an child model without any configuration is
enough. In these cases, you can pass a string designating
that child's kind; when the child is loaded, its default
configuration will be used.

```
kind: Parent
id: parent
children:
	- Child
```

Assuming there is a model class called `Child`. Note that a reference name
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

## Dynamic Child Expressions: IFTT Models

It's sometimes convenient to decide what a model should be at runtime.
You can specify **a special `Iftt` Model (If This Then That)** in place of a
regular child. An Iftt evaluates a list of Predicates one by one and returns the 
value associated with the first Predicate that evaluates to true:

```yaml
kind: Iftt
id: nectar.iftts.telem-db-action-iftt
items:
  - predicate:
      challenge: "{operation/telem_db.strategy}"
      check_against: managed_pvc
    value: nectar.actions.delete-telem-db-resources-then-apply
  - predicate: TruePredicate
    value: nectar.actions.delete-telem-db-resources
```  

> To express an `else` or `default` case, give that clause a `TruePredicate`.

## The Model Hierarchy: Inheriting in YAML

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

# Writing Custom Models

Writing custom models is trivial. You need to subclass a `WizModel` or
one of its subclasses and then overwrite whichever methods are necessary.

For example, to write a custom `Action` that POSTed a value supplied by the
user during an Operation, the code might be: 

```python
class PostToOurApiAction(Action):
  def _perform(self, **kwargs):
    value = kwargs.get('state').get('value-of-interest')
    requests.post("our-api.com/endpoint", {value: value})
```

# Registering Models

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

