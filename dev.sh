docker build . -f Dockerfile.hub-wiz -t gcr.io/nectar-bazaar/hub-wizard:latest
docker push gcr.io/nectar-bazaar/hub-wizard:latest
kubectl delete pod -l app=nectar-wizard -n self-hosted-hub
kubectl port-forward svc/nectar-wizard 5001:5000 -n self-hosted-hub