import requests
import os
import time
import uuid

# Set up environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is not set")

REPO_OWNER = 'Grantvango'
REPO_NAME = 'gvg-test'
WORKFLOW_ID = 'test.yml'  # Fixed workflow ID
BRANCH = 'main'  # Fixed branch

# Generate a unique trigger ID
trigger_id = str(uuid.uuid4())

# GitHub API endpoint to trigger the workflow
trigger_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_ID}/dispatches'

# Headers for the request
headers = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github+json'
}

# Data payload for the request
data = {
    'ref': BRANCH,  # Fixed branch
    'inputs': {'trigger_id': trigger_id}  # Pass unique trigger ID
}

# Make the request to trigger the workflow
trigger_response = requests.post(trigger_url, headers=headers, json=data)

# Check the response
if trigger_response.status_code == 204:
    print(f'Workflow triggered successfully with ID: {trigger_id}')
else:
    print(f'Failed to trigger workflow: {trigger_response.status_code}')
    print(trigger_response.json())
    exit(1)

# GitHub API endpoint to get the workflow runs
runs_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs'

# Wait for the workflow to start and get the workflow run ID
workflow_run_id = None
while True:
    runs_response = requests.get(runs_url, headers=headers)
    runs_data = runs_response.json()

    for run in runs_data['workflow_runs']:
        if run['head_branch'] == BRANCH and run['status'] == 'in_progress' and f'Python Script Trigger - {trigger_id}' in run['name']:
            workflow_run_id = run['id']
            break

    if workflow_run_id:
        break

    print('Waiting for workflow to start...')
    time.sleep(10)

# GitHub API endpoint to get the workflow run details
run_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{workflow_run_id}'

# Wait for the workflow to complete
while True:
    run_response = requests.get(run_url, headers=headers)
    print(run_response.text)
    run_data = run_response.json()

    print(run_data)

    if run_data['status'] == 'completed':
        break

    print('Waiting for workflow to complete...')
    time.sleep(10)

# Print the workflow run conclusion
print(f'Workflow run conclusion: {run_data["conclusion"]}')
