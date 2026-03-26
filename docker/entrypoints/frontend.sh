#!/bin/sh
set -eu

backend_upstream="${BACKEND_UPSTREAM:-http://host.docker.internal:8000}"
export BACKEND_UPSTREAM="$backend_upstream"

# shellcheck disable=SC2016
envsubst '${BACKEND_UPSTREAM}' \
  < /etc/nginx/templates/default.conf.template \
  > /etc/nginx/conf.d/default.conf

exec "$@"
