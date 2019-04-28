def parseList(*titleList):
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