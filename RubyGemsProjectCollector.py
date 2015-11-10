# -*- coding: utf-8 -*-
'''
This program is free software; you can redistribute it
and/or modify it under the terms of the Perl Artistic License 2.0.

Copyright (C) 2015 Megan Squire and Gavan Roth

We're working on this at http://flossmole.org - Come help us build 
an open and accessible repository for data and analyses for open
source projects.

If you use this code or data for preparing an academic paper please
provide a citation to 

Howison, J., Conklin, M., & Crowston, K. (2006). FLOSSmole: 
A collaborative repository for FLOSS research data and analyses. 
International Journal of Information Technology and Web Engineering, 
1(3), 17–26.

and

FLOSSmole (2004-2016) FLOSSmole: a project to provide academic access to data 
and analyses of open source projects.  Available at http://flossmole.org 

usage:
python RubyGemsProjectCollector.py <datasource_id> <password>

'''

import urllib
from bs4 import BeautifulSoup
import sys
import mysql.connector
from mysql.connector import errorcode
import datetime

datasource_id = int(sys.argv[1])
password = str(sys.argv[2])

urlBase = "https://rubygems.org/gems"
countT = 1
count = 0
page = 1
i = 0

#Create arrays with letters and their corresponding number of pages
letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
nums = [None]*26

#Populates the nums array with the curent total number of pages of projects for each letter
while i < len(letters):
    p = urllib.request.urlopen(urlBase+"?letter=" + letters[i])
    s = BeautifulSoup(p)
    for row in s.findAll('div', { "class" : "pagination" }):
        allTag = row.find_all('a')
        for tag in allTag:
            if countT == 10:
                nums[i] = int(tag.text)
            countT=countT+1
    i = i+1
    countT = 1
# establish database connection: ELON
try:
    db = mysql.connector.connect(host='grid6.cs.elon.edu',
                                  database='rubygems',
                                  user='megan',
                                  password=password)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password on ELON")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cursor = db.cursor(dictionary=True)

# establish database connection: SYR      
try:
    db1 = mysql.connector.connect(host='flossdata.syr.edu',
                                  database='rubygems',
                                  user='megan',
                                  password=password)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password on SYR")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
else:
    cursor1 = db1.cursor(dictionary=True)

#outer while loop used to iterate through the 26 letters
while count < len(letters):
    letter = letters[count]
    pages = nums[count]
    
    #This while loop itterates through all the pages listing the projects of the current letter
    while page < pages+1:
        listUrl = urlBase + "?letter=" + letter +"&" 
        listUrl = listUrl + "page=%d" % page
        try:
            listPage = urllib.request.urlopen(listUrl)
        except urllib.error.URLError as e:
            print (e.reason)
        else:
            soup = BeautifulSoup(listPage)
            print(listUrl)

        #Pulls all project names on the given list page
        for row in soup.findAll('a', { "class" : "gems__gem" }):
            ref = row['href']
            projectName = ref[6:]
            print(projectName)
            
            #---- get RSS for each project
            RSSurl = urlBase + "/" + projectName + "/versions.atom"
            try:
                RSSfile = urllib.request.urlopen(RSSurl)

            except urllib.error.URLError as e:
                print(e.reason)
            else:
                RSSsoup = BeautifulSoup(RSSfile)
                RSSpage = RSSsoup.find('feed')
                RSSstring = str(RSSpage)
            
            #---- get HTML for each project
            homePageURL = urlBase + "/" + projectName
            try:
                homePageFile = urllib.request.urlopen(homePageURL)
                
            except urllib.error.URLError as e:
                print(e.reason)
         
            else:
                homePageSoup = BeautifulSoup(homePageFile)
                homePageString = str(homePageSoup)

            #---- get HTML versions for each project            
            versionsPageURL = urlBase + "/" + projectName + "/versions"
            
            try:
                versionFile = urllib.request.urlopen(versionsPageURL)
            except urllib.error.URLError as e:
                print(e.reason)
            else:
                versionSoup = BeautifulSoup(versionFile)
                versionString = str(versionSoup)
            
            #---- put everything in the database
            try:
                cursor.execute("INSERT IGNORE INTO rubygems_projects( \
                    project_name, \
                    datasource_id, \
                    rss_file, \
                    html_file, \
                    html_versions_file, \
                    last_updated) \
                     VALUES (%s,%s,%s,%s,%s,%s)", 
                     (projectName, 
                      datasource_id, 
                      RSSstring, 
                      homePageString, 
                      versionString, 
                      datetime.datetime.now()))
                db.commit()
            except mysql.connector.Error as err:
                print(err)
                db2.rollback()
 
            try:
                cursor1.execute("INSERT IGNORE INTO rubygems_projects( \
                    project_name, \
                    datasource_id, \
                    rss_file, \
                    html_file, \
                    html_versions_file, \
                    last_updated) \
                     VALUES (%s,%s,%s,%s,%s,%s)", 
                     (projectName, 
                      datasource_id, 
                      RSSstring, 
                      homePageString, 
                      versionString, 
                      datetime.datetime.now()))
                db1.commit()
            except mysql.connector.Error as err:
                print(err)
                db2.rollback()
        
        page = page+1
    count = count +1
    page = 1
    
cursor.close()
db.close()  
cursor1.close()
db1.close()  
