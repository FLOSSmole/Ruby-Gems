'''
Created 8/6/2015
This project can be used to gather and store project names and their RSS files for Rubygem projects
Author: Gavan Roth
'''

import urllib2
from bs4 import BeautifulSoup
import sys
import MySQLdb
import datetime
# io provides better access to files with working universal newline support
import io
# open a file in text mode, encoding all output to utf-8
output_file = io.open("output.txt", "w", encoding="utf-8")

#constants
entry_id = 1
datasource_id = int(sys.argv[1])
url = "https://rubygems.org/gems"

#establish database connection
db = MySQLdb.connect(host="grid6.cs.elon.edu", user="groth", passwd="Monsterhunter12", db="rubygems", use_unicode=True, charset = "utf8")
cursor = db.cursor()
cursor.execute('SET NAMES utf8mb4')
cursor.execute('SET CHARACTER SET utf8mb4')
cursor.execute('SET character_set_connection=utf8mb4')

#get all project names
try:
    cursor.execute("SELECT rss_file FROM `rubygems_projects`")
    files = cursor.fetchall()
except MySQLdb.Error as error:
    print error

def checkNull(item):
    if item != None:
        return item.text.rstrip()
    return " "


print len(files)
#Using the names, goes to each project's RSS page and gathers the required information to be stored in the DB
for f in files:
    rss = str(f)
    soup = BeautifulSoup(rss)
    entries = soup.findAll('entry')
    for entry in entries:
        if entry_id == 9:
            sys.exit()
        
        summary = entry.find('summary')
        author = entry.find('author')
        title = entry.find('title')
        t_text = checkNull(title)
        p_name_int = t_text.find("(")
        project = t_text[:p_name_int]
        ent_id = entry.find('id')
        updated = entry.find("updated")
        content = entry.find("content")
        dateTime = checkNull(updated)
        split = dateTime.find("T")
        end = dateTime.find("Z")
        date = dateTime[:split] 
        time = dateTime[split+1:end]
        
        print time
        
        # If not null or not empty
        if author:
            for name in author.findAll("name"):
                print name
                # .text contains the actual Unicode string value
                if name.text:
                    names = name.text.split(",", 1)
                    # If string contained a comma, you'll have two elements in a list
                    # else you'll just have the 1 length list
                    for flname in names:
                        # remove any whitespace on either side
                        output_file.write(flname.strip() + "\n")
                else:
                    output_file.write(name.text+ "\n")
        
                   
        
        #try:
        #    cursor.execute("INSERT IGNORE INTO `rubygems_entry`(`entry_id`, `project_name`, \
        #    `datasource_id`, `title`, `id`, `date_of_entry`, `time_of_entry`, `summary`,\
        #    `content`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", 
        #    (entry_id,project,datasource_id,checkNull(title), checkNull(ent_id),date,time
        #    ,checkNull(summary), checkNull(content)))
        #    db.commit    
        #except MySQLdb.Error as error:
        #        print "execute"
        #        print error
        #        db.rollback()
                
        entry_id = entry_id+1
        
output_file.close()         
cursor.close()
db.close()    
