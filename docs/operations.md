# Operations


The `Operation` model holds the information and logic 
used to present users with the interactive sequences
they [see on on screen](features.md).

Operations can be written to perform any task, but the API's
configuration scheme is biased to facilitate common Kubernetes
tasks, like updating a variable then reapplying the manifest,
deleting resources, and starting Jobs.


For example, the following operation deletes 

```yaml
kind: Operation
id: demo
title: Delete all cache Pods
synopsis: <h1>Demo Operation</h1><p>Delete service, recreate it with a new type.</p>
preflight_checks:
	- nectar.predicates.ensure-config-backups-enabled
	- kind: ResourcePropertyCountPredicate
	  id: demo.check-svc-exists-preflight
	  title: "Ensure there exists a service to change"
	  selector:
	  	k8s_kind: services
	  	label_selector:
	  		app: chatbot
	  check_against: 0
	  operator: greater-than
stages:
	- id: demo.stage1
	  title: "Stage One"
	  info: "Perform one step and exit"
	  steps:
	  	- id: demo.stage1.step1
	  	  action


```


The entity hierarchy is
as follows:
![text](https://storage.googleapis.com/nectar-mosaic-public/images/operation-hierarchy%20(2).png)

## Operation

The Operation model only holds static information, namely 
- `title`
- `info`
- `synopsis`

Note that the `synopsis` field supports asset loading, e.g
```yaml
kind: Operation
synopsis: file::my-long-synopsis.html
```


## Preflight Check Predicates

Preflight checks are validations performed before an operations starts.
Their purpose is to assure the user that the system is in the required
state for this operation to be carried out.


  
