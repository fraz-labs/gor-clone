import os
import requests
import csv
import datetime
import base64

def encode_content(content):
    """Encode content to base64."""
    return base64.b64encode(content.encode('utf-8')).decode('utf-8')

def get_csv_content(repo, path, token):
    """Get existing CSV content or return headers for a new CSV."""
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = base64.b64decode(response.json()['content']).decode('utf-8')
        return content.split('\n')
    else:
        # Return default CSV headers if file does not exist
        return ["Draft Creation Date,PR Name,Submission Date,Merge Date,Total Lines - Blanks,Average Char per Line,Total Draft PRs,Total PRs Merged,PR Number,Repo Name"]

def create_or_update_file(repo, path, content, token, message="Update file"):
    """Create or update a file in the repository."""
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message, "content": encode_content(content)}
    response = requests.get(url, headers=headers)  # Check if file exists
    if response.status_code == 200:
        data["sha"] = response.json()["sha"]  # If exists, update it
    response = requests.put(url, json=data, headers=headers)
    if response.status_code in [200, 201]:
        print(f"Successfully created/updated the file: {path}")
    else:
        print(f"Failed to create/update the file: {response.json()}")

def update_csv_on_merge(repo, user_name, token):
    """Update CSV file when a PR is merged."""
    csv_path = f"contributors/{user_name}/contributions.csv"
    csv_lines = get_csv_content(repo, csv_path, token)
    csv_reader = csv.reader(csv_lines)
    csv_data = list(csv_reader)

    # Update the last entry with the merge date
    merge_date = datetime.datetime.now().strftime('%Y-%m-%d')
    if csv_data:
        csv_data[-1][3] = merge_date  # Merge date column

    # Convert back to CSV string
    updated_csv = "\n".join([",".join(row) for row in csv_data])
    create_or_update_file(repo, csv_path, updated_csv, token, "Update contributions CSV on PR merge")

def main():
    """Main function to execute script logic."""
    repo = os.environ['REPO']
    user_name = os.environ.get('USER_NAME')  # USER_NAME needs to be set in your GitHub Actions workflow
    token = os.environ['GH_TOKEN']

    update_csv_on_merge(repo, user_name, token)

if __name__ == "__main__":
    main()
