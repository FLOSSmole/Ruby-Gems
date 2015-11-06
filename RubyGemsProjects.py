'''
Created 7/24/2015
This project can be used to gather and store project names 
  and their RSS & html files for Rubygem projects
Author: Gavan Roth
Updated by: Megan Squire
Requires: Python 3
Usage: python RubyGemsProjectCollector.py <datasource_id> <password>
'''

from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys
import mysql.connector
from mysql.connector import errorcode
import datetime

datasource_id = int(sys.argv[1])
password = str(sys.argv[2])

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
    p = urlopen(url+"?letter=" + letters[i])
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
    cursor = db.cursor()

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
    cursor1 = db1.cursor()

#outer while loop used to itterate through the 26 letters
while count < len(letters):
    letter = letters[count]
    pages = nums[count]
    
    #This while loop itterates through all the pages listing the projects of the current letter
    while page < pages+1:
        listUrl = url + "?letter=" + letter +"&" 
        listUrl = listUrl + "page=%d" % page
        listPage = urlopen(listUrl)
        soup = BeautifulSoup(listPage)
        
        #Pulls all project names on the given list page
        for row in soup.findAll('a', { "class" : "gems__gem" }):
            ref = row['href']
            name = ref[6:]
            print(name)
            #---- get RSS for each project
            RSSLink = url + "/" + name + "/versions.atom"
            RSS = urlopen(RSSLink)
            soup2 = BeautifulSoup(RSS)
            RSStext = soup2.find('feed')
            Pagetext = str(RSStext)

            #--- get HTML versions for each project            
            versionsPage = url + "/" + name + "/versions"
            html = urlopen(versionsPage)
            htmlsoup = BeautifulSoup(html)
            htmltext = str(htmlsoup)
            
            cursor.execute("INSERT IGNORE INTO `rubygems_projects`(`project_name`, \
                     `datasource_id`, `rss_file`, html_versions_file, `last_updated`) VALUES (%s,%s,%s,%s,%s)", 
                     (name, datasource_id, Pagetext, htmltext, datetime.datetime.now()))
            db.commit()
 
            cursor1.execute("INSERT IGNORE INTO `rubygems_projects`(`project_name`, \
                    `datasource_id`, `rss_file`, html_versions_file, `last_updated`) VALUES (%s,%s,%s,%s,%s)", 
                    (name, datasource_id, Pagetext, htmltext, datetime.datetime.now()))
            db1.commit()
            
        print(listUrl)
        page = page+1
    count = count +1
    page = 1
    
cursor.close()
db.close()  
cursor1.close()
db1.close()  
