#!/usr/bin/env sh

source .python_packages/bin/activate

export ABNORMAL_SECURITY_REST_API_TOKEN=123 
export SENTINEL_WORKSPACE_ID=123 
export SENTINEL_SHARED_KEY=123

pip install pytest-asyncio pytest pytest-aiohttp

pytest