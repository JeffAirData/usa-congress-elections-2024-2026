#!/usr/bin/env bash
# Rebuild everything. Pass --download to fetch fresh results first.
set -euo pipefail
cd "$(dirname "$0")/src"
if [[ "${1:-}" == "--download" ]]; then python3 download_sources.py; fi
python3 build_dataset.py
python3 download_winner_pages.py
python3 build_dataset.py gender
python3 build_groups.py
python3 build_charts.py
python3 build_page.py
python3 build_post.py
python3 build_cards.py
