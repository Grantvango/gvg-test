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

# Headers for the request
headers = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github+json'
}

# test

def trigger_workflow():
    # Generate a unique trigger ID
    trigger_id = str(uuid.uuid4())

    # GitHub API endpoint to trigger the workflow
    trigger_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_ID}/dispatches'

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

    return trigger_id

def get_workflow_runs():
    runs_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs'
    runs_response = requests.get(runs_url, headers=headers)
    if runs_response.status_code == 200:
        return runs_response.json()['workflow_runs']
    else:
        print(f'Failed to fetch workflow runs: {runs_response.status_code}')
        print(runs_response.json())
        return []

def get_specific_run(run_id):
    run_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}'
    run_response = requests.get(run_url, headers=headers)
    if run_response.status_code == 200:
        return run_response.json()
    else:
        print(f'Failed to fetch workflow run: {run_response.status_code}')
        print(run_response.json())
        return None

def fetch_workflow_artifacts(run_id):
    # Fetch artifacts for the workflow run
    artifacts_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/artifacts"
    artifacts_response = requests.get(artifacts_url, headers=headers)

    if artifacts_response.status_code == 200:
        artifacts = artifacts_response.json()["artifacts"]
        for artifact in artifacts:
            if artifact["name"] == "workflow-output":
                artifact_id = artifact["id"]
                download_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/artifacts/{artifact_id}"
                action_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}"
                print(f"Artifact Download URL: {download_url}")
                print(f"Action URL: {action_url}")
                break
    else:
        print(f"Failed to fetch artifacts: {artifacts_response.text}")

if __name__ == "__main__":
    trigger_id = trigger_workflow()

    # Wait for the workflow to start and get the workflow run ID
    workflow_run_id = None
    while True:
        runs = get_workflow_runs()
        for run in runs:
            if run['name'] == f'Python Script Trigger - {trigger_id}':
                workflow_run_id = run['id']
                print(f'Found workflow run ID: {workflow_run_id}')
                break

        if workflow_run_id:
            break

        print('Waiting for workflow to start...')
        time.sleep(10)

    # Wait for the workflow to complete
    while True:
        run_data = get_specific_run(workflow_run_id)
        if run_data and run_data['status'] == 'completed':
            break

        print('Waiting for workflow to complete...')
        time.sleep(10)

    # Print the workflow run conclusion
    print(f'Workflow run conclusion: {run_data["conclusion"]}')

    # Fetch and print the artifact download URL
    fetch_workflow_artifacts(workflow_run_id)