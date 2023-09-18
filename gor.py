#!/usr/bin/env python3

import os
import sys
import json
import requests
import pandas as pd

# authorization for posting comments/retrieving data from private repo
try:
    os.environ['GH_AUTH_TOKEN'] = 'GH_AUTH_TOKEN'
except KeyError:
    print('Github auth token not found')
    sys.exit(1)

# obtain PR number from action variable
try:
    PR_ID = 1
except KeyError:
    print('Could not get PR ID')
    sys.exit(1)

# sample repo for testing (private)
pr_base_url = 'https://api.github.com/repos/waymobetta/gor'

# categories for gor contributions
categories = {
    'docs': 1,
    'dao': 2,
    'core': 3,
}

# subcategories for gor contributions
sub_categories = {
    'typo': 0.5,
    'bug fix': 5,
    'improvement': 5,
}

# threshold values
thresholds = {
    'commits': {
        'limit': 15,
        'weight': 1
    },
    'deletions': {
        'limit': 1,
        'weight': 3
    },
    'additions': {
        'limit': 15,
        'weight': 2
    },
    'changed_files': {
        'limit': 1,
        'weight': 1
    },
    'additions_and_deletions_combined': {
        'limit': 100,
        'weight': 5   # Adjust this value to modify the points awarded
    },
    'avg_chars_per_line': {
        'limit': 25,
        'weight': 2   # Adjust this value to modify the points awarded
    }
}

class PR:
    # assign null values for initialization
    def __init__(self):
        self.id = 0
        self.commit = ''
        self.content = ''
        self.author = ''
        self.evaluation = 0
        self.evaluation_max = 0
        self.is_rewarded = False
        self.commits = 0
        self.changed_files = 0
        self.additions = 0
        self.deletions = 0
        self.category = ''
        self.sub_category = ''

    # setters
    def set_id(self, id):
        self.id = id

    def set_commit(self, commit):
        self.commit = commit

    def set_content(self, content):
        self.content = content

    def set_author(self, author):
        self.author = author

    def set_evaluation(self, evaluation):
        self.evaluation = evaluation

    def set_evaluation_max(self, evaluation_max):
        self.evaluation_max = evaluation_max

    def set_is_rewarded(self, is_rewarded):
        self.is_rewarded = is_rewarded

    def set_commits(self, commits):
        self.commits = commits

    def set_changed_files(self, changed_files):
        self.changed_files = changed_files

    def set_additions(self, additions):
        self.additions = additions

    def set_deletions(self, deletions):
        self.deletions = deletions

    def set_category(self, category):
        self.category = category

    def set_sub_category(self, sub_category):
        self.sub_category = sub_category

    # getters
    def get_id(self):
        return self.id

    def get_commit(self):
        return self.commit

    def get_content(self):
        return self.content

    def get_author(self):
        return self.author

    def get_evaluation(self):
        return self.evaluation

    def get_evaluation_max(self):
        return self.evaluation_max

    def get_is_rewarded(self):
        return self.is_rewarded

    def get_commits(self):
        return self.commits

    def get_changed_files(self):
        return self.changed_files

    def get_additions(self):
        return self.additions

    def get_deletions(self):
        return self.deletions

    def get_category(self):
        return self.category

    def get_sub_category(self):
        return self.sub_category

    # summary
    def summary(self):
        gor_id = construct_gor_id(self.id)
        total_effective = self.get_additions() + self.get_deletions()  # Sum of additions and deletions
        avg_chars_per_line = (len(self.get_content()) / self.get_content().count('\n')) if self.get_content().count('\n') != 0 else 0  # Average characters per line

        summary = f'''
Greetings, Game of Realms Contributor, {self.get_author()}! 

Your contribution has been evaluated. The following are your results:

###### ID: {gor_id}

**Points:** {self.get_evaluation()}
**Max Points:** {self.get_evaluation_max()}

#### Breakdown
**Category:** {self.get_category()}
**Sub Category:** {self.get_sub_category()}
**Commits:** {self.get_commits()}
**Additions:** {self.get_additions()}
**Deletions:** {self.get_deletions()}
**Total Effective Lines (Additions + Deletions):** {total_effective}
**Average Characters Per Line:** {avg_chars_per_line:.2f}
'''
        return summary


    # evaluation
    def eval(self):
        total, max_total, total_effective, avg_chars_per_line = math_things(
            self.additions, 
            self.deletions, 
            self.commits,
            self.changed_files,
            self.category,
            self.sub_category,
            self.content
        )
        self.set_evaluation(total)
        self.set_evaluation_max(max_total)

    # reward
    def reward(self):
        reward_msg = f'''
Greetings, Game of Realms Contributor, {self.author}!

You have been successfully rewarded through our Proof of Contribution mechanism- check your wallet!

Thank you for playing the Game of Realms!

gno.land
'''
        self.post(reward_msg)
        self.set_is_rewarded(True)

    # post
    def post(self, data):
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': '',
            'X-GitHub-Api-Version': '2022-11-28',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        headers['Authorization'] = f'Bearer {os.environ["GH_AUTH_TOKEN"]}'
        payload = {'body': data}
        payload = json.dumps(payload)
        pr_comment_url = f'{pr_base_url}/issues/{self.id}/comments'
        resp = requests.post(pr_comment_url, headers=headers, data=payload)
        if resp.status_code not in [200, 201]:
            print(f"request failed with status code {resp.status_code}")
            sys.exit(1)

    # fetch
    def fetch(self):
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': '',
            'X-GitHub-Api-Version': '2022-11-28',
        }

        headers['Authorization'] = f'Bearer {os.environ["GH_AUTH_TOKEN"]}'

        pr_url = f'{pr_base_url}/pulls/{self.id}'

        resp = requests.get(pr_url, headers=headers)

        # Ensure the request was successful
        if resp.status_code == 200:
            data = resp.json()

            # write to local file for debugging
            write_to_file(data)

            # update PR struct
            self.set_commit(data['merge_commit_sha'])
            self.set_content(data['body'] or '')  # Set to empty string if content is None
            self.set_author(data['user']['login'])
            self.set_commits(data['commits'])
            self.set_changed_files(data['changed_files'])
            self.set_additions(data['additions'])
            self.set_deletions(data['deletions'])

            return self
        else:
            print(f"request failed with status code {resp.status_code}")
            print(resp.text)  # Using resp.text instead of resp.body for better compatibility
            sys.exit(1)


    def __str__(self):
        return f'PR: {self.id}, {self.commit}, {self.content}, {self.author}'

    # helpers

def write_to_file(data):
    with open('pr_response.json', 'a') as f:
        json.dump(data, f, indent=4)

def construct_gor_id(id):
    return f'[gno/gor:{id}]'

def math_things(additions, deletions, commits, changed_files, category, sub_category, content):
    # contribution total
    total = 0

    # calculate max total for the category
    max_total = 0

    # Calculate effective code changes (excluding blank lines) and average characters per line
    total_effective = additions + deletions - content.count('\n\n')
    avg_chars_per_line = len(content) / content.count('\n') if content.count('\n') != 0 else 0

    # Check the thresholds for the newly added metrics and add to max_total
    if total_effective >= thresholds['additions_and_deletions_combined']['limit']:
        total += thresholds['additions_and_deletions_combined']['weight']
    max_total += thresholds['additions_and_deletions_combined']['weight']

    if avg_chars_per_line > thresholds['avg_chars_per_line']['limit']:
        total += thresholds['avg_chars_per_line']['weight']
    max_total += thresholds['avg_chars_per_line']['weight']

    match category:
        case 'docs':
            total += categories['docs']
            max_total += categories['docs']
        case 'dao':
            total += categories['dao']
            max_total += categories['dao']
        case 'core':
            total += categories['core']
            max_total += categories['core']
        # default
        case _:
            total += 0
            max_total += 0

    match sub_category:
        case 'typo':
            total += sub_categories['typo']
            max_total += sub_categories['typo']
        case 'bug fix':
            total += sub_categories['bug fix']
            max_total += sub_categories['bug fix']
        case 'improvement':
            total += sub_categories['improvement']
            max_total += sub_categories['improvement']

    # additions/deletions
    total += additions_deletions(additions, deletions, False)
    max_total += additions_deletions(additions, deletions, True)

    # commits
    if commits >= thresholds['commits']['limit']:
        total -= thresholds['commits']['weight']
    max_total += thresholds['commits']['weight']

    # changed files
    if changed_files >= thresholds['changed_files']['limit']: 
        total += thresholds['changed_files']['weight']
    max_total += thresholds['changed_files']['weight']

    return total, max_total, total_effective, avg_chars_per_line


def additions_deletions(additions, deletions, is_max):
    adds_dels = 0

    if is_max:
        return thresholds['additions']['weight'] + thresholds['deletions']['weight']

    # additions
    if additions >= thresholds['additions']['limit']:
        adds_dels += thresholds['additions']['weight']

    # deletions
    if deletions >= thresholds['deletions']['limit']:
        adds_dels += thresholds['deletions']['weight']

    return adds_dels

if __name__ == '__main__':
    # test data
    id = 1
    category = 'dao'
    sub_category = 'improvement'

    # instantiate new PR object
    pr = PR()

    # pulled from Github Actions (workflow/actions.yml)
    pr.set_id(PR_ID)
    pr.set_category(category)
    pr.set_sub_category(sub_category)

    # fetch PR
    print(f'[+] fetching PR: {pr.get_id()}')
    pr.fetch()
    print('[*] successfully fetched PR\n')

    # evaluate PR
    print(f'[+] evaluating PR: {pr.get_id()}')
    pr.eval()
    print('[*] successfully evaluated PR\n')

    # generate summary
    summary = pr.summary()

    # publish PR review
    print(f'[+] publishing review for PR: {pr.get_id()}')
    pr.post(summary)
    print('[*] successfully published PR review\n')

    # reward contributor
    print(f'[+] rewarding {pr.get_author()} with {pr.get_evaluation()} points for a {pr.get_category()}/{pr.get_sub_category()} contribution')
    pr.reward()
    print('[*] successfully rewarded contributor\n')
