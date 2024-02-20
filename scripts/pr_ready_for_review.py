import os
import requests
import csv
import datetime

def fetch_pr_details(repo, pr_number):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    response = requests.get(url, headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}"})
    return response.json()

def count_lines_and_chars(pr_files_url):
    response = requests.get(pr_files_url, headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}"})
    files_data = response.json()

    total_lines = 0
    total_chars = 0

    for file in files_data:
        if file['status'] != 'removed':
            patch = file.get('patch', '')
            lines = patch.split('\n')
            lines = [line for line in lines if line.strip() and not line.startswith('@@')]
            total_lines += len(lines)
            total_chars += sum(len(line) for line in lines)

    avg_chars_per_line = total_chars / total_lines if total_lines else 0
    return total_lines, avg_chars_per_line

def update_csv(user_name, repo, pr_details):
    csv_file_path = f"contributors/{user_name}/contributions.csv"
    csv_url = f"https://api.github.com/repos/{repo}/contents/{csv_file_path}"

    # Fetch existing CSV content
    response = requests.get(csv_url, headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}"})
    if response.status_code == 200:
        content = response.json()['content']
        decoded_csv = content.encode("utf-8").decode("utf-8")
        csv_data = list(csv.reader(decoded_csv.splitlines()))
    else:
        # Initialize new CSV data if file doesn't exist
        csv_data = [["Draft Creation Date", "PR Name", "Submission Date", "Merge Date", "Total Lines - Blanks", "Average Char per Line", "Total Draft PRs", "Total PRs Merged"]]

    # Update the last entry with new details
    total_lines, avg_chars_per_line = count_lines_and_chars(pr_details['url'])
    submission_date = datetime.datetime.now().strftime('%Y-%m-%d')

    if csv_data[-1][0] == "":  # No draft date recorded, create new entry
        csv_data.append(["", pr_details['title'], submission_date, "", total_lines, avg_chars_per_line, "", ""])
    else:  # Update last entry
        csv_data[-1][1] = pr_details['title']  # Update PR name if changed
        csv_data[-1][2] = submission_date
        csv_data[-1][4] = total_lines
        csv_data[-1][5] = avg_chars_per_line

    # Convert back to CSV string
    updated_csv = "\n".join([",".join(map(str, row)) for row in csv_data])

    # Update CSV in the repository
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
    pr_details = fetch_pr_details(repo, pr_number)
    user_name = pr_details['user']['login']

    # Update CSV with PR details
    update_csv(user_name, repo, pr_details)

if __name__ == "__main__":
    main()
