#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 18:14:04 2019

@author: jeremy
"""

import argparse
import os
import re
from github import Github
from git import repo

# Set up argument parser
parser = argparse.ArgumentParser(description="github-backup clones and updates specified github repositories",
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-t", "--token",
                    help="Access token, optional. Used to access private repositories.",
                    default=None,
                    type=str)
parser.add_argument("-u", "--user",
                    help="Username, optional. Used with -p to access private repositories.",
                    default=None,
                    type=str)
parser.add_argument("-p", "--password",
                    help="Password, optional. Used with -u to access private repositories.",
                    default=None,
                    type=str)
parser.add_argument("-o", "--output",
                    default=os.getcwd(),
                    help="Path to output directory. Defaults to current directory.",
                    type=str)
parser.add_argument("-b", "--bare",
                    help="Clone repository into bare git folders.",
                    action="store_true")
parser.add_argument("repositories",
                    help="List of repositories for backup. May be entered as:\n[githubUsername] or [githubOrganization] to clone all accessable repos\n[githubUsername/repoName]\n[http(s)://...] or [git://...] or [user@server:path/to/repo]",
                    type=str,
                    nargs='+')

# Parse arguments 
args = parser.parse_args()

github_repo_list = []
github_user_list = []
git_repo_list = []

# Sort repository entries
for item in args.repositories:
    r = re.search(r"(^[\w.]+?)\/([\w.]*)", item) # user/repo
    
    r = re.search(r"^[\w.]+$", item) # github user
    
    r = re.search(r"(?:http|https|git):\/\/[\w.]+\/[\w.]*", item) # direct url
    
    r = re.search(r"[\w.]+?\@[\w.]+?:[\w.\/]+", item) # ssh repo urls

# Log into github api if any github user links were specified
if github_user_list:
    # Log in to github api, use token if available
    if args.token is not None:
        gapi = Github(args.token)
    
    # Use username/password if available
    elif None not in (args.user, args.password):
        gapi = Github(args.user, args.password)
    
    # Use no login
    else:
        gapi = Github()
