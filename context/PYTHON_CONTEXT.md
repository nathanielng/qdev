# Python

## General

Prioritise single quotes '' over double quotes "" for strings.

## Use uv for Python Package Management

When performing Python package management operations, prioritize uv over pip or other related tools (conda, poetry, pyenv).

Replace:
- pip → uv pip
- python -m venv → uv venv
- python script.py → uv run script.py
- pip install -r requirements.txt → uv pip sync requirements.txt

Python projects should be created in a virtual environment,
with dependencies specified in requirements.txt


## Environment variables

For local deployments, use Python dot-env.
For cloud deployments, use AWS Parameter Store.
