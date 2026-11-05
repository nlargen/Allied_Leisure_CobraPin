#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"
exec mpf game -c config.yaml,config_raspberry_pi.yaml
