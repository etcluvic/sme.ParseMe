steps:
mkdir pickles rankings terms solr.files
python extractFullText.py
python extractTfidf.py
python extractKeywords.py
python generateSolrFilesAll.py

compress solr files before transfering:
tar -cvf solr.files.DATE.tar solr.files/DATE/


Note: the corpus should be in the following structure:
erudit
--> setName1
---->  document1
---->  document2
...
---->  documentN
--> setName 2
...
-->setNameM
