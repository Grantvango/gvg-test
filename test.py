import requests
import os
import time

# Set up environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is not set")

REPO_OWNER = 'gvg'
REPO_NAME = 'gvg-test'
WORKFLOW_ID = 'test.yml'

# GitHub API endpoint to trigger the workflow
trigger_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_ID}/dispatches'

# Headers for the request
headers = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github+json'
}

# Data payload for the request
data = {
    'ref': 'main'  # Branch to trigger the workflow on
}

# Make the request to trigger the workflow
trigger_response = requests.post(trigger_url, headers=headers, json=data)

# Check the response
if trigger_response.status_code == 204:
    print('Workflow triggered successfully.')
else:
    print(f'Failed to trigger workflow: {trigger_response.status_code}')
    print(trigger_response.json())
    exit(1)

# GitHub API endpoint to get the workflow runs
runs_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs'

# Wait for the workflow to complete
workflow_run_id = None
while True:
    runs_response = requests.get(runs_url, headers=headers)
    runs_data = runs_response.json()

    for run in runs_data['workflow_runs']:
        if run['head_branch'] == 'main' and run['status'] == 'completed':
            workflow_run_id = run['id']
            break

    if workflow_run_id:
        break

    print('Waiting for workflow to complete...')
    time.sleep(10)

# GitHub API endpoint to get the workflow run details
run_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{workflow_run_id}'

# Get the workflow run details
run_response = requests.get(run_url, headers=headers)
run_data = run_response.json()

# Print the workflow run conclusion
print(f'Workflow run conclusion: {run_data["conclusion"]}')
