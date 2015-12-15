# -*- coding: utf-8 -*-
# usage: extractGemFirstVersion.py <datasource_id> <password>
# purpose:
# select all the gems in order by lowest version date
# insert their first known version into the db

import pymysql
import sys

testmode = 0

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

if testmode == 1:
    selectQuery = "SELECT project_name, MIN(version_date_conv) \
                FROM rubygems_project_versions \
                WHERE datasource_id = %s \
                GROUP BY 1 ORDER BY 2, 1 ASC \
                LIMIT 10"
else:
    selectQuery = "SELECT project_name, MIN(version_date_conv) \
                FROM rubygems_project_versions \
                WHERE datasource_id = %s \
                GROUP BY 1 ORDER BY 2, 1 ASC"

selectData = (datasource_id,)
cursor.execute(selectQuery, selectData)

def iter_row(cursor):
    while True:
        row = cursor.fetchone()
        if not row:
            break
        yield row

for row in iter_row(cursor):
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
