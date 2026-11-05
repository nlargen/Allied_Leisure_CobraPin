#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"
exec mpf game -b -c config.yaml,config_raspberry_pi.yaml
