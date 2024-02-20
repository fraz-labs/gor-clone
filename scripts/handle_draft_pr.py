import os
import requests
import csv
import datetime

def post_comment(repo, pr_number, message):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    payload = {"body": message}
    headers = {"Authorization": f"Bearer {os.environ['GH_TOKEN']}"}
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code

def create_user_directory(user_name, repo):
    base_path = f"contributors/{user_name}"
    file_paths = [f"{base_path}/README.md", f"{base_path}/notable-contributions.md", f"{base_path}/contributions.csv"]

    for file_path in file_paths:
        file_url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
        response = requests.get(file_url, headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}"})
        if response.status_code == 404:
            content = "Initial content" if "README" in file_path else "List of notable contributions" if "notable-contributions" in file_path else "Draft Creation Date,PR Name,Submission Date,Merge Date,Total Lines - Blanks,Average Char per Line,Total Draft PRs,Total PRs Merged,PR Number,Repo Name"
            payload = {
                "message": f"Create {file_path}",
                "content": content.encode("utf-8").decode("utf-8")
            }
            requests.put(file_url, json=payload, headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}"})
    
    return True

def update_csv(user_name, repo, pr_name, draft_date, pr_number, repo_name):
    csv_file_path = f"contributors/{user_name}/contributions.csv"
    csv_url = f"https://api.github.com/repos/{repo}/contents/{csv_file_path}"
    # Check if CSV exists
    response = requests.get(csv_url, headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}"})
    if response.status_code == 200:
        content = response.json()['content']
        decoded_csv = content.encode("utf-8").decode("utf-8")
        csv_data = list(csv.reader(decoded_csv.splitlines()))
    else:
    # Initialize new CSV data
        csv_data = [["Draft Creation Date", "PR Name", "Submission Date", "Merge Date", "Total Lines - Blanks", "Average Char per Line", "Total Draft PRs", "Total PRs Merged", "PR Number", "Repo Name"]]
    # Append new data
    csv_data.append([draft_date, pr_name, "", "", "", "", "", "", pr_number, repo_name])
    # Convert back to CSV string
    updated_csv = "\n".join([",".join(row) for row in csv_data])
    # Update or create CSV in the repository
    payload = {
        "message": f"Update {csv_file_path}",
        "content": updated_csv.encode("utf-8").decode("utf-8")
    }
    if response.status_code == 200:
        payload["sha"] = response.json()['sha']
    requests.put(csv_url, json=payload, headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}"})

def main():
    repo = os.environ['REPO']
    pr_number = os.environ['PR_NUMBER']

    # Fetch PR details
    pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    pr_response = requests.get(pr_url, headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}"})

    #Debugging

    print(f"Status Code: {pr_response.status_code}")
    print(f"Response: {pr_response.json()}")

    # Recheck if the API call was successful
    if pr_response.status_code != 200:
        print(f"Failed to fetch PR data: {pr_response.status_code}")
        print(pr_response.text)
        return  # Exit if unsuccessful

    
    pr_data = pr_response.json()
    user_name = pr_data['user']['login']
    pr_name = pr_data['title']
    draft_date = datetime.datetime.now().strftime('%Y-%m-%d')

    comment_status = post_comment(repo, pr_number, "Thank you for your Game of Realms submission! It will be reviewed shortly.")

    if create_user_directory(user_name, repo):
        update_csv(user_name, repo, pr_name, draft_date, pr_number, repo)

if __name__ == "__main__":
    main()
