#!/usr/bin/env python3

import os
import sys
import json
import requests

# authorization for posting comments/retrieving
# data from private repo
github_auth_token = os.getenv('GITHUB_AUTH_TOKEN')

# sample repo for testing (private)
pr_base_url = '  https://api.github.com/repos/waymobetta/gor'

class PR:
	# setters

	# assign null values for initialization
	def __init__(self):
		self.id = 0
		self.commit = ''
		self.content = ''
		self.author = ''
		self.evaluation = ''
		self.is_rewarded = False

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

	def set_is_rewarded(self, is_rewarded):
		self.is_rewarded = is_rewarded

	# getters

	def id(self):
		return self.id

	def commit(self):
		return self.commit

	def content(self):
		return self.content

	def author(self):
		return self.author

	def evaluation(self):
		return self.evaluation

	def is_rewarded(self):
		return self.is_rewarded

	# sanitizes and prepares data that was previously 
	# fetched via fetch()
	def prepare(self):
		print('preparing PR: {self.id}')

	# performs evaluation on specific PR
	def eval(self):
		self.set_evaluation('50 points')

	# rewards contributor based on evaluation results
	def reward(self):
		self.is_rewarded(True)

	# publishes a report on the contribution to the PR thread
	def publish(self):
		headers = {
		    'Accept': 'application/vnd.github+json',
		    'Authorization': '',
		    'X-GitHub-Api-Version': '2022-11-28',
		    'Content-Type': 'application/x-www-form-urlencoded',
		}

		headers['Authorization'] = f'Bearer {github_auth_token}'

		# comment body
		data = {'body':''}
		data['body'] = self.evaluation
	
		# unmarshal data
		data = json.dumps(data)

		pr_comment_url = f'{pr_base_url}/issues/{self.id}/comments'

		resp = requests.post(pr_comment_url, headers=headers, data=data)

		# Ensure the request was successful
		if resp.status_code != 200 and resp.status_code != 201:
			print(f"request failed with status code {resp.status_code}")
			sys.exit(1)

	# fetches the PR in question and returns an object 
	# containing data from PR
	def fetch(self):
		headers = {
			'Accept': 'application/vnd.github+json',
			'Authorization': '',
			'X-GitHub-Api-Version': '2022-11-28',
		}

		headers['Authorization'] = f'Bearer {github_auth_token}'

		pr_url = f'{pr_base_url}/pulls/{self.id}'

		resp = requests.get(pr_url, headers=headers)

		# Ensure the request was successful
		if resp.status_code == 200:
		    data = resp.json()
		    
		    # write to local file for debugging
		    write_to_file(data)

		    self.set_commit(data['merge_commit_sha'])
		    self.set_content(data['body'])
		    self.set_author(data['user']['login'])

		    return self
		else:
			print(f"request failed with status code {resp.status_code}")
			print(resp.body)
			sys.exit(1)

	def __str__(self):
		return f'PR: {self.id}, {self.commit}, {self.content}, {self.author}'

def write_to_file(data):
    f = open('pr_response.json', 'a')
    d = json.dumps(data, indent=4)
    f.write(d)
    f.close()

if __name__ == '__main__':
	# define PR ID
	id = 1

	# instantiate new PR object
	pr = PR()
	pr.set_id(id)

	# fetch PR
	print(f'[+] fetching PR: {pr.id}')
	pr.fetch()
	print('[*] successfully fetched PR\n')

	# prepare PR
	print(f'[+] preparing PR: {pr.id}')
	# pr.prepare()
	print('[*] successfully prepared PR\n')

	# evaluate PR
	print(f'[+] evaluating PR: {pr.id}')
	# pr.eval()
	print('[*] successfully evaluated PR\n')

	# publish PR review
	print(f'[+] publishing review for PR: {pr.id}')
	# pr.publish()
	print('[*] successfully published PR review\n')

	# reward contributor
	print(f'[+] rewarding contributor: {pr.author}')
	# pr.reward()
	print('[*] successfully rewarded contributor\n')
