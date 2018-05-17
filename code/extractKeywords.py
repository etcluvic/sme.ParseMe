from bs4 import BeautifulSoup
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
from datetime import datetime
from settingsFile import extractedTextPath, rankingsPath, termsPath, picklePath
import time
import os
import fnmatch
import codecs
import pickle

def printSeparator(character, times):
	print(character * times)

if __name__ == '__main__':

	#termsPath		= 'terms/'
	#picklePath		= 'pickles/'
	all				= {}


	for root, dirnames, filenames in os.walk(termsPath):
		for filename in fnmatch.filter(filenames, '*.xml'):

			print(filename)
			thisPath = os.path.join(termsPath, filename)

			f = codecs.open(thisPath,'r','utf-8')
			markup = f.read()
			f.close()

			soup = BeautifulSoup(markup, "lxml-xml")
			documents = soup.find_all('document')

			for d in documents:
				print(d['name'])
				documentName 	= d['name'].split('.')[1] #use only the doi
				setName 		= d['set']

				termsByDocument = []
				terms = d.find_all('term')
				for t in terms:
					termsByDocument += [t['name']]

				termsByDocument = tuple(termsByDocument)


				all[ documentName ] = {'set':setName, 'terms':termsByDocument}



			printSeparator('*',50)

	print(len(all.keys()))

	#next - save "all" dictionary as a pickle

	printSeparator('*',50)
	printSeparator('*',50)
	printSeparator('*',50)


	print('saving file...')

	savePath = os.path.join(picklePath, 'keywords.p')
	pickle.dump( all, open( savePath, "wb" ) )

	print('file saved!')
