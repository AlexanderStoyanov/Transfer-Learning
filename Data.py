class Data(object):
    def __init__(self, *classes):
        self.classes = classes
    
    def ngram_vectorize(self, **kwargs=None, train_texts=None, train_labels=None, val_texts=None, test_texts):
        # Method overloading
        if train_texts is None:
            x_test = self.vectorizer.transform(test_texts)
            x_test = self.selector.transform(x_test).astype('float32')
            return x_test
        else:
            vectorizer = TfidfVectorizer(kwargs)

            # Learn vocabulary from training texts and vectorize training texts.
            x_train = vectorizer.fit_transform(train_texts)
            self.vectorizer = vectorizer

            # Vectorize validation texts.
            x_val = vectorizer.transform(val_texts)
            
            # Vectorize test texts.
            x_test = self.vectorizer.transform(test_texts)

            # Select top 'k' of the vectorized features.
            selector = SelectKBest(f_classif, k=min(20000, x_train.shape[1]))
            selector.fit(x_train, train_labels)
            self.selector = selector
        
            x_train = selector.transform(x_train).astype('float32')
            x_val = selector.transform(x_val).astype('float32')
            x_test = self.selector.transform(x_test).astype('float32')
            return x_train, x_val, x_test
    
    def populateList(self, filename, keyword, limit=10000, notClassList=True):
        import random
        classList = []
        classNames = []
        classCount = 0
        notClassCount = 0
        with open(filename, "r") as f:
            #making a list of all lines from the file
            lines = f.readlines()

            #making a list (classNames) of all lines that contain the keyword
            for line in lines:
                loweredLine = line.lower()
                strippedLine = line.strip()
                if keyword in loweredLine:
                    classNames.append(strippedLine)

            #making a list of size limit by randomly picking names from classNames       
            while len(classList) != limit and len(classNames) > 0:
                random_int = random.randint(0, len(classNames)-1)
                classList.append(classNames.pop(random_int))
                classCount += 1
            print("Article names in the %s list: %d" % (keyword, len(classList)))

            #do we want list of names that don't have a keyword?
            if(notClassList):
                notClassList = []
                #making a list of random lines of size(classList) that do not contain the keyword
                while len(notClassList) != int(len(classList)*1):
                    random_int = random.randint(0, len(lines)-1)
                    line = lines[random_int]
                    if keyword not in line.lower():
                        notClassList.append(line.strip())
                        notClassCount += 1
                print("Article names in the not %s list: %d" % (keyword, len(notClassList)))
                return classList, notClassList
        return classList
    
    def makeLabels(self, data, labelValue):
        #generating labels list that matches pageContent list in length
        labels = []
        for x in range(0, len(trainData)):
            labels.append(labelValue)
        print("Labels made successfully")
        return labels
    
    
    def parseList(self, *titleList):
        import csv
        import requests
        import nltk
        from nltk.corpus import stopwords
        nltk.download('stopwords')
        stopWords = stopwords.words('english')
        stemmer = nltk.stem.SnowballStemmer('english')

        S = requests.Session()
        URL = "https://en.wikipedia.org/w/api.php"

        train = []
        b = ",-\":;~!@#$%^&?[]{}<>`1234567890\\*()\'/|=\n"
        for title in titleList:
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
            for char in b:
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
                sentence = [stemmer.stem(i) for i in sentence]
                #Check word by word, if the word is not in stop words and not a single letter, join
                sentence = ' '.join(word for word in sentence if word not in stopWords and len(word) > 2)
                train.append(sentence)
        return train