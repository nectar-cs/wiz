# Operations


The `Operation` model holds the information and logic 
used to present users with the interactive sequences
they use in the client application:

![see on on screen](https://storage.googleapis.com/nectar-mosaic-public/images/Screenshot%20from%202020-12-02%2010-30-51.png) 

Structurally, an operation is a sequence of stages, which are in
turn a sequence steps. Steps have 1) an input phase, where the user 
enters values via their client app, and 2) an action phase, where
work is performed based on that input. 

The work performed can be any computation, but Nectar facilitates
Kubernetes-related work, like applying the manifest, deleting resources,
querying the cluster, etc... 

The entity hierarchy is
as follows:
![text](https://storage.googleapis.com/nectar-mosaic-public/images/operation-hierarchy%20(2).png)

## Operation

The Operation model only holds static information, namely `title`, `info`, and `synopsis`.

Note that the `synopsis` property, like all properties, supports asset loading:
```yaml
kind: Operation
id: my-org.operations.delete-old-backups
title: "Delete old backups"
synopsis: file::my-long-synopsis.html
```

Stages provided by Operations are in a fixed order that cannot be changed
at runtime.

## Preflight Check Predicates

Preflight checks are validations performed before an operations starts.
Their purpose is to assure the user that the application is in the required
state for this operation to be carried out. Zero or many may be provided.

  
```yaml
kind: Operation
id: demo
title: Delete all cache Pods
synopsis: <h1>Demo Operation</h1><p>Delete service, recreate it with a new type.</p>
preflight_checks:
	- nectar.predicates.ensure-config-backups-enabled
	- kind: Predicate
	  id: operation.demo.predicates.ensure-space-is-constrained
	  title: "Verify that database space is strained"
	  tone: warning
	  reason: "The backups database still has 90% capacity; you may not need to purge"  
      check_against: 10
      operator: less-than-or-equal
      challenge:
        kind: DatabaseStateSupplier
        database_id: backups 
        output: space-allocated-pct
```

## Stage

Like Operations, Stages are logical containers for organizing Steps.


```yaml
kind: Operation
stages:
    - kind: Stage
      id: my-org.stages.some
      steps:
          - id.to-some-step
          - id.to-some-other-step   
```

One difference in the Stage-Step relationship, compared with the Operation-Stage
relationship is determinism. When a Step has finished, it will have to option
to dictate the id of the next step, thus overriding the implied order. For example

```yaml
kind: Stage
id: my-org.stages.some-stage
steps:
    - id: step-one
      ...
      next: step-three
    - step-two
    - step-three
```
When combined with an Iftt Matrix, you can use `next` to 
conditionally define the sequence of steps:

```yaml
kind: Stage
id: my-org.stages.some-stage
steps:
    - id: step-one
      ...
      next: 
        kind: Iftt
        items:
          - predicate:
              challenge: "{manifest_variables/deployment.hpa.enabled}"
              check_against: true
            value: step-two
          - predicate: TruePredicate
            value: step-three
    - step-two
    - step-three
```

## Step

Steps hold collections of Fields that define what inputs the user sees, and an Action 
to perform work when the user clicks "submit".

```yaml
kind: Step
id: simple-read-and-apply-manifest
action: ApplyManifestAction
fields:
    - id: deployment-replicas
      variable: deployment-replicas
```

#### Routing input from Fields 
When a step is submitted, regardless of the step's Action, any values associated with
Fields whose `target` is `chart` or `prefs` will be written to
the master `ConfigMap`'s `manifest_variables` and `prefs` properties 
accordingly. Read more about [Field targets](#Field). 

Additionally, you can optionally specify a Field value re-mapping before any 
values are committed. In this example, a Field whose declared target was `state`
will have its value reassigned to `inline` when the step is submitted:
```yaml
kind: Step
id: var-multiplexer
info: "Redirect value from prev step to an inline assignment"
reassignments:
  - from: state
    to: inline
    id: 'password'
``` 

## Field

Fields are light but important models; they act as routers between
steps and Variables.

#### Specifying a Field's Target

Depending the meaning of the variable referenced by the Field, 
you may want to do different things with it once the 
step is submitted. 

For example, if your Field's variable is simply a 
CheckBox asks for consent, you won't want this 
to the manifest variables.

But conversely, if your field's variable has a 1-to-1 mapping with
the application's manifest variables, you 


For this reason, each Field has a `target` property that specifies
how to treat the submitted value. The `target` property can take on four different values:
- `chart`. This is the default. The value will be committed to the `manifest_variables`
dictionary in the master `ConfigMap`. 
- `prefs`.  The value will be committed to the `prefs` dictionary in 
the master `ConfigMap`.
- `inline`. The value will not be committed anywhere, but will be as an inline assignment
by any `ApplyManifestAction` subclass.
- `state`. The value will be cached  
 
#### Dynamically Displaying Fields

Oftentimes, you'll want to hide or show fields depending on the
value of other fields, or of other things, like already committed manifest 
variables. To do this, supply a Predicate to a Field's `show_condition`:

```yaml
kind: Step
# ...
fields:
      - id: var1
        variable: 
          id: var1
          default: foo
      - id: var2
        variable: var2
        show_condition:
          challenge: "{input/var1}"
          check_against: bar
```