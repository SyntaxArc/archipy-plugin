#!/usr/bin/env bash
# Stage a minimal ArchiPy app so the plugin's ArchiPy-app hooks and skills apply.
set -euo pipefail
mkdir -p configs models repositories logics services
cat > pyproject.toml <<'TOML'
[project]
name = "shop"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = ["archipy[postgres,redis,fastapi,dependency-injection]>=5.4"]
TOML
touch configs/__init__.py models/__init__.py repositories/__init__.py logics/__init__.py services/__init__.py
