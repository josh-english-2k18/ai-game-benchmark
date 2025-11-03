# TPU Deployment Stub

Use this directory as the starting point for provisioning a Cloud TPU-backed inference service. Suggested steps:

1. Configure variables for project, region, and TPU type in `variables.tf`.
2. Stand up a Compute Engine VM with TPU access and deploy the FastAPI server via the GPU Docker image.
3. Expose ports 8000 (HTTP) and 9000 (metrics) through a load balancer.

> Implementation intentionally left minimal so teams can tailor to their cloud environment.
