
# Turning a Helm Chart into an API 

Assuming Helm v3+. Ensure you have a working Helm chart that outputs the expected
text on both:
```shell script
helm template foo .
# and
helm show values
``` 

Then in your chart's home directory, create a Dockerfile with:

```dockerfile
FROM gcr.io/nectar-bazaar/helm2api:1.0.0
WORKDIR /app
ADD . .
RUN ['tam_server']
```

The `tam_server` is a binary from built from Nectar's open source 
[tam_server repo](https://github.com/nectar-cs/tam_server/releases). It converts HTTP requests
to `helm` commands.

The `gcr.io/nectar-bazaar/helm2api:latest` base image installs `helm` and `tam-server` and starts it 
on port 80.

Verify your server image by running: 
```
docker build . -t my-helm-server
docker run -p 5005:5005 my-helm-server
```

Inspect the server's output by visiting 

#### Step 2: Host

#### API-based TAM Protocol

There must be a publicly accessible server that supports two API calls:
```
GET https://<tam-api-uri>/api/values
POST https://<tam-api-uri>/api/template {values: <JSON value dump>}
```

When the `wiz` invokes a remote API-based TAM, it will be `POST`ing 
values over the web, so the API **must be behind HTTPS**.

> **Note:** Container based TAMs are more secure 
but are also **slower** due to the Pod-creation overhead.


# Turning a Kerbi Mixer into an API