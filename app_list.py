#!/usr/bin/env python

"""
This script will print out all existing apps with their Apple ID and bundle name.
"""

import PyTunesAPIHandler as pytunes

if __name__ == "__main__":

	app_list = pytunes.list_apps()

	for app in app_list:
		print (app['adamId'] + ': ' + app['name'])