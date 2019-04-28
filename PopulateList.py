def populateList(filename, keyword, limit=10000, notClassList=True):
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