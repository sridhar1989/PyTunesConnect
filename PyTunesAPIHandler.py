#!/usr/bin/env python

"""
This logs a user into the iTunesConnect portal given a username and password.
It will return a parsed authentication cookie to be used in future requests.
"""

from urllib.parse import urlencode
import httplib2
import json
import sys

global_path = "https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa"
user_agent = "PyTunesConnect/0.0.1 (Macintosh; OS X/10.10.1) GCDHTTPRequest"
http = httplib2.Http()

################################# LOCAL AUTH ####################################

def get_auth_cookie():
	with open("token.txt", "r") as f:
		cookie = f.read()
		return cookie

def store_auth_cookie(cookie):
	with open("token.txt", "w") as f:
		f.write(cookie)

################################# LOGIN ####################################

def parse_cookie_from_response(input):
	# take raw cookie string and return the usable part
	# the response cookie is a long string (not valid JSON)
	# need to extract "ds01", "myacinfo", "wosid", and "woinst"
	# return value should be formatted as such: "ds01=AAA; myacinfo=BBB; wosid=CCC; woinst=DDD"
	ds01 = ""
	myacinfo = ""
	woinst = ""
	wosid = ""
	for si in input.split(";"):
		if "ds01=" in si:
			ds01 = si.split("ds01=")[-1]
		elif "myacinfo=" in si:
			myacinfo = si.split("myacinfo=")[-1]
		elif "woinst=" in si:
			woinst = si.split("woinst=")[-1]
		elif "wosid=" in si:
			wosid = si.split("wosid=")[-1]
	return "ds01={}; myacinfo={}; woinst={}; wosid={}".format(ds01, myacinfo, woinst, wosid)

def login(username, password):
	url_path = global_path + "/wo/0.0.1.11.3.15.2.1.1.3.1.1"

	body = { 
		"theAccountName": username,
		"theAccountPW": password
	}

	headers = {
		"Host": "itunesconnect.apple.com",
		"Connection": "close",
		"Content-Type": "application/x-www-form-urlencoded",
		"User-Agent": user_agent
	}

	# make request
	response, content = http.request(url_path, "POST", headers=headers, body=urlencode(body))

	print(response)
	# pull out the cookie from the response
	cookie_str = response["set-cookie"]
	
	# return parsed value
	auth_cookie = parse_cookie_from_response(cookie_str)
	store_auth_cookie(auth_cookie)
	return auth_cookie

################################# LIST APPS ####################################

def list_apps():
	cookie = get_auth_cookie()

	url_path = global_path + "/ra/apps/manageyourapps/summary"

	body = {}

	headers = {
		"Cookie": cookie,
		"Host": "itunesconnect.apple.com",
		"Connection": "close",
		"User-Agent": user_agent
	}

	response, content = http.request(url_path, "GET", headers=headers, body=body)

	#content will contain the relevant details
	jsonResp = json.loads(content.decode("utf-8"))

	app_list = jsonResp["data"]["summaries"]

	return app_list

################################# NEW VERSION ####################################

def new_version_for_app(app_id, version):
	cookie = get_auth_cookie()

	url_path = global_path + "/ra/apps/version/create/" + app_id

	body = { 
		"version": version
	}

	headers = {
		"Cookie": cookie,
		"Host": "itunesconnect.apple.com",
		"User-Agent": user_agent
	}

	# make request
	response, content = http.request(url_path, "POST", headers=headers, body=urlencode(body))

	# pull out the cookie from the response
	status = response["status"]

	if (status == 200):
		print("Successfully created new version " + version + " for app " + app_id)
	else:
		print("Error creating version")

def new_version_all_apps(version, release_notes):
	# Get list of apps from iTunesConnect
	all_apps = list_apps()

	# Ignore apps that won't be updated
	ignored_app_ids = ['553647769', '874966350', '888344666', '857823988', '785495390']

	results = []
	for app in all_apps:
		app_id = app["adamId"]

		# Create the new version
		if app_id not in ignored_app_ids:
			new_version_for_app(app_id, version)
