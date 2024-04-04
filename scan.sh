#!/bin/bash

source targets.env

echo "Starting bbot..."
docker compose up -d scan graph

echo "Attaching to bbot output..."
docker compose logs -f scan
