#!/bin/bash

echo "This command needs to be run inside the bbot source root directory"
docker buildx build --platform linux/amd64 -t blacklanternsecurity/bbot:bsi_compliance .
