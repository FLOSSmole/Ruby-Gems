# -*- coding: utf-8 -*-
'''
This program is free software; you can redistribute it
and/or modify it under the terms of the Perl Artistic License 2.0.

Copyright (C) 2016 Megan Squire 

We're working on this at http://flossmole.org - Come help us build 
an open and accessible repository for data and analyses for open
source projects.

If you use this code or data for preparing an academic paper please
provide a citation to:

Howison, J., Conklin, M., & Crowston, K. (2006). FLOSSmole: 
A collaborative repository for FLOSS research data and analyses. 
International Journal of Information Technology and Web Engineering, 
1(3), 17–26.

and

FLOSSmole (2004-2016) FLOSSmole: a project to provide academic access to data 
and analyses of open source projects.  Available at http://flossmole.org 

usage:
> python extractGemFirstVersion.py <datasource_id> <password>
purpose:
select all the gems in order by lowest version date
insert their first known version into the db
'''

import pymysql
import sys

# modes are 0=normal, 1=test, 2=restart
mode = 0
startdate = ''
if mode == 2 and startdate == '':
    print('You must enter a startdate if you are in RESTART mode.')
    exit()

datasource_id = sys.argv[1]
password = sys.argv[2]

# Open local database connection: SELECT
db = pymysql.connect(host='grid6.cs.elon.edu',
                     db='rubygems',
                     user='megan',
                     passwd=password,
                     port=3306,
                     charset='utf8mb4')
cursor = db.cursor()

# Open local database connection: INSERT
db1 = pymysql.connect(host='grid6.cs.elon.edu',
                     db='rubygems',
                     user='megan',
                     passwd=password,
                     port=3306,
                     charset='utf8mb4')
cursor1 = db1.cursor()

# Open remote database connection: INSERT
db2 = pymysql.connect(host='flossdata.syr.edu',
                     db='rubygems',
                     user='megan',
                     passwd=password,
                     port=3306,
                     charset='utf8mb4')
cursor2 = db2.cursor()

selectData = (datasource_id,)
if mode == 1:
    selectQuery = "SELECT project_name, MIN(version_date_conv) \
                FROM rubygems_project_versions \
                WHERE datasource_id = %s \
                GROUP BY 1  \
                ORDER BY 2, 1 ASC \
                LIMIT 10;"
elif mode == 2:
    selectQuery = "SELECT project_name, MIN(version_date_conv) \
                FROM rubygems_project_versions \
                WHERE datasource_id = %s \
                GROUP BY 1  \
                HAVING MIN(version_date_conv) >= %s \
                ORDER BY 2, 1 ASC;"
    selectData = (datasource_id,startdate)
else:
    selectQuery = "SELECT project_name, MIN(version_date_conv) \
                FROM rubygems_project_versions \
                WHERE datasource_id = %s \
                GROUP BY 1 \
                ORDER BY 2, 1 ASC;"

cursor.execute(selectQuery, selectData)

rows = cursor.fetchall()
for row in rows:
    projectName      = row[0] 
    firstCreateDate  = row[1]  
    
    print(projectName, firstCreateDate)
    
    if testmode == 0:
        insertQuery = "INSERT IGNORE INTO rubygems_project_create_dates( \
                project_name, \
                datasource_id, \
                first_known_create) \
                VALUES (%s,%s,%s)" 
        insertData = (projectName, 
                int(datasource_id), 
                firstCreateDate)
        cursor1.execute(insertQuery, insertData)
        db1.commit()
        cursor2.execute(insertQuery, insertData)
        db2.commit()

cursor.close()
cursor1.close()
cursor2.close()
db.close()
db1.close() 
db2.close() 
