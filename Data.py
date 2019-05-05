import abc 
from abc import ABC, abstractmethod

import nltk
nltk.download('punkt')
from nltk.corpus import stopwords
nltk.download('stopwords')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif

import csv
import random
import requests


class Data(ABC):
    def __init__(self):
        self.stopWords = stopwords.words('english')
        self.stemmer = nltk.stem.SnowballStemmer('english')
        self.charsToRemove = ',-\":;~!@#$%^&?[]{}<>`1234567890\\*()\'/|=\n'
        self.vectorizer = None
        self.selector = None
        
    # Preprocessing data: removing all junk characters (found in self.charsToRemove), 
    # stemming all words, removing all stopwords
    def preprocess(self, data):
        newData = []
        for sentence in data:
            sentence = sentence.translate({ord(i):None for i in self.charsToRemove}).strip().split(" ")
            sentence = [self.stemmer.stem(i) for i in sentence]
            sentence = ' '.join(word for word in sentence if word not in self.stopWords and len(word) > 1).strip()
            newData.append(sentence)
        return newData
    
    # Generating labels list with appropriate label value
    def makeLabels(self, labelValue):
        labels = []
        for _ in range(0, len(self.data)):
            labels.append(int(labelValue))
        print("Labels made successfully")
        return labels
    
    # Vectorizing all data with tf-idf vectorizer
    def ngram_vectorize(self, data=None, labels=None, vectorizer=None, selector=None):
        kwargs = {
            'ngram_range': (1,1),
            'dtype': 'int32',
            'strip_accents': 'unicode',
            'decode_error': 'replace',
            'analyzer': 'word',  # Split text into word tokens.
            'min_df': 2, # Words that appear less than this value do not contribute
        }
        
        # Method overloading
        if vectorizer is not None and selector is not None:
            x_data = vectorizer.transform(data)
            x_data = selector.transform(x_data).astype('float32')
        else:
            vectorizer = TfidfVectorizer(kwargs)

            # Learn vocabulary from training texts and vectorize training texts.
            x_data = vectorizer.fit_transform(data)
            self.vectorizer = vectorizer

            # Select top 'k' of the vectorized features.
            selector = SelectKBest(f_classif, k=min(20000, x_data.shape[1]))
            selector.fit(x_data, labels)
            self.selector = selector
        
            x_data = selector.transform(x_data).astype('float32')
        return x_data

    
class TestData(Data):
    # @param data, list of sentences to be preprocessed
    # @param labelValue, integer value to be associated with passed data
    def __init__(self, data=None, labelValue=None):
        super().__init__()
        self.data = super().preprocess(data)
        self.labels = super().makeLabels(labelValue)
        assert len(self.data) == len(self.labels), 'Lengths of data and labels are not equal'
    
    
class WikiData(Data):
    def __init__(self, articlesFile, keyword, size, labelValue):
        super().__init__()
        self.articleNames = self.populateList(articlesFile, keyword, size)
        self.data = self.parseList()
        self.labels = super().makeLabels(labelValue)
        
    # Makes list of names of Wiki articles of size limit that contain keyword
    def populateList(self, filename, keyword, limit=10000):
        allClassNames = []
        namesList = []
        with open(filename, "r") as f:
            # making a list of all lines from the file
            lines = f.readlines()
            if(keyword != 'rand'):
                # making a list (allClassNames) of all lines that contain the keyword
                for line in lines:
                    loweredLine = line.lower()
                    strippedLine = line.strip()
                    if keyword.lower() in loweredLine:
                        allClassNames.append(strippedLine)

                # making a list of size limit by randomly picking names from allClassNames       
                while len(namesList) != limit and len(allClassNames) > 0:
                    random_int = random.randint(0, len(allClassNames)-1)
                    namesList.append(allClassNames.pop(random_int))
                print("Article names in the %s list: %d" % (keyword, len(namesList)))
            else:
                # making a list of random lines of size(namesList) that do not contain the keyword
                while len(namesList) != limit:
                    random_int = random.randint(0, len(lines)-1)
                    line = lines[random_int]
                    if keyword.lower() not in line.lower():
                        namesList.append(line.strip())
                print("Article names in random list: %d" % len(namesList))
        return namesList
    
    
    def parseList(self):
        S = requests.Session()
        URL = "https://en.wikipedia.org/w/api.php"

        train = []
        for title in self.articleNames:
            PARAMS = {
            'action': "parse",
            'redirects': 'true',
            'page': title,
            'prop': 'wikitext',
            'format': "json"
            }

            res = S.get(url=URL, params=PARAMS)
            data = res.json()
            #if page did not parse successfully, continue
            if 'error' in data:
                continue
            wikitext = data['parse']['wikitext']['*']
            seeAlsoIndex = wikitext.find("==See also==")
            if(seeAlsoIndex == -1):
                seeAlsoIndex = wikitext.find("== See also ==")

            #we do not need everything after and including See Also section
            if seeAlsoIndex != -1:
                paragraph = wikitext[:seeAlsoIndex]
            else:
                paragraph = wikitext

            #remove all unnecessary characters (defined in string b above)
            for char in self.charsToRemove:
                paragraph = paragraph.replace(char, "")

            #if wordcount < 10, paragraph will be disregarded
            if (len(paragraph.split(" ")) < 10):
                continue

            #removing words that do not carry any meaning (longer than 16 chars and smaller than 2)
            for key in paragraph.split(" "):
                if len(key) > 16:
                    paragraph = paragraph.replace(key, "")

            #line in this case is a whole paragraph
            for sentence in paragraph.split("."):
                sentence = sentence.strip().split(" ")
                #disregard sentence if it has less than 10 words or starts with ref
                if sentence[0] == 'ref' or len(sentence) < 5:
                    continue
                #Stem each word separately
                sentence = [self.stemmer.stem(i) for i in sentence]
                #Check word by word, if the word is not in stop words and not a single letter, join
                sentence = ' '.join(word for word in sentence if word not in self.stopWords and len(word) > 2)
                train.append(sentence)
        return train 