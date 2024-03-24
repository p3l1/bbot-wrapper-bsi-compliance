#!/bin/bash

echo "Cleaning up..."
docker compose down

echo "Starting Docker Compose stack..."
docker compose up -d

echo "Attaching to bbot output..."
docker compose logs -f scan
