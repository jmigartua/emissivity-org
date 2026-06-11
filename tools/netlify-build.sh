#!/usr/bin/env bash
# Netlify build script for emissivity.org
# Runs in Netlify's build image: installs Quarto, regenerates the
# data-driven pages, renders the site into _site.
set -euo pipefail

QUARTO_VERSION="1.6.42"

echo "--- Installing Quarto ${QUARTO_VERSION}"
mkdir -p "$HOME/quarto"
curl -sL "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz" \
  | tar xz -C "$HOME/quarto" --strip-components=1
export PATH="$HOME/quarto/bin:$PATH"
quarto --version

echo "--- Python dependencies"
python3 -m pip install --quiet pyyaml

echo "--- Generating data-driven pages"
python3 tools/generate_network.py
python3 tools/generate_featured.py

echo "--- Rendering site"
quarto render

echo "--- Copying script/data resources"
mkdir -p _site/assets
cp -r assets/data assets/scripts _site/assets/

echo "--- Build complete: $(find _site -name '*.html' | wc -l) pages"
