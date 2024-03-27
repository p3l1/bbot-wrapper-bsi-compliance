# bbot-wrapper-bsi-compliance
This repository contains all the files needed beyond bbot to create a compliance report based on BSI guidelines for TLS, SSH, IPSec.

## Running a scan

We execute bbot within a Docker container to ensure reproducible results in all environments.
To build the container including our additions use the following command within the
[bbot sources](https://github.com/p3l1/bbot). Make sure to use the `bsi_compliance_report` branch to build the image
including all `bsi_compliance_<service>` modules.

```
docker buildx build --platform linux/amd64 -t blacklanternsecurity/bbot:bsi_compliance .
```

The above command builds the container for x86 systems. This is currently required due to a python dependency (nassl),
which is not available for ARM systems. The x86 container has also successfully been tested on ARM powered macOS
devices. For usage within the `docker-compose.yml` the image is tagged with `bsi_compliance`.

For development purposes this repository contains mock services for IPSec, SSH and TLS. To use them,
run the `start_environment.sh` script.

To start a scan run the `scan.sh` script. The targets are specified within the `targets.env` file which is read
within the `scan.sh` script. The default name of the scan is `bsi_compliance`. Use the `BBOT_SCAN_NAME` variable to
change the name of the scan.

For developing purposes the following services are available within the Docker Compose network provided by
the `docker-compose.yml` and can be used as targets.

| Service | DNS              | Port                  |
|---------|------------------|-----------------------|
| SSH     | `ssh.internal`   | `22/tcp`              |
| HTTPS   | `tls.internal`   | `443/tcp`             |
| IPSec   | `ipsec.internal` | `500/udp`, `4500/udp` |


## Viewing the results

The scan results are by default available as newline-delimited JSON at `./scans/bsi_compliance/output.ndjson`. To view 
the results within the shell, the following command can be used. It filters for the `BSI_COMPLIANCE_RESULT` events.

```
jq -c 'select(.type == "BSI_COMPLIANCE_RESULT")' scans/bsi_compliance/output.ndjson | jless
```

## Generating compliance report

TODO