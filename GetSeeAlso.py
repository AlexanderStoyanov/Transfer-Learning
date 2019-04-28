def getSeeAlso(*titleList):
    import csv
    import requests
    S = requests.Session()
    URL = "https://en.wikipedia.org/w/api.php"
    
    seeAlsoList = []
    for title in titleList:
        PARAMS = {
        'action': "parse",
        'redirects': 'true',
        'page': title,
        'prop': 'wikitext',
        'format': "json",
        }
        
        res = S.get(url=URL, params=PARAMS)
        data = res.json()
        #if page did not parse successfully, continue
        if 'error' in data:
            continue
        wikitext = data['parse']['wikitext']['*']
        
        seeAlsoIndex = wikitext.find("==See also==")
        if seeAlsoIndex == -1:
            seeAlsoIndex = wikitext.find("== See also ==")
        if seeAlsoIndex == -1:
            continue
        
        refIndex = wikitext.find("== References ==")
        if refIndex == -1:
            refIndex = wikitext.find("==References==")
            
        wikitext = wikitext[seeAlsoIndex:refIndex]

        wikitext = wikitext.split("\n")
        for x in wikitext:
            start = x.find("[[")
            if start == -1:
                continue
                
            end = x.find("|")
            if end == -1:
                end = x.find("]]")
                
            if x[start+2:end] not in seeAlsoList:
                seeAlsoList.append(x[start+2:end])
    print("See also has %d articles" % len(seeAlsoList))
    return seeAlsoList