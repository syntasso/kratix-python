# How to use this example

This Promise was generated with using kratix CLI:

```bash
kratix init promise database  --group demo.kratix.io --kind Database
```

To see this example promise working, you need to build and load two images to your environment:
1. promise configure workflow container image
2. resource configure workflow container image

You can build and load the promise configure workflow image by running:
```bash
docker build -t kratix-demo/promise-pipeline:v0.1.0 workflows/promise/configure/dependencies/configure-deps
kind load docker-image kratix-demo/promise-pipeline:v0.1.0 -n <your-local-kind-cluster>
```

For the resource configure workflow, run:
```bash
docker build -t kratix-demo/resource-pipeline:v0.1.0 workflows/resource/configure/database-configure/kratix-demo-resource-pipeline
kind load docker-image kratix-demo/resource-pipeline:v0.1.0 -n <your-local-kind-cluster>
```

After making these two images available in your k8s cluster, you can install the promise:
```bash
kubectl apply -f promise.yaml
```

you can request a database by:
```bash
kubectl apply -f example-resource.yaml
```
