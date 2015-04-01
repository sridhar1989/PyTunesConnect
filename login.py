#!/usr/bin/env python

"""
This script logs a user into the iTunesConnect portal given a username and password.
The login credentials will be stored in the home directory, and generally expire after a few hours.
"""

import sys
import PyTunesAPIHandler as pytunes

if __name__ == "__main__":

	# Read login credentials from command line inputs
	arguments = sys.argv
	username = arguments[1]
	password = arguments[2]

	pytunes.login(username, password)