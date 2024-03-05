#!/bin/bash

echo "Cleaning..."
docker compose down

echo "Starting Docker Compose stack..."
docker compose up -d

echo "Attaching to bbot output..."
docker compose logs -f scan
