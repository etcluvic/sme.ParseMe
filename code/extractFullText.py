import os
import fnmatch
import codecs
import datetime
from lxml import etree
from bs4 import BeautifulSoup
from settingsFile import fullTextPath

def printSeparator(character, times):
	print(character * times)

if __name__ == '__main__':

	separator 			= '*'
	repeatSeparator 	= 50
	outputPath 			= 'fullText/'
	today 				= str(datetime.date.today())

	matches = []
	for root, dirnames, filenames in os.walk(fullTextPath):
		for filename in fnmatch.filter(filenames, '*.xml'):
			t = os.path.join(root, filename)
			print(t)
			matches.append(t)

	printSeparator('*', 50)
	print(len(matches))
	printSeparator('*', 50)

	for i, m in enumerate(matches):
		print(i, m)

		temp = m.split('/')
		setId = temp[-4]
		doi = temp[-2]
		filename = setId + '.' + doi + '.xml'

		fileExists = os.path.isfile(outputPath + filename)

		#statinfo = os.stat(outputPath + filename)
		#size = statinfo.st_size

		#only check for files with no bytes
		if not fileExists:

			f = codecs.open(m,'r','utf-8')

			contents = f.read()
			f.close()

			text = []
			soup = BeautifulSoup(contents, 'lxml')

			docDoi = soup.find("idpublic", {"scheme" : "doi"})
			if docDoi:
				docDoiText = docDoi.get_text()
			else:
				docDoiText = u'None'

			title = soup.find('titre')
			if title:
				titleText = title.get_text()
			else:
				titleText = u'None'

			mainBody = soup.find('corps')
			if mainBody:

				lines = mainBody.find_all('alinea')
				text = [l.get_text() for l in lines]

				if len(text) == 0:

					lines2 = mainBody.find_all('texte')
					text = [l.get_text() for l in lines2]

				if len(text) == 0:

					lines3 = mainBody.find_all('ligne')
					text = [l.get_text() for l in lines3]


			#xml root element
			rootElement = etree.Element("document")
			rootElement.set("set", setId)
			rootElement.set("title", titleText)
			rootElement.set("parsed", today)
			rootElement.set("doi", docDoiText)

			contentsElement 		= etree.SubElement(rootElement, "contents")
			contentsElement.text 	= ' '.join(text)

			#create direcoty
			if not os.path.exists(outputPath + setId):
    				os.makedirs(outputPath + setId)

			#save output

			print(os.path.join(setId, filename))

			xmlString = etree.tostring(rootElement, pretty_print=True, encoding='UTF-8')
			fh = codecs.open(os.path.join(outputPath, setId, filename),'w', encoding='utf-8' )
			fh.write(xmlString.decode('utf-8'))
			fh.close()

		printSeparator('*', 50)
