# usage: gemFirstVersion.py
# purpose:
# select all the gems in order by lowest version date

import MySQLdb

# Open local database connection
db1 = MySQLdb.connect(host="grid6.cs.elon.edu",\
    user="megan", \
    passwd=p, \
    db="rubyforge", \
    use_unicode=True, \
    charset="utf8")
cursor1 = db1.cursor()
db1.autocommit(True)

counter = 0
cursor1.execute('SELECT project_name, MIN(version_date_conv) FROM rubygems_project_versions GROUP BY 1 ORDER BY 2, 1 ASC')
rows = cursor1.fetchall()
for row in rows:
    proj = row[0]
    date = row[1]
    
    cursor2 = db1.cursor()
    try:
        cursor2.execute('INSERT INTO rpt_rubygems_proj_first_version (cols) VALUES())
        cursor2.close()
    except:
        pass
