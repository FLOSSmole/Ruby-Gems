# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import MySQLdb


#establish database connection
db = MySQLdb.connect(host="grid6.cs.elon.edu", user="", passwd="", db="rubygems", use_unicode=True, charset = "utf8")
cursor = db.cursor()
cursor.execute('SET NAMES utf8mb4')
cursor.execute('SET CHARACTER SET utf8mb4')
cursor.execute('SET character_set_connection=utf8mb4')

#get all project names
try:
    cursor.execute("SELECT rss_file FROM `rubygems_projects`")
    rss_files = cursor.fetchall()
except MySQLdb.Error as error:
    print error

def checkNull(item):
    if item != None:
        return item.text.rstrip()
    return " "

for row in rss_files:
    rss = unicode(row[0])
    soup = BeautifulSoup(rss)
    entries = soup.findAll('entry')
    for entry in entries:
        #---handle parsed fields, except author
        
        '''
        Gavan, put the rest of the parser code here
        
        NOTE: you will need to INSERT INTO rubygems_entry
        Since this has an autoincrement id, pass nothing for that value
        Then, in order to USE that value in teh INSERT below for authors, you'll need to select  the last inserted id:
        http://stackoverflow.com/questions/2548493/how-do-i-get-the-id-after-insert-into-mysql-database-with-python
        
        That becomes the first inserted column for the authors below. The value is called entry_id below.
        '''
        
        #---handle authors
        author = entry.find('author')
        if author:
            author_count=1
            for person_list in author.find_all("name"): 
                if person_list.text:
                    people = person_list.text.split(',')
                    
                    print people
                    for person in people:
                        # remove any whitespace on either side
                        clean_person = person.strip()
                        print clean_person,":",author_count
                
                try:
                    cursor.execute(u"INSERT INTO `rubygems_authors`(`entry_id`, `author_count`, `name`) VALUES (%s,%s,%s)", (entry_id, author_count, clean_person))
                    db.commit    
                except MySQLdb.Error as error:
                    print "execute"
                    print error
                    db.rollback() 
                
                author_count += 1
                
        
cursor.close()
db.close()    
