# bbot-wrapper-bsi-compliance
This repository contains all the files needed beyond bbot to create a compliance report based on BSI guidelines for TLS, SSH, IPSec.

## Running a scan

We execute bbot within a Docker container to ensure reproducible results in all environments.
To build the container including our additions use the following command:

```
docker buildx build --platform linux/amd64 -t blacklanternsecurity/bbot:bsi_compliance .
```

The above command builds the container for x86 systems. This is currently required due to a python dependency (nassl),
which is not available for ARM systems.
For usage within the `docker-compose.yml` the image is tagged with `bsi_compliance`.

For development purposes this repository contains mock services for IPSec, SSH and TLS. To use them,
run the `start_environment.sh` script.

To start a scan run the `scan.sh` script. The targets are specified within the `targets.env` file which is read
within the `scan.sh` script.
