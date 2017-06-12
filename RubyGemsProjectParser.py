#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it
# and/or modify it under the terms of GPL v3
#
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# Contribution from:
# Caroline Frankel
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
# FLOSSmole(2004-2017) FLOSSmole: a project to provide academic access to data
# and analyses of open source projects. Available at http://flossmole.org
#
################################################################
# usage:
# 1getCodeplexPages.py <datasource_id> <db password>

# purpose:
# update RubyGems tables
################################################################

from bs4 import BeautifulSoup
import sys
import pymysql
import datetime

datasource_id = sys.argv[1]
password      = sys.argv[2]

# these can be used for testing in case of error
# testmode = 1 will just run a single project for testing purposes. The
#    project it runs will be identified in 'startname'
# testmode = 0 will run all projects, starting with 'startname'. The default
#    for 'startname' is ''
testmode      = 0
startName     = ''


# gives the current version of a project in RubyGems
def parseHTMLversion(htmlVersionsFile, projectName):
    htmlVersionsSoup = BeautifulSoup(htmlVersionsFile, "html.parser")
    versionList = htmlVersionsSoup.find_all("li", class_="gem__version-wrap")
    for versionBlob in versionList:
        a = versionBlob.find("a")
        if a:
            versionNumber = a.string
        small = versionBlob.find("small")
        if small:
            versionDate = small.string[2:]
            # print (versionDate)
            if versionDate:
                dateConverted = datetime.datetime.strptime(versionDate, "%B %d, %Y").date()
            else:
                dateConverted = None
        # ---- put everything in the database
        if testmode == 1:
            print("version number: ", versionNumber)
            print("version date: ", versionDate)
            print("date converted: ", dateConverted)
        else:
            # print("--entering project versions")
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

            cursor.execute(queryVersions, dataVersions)
            db.commit()


# gives the updated information for each project
def parseHTML(htmlFile, projectName):
    projectDescription = None
    currentVersion     = None
    totalDownloads     = None
    versionDownloads   = None
    projectLicense     = None
    reqRubyVersion     = None

    htmlSoup = BeautifulSoup(htmlFile, "html.parser")

    projectDescriptionBlob = htmlSoup.find("div", class_="gem__desc")
    if projectDescriptionBlob:
        p = projectDescriptionBlob.find("p")
        if p:
            projectDescription = str(p.string)

    currentVersionBlob = htmlSoup.find("h1", class_="t-display page__heading")
    if currentVersionBlob:
        i = currentVersionBlob.find("i")
        if i:
            currentVersion = str(i.string)

    dlh2List = htmlSoup.find_all("h2", class_="gem__downloads__heading t-text--s")
    print(dlh2List)
    if dlh2List:
        dlNumbers = []
        for dlh2 in dlh2List:
            span = dlh2.find("span")
            dl = span.string
            dl = dl.replace(',', '')
            dlNumbers.append(dl)
        totalDownloads = int(dlNumbers[0])
        versionDownloads = int(dlNumbers[1])

    h2List = htmlSoup.find_all("h2", class_="gem__ruby-version__heading t-list__heading")
    if h2List:
        for h2 in h2List:
            span = h2.find("span", class_="gem__ruby-version")
            if span:
                p = span.find("p")
                if p:
                    projectLicense = str(p.string)
            i = h2.find("i")
            if i:
                reqRubyVersion = str(i.string.strip())

    if testmode == 1:
        print("project description: ", projectDescription)
        print("current version: ", currentVersion)
        print("total downloads: ", totalDownloads)
        print("version downloads: ", versionDownloads)
        print("project license: ", projectLicense)
        print("required Ruby version: ", reqRubyVersion)
    else:
        # print("--entering project facts")
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
        cursor.execute(queryFacts, dataFacts)
        db.commit()

    rtDepBlob = htmlSoup.find(id="runtime_dependencies")
    if rtDepBlob:
        rtDepList = rtDepBlob.find_all("a", class_="t-list__item")
        rtDepNum = 1
        for rtDep in rtDepList:
            rtDepHref = str(rtDep['href'])
            rtDepName = str(rtDep.find("strong").string)
            if testmode == 1:
                print("rt Dep Num: ", rtDepNum)
                print("rt Dep Href: ", rtDepHref)
                print("rt Dep Name: ", rtDepName)
            else:
                # print("--entering rtdep")
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
                cursor.execute(queryRT, dataRT)
                db.commit()
            rtDepNum += 1

    devDepBlob = htmlSoup.find(id="development_dependencies")
    if devDepBlob:
        devDepList = devDepBlob.find_all("a", class_="t-list__item")
        devDepNum = 1  # counter for dependencies
        for devDep in devDepList:
            devDepHref = str(devDep['href'])
            devDepName = str(devDep.find("strong").string)
            if testmode == 1:
                print("dev Dep Num: ", devDepNum)
                print("dev Dep Href: ", devDepHref)
                print("dev Dep Name: ", devDepName)
            else:
                # print("--entering devdep")
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

                cursor.execute(queryDev, dataDev)
                db.commit()
            devDepNum += 1

    authorBlob = htmlSoup.find("div", class_="gem__members")
    if authorBlob:
        authorList = authorBlob.find_all("li", class_="t-list__item")
        authorNum = 1
        for author in authorList:
            authorName = str(author.find("p").string)
            if testmode == 1:
                print("authorNum: ", authorNum)
                print("authorName: ", authorName)
            else:
                # print("--entering authors")
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

                cursor.execute(queryAuthor, dataAuthor)
                db.commit()
            authorNum += 1

    ownerBlob = htmlSoup.find("div", class_="gem__owners")
    if ownerBlob:
        ownerList = ownerBlob.find_all("a")
        ownerNum = 1
        for owner in ownerList:
            ownerName = owner['title']
            ownerHref = owner['href']
            if testmode == 1:
                print("ownerNum: ", ownerNum)
                print("ownerName: ", ownerName)
            else:
                # print("--entering owners")
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

                cursor.execute(queryOwner, dataOwner)
                db.commit()

            ownerNum += 1

    linkList = htmlSoup.find_all("a", class_="gem__link t-list__item")
    for link in linkList:
        linkType = str(link.string)
        linkHref = str(link['href'])
        if testmode == 1:
            print("linkType: ", linkType)
            print("linkHref: ", linkHref)
        else:
            # print("--entering links")
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

            cursor.execute(queryLink, dataLink)
            db.commit()

# MAIN
# establish database connection: SYR

db = pymysql.connect(host='',
                     user='',
                     passwd='',
                     db='',
                     use_unicode=True,
                     charset="utf8mb4",
                     autocommit=True)
cursor = db.cursor()

# select the project names and files from the database for this datasource_id
if testmode == 1:
    selectQuery = "SELECT project_name, html_file, html_versions_file \
                    FROM rubygems_project_pages \
                    WHERE project_name = %s \
                    AND datasource_id = %s \
                    LIMIT 10"
else:
    selectQuery = "SELECT project_name, html_file, html_versions_file \
                    FROM rubygems_project_pages \
                    WHERE project_name >= %s \
                    AND datasource_id = %s \
                    LIMIT 10"

selectData = (startName, datasource_id)
cursor.execute(selectQuery, selectData)
rows = cursor.fetchall()

for row in rows:
    projectName      = row[0] 
    htmlFile         = row[1] 
    htmlVersionsFile = row[2] 

    print(projectName)

    parseHTML(htmlFile, projectName)
    parseHTMLversion(htmlVersionsFile, projectName)

cursor.close()
db.close()
