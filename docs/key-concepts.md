
# Key Concepts for Publishers


## Architecture

Nectar follows a losely coupled architecture; applications 
run _with_ it rather than _on_ it, in the sense that Nectar does 
not change an application's relationship with Kubernetes. In
fact, by default, **the vendor's core application has no knowledge of Nectar**. 

Instead, the extra functionality Nectar gives application users is 
tucked away in into a single workload (and optionally a databasse for telemetry)
whose state (including whether it randomly dies) has no bearing on
the actual application.

![alt text](https://storage.googleapis.com/nectar-mosaic-public/images/sys-arch-detail-1.png)

Below is a list of noteworthy characteristics.

#### One Application per Namespace

When a user begins installing an application, a namespace is 
created and populated with:
- The `wiz` workload - a single-pod `Deployment`
- The `master ConfigMap` detailed below
- An internal (i.e `ClusterIP`) service
- The ` master Secret` for various secrets
- RBAC resources - a `ServiceAccount`, `Roles`, `ClusterRoles`, and bindings

Nectar currently only understands "traditional" applications, i.e
a set of resources that can be grouped into a namespace. 

If your application is "Kubernetes aware" in that it creates 
resources that other workloads in other namespaces use (like sidecars),
then some additional configuration will be required if you want end-users
to make the most of Nectar.


#### Single Master ConfigMap

To minimize resource pollution, Nectar keeps all state data 
in a single ConfigMap called `master`:
- All TAM variable values
- All Nectar user-preferences
- A cache of all manifest default variable values
- `wiz` and `tam` connection configs

To mitigate the risk of a single point of failure, users
can opt-in to back these



#### Always Explicit, Seldom Autonomous

Vanilla Kubernetes + Operators give developers ample options for automating 
infrastructure workflows. Nectar is designed to put strangers to
the application in control. As such the `wiz` SDK's API is devoid of
any passive trigger logic, e.g "watch resources X and do Y when Z". For this,
developers are encouraged to use Operators. The only exception is checking
for updates in the background, which is disabled by default.

#### RBAC Bound

When a vendor publishes an app, they upload a fixed list of 
`Roles`, and `ClusterRoles` that their `wiz` must adhere to.
At install time, time the client application will **create
a `ServiceAccount` for the `wiz` bound to those policies**. 



## Templating with TAMs

Templating resource manifests is central to Kubernetes application development.
While the templating logic itself can vary widely in shape and complexity,
the **templating contract** is always the same and is always simple: 
provide variables as input, get Kubernetes-ready YAML/JSON back as output.   
As such, Nectar mandates a very simple **standard templating contract** while
making no assumptions about the templating method. We call this contract the **TAM:
Templatable Application Manifest**. 

## The Client Application

Users have two client programs to choose from: Nectop the desktop
application and `nectl` the CLI application.

Both client applications communicate with the application's `wiz` 
over HTTP using the Kubernetes cluster's `proxy` feature. 

Client applications offload as much functionality to an application's
`wiz` as possible, so as keep vendors in control of their apps. The client
applications themselves, while open-source, cannot be customized by vendors.


//## Wiz's
//### k8kat Kubernetes Client




