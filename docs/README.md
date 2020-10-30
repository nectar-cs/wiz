# Shipping Apps on a Red Carpet

Nectar is a software distribution system for Kubernetes
applications. It gives publishers and their users an AppStore-like
platform for a best in class application handover, installation, troubleshooting, 
and updating experience.

Where Helm and Operators provide the functional primitives 
to make applications more portable, Nectar provides publishers
and users with structural components to operationalize that portability
in the real world.   

You can use Helm charts, Operators, Kustomize, [Kerbi](), client libraries, 
and anything a Kubernetes cluster can natively understand with Nectar.

## How it Works

It's easy to explain Nectar in terms of the technologies that closely relate to
it: Helm and Operators.

![alt text](https://storage.googleapis.com/nectar-mosaic-public/images/sys-arch-2.png "Logo Title Text 1")

### <u>Like Helm</u>: Variable-based Manifest Templating

Nectar follows Helm's variable-based templating model: 
applications are expected to generate their manifests by 
interpolating template files with variables from variables files
and command line args. 

Any templating engine works as long as it conforms to a simple protocol 
(next section). Three ingredient are necessary:
1. A template file (e.g a chart) with some substitution scheme
2. A values file for all substitutions
3. Some Templating Engine that prints out the interpolated result:

Like Helm, Nectar creates a ConfigMap/Secret to store the current
state of the `values` the user passes to the templating engine.

### <u>Unlike Helm</u>: Bring your own Templating Engine

Unlike Helm, with Nectar, application distribution is decoupled
from manifest templating. That means Nectar is **not bound to
 any one templating engine**. 
Instead, it works with any **container image** or **API** that, when invoked, 
outputs templated YAML/JSON given a collection of values for substitution.
We call this abstraction the **Templatable Application Manifest** 
or **TAM** for short.   

#### TAMs as Containers

Any container image that performs the following works:
1. `docker run <my-tam> values` => dump of default values in YAML/JSON
2. `docker run <my-tam> template -f <values-file-path> --set var=val` => 
	dump templated manifest as YAML/JSON

If you use Helm today, you can grab the `helm2nectar` 
docker image to do this automatically.
Otherwise, you can roll out your own by hacking a simple script together.

#### TAMs as APIs

Any API that performs the following works:
1. `GET https://<my-tam-host>/values` => dump of default values as JSON
2. `POST https://<my-tam-host>/template {values: <values as JSON>}` => dump templated manifest as JSON


### <u>Like Operators</u>: Encoding Operational Knowledge

Transfering application-specific infrastructure knowledge is
necessary for successful Kubernetes application handovers.
Operators do this by adding automation logic around resource lifecycle. 
At scale though, because the interfaces for
Operators are themselves Kubernetes resources (i.e 
`CustomResourceDefinition`s), **operating the operator**
can become the new knowledge bottleneck.

Nectar thinks about Operators as low level control modules.
Instead, vendors define interactive step-by-step operations 
for users to invoke on demand. These operations can in turn
interact with traditional Operators.


### <u>Unlike Operators</u>: Centralized, Simple, Interactive

The biggest change in Nectar, and the object of most of the ensuing
documentation is **the `wiz`**. The `wiz` is a micro-application 
that ships with the vendor's main application (like a `sidecar` 
except 1 per namespace). 
It is a feature-rich backend that exposes a standardized control interface for installing,
monitoring, updating, configuring, troubleshooting, and uninstalling
applications from their clusters. It is essentially a portable devops 
central hub for an application.

A vendor develops a `wiz` micro-app with the `nectwiz` SDK. 
The `wiz` is then containerized and injected into the vendor's application's namespace
when the user decides to begin the installation.
The main application **does not depend on the `wiz` to run**. The `wiz` 
workload can be destroyed at any time, and the client application will
recreate it as needed.
 
### <u>Like any App Store</u>: Centralization & Telemetry 

With regard to distribution, Nectar is similar to the Artifact Hub: 
- Publisher creates a listing on the [vendor portal](https://vendor.codenectar.com)
- User installs/operates application via dedicated desktop/CLI program

In addition, publishers can create distribution channels (e.g `main, alpha, beta` etc)
as well as setup access rules with payment plans and licenses.


## Next Steps

Familiarize yourself with the [Key Concepts](key-concepts.md), 
or learn by doing by [Getting Started](getting-started.md).