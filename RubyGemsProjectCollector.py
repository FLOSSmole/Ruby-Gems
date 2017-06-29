# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it
# and/or modify it under the GPLv3
#
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# Contributors: Evan Ashwell, Gavan Roth, Caroline Frankel
#
# We're working on this at http://flossmole.org - Come help us build
# an open and accessible repository for data and analyses for open
# source projects.
#
# If you use this code or data for preparing an academic paper please
# provide a citation to
#
# Howison, J., Conklin, M., & Crowston, K. (2006). FLOSSmole:
# A collaborative repository for FLOSS research data and analyses.
# Int. Journal of Information Technology & Web Engineering, 1(3), 17–26.
#
# and
#
# FLOSSmole: a project to provide research access to
# data and analyses of open source projects.
# Available at http://flossmole.org
#
# ---------------------------------------------------------------
# usage:
# python RubyGemsProjectCollector.py <datasource_id> <status> <password>
# where <status> is one of RESTART or NEW
#
# purpose:
#
# ---------------------------------------------------------------

import urllib.request
from bs4 import BeautifulSoup
import sys
import pymysql

datasource_id = sys.argv[1]
status = sys.argv[2]
password = sys.argv[3]

dbschema = ''
dbuser = ''
dbhost = ''

urlBase = "https://rubygems.org/gems"
countT = 1
count = 0
page = 1
i = 0

# establish database connection: SYR
try:
    dbconn = pymysql.connect(host=dbhost,
                             db=dbschema,
                             user=dbuser,
                             password=password,
                             use_unicode=True,
                             charset='utf8mb4')
except pymysql.Error as err:
    print(err)
else:
    cursor = dbconn.cursor()

# Create arrays with letters and their corresponding number of pages
letters = ["A", "B", "C", "D", "E", "F",
           "G", "H", "I", "J", "K", "L",
           "M", "N", "O", "P", "Q", "R",
           "S", "T", "U", "V", "W", "X",
           "Y", "Z"]
nums = [None]*26

insertQuery = 'INSERT IGNORE INTO rubygems_project_pages(\
               project_name, \
               datasource_id, \
               page_number, \
               rss_file, \
               html_file, \
               html_versions_file, \
               last_updated) \
               VALUES (%s,%s,%s,%s,%s,%s,now())'

# if this is a re-start, figure out where we left off
if status == 'RESTART':
    selectQuery = "SELECT project_name, page_number \
                    FROM rubygems_project_pages \
                    WHERE datasource_id = %s \
                    ORDER BY project_name DESC \
                    LIMIT 1;"
    cursor.execute(selectQuery, (datasource_id))
    found = cursor.fetchone()
    project = found[0][0].upper()
    print('restarting with:', project)

    position = letters.index(project)
    while position > 0:
        letters.remove(letters[0])
        nums.remove(nums[0])
        position = position-1
    page = (page + int(found[1]))-1
    print(page)
    print(letters)
    print(nums)

while i < len(letters):
    p = urllib.request.urlopen(urlBase+"?letter=" + letters[i])
    s = BeautifulSoup(p, "lxml")
    for row in s.findAll('div', {"class": "pagination"}):
        allTag = row.find_all('a')
        for tag in allTag:
            if countT == 10:
                nums[i] = int(tag.text)
            countT = countT+1
    i = i+1
    countT = 1

# outer while loop used to iterate through the 26 letters
while count < len(letters):
    letter = letters[count]
    pages = nums[count]

    # This while loop iterates through all the pages
    # grabbing the projects of the current letter
    while page <= pages:
        listUrl = urlBase + "?letter=" + letter + "&"
        listUrl = listUrl + "page=%d" % page
        try:
            listPage = urllib.request.urlopen(listUrl)
        except urllib.error.URLError as e:
            print(e.reason)
        else:
            soup = BeautifulSoup(listPage, "lxml")
            print(listUrl)

        # Pulls all project names on the given list page
        for row in soup.findAll('a', {"class": "gems__gem"}):
            ref = row['href']
            projectName = ref[6:]

            # something was wrong with the RSS file for
            # some large projects. They are causing a socket error to SYR
            # if projectName != 'bioroebe':
            # if projectName != 'cookbook':
            if projectName != 'beautiful_url':
                # ---- get RSS atom file for each project
                RSSurl = urlBase + "/" + projectName + "/versions.atom"
                print("getting RSS for", projectName)
                try:
                    RSSfile = urllib.request.urlopen(RSSurl)

                except urllib.error.URLError as e:
                    print(e.reason)
                else:
                    RSSsoup = BeautifulSoup(RSSfile, "lxml")
                    RSSpage = RSSsoup.find('feed')
                    RSSstring = str(RSSpage)

                # ---- get HTML base page for each project
                homePageURL = urlBase + "/" + projectName
                print("getting HTML for", projectName)
                try:
                    homePageFile = urllib.request.urlopen(homePageURL)

                except urllib.error.URLError as e:
                    print(e.reason)

                else:
                    homePageSoup = BeautifulSoup(homePageFile, "lxml")
                    homePageString = str(homePageSoup)

                # ---- get HTML versions for each project
                versionsPageURL = urlBase + "/" + projectName + "/versions"
                print("getting HTML Versions for", projectName)
                # little confused on how this directly obtains the version
                try:
                    versionFile = urllib.request.urlopen(versionsPageURL)
                except urllib.error.URLError as e:
                    print(e.reason)
                else:
                    versionSoup = BeautifulSoup(versionFile, "lxml")
                    versionString = str(versionSoup)

                # ---- put everything in the database
                try:
                    print("inserting", projectName, "into db")
                    cursor.execute(insertQuery, (projectName,
                                                 datasource_id,
                                                 page,
                                                 RSSstring,
                                                 homePageString,
                                                 versionString))
                    dbconn.commit()
                except pymysql.Error as err:
                    print(err)
                    dbconn.rollback()
        page += 1
    count += 1
    page = 1

cursor.close()
dbconn.close()
