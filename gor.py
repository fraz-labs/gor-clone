#!/usr/bin/env python3

import os
import json
import requests

class PR:
	# assign null values for initialization
	def __init__(self)
		self.id = 0
		self.commit = ''
		self.content = ''
		self.author = ''

	def add_id(self, id):
		self.id = id

	def add_commit(self, commit):
		self.commit = commit

	def add_content(self, content):
		self.content = content

	def add_author(self, author):
		self.author = author


# authorization for posting comments/retrieving
# data from private repo
github_auth_token = os.getenv('GITHUB_AUTH_TOKEN')

# sample repo for testing (private)
pr_base_url = 'https://github.com/waymobetta/gor/pulls'

# fetches the PR in question and returns an object 
# containing data from PR
def get_pr(id):
	pr_url = f'{pr_base_url}/{id}'
	resp = requests.get(pr_url)

	# Ensure the request was successful
	    if resp.status_code == 200:
		    data = resp.json()
		    print(data)

		    pr = PR(id)

		    pr.add_commit('')
		    pr.add_content('')
		    pr.add_author('')

		    return pr
		else:
        	print(f"request failed with status code {resp.status_code}")

# posts a comment to the PR thread
def post_comment(comment):
	headers = {
	    'Accept': 'application/vnd.github+json',
	    'Authorization': '',
	    'X-GitHub-Api-Version': '2022-11-28',
	    'Content-Type': 'application/x-www-form-urlencoded',
	}

	headers['Authorization'] = f'Bearer {github_auth_token}'

	# pulled from parsing response from prepare_pr()
	commit_id = 

	# pulled from parsing response from prepare_pr()
	path = 

	data = f'{"body":"test","commit_id":"","path":"","start_line":1,"start_side":"RIGHT","line":2,"side":"RIGHT"}'

	pr_comment_url = f'{pr_base_url}/{pr_id}/comments'

	resp = requests.post(pr_comment_url, headers=headers, data=data)

# sanitizes and prepares data that was previously 
# fetched via get_pr()
def prepare_pr(pr):
	print('preparing PR: {pr.id}')

# performs evaluation on specific PR
def perform_eval(pr):
	print('performing evaluation on PR: {pr.id}')

if __name__ == '__main__':
	# define PR ID 
	id = 1

	# fetch PR
    print(f'[+] fetching PR: {id}')
    pr = get_pr(id)
    print('[*] successfully fetched PR')
    print(pr)

    # prepare PR
    print(f'[+] preparing PR: {pr.id}')
    # pr_prepped = prepare_pr(pr)
    print('[*] successfully prepared PR')

    # evaluate PR
    print(f'[+] evaluating PR: {pr.id}')
    # pr_eval = perform_eval(pr)
    print('[*] successfully evaluated PR')

    # reward contributor
    print(f'[+] rewarding contributor: {pr.author}')
    # reward_contributor(pr_eval)
    print('[*] successfully rewarded contributor')
