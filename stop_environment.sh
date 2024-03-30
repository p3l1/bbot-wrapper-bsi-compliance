#!/bin/bash

source targets.env

echo "Cleaning up..."
docker compose down --remove-orphans
