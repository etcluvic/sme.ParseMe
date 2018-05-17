import os
import fnmatch
import codecs
from sklearn.feature_extraction.text import TfidfVectorizer
from bs4 import BeautifulSoup
from lxml import etree
from settingsFile import extractedTextPath, rankingsPath, termsPath

def printSeparator(character, times):
	print(character * times)

if __name__ == '__main__':

	#rankingsPath 	= 'rankings/'
	#termsPath		= 'terms/'
	precision 		= '.8f'
	minTermLenght 	= 4
	cutoff			= 3
	termsToGenerate	= 10

	#setNames
	setNames = [d for root, dirnames, filenames in os.walk(extractedTextPath) for d in dirnames]

	for setNumber, thisSet in enumerate(setNames):

		print(setNumber, thisSet)

		corpus = []
		docs = []
		extraTFIDFTermsArray = []

		thisPath = os.path.join(extractedTextPath,thisSet)
		print(thisPath)

		for root, dirnames, filenames in os.walk(thisPath):
			for filename in fnmatch.filter(filenames, '*.xml'):

				f = codecs.open(os.path.join(thisPath, filename),'r','utf-8')
				contents = f.read()
				f.close()

				#add bs4 stuff here
				soup = BeautifulSoup(contents, 'lxml')

				rawContents = soup.find("contents")
				if rawContents:
					text = rawContents.get_text()
				else:
					text = u''

				corpus += [text]
				docs += [filename]

		print('files:', len(corpus))
		print('done - reading files')

		vocab = []

		#tf idf
		tf = TfidfVectorizer(analyzer='word', lowercase=True)
		tfidfMatrix = tf.fit_transform(corpus)

		#tf2 idf - not specifying the vocabulary
		tfExpanded = TfidfVectorizer(analyzer='word', lowercase=True)
		tfidfMatrixExpanded = tfExpanded.fit_transform(corpus)
		vocab2 = []

		#print(tfidfMatrix)
		#print(tfidfMatrix.shape)

		#sum of the rows
		simpleRankingMatrix = tfidfMatrix.sum(axis=1)
		print('done - simple ranking matrix')



		#generate extra terms from tf idf
		for i,fn in enumerate(docs):

			rank = simpleRankingMatrix[i][0,0]

			#print(fn, rank)
			#if rank == 0:
			#extract additional terms
			#print(tfidfMatrixExpanded[i])
			#titles_tfidf = tfExpanded.fit_transform(titles)

			rankedTerms = tfExpanded.inverse_transform(tfidfMatrixExpanded[i])
			#print(type(rankedTerms[0]))
			#print(len(rankedTerms[0]))

			temp = [rt for rt in rankedTerms[0] if len(rt) > minTermLenght]
			cutoffIndex = len(temp)/cutoff
			extraTFIDFTerms = temp[cutoffIndex:cutoffIndex + termsToGenerate]
			#print(extraTFIDFTerms)
			#adding to the overall Array
			extraTFIDFTermsArray += [extraTFIDFTerms]

			for eTT in extraTFIDFTerms:
				if eTT not in vocab and eTT not in vocab2:
					vocab2 += [eTT]

		#printSeparator('*', 50)


		#tf idf - again
		tf2 = TfidfVectorizer(analyzer='word', lowercase=True, vocabulary = vocab2)
		tfidfMatrix2 = tf2.fit_transform(corpus)
		#sum of the rows
		simpleRankingMatrix2 = tfidfMatrix2.sum(axis=1)

		#tf idf - again
		tf3 = TfidfVectorizer(analyzer='word', lowercase=True, vocabulary = vocab + vocab2)
		tfidfMatrix3 = tf3.fit_transform(corpus)
		#sum of the rows
		simpleRankingMatrix3 = tfidfMatrix3.sum(axis=1)

		#xml root element
		rootElement = etree.Element("rankings")
		rootElement.set("set", thisSet)


		for i,fn in enumerate(docs):

			rank1 = simpleRankingMatrix[i][0,0]
			rank2 = simpleRankingMatrix2[i][0,0]
			rank3 = simpleRankingMatrix3[i][0,0]
			#print(fn, rank1, rank2,rank3)


			documentElement = etree.SubElement(rootElement, "document")
			documentElement.set("name", fn)
			documentElement.set("tm", format(float(rank1), precision) )
			documentElement.set("tfidf", format(float(rank2), precision) )
			documentElement.set("combined", format(float(rank3), precision) )


		#printSeparator('*', 50)

		print 'Rankings - Saving xml file...'
		xmlString = etree.tostring(rootElement, pretty_print=True, encoding='UTF-8')
		fh = codecs.open(os.path.join(rankingsPath, thisSet + '.xml'),'w', encoding='utf-8' )
		fh.write(xmlString)
		fh.close()
		print 'done'


		#save tfidf terms to xml

		rootElement = etree.Element("results")
		rootElement.set("method", 'tf-idf')

		for i,fn in enumerate(docs):

			documentElement = etree.SubElement(rootElement, "document")
			documentElement.set("name", fn)
			documentElement.set("set", thisSet)

			for t in extraTFIDFTermsArray[i]:
				#print(type(t[0]), t)
				termElement = etree.SubElement(documentElement, "term")
				termElement.set("name", t)


		print 'Extra terms - Saving xml file...'
		xmlString = etree.tostring(rootElement, pretty_print=True, encoding='UTF-8')
		fh = codecs.open(os.path.join(termsPath, thisSet + '.xml'),'w', encoding='utf-8' )
		fh.write(xmlString.decode('utf-8'))
		fh.close()
		print 'done'


		printSeparator('*', 50)

	print('bye')
