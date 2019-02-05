#!/usr/bin/env python
# coding=utf-8

from distutils.core import setup
import os

setup(
    name="PyTunesConnect",
    version="0.0.1",
    author="Tom Bachant",
    author_email="sridhar.p1987@gmail.com",
    py_modules=["pytunesconnect"],
    scripts=["scripts/pytunesconnect-list-apps",
             "scripts/pytunesconnect-login",
             "scripts/pytunesconnect-new-version"],
    url="https://github.com/bachonk/PyTunesConnect.git",
    license="MIT",
    description="An unofficial python client for interacting with the iTunesConnect API.",
    long_description=open("README.md").read(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4"],
)
