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
        return content
    else:
        # Return default CSV headers if file does not exist
        return "Draft Creation Date,PR Name,Submission Date,Merge Date,Total Lines - Blanks,Average Char per Line,Total Draft PRs,Total PRs Merged,PR Number,Repo Name\n"

def update_csv(repo, user_name, pr_data, token):
    """Append new data to the CSV or create it if it doesn't exist."""
    csv_path = f"contributors/{user_name}/contributions.csv"
    existing_csv_content = get_csv_content(repo, csv_path, token)
    csv_lines = existing_csv_content.strip().split('\n')
    csv_reader = csv.reader(csv_lines)
    csv_data = list(csv_reader)

    # Append new data
    pr_name = pr_data['title']
    draft_date = datetime.datetime.now().strftime('%Y-%m-%d')
    pr_number = pr_data['number']
    new_row = [draft_date, pr_name, "", "", "", "", "", "", str(pr_number), repo]
    csv_data.append(new_row)

    # Convert back to CSV string
    updated_csv = "\n".join([",".join(row) for row in csv_data])
    create_or_update_file(repo, csv_path, updated_csv, token)

def post_comment(repo, pr_number, message, token):
    """Post a comment on a PR."""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    payload = {"body": message}
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        print("Comment posted successfully.")
    else:
        print(f"Failed to post comment: {response.json()}")

def create_or_update_file(repo, path, content, token, message="Update file"):
    """Create or update a file in the repository."""
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "message": message,
        "content": encode_content(content),
    }
    # Try to get the file's current SHA to update; if not found, it will create a new file
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data["sha"] = response.json()["sha"]

    response = requests.put(url, json=data, headers=headers)
    if response.status_code in [200, 201]:
        print(f"Successfully created/updated the file: {path}")
    else:
        print(f"Failed to create/update the file: {response.json()}")

def create_user_directory_and_files(user_name, repo, token):
    """Create user directory and initial files if they don't exist."""
    base_path = f"contributors/{user_name}"
    file_paths = {
        f"{base_path}/README.md": "This is your README. Update it as you see fit.",
        f"{base_path}/notable-contributions.md": "List your notable contributions here.",
        f"{base_path}/contributions.csv": "Draft Creation Date,PR Name,Submission Date,Merge Date,Total Lines - Blanks,Average Char per Line,Total Draft PRs,Total PRs Merged,PR Number,Repo Name"
    }

    for path, content in file_paths.items():
        create_or_update_file(repo, path, content, token, f"Create {path.split('/')[-1]}")

def main():
    token = os.environ['GH_TOKEN']
    repo = os.environ['REPO']
    pr_number = os.environ['PR_NUMBER']

    # Fetch PR details
    pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {"Authorization": f"Bearer {token}"}
    pr_response = requests.get(pr_url, headers=headers)
    if pr_response.status_code == 200:
        pr_data = pr_response.json()
        user_name = pr_data['user']['login']

        # Post a comment on the PR
        post_comment(repo, pr_number, "Thank you for your Game of Realms submission! It will be reviewed shortly.", token)

        # Create user directory and initial files if they don't exist
        create_user_directory_and_files(user_name, repo, token)  # Ensure this function is defined

        # Update or create CSV with the new PR data
        update_csv(repo, user_name, pr_data, token)
    else:
        print(f"Failed to fetch PR details: {pr_response.status_code}")

if __name__ == "__main__":
    main()
