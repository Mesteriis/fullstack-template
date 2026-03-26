#!/bin/sh
set -eu

host="${API__HOST:-0.0.0.0}"
port="${API__PORT:-8000}"

exec uvicorn main:app --host "$host" --port "$port"
