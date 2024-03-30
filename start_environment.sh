#!/bin/bash

source targets.env

echo "Starting service containers..."
docker compose up -d ipsec ssh tls graph
