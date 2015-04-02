# PyTunesConnect
An unofficial python client for interacting with the iTunesConnect API

## Installing

If using Python 2:

    pip install -r requirements.txt

Then

    python setup.py install

## Usage

To login:

    pytunesconnect-login {username} {password}

To list all apps associated with your account:

    pytunesconnect-list-apps

To create a new version on iTunesConnect given a version and release notes:

    pytunesconnect-new-version {version} {release_notes}
