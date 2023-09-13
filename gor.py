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
#
# these are votable values to assign objective points to 
# contributions
#
# note: this total number will not change outside of this 
# equation though it will be combined with a multipler granted
# by the evaluation DAO to craft a final score
thresholds = {
	'commits': {
		# >=15 commits is too many and will deduct points
		'limit': 15,
		'weight': 1
	},
	'deletions': {
		# >=1 deletions will award points
		'limit': 1,
		'weight': 3
	},
	'additions': {
		# >=15 additions will award points
		'limit': 15,
		'weight': 2
	},
	'changed_files': {
		# >=1 file must be updated
		'limit': 1,
		'weight': 1
	},
}

class PR:
	# setters

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

	def evaluation_max(self):
		return self.evaluation_max

	def is_rewarded(self):
		return self.is_rewarded

	def commits(self):
		return self.commits

	def changed_files(self):
		return self.changed_files

	def additions(self):
		return self.additions

	def deletions(self):
		return self.deletions

	def category(self):
		return self.category

	def sub_category(self):
		return self.sub_category

	# constructs summary of the contribution review
	def summary(self):
		# construct gor id
		gor_id = construct_gor_id(self.id)

		summary = f'''
Greetings, Game of Realms Contributor, {self.author}! 

Your contribution has been evaluated. The following are your results:

###### ID: {gor_id}

**Points:** {self.evaluation}
**Max Points:** {self.evaluation_max}

#### Breakdown
**Category:** {self.category}
**Sub Category:** {self.sub_category}
**Commits:** {self.commits}
**Additions:** {self.additions}
**Deletions:** {self.deletions}
'''
		return summary

	# performs evaluation on specific PR
	def eval(self):
		total, max_total = math_things(
			self.additions, 
			self.deletions, 
			self.commits,
			self.changed_files,
			self.category,
			self.sub_category
		)
		self.set_evaluation(total)
		self.set_evaluation_max(max_total)

	# rewards contributor based on evaluation results
	def reward(self):
		# todo: issue tokens

		# put full PR URL in tx memo to be associated with gor 
		# contribution/receipt
		# todo: address privacy concern of wallet/id dox
		reward_msg = f'''
Greetings, Game of Realms Contributor, {self.author}!

You have been successfully rewarded through our Proof of Contribution mechanism- check your wallet!

Thank you for playing the Game of Realms!

gno.land
'''
		self.post(reward_msg)
		self.set_is_rewarded(True)

	# publishes a report on the contribution to the PR thread
	def post(self, data):
		headers = {
		    'Accept': 'application/vnd.github+json',
		    'Authorization': '',
		    'X-GitHub-Api-Version': '2022-11-28',
		    'Content-Type': 'application/x-www-form-urlencoded',
		}

		headers['Authorization'] = f'Bearer {github_auth_token}'

		# comment body
		payload = {'body':''}
		payload['body'] = data
	
		# unmarshal data
		payload = json.dumps(payload)

		pr_comment_url = f'{pr_base_url}/issues/{self.id}/comments'

		resp = requests.post(pr_comment_url, headers=headers, data=payload)

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

		    # update PR struct
		    self.set_commit(data['merge_commit_sha'])
		    self.set_content(data['body'])
		    self.set_author(data['user']['login'])
		    self.set_commits(data['commits'])
		    self.set_changed_files(data['changed_files'])
		    self.set_additions(data['additions'])
		    self.set_deletions(data['deletions'])

		    return self
		else:
			print(f"request failed with status code {resp.status_code}")
			print(resp.body)
			sys.exit(1)

	def __str__(self):
		return f'PR: {self.id}, {self.commit}, {self.content}, {self.author}'

# helpers

def write_to_file(data):
    f = open('pr_response.json', 'a')
    d = json.dumps(data, indent=4)
    f.write(d)
    f.close()

def construct_gor_id(id):
	return f'[gno/gor:{id}]'

def math_things(additions, deletions, commits, changed_files, category, sub_category):
	# contribution total
	total = 0
	
	# calculate max total for the category
	max_total = 0

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

	# add max total for commits
	max_total += thresholds['commits']['weight']

	# changed files
	if changed_files >= thresholds['changed_files']['limit']: 
		total += thresholds['changed_files']['weight']

	# add max total for changed_files
	max_total += thresholds['changed_files']['weight']

	return total, max_total

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
	# todo: add watcher to inform when new gor-tagged 
	# PR/issue appears on one our repositories

	# todo: add logic to triage PR vs. issue evaluation

	# test data
	id = 1
	category = 'dao'
	sub_category = 'improvement'

	# instantiate new PR object
	pr = PR()
	pr.set_id(id)
	pr.set_category(category)
	pr.set_sub_category(sub_category)

	# fetch PR
	print(f'[+] fetching PR: {pr.id}')
	pr.fetch()
	print('[*] successfully fetched PR\n')

	# evaluate PR
	print(f'[+] evaluating PR: {pr.id}')
	pr.eval()
	print('[*] successfully evaluated PR\n')

	# generate summary
	summary = pr.summary()

	# publish PR review
	print(f'[+] publishing review for PR: {pr.id}')
	pr.post(summary)
	print('[*] successfully published PR review\n')

	# reward contributor
	print(f'[+] rewarding {pr.author} with {pr.evaluation} points for a {pr.category}/{pr.sub_category} contribution')
	pr.reward()
	print('[*] successfully rewarded contributor\n')
