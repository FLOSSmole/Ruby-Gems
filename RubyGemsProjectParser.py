# -*- coding: utf-8 -*-
'''
This program is free software; you can redistribute it
and/or modify it under the terms of the Perl Artistic License 2.0.

Copyright (C) 2015 Megan Squire and Gavan Roth

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
python RubyGemsProjectParser.py <datasource_id> <password>

'''

from bs4 import BeautifulSoup
import sys
#import mysql.connector
#from mysql.connector import errorcode
import pymysql
import datetime

testmode = 0
startName = 'bosh_cli'
datasource_id = sys.argv[1]
password = sys.argv[2]


'''
#----------------------------------
parseHTMLversion()
arguments:
 --htmlVersionsFile - the file containing the versions of the gem
 --projectName - which project you are working on actions:
 --pulls out the version 1.0.1 etc
 -- pulls out the date and converts date to proper date format
 -- inserts this info into database

the relevant section of the version file looks like this:
<ul class="t-list__items">
<li class="gem__version-wrap">
<a class="t-list__item" href="https://rubygems.org/gems/concerto_audio/versions/0.0.1">0.0.1</a>
<small class="gem__version__date">- January  7, 2014</small>
<span class="gem__version__date">(8 KB)</span>
</li>
</ul>
#----------------------------------
'''
def parseHTMLversion(htmlVersionsFile, projectName):
    htmlVersionsSoup = BeautifulSoup(htmlVersionsFile)
    versionList = htmlVersionsSoup.find_all("li",class_="gem__version-wrap")
    for versionBlob in versionList:
        a = versionBlob.find("a")
        if a:
            versionNumber = a.string
        small = versionBlob.find("small")
        if small:
            versionDate = small.string[2:]
            #print (versionDate)
            if versionDate:
                dateConverted = datetime.datetime.strptime(versionDate, "%B %d, %Y").date()
            else:
                dateConverted = None
        #---- put everything in the database
        if testmode == 1:
            print("version number: ",versionNumber)
            print("version date: ",versionDate)
            print("date converted: ", dateConverted)
        else:
            #print("--entering project versions")
            queryVersions = "INSERT IGNORE INTO rubygems_project_versions( \
                    project_name, \
                    datasource_id, \
                    version_number, \
                    version_date, \
                    version_date_conv) \
                     VALUES (%s,%s,%s,%s,%s)"
            dataVersions = (str(projectName), 
                      int(datasource_id), 
                      str(versionNumber),
                      str(versionDate),
                      str(dateConverted))
                      
            cursor1.execute(queryVersions, dataVersions)
            db1.commit()
            cursor2.execute(queryVersions, dataVersions)
            db2.commit()

'''
#----------------------------------
parseHTML()
arguments:
 --htmlFile - the homepage for the gem
 --projectName - which project you are working on
#----------------------------------
'''       
def parseHTML(htmlFile, projectName):
    projectDescription = None
    currentVersion     = None
    totalDownloads     = None
    versionDownloads   = None
    projectLicense     = None
    reqRubyVersion     = None
        
    htmlSoup = BeautifulSoup(htmlFile)
    
    '''
    **Project description
    <div class="gem__desc" id="markup">
    <p>Add streaming audio such as shoutcast to Concerto 2.</p>
    </div>
    '''
    projectDescriptionBlob = htmlSoup.find("div",class_="gem__desc")
    if projectDescriptionBlob:
        p = projectDescriptionBlob.find("p")
        if p:
            projectDescription = str(p.string)

    '''
    **Current version
    <h1 class="t-display page__heading">
    <a class="t-link--black" href="/gems/concerto_audio">concerto_audio</a>
    <i class="page__subheading">0.0.5</i>
    </h1>
    '''
    currentVersionBlob = htmlSoup.find("h1",class_="t-display page__heading")
    if currentVersionBlob:
        i = currentVersionBlob.find("i")
        if i:
            currentVersion = str(i.string)

    '''
    **Total downloads & downloads for this version
    <div class="gem__downloads-wrap" data-href="/api/v1/downloads/concerto_audio-0.0.5.json">
    <h2 class="gem__downloads__heading t-text--s">
                Total downloads
                <span class="gem__downloads">3,892</span>
    </h2>
    <h2 class="gem__downloads__heading t-text--s">
                For this version
                <span class="gem__downloads">725</span>
    </h2>
    </div>
    '''
    dlh2List = htmlSoup.find_all("h2",class_="gem__downloads__heading t-text--s")
    if dlh2List:
        dlNumbers=[]
        for dlh2 in dlh2List:
            span = dlh2.find("span")
            dl = span.string
            dl = dl.replace(',', '')
            dlNumbers.append(dl)
        totalDownloads = int(dlNumbers[0])
        versionDownloads = int(dlNumbers[1])

    '''
    **License & Required Ruby Version
    **there are 4 of these poorly named h2's on the page;  
    **the 3rd and 4th are the ones we want
    
    <h2 class="gem__ruby-version__heading t-list__heading">
              License:
              <span class="gem__ruby-version">
    <p>Apache 2.0</p>
    </span>
    </h2>
    
        
    <h2 class="gem__ruby-version__heading t-list__heading">
            Required Ruby Version:
            <i class="gem__ruby-version">
                &gt;= 0
            </i>
    </h2>  
    
    
    '''
    
    h2List = htmlSoup.find_all("h2",class_="gem__ruby-version__heading t-list__heading")
    if h2List:
        for h2 in h2List:
            span = h2.find("span",class_="gem__ruby-version")
            if span:
                p = span.find("p")
                if p:
                    projectLicense = str(p.string)
            i = h2.find("i")
            if i:
                reqRubyVersion = str(i.string.strip())
        
        '''
    if h2List[2]:
        h2License = h2List[2]
        span = h2License.find("span")
        p = span.find("p")
        projectLicense = p.string
    if h2List[3]:
        h2Version = h2List[3]
        i = h2Version.find("i")
        reqRubyVersion = i.string.strip()
    '''
    if testmode == 1:
        print("project description: ",projectDescription)
        print("current version: ",currentVersion)
        print("total downloads: ",totalDownloads)
        print("version downloads: ",versionDownloads)
        print("project license: ",projectLicense)
        print("required Ruby version: ", reqRubyVersion)
    else:
        #print("--entering project facts")
        queryFacts = "INSERT IGNORE INTO rubygems_project_facts( \
                project_name, \
                datasource_id, \
                project_description, \
                current_version, \
                total_downloads, \
                current_downloads, \
                project_license, \
                req_ruby_version) \
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)" 
        dataFacts = (projectName, 
                int(datasource_id), 
                projectDescription,
                currentVersion, 
                totalDownloads,
                versionDownloads,
                projectLicense,
                reqRubyVersion)
        cursor1.execute(queryFacts, dataFacts)
        db1.commit()
        cursor2.execute(queryFacts, dataFacts)
        db2.commit()
            
    '''
    --Runtime Dependencies
    <div class="dependencies" id="runtime_dependencies">
    <h3 class="t-list__heading">Runtime Dependencies:</h3>
    <div class="t-list__items">
    <a class="t-list__item" href="/gems/rails">
    <strong>rails</strong> ~&gt; 3.2.12
    </a> </div>
    </div>
    </div>
    '''
    rtDepBlob = htmlSoup.find(id="runtime_dependencies")
    if rtDepBlob:
        rtDepList = rtDepBlob.find_all("a",class_="t-list__item")
        rtDepNum = 1 
        for rtDep in rtDepList:
            rtDepHref = str(rtDep['href'])
            rtDepName = str(rtDep.find("strong").string)
            if testmode == 1:
                print("rt Dep Num: " ,rtDepNum)
                print("rt Dep Href: ",rtDepHref)
                print("rt Dep Name: ",rtDepName)
            else:
                #print("--entering rtdep")
                queryRT = "INSERT IGNORE INTO rubygems_project_rtdep(\
                        project_name, \
                        datasource_id, \
                        dependency_num, \
                        dependency_href, \
                        dependency_name) \
                        VALUES (%s,%s,%s,%s,%s)" 
                dataRT = (str(projectName), 
                          int(datasource_id), 
                          rtDepNum,
                          rtDepHref,
                          rtDepName)
                cursor1.execute(queryRT, dataRT)
                db1.commit()
                cursor2.execute(queryRT, dataRT)
                db2.commit()
            rtDepNum += 1        
    '''
    --Development Dependencies
    <div class="dependencies" id="development_dependencies">
    <h3 class="t-list__heading">Development Dependencies:</h3>
    <div class="t-list__items">
    <a class="t-list__item" href="/gems/sqlite3">
    <strong>sqlite3</strong> &gt;= 0
    </a> </div>
    '''             
    devDepBlob = htmlSoup.find(id="development_dependencies")
    if devDepBlob:
        devDepList = devDepBlob.find_all("a",class_="t-list__item")
        devDepNum = 1 # counter for dependencies
        for devDep in devDepList:
            devDepHref = str(devDep['href'])
            devDepName = str(devDep.find("strong").string)
            if testmode == 1:
                print("dev Dep Num: " ,devDepNum)
                print("dev Dep Href: ",devDepHref)
                print("dev Dep Name: ",devDepName)
            else:
                #print("--entering devdep")
                queryDev = "INSERT IGNORE INTO rubygems_project_devdep(\
                        project_name, \
                        datasource_id, \
                        dependency_num, \
                        dependency_href, \
                        dependency_name) \
                        VALUES (%s,%s,%s,%s,%s)" 
                dataDev = (str(projectName), 
                          int(datasource_id), 
                          devDepNum,
                          devDepHref,
                          devDepName)
                          
                cursor1.execute(queryDev, dataDev)
                db1.commit()
                cursor2.execute(queryDev, dataDev)
                db2.commit()
            devDepNum += 1
    '''
    ** Authors
    <div class="gem__members">
    <h3 class="t-list__heading">Authors:</h3>
    <ul class="t-list__items">
    <li class="t-list__item">
    <p>Marvin Frederickson</p>
    </li>
    </ul>
    '''
    authorBlob = htmlSoup.find("div",class_="gem__members")
    if authorBlob:
        authorList = authorBlob.find_all("li",class_="t-list__item")
        authorNum = 1
        for author in authorList:
            authorName = str(author.find("p").string)
            if testmode == 1:
                print("authorNum: " ,authorNum)
                print("authorName: ",authorName)
            else:
                #print("--entering authors")
                queryAuthor = "INSERT IGNORE INTO rubygems_project_authors(\
                        project_name, \
                        datasource_id, \
                        author_num, \
                        author_name) \
                        VALUES (%s,%s,%s,%s)" 
                dataAuthor = (str(projectName), 
                          int(datasource_id), 
                          authorNum,
                          authorName)

                cursor1.execute(queryAuthor, dataAuthor)
                db1.commit() 
                cursor2.execute(queryAuthor, dataAuthor)
                db2.commit()
            authorNum += 1
    '''
    ** Owners
    <h3 class="t-list__heading">Owners:</h3>
    <div class="gem__owners">
    <a alt="augustf" href="/profiles/augustf" title="augustf"><img alt="E959b799a48a91ab4c1dcafd73ac3294" height="48" id="gravatar-66271" src="https://secure.gravatar.com/avatar/e959b799a48a91ab4c1dcafd73ac3294.png?d=retro&amp;r=PG&amp;s=48" width="48"/></a>
    </div>
    '''
    ownerBlob = htmlSoup.find("div",class_="gem__owners")
    if ownerBlob:
        ownerList = ownerBlob.find_all("a")
        ownerNum = 1
        for owner in ownerList:
            ownerName = owner['title']
            ownerHref = owner['href']
            if testmode == 1:
                print("ownerNum: " ,ownerNum)
                print("ownerName: ",ownerName)
            else:
                #print("--entering owners")
                queryOwner = "INSERT IGNORE INTO rubygems_project_owners(\
                        project_name, \
                        datasource_id, \
                        owner_num, \
                        owner_name, \
                        owner_href) \
                        VALUES (%s,%s,%s,%s,%s)" 
                dataOwner = (str(projectName), 
                          int(datasource_id), 
                          ownerNum,
                          ownerName,
                          ownerHref)

                cursor1.execute(queryOwner, dataOwner)
                db1.commit()
                cursor2.execute(queryOwner, dataOwner)
                db2.commit()
            ownerNum += 1                
    '''
    ** Links
    <h3 class="t-list__heading">Links:</h3>
    <div class="t-list__items">
    <a class="gem__link t-list__item" href="https://github.com/mfrederickson/concerto-audio" rel="nofollow">Homepage</a>
    <a class="gem__link t-list__item" href="/downloads/concerto_audio-0.0.5.gem" id="download">Download</a>
    <a class="gem__link t-list__item" href="http://www.rubydoc.info/gems/concerto_audio/0.0.5" id="docs">Documentation</a>
    <a class="gem__link t-list__item" href="https://badge.fury.io/rb/concerto_audio/install" id="badge">Badge</a>
    <a class="toggler gem__link t-list__item" href="/sign_in" id="subscribe">Subscribe</a>
    <a class="gem__link t-list__item" href="/gems/concerto_audio/versions.atom" id="rss">RSS</a>
    <a class="gem__link t-list__item" href="http://help.rubygems.org/discussion/new?discussion[private]=1&amp;discussion[title]=Reporting%20Abuse%20on%20concerto_audio">Report Abuse</a>
    </div>
    '''
    linkList = htmlSoup.find_all("a", class_="gem__link t-list__item")
    for link in linkList:
        linkType = str(link.string)
        linkHref = str(link['href'])
        if testmode == 1:
            print("linkType: ",linkType)
            print("linkHref: ",linkHref)
        else:
            #print("--entering links")
            queryLink = "INSERT IGNORE INTO rubygems_project_links(\
                    project_name, \
                    datasource_id, \
                    link_type, \
                    link_href) \
                    VALUES (%s,%s,%s,%s)" 
            dataLink = (str(projectName), 
                      int(datasource_id), 
                      linkType,
                      linkHref)

            cursor1.execute(queryLink, dataLink)
            db1.commit()
            cursor2.execute(queryLink, dataLink)
            db2.commit()

        
# MAIN
# establish database connection: ELON, for SELECT

db = pymysql.connect(host='grid6.cs.elon.edu',
                                 db='rubygems',
                                 user='megan',
                                 passwd=password,
                                 port=3306)
cursor = db.cursor()

# establish database connection: ELON, for INSERT
db1 = pymysql.connect(host='grid6.cs.elon.edu',
                                 db='rubygems',
                                 user='megan',
                                 passwd=password,
                                 port=3306)

cursor1 = db1.cursor()

# establish database connection: SYR      

db2 = pymysql.connect(host='flossdata.syr.edu',
                                  db='rubygems',
                                  user='megan',
                                  passwd=password,
                                  port=3306)
cursor2 = db2.cursor()
    
# select the project names and files from the database for this datasource_id
if testmode == 1:
    selectQuery = "SELECT project_name, html_file, html_versions_file \
        FROM rubygems_project_pages \
        WHERE project_name = %s AND datasource_id = %s"
    selectData = (startName, datasource_id)
    cursor.execute(selectQuery, selectData)
else:
    selectQuery = "SELECT project_name, html_file, html_versions_file \
        FROM rubygems_project_pages \
        WHERE project_name >= %s AND datasource_id = %s"
    cursor.execute(selectQuery, (startName, datasource_id,))

def iter_row(cursor):
    while True:
        row = cursor.fetchone()
        if not row:
            break
        yield row

for row in iter_row(cursor):
    projectName      = row[0]#.decode() #utf8mb4 datatype  
    htmlFile         = row[1]#.decode() 
    htmlVersionsFile = row[2]#.decode() 
    
    print(projectName)
    
    parseHTML(htmlFile, projectName)
    parseHTMLversion(htmlVersionsFile, projectName)

cursor.close()
cursor1.close()
cursor2.close()
db.close()
db1.close()
db2.close()
