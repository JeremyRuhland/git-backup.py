#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

__title__ = 'git-backup.py'
__author__ = 'Goopypanther'
__license__ = 'GPL'
__copyright__ = 'Copyright 2019 Goopypanther'
__version__ = '0.1'


import argparse
import os
import sys
import re
import json
import pygit2
from github import Github

# Set up argument parser
parser = argparse.ArgumentParser(description="git-backup clones and updates git repositories from github and elsewhere. Repositories are automatically cloned or fetched into bare repos.",
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-t", "--token",
                    help="Github access token, optional. Used to access private repositories.",
                    default=None,
                    type=str)
parser.add_argument("-u", "--user",
                    help="Github username, optional. Used with -p to access private repositories.",
                    default=None,
                    type=str)
parser.add_argument("-p", "--password",
                    help="Github password, optional. Used with -u to access private repositories.",
                    default=None,
                    type=str)
parser.add_argument("-o", "--output",
                    default=os.getcwd(),
                    help="Path to output directory. Defaults to current directory.",
                    type=str)
parser.add_argument("-c", "--config",
                    help="Config file for automatic execution. Values supersede command line arguments. Argument following flag specifies location of configuration file. If flag is used without argument config file will be read from default location, ~/.config/git-backup.py/git-backup.py.json",
                    nargs="?",
                    default=False,
                    const="~/.config/git-backup.py/git-backup.py.json",
                    type=str)
parser.add_argument("--generate-config",
                    help="Print default config file to screen. Edit and save this file to ~/.config/git-backup.py/git-backup.py.json and run git-backup.py with -c flag to use values from config file",
                    action="store_true")
parser.add_argument("repositories",
                    help="List of repositories for backup. May be entered as:\n[githubUsername] or [githubOrganization] to clone all accessable repos\n[githubUsername/repoName]\n[http(s)://...] or [git://...] or [user@server:path/to/repo]",
                    type=str,
                    nargs="*")

# Parse arguments
args = parser.parse_args()


# If no arguments were given
if not args.config and args.generate_config and len(args.repositories):
    print("Arguments are required, run again with -h to learn how to configure.")
    sys.exit()


config_data = {'github_token': '', 'github_user': '', 'github_password': '', 'output_directory': '', 'repositories': ['', '', '']}

# Handle config generation
if args.generate_config:
    print("Fill out the following config and save to ~/.config/git-backup.py/git-backup.py.json:\nSee help for more details.\n")
    print(json.dumps(config_data, indent=4, separators=(',', ': ')))
    sys.exit()

# Read in configuration file if specified
if args.config:
    try:
        with open(args.config, 'r') as config_file:
            config_data = json.load(config_file)
    except FileNotFoundError:
        sys.exit("Config file was not found. Exiting.")
else:
    config_data['github_token'] = args.token
    config_data['github_user'] = args.user
    config_data['github_password'] = args.password
    config_data['output_directory'] = args.output
    config_data['repositories'] = args.repositories


github_repo_list = []
github_user_list = []
git_repo_list = []

# Sort repository entries
for item in args.repositories:
    # Capture groups: 0 -- Full match, 1 -- Username, 2 -- repo name
    r = re.search(r"(^[\w.]+?)\/([\w.]*)", item) # githubUsername/reponame
    if r:
        github_repo_list.append((r.group(1), r.group(2)))

    r = re.search(r"^[\w.]+$", item) # github user
    if r:
        github_user_list.append(r.group(0))

    r = re.search(r"((?:http|https|git):\/\/[\w.]+\/[\w.]*)|([\w.]+?\@[\w.]+?:[\w.\/]+)", item) # direct url and ssh repo urls
    if r:
        git_repo_list.append(r.group(0))


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


# Find every accessable repo from each specified user and add to repo list
for github_user in github_user_list:
    github_repo_list.extend([x.git_url for x in gapi.get_user(github_user).get_repos()])