# bbot-wrapper-bsi-compliance
This repository contains all the files needed beyond bbot to create a compliance report based on
BSI guidelines for TLS, SSH, IPSec. The BSI is the German ministry for cyber security.

## Requirements

- Python 3.12
- `pdflatex` binary must be present in `$PATH`
  - Debian/Ubuntu: `sudo apt-get install texlive-latex-base`
  - macOS: `brew install basictex`
- `docker compose` command must be available,
  - For `docker-compose` you may have to adjust the `*.sh` scripts

## Running a scan

We execute bbot within a Docker container to ensure reproducible results in all environments.
To build the container including our additions use the following command within our adjusted
[bbot sources](https://github.com/p3l1/bbot). Make sure to use the `bsi_compliance_report` branch to build the image
including all `bsi_compliance_<service>` modules.

```
git checkout bsi_compliance_report
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
| Neo4j   | `graph.internal` | `7474/tcp`            |


## Viewing the results

The scan results are by default available as newline-delimited JSON at `./scans/bsi_compliance/output.ndjson`. To view 
the results within the shell, the following command can be used. It filters for the `BSI_COMPLIANCE_RESULT` events.

```
jq -c 'select(.type == "BSI_COMPLIANCE_RESULT")' scans/bsi_compliance/output.ndjson | jless
```

### Neo4j

Alternatively the output can be viewed and managed using Neo4j. For this purpose the `docker-compose.yml` contains the
service called `graph` which starts a web interface at https://localhost:7474. For information on how to interact with
the data using Neo4j, check out the bbot [documentation](https://www.blacklanternsecurity.com/bbot/scanning/output/#neo4j).

## Generating compliance report

To generate a LaTeX compliance report you can use the `report.sh` bash script. It creates local python environment and
installs all dependencies needed for the report generation. Make sure you are inside the root of the project for the
script to work.

The report contains all `BSI_COMPLIANCE_RESULT`, `VULNERABILITY` and `FINDING` events. All scanned Host/Port pairs are
shown together with the given scan timestamp. By default, the report is based on `report/templates/report.tex.j2` and
the data is rendered into the template using Jinja2.
