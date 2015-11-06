'''
Created 7/24/2015
This project can be used to gather and store project names 
  and their RSS & html files for Rubygem projects
Author: Gavan Roth
Updated by: Megan Squire
Usage: python RubyGemsProjectCollector.py <datasource_id> <password>
'''

import urllib2
from bs4 import BeautifulSoup
import sys
import MySQLdb
import datetime

datasource_id = int(sys.argv[1])
password = int(sys.argv[2])

url = "https://rubygems.org/gems"
countT = 1
count = 0
page = 1
i = 0

#Create arrays with letters and their corresponding number of pages
letters = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
nums = [None]*26

#Populates the nums array with the curent total number of pages of projects for each letter
while i < len(letters):
    p = urllib2.urlopen(url+"?letter=" + letters[i])
    s = BeautifulSoup(p)
    for row in s.findAll('div', { "class" : "pagination" }):
        allTag = row.find_all('a')
        for tag in allTag:
            if countT == 10:
                nums[i] = int(tag.text)
            countT=countT+1
    i = i+1
    countT = 1
#establish database connections
db = MySQLdb.connect(host="grid6.cs.elon.edu", 
    user="megan", 
    passwd=password, 
    db="rubygems", 
    use_unicode=True, 
    charset = "utf8")
cursor = db.cursor()
cursor.execute('SET NAMES utf8mb4')
cursor.execute('SET CHARACTER SET utf8mb4')
cursor.execute('SET character_set_connection=utf8mb4')

db1 = MySQLdb.connect(host="flossdata.syr.edu", 
    user="megan", 
    passwd=password, 
    db="rubygems", 
    use_unicode=True, 
    charset = "utf8")
cursor1 = db1.cursor()
cursor1.execute('SET NAMES utf8mb4')
cursor1.execute('SET CHARACTER SET utf8mb4')
cursor1.execute('SET character_set_connection=utf8mb4')

#outer while loop used to itterate through the 26 letters
while count < len(letters):
    letter = letters[count]
    pages = nums[count]
    
    #This while loop itterates through all the pages listing the projects of the current letter
    while page < pages+1:
        listUrl = url + "?letter=" + letter +"&" 
        listUrl = listUrl + "page=%d" % page
        listPage = urllib2.urlopen(listUrl)
        soup = BeautifulSoup(listPage)
        
        #Pulls all project names on the given list page
        for row in soup.findAll('a', { "class" : "gems__gem" }):
            ref = row['href']
            name = ref[6:]
            print name
            #---- get RSS for each project
            RSSLink = url + "/" + name + "/versions.atom"
            RSS = urllib2.urlopen(RSSLink)
            soup2 = BeautifulSoup(RSS)
            RSStext = soup2.find('feed')
            Pagetext = str(RSStext)
            try:
                 cursor.execute("INSERT INTO `rubygems_projects`(`project_name`, \
                 `datasource_id`, `rss_file`, `last_updated`) VALUES (%s,%s,%s,%s)", 
                 (name, datasource_id, Pagetext, datetime.datetime.now()))
                 db.commit()
            except MySQLdb.Error as error:
                print "insert error"
                print error
                db.rollback()
                
            try:
                 cursor1.execute("INSERT INTO `rubygems_projects`(`project_name`, \
                 `datasource_id`, `rss_file`, `last_updated`) VALUES (%s,%s,%s,%s)", 
                 (name, datasource_id, Pagetext, datetime.datetime.now()))
                 db1.commit()
            except MySQLdb.Error as error:
                print "insert error"
                print error
                db1.rollback()
                
           #---- get HTML version for each project
           # we need these since the Atom file only shows dates > July 2009
           # but the html version shows dates earlier than that
            versionsPage = url + "/" + name + "/versions"
            html = urllib2.urlopen(versionsPage)
            
            try:
                 cursor.execute("UPDATE `rubygems_projects` \
                    SET html_versions_file = %s, last_updated = %s"), 
                 (html, datetime.datetime.now()))
                 db.commit()
            except MySQLdb.Error as error:
                print "update error"
                print error
                db.rollback()
                
            try:
                 cursor1.execute("UPDATE `rubygems_projects` \
                    SET html_versions_file = %s, last_updated = %s"), 
                 (html, datetime.datetime.now()))
                 db1.commit()
            except MySQLdb.Error as error:
                print "update error"
                print error
                db1.rollback()
        print listUrl
        page = page+1
    count = count +1
    page = 1
    
cursor.close()
db.close()  
cursor1.close()
db1.close()  
