#!/usr/bin/env python3

import json
import requests

# sample repo for testing (private)
pr_url_base = 'https://github.com/gnolang/devrel/pulls/'

def get_pr(id):
	pr_url = f'{pr_url_base}{id}'
	resp = requests.get(pr_url)

	# Ensure the request was successful
	    if resp.status_code == 200:
		    data = resp.json()
		    print(data)
		else:
        	print(f"request failed with status code {resp.status_code}")

# def organize_pr(pr):

if __name__ == '__main__':
	# fetch PR
	id = 1
    print(f'[+] fetching PR: {id}')
    pr=get_pr(id)
    print('[*] successfully fetched PR')

    # evaluate PR
    print(f'[+] running evaluation DAO algorithm against PR')
    # do_alg(pr)
    print('[*] successfully evaluated PR')

    # reward contributor
    print(f'[+] rewarding contributor')
    # reward_contributor(pr_eval)
    print('[*] successfully rewarded contributor')
