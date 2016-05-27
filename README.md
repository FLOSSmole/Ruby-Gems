# Ruby-Gems
This code collects the pages for each gem at RubyGems.org, and parses out the pertinent facts about the projects. This code can be run by a FLOSSmole administrator in order to populate the FLOSSmole tables and release the associated flat files.

To get started running this code, do the following:

1. first create a datasource_id in the 'ossmole_merged.datasources' table on the FLOSSmole server.
2. run RubygemsProjectCollector.py <datasource_id> <password>
3. run RubygemsProjectParser.py <datasource_id> <password>
4. create the flat files, zip them, and ftp them to flossdata.syr.edu/data/rg
