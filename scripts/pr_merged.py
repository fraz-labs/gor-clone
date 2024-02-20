import os
import requests
import csv
import datetime

def update_csv_on_merge(user_name, repo):
    csv_file_path = f"contributors/{user_name}/contributions.csv"
    csv_url = f"https://api.github.com/repos/{repo}/contents/{csv_file_path}"

    # Fetch existing CSV content
    response = requests.get(csv_url, headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}"})
    if response.status_code == 200:
        content = response.json()['content']
        decoded_csv = content.encode("utf-8").decode("utf-8")
        csv_data = list(csv.reader(decoded_csv.splitlines()))

        # Update the last entry with merge date
        merge_date = datetime.datetime.now().strftime('%Y-%m-%d')
        csv_data[-1][3] = merge_date  # Merge date
        csv_data[-1][-1] = str(int(csv_data[-1][-1]) + 1) if csv_data[-1][-1] else "1"  # Increment merged PRs

        # Convert back to CSV string
        updated_csv = "\n".join([",".join(map(str, row)) for row in csv_data])

        # Update CSV in the repository
        payload = {
            "message": f"Update {csv_file_path}",
            "content": updated_csv.encode("utf-8").decode("utf-8"),
            "sha": response.json()['sha']
        }
        requests.put(csv_url, json=payload, headers={"Authorization": f"Bearer {os.environ['GH_TOKEN']}"})
    else:
        print(f"Error: CSV file not found for {user_name}")

def main():
    repo = os.environ['REPO']
    user_name = os.environ['USER_NAME']

    # Update CSV on PR merge
    update_csv_on_merge(user_name, repo)

if __name__ == "__main__":
    main()
