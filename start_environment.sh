#!/bin/bash

echo "Starting service containers..."
docker compose up -d ipsec ssh tls neo4j
