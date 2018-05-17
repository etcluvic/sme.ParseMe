from lxml import etree
from datetime import datetime
import os
import fnmatch
import codecs
import pickle
import random
from bs4 import BeautifulSoup
from settingsFile import extractedTextPath, rankingsPath, termsPath, picklePath, SolrFilesPath

def printSeparator(character, times):
	print(character * times)

#https://stackoverflow.com/questions/3744451/is-this-how-you-paginate-or-is-there-a-better-algorithm
def getrows_byslice(seq, rowlen):
	for start in xrange(0, len(seq), rowlen):
		yield seq[start:start+rowlen]

if __name__ == '__main__':

	#picklePath		= 'pickles/'
	#fullTextPath 	= 'fullText/'
	savePath 		= os.path.join(picklePath, 'keywords.p')
	#SolrFilesPath 		= 'solr.files/'
	pagination		= 1000
	myTime			= datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')

	#create directory to save the files:
	os.makedirs(os.path.join(SolrFilesPath, myTime))


	print('loading pickle...')
	data = pickle.load( open( savePath, "rb" ) )
	print('pickle loaded!')

	dataKeys = data.keys()
	#random.shuffle(dataKeys)

	sliced = getrows_byslice(dataKeys, pagination)
	print(sliced)
	for outputFileNumber, thisSlice in enumerate(sliced):

		rootElement = etree.Element("add")

		for i, s in enumerate(thisSlice):

			docElement = etree.SubElement(rootElement, "doc")

			print(outputFileNumber, i, s)
			#print(data[s])

			setName = data[s]['set']

			#***** id *****
			fieldElement = etree.SubElement(docElement, "field")
			fieldElement.set("name", 'id')
			fieldElement.text = s

			#***** set *****
			fieldElement = etree.SubElement(docElement, "field")
			fieldElement.set("name", 'set')
			fieldElement.text = setName


			#***** text *****
			filename = os.path.join(extractedTextPath, setName, setName + '.' + s + '.xml')
			print(filename)
			f = codecs.open(filename,'r','utf-8')
			contents = f.read()
			f.close()

			soup = BeautifulSoup(contents, 'lxml')

			rawContents = soup.find("contents")
			if rawContents:
				text = rawContents.get_text()
			else:
				text = u''

			#print(text)

			fieldElement = etree.SubElement(docElement, "field")
			fieldElement.set("name", 'text')
			#fieldElement.set("type", 'text_general')
			fieldElement.text = text

			metadata  = soup.find("document")
			if metadata:
				docSet 		= metadata['set']
				docTitle 	= metadata['title']
				docDoi 		= metadata['doi']
			else:
				docSet 		= u''
				docTitle 	= u''
				docDoi 		= u''

			"""
			fieldElement = etree.SubElement(docElement, "field")
			fieldElement.set("name", 'set')
			fieldElement.text = docSet
			"""

			fieldElement = etree.SubElement(docElement, "field")
			fieldElement.set("name", 'title')
			fieldElement.text = docTitle

			fieldElement = etree.SubElement(docElement, "field")
			fieldElement.set("name", 'doi')
			fieldElement.text = docDoi

			#***** keywords *****
			keywords = setName = ' '.join(data[s]['terms'])
			#print(keywords)

			fieldElement = etree.SubElement(docElement, "field")
			fieldElement.set("name", 'keywords')
			fieldElement.text = keywords

			printSeparator('*',50)


		printSeparator('*', 50)

		print 'Results - Saving xml file...'
		xmlString = etree.tostring(rootElement, pretty_print=True, encoding='UTF-8')
		fh = codecs.open(os.path.join(SolrFilesPath, myTime, str(outputFileNumber) + '.xml'),'w', encoding='utf-8' )
		fh.write(xmlString.decode('utf-8'))
		fh.close()
		print 'done'

		printSeparator('*', 50)

	print('bye')
