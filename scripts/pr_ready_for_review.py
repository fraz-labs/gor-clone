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

def update_csv_on_ready_for_review(repo, user_name, pr_number, token):
    csv_path = f"contributors/{user_name}/contributions.csv"
    csv_lines = get_csv_content(repo, csv_path, token)
    csv_reader = csv.reader(csv_lines)
    csv_data = list(csv_reader)

    # Fetch PR details
    pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    pr_response = requests.get(pr_url, headers={"Authorization": f"Bearer {token}"})
    if pr_response.status_code != 200:
        print(f"Failed to fetch PR details for PR #{pr_number}")
        return
    pr_data = pr_response.json()

    # Append or update data
    submission_date = datetime.datetime.now().strftime('%Y-%m-%d')
    pr_name = pr_data['title']
    pr_number = pr_data['number']
    new_row = [submission_date, pr_name, "", "", "", "", "", "", pr_number, repo]
    csv_data.append(new_row)

    # Convert back to CSV string
    updated_csv = "\n".join([",".join(map(str, row)) for row in csv_data])

    # Create or update the CSV file
    content = encode_content(updated_csv)
    create_or_update_file(repo, csv_path, content, token, "Update contributions CSV for PR ready for review")

def create_or_update_file(repo, path, content, token, message="Update file"):
    """Create or update a file in the repository."""
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message, "content": content}
    response = requests.get(url, headers=headers)  # Check if file exists
    if response.status_code == 200:
        data["sha"] = response.json()["sha"]  # If exists, update it
    response = requests.put(url, json=data, headers=headers)
    if response.status_code in [200, 201]:
        print(f"Successfully created/updated the file: {path}")
    else:
        print(f"Failed to create/update the file: {response.json()}")

def main():
    repo = os.environ['REPO']
    pr_number = os.environ['PR_NUMBER']
    token = os.environ['GH_TOKEN']
    user_name = os.environ.get('USER_NAME')  # Adjust as needed to obtain the GitHub username

    update_csv_on_ready_for_review(repo, user_name, pr_number, token)

if __name__ == "__main__":
    main()
