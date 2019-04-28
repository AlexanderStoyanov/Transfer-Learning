def makeLabels(trainData, labelNumber):
    #generating labels list that matches pageContent list in length
    labels = []
    for x in range(0, len(trainData)):
        labels.append(labelNumber)
    print("Labels made successfully")
    return labels