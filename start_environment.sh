#!/bin/bash

echo "Cleaning up..."
docker compose down

echo "Starting Docker Compose stack..."
docker compose up -d ipsec ssh tls
