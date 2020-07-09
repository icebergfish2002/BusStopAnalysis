import arcpy, csv
arcpy.env.workspace = r''
arcpy.env.overwriteOutput = True


# buffer geometry and add to a dictionary
aQuery = '"NAME" = \'71 IB\' AND "BUS_SIGNAG" = \'Ferry Plaza\''
dataDict = {}
with arcpy.da.SearchCursor('Bus_Stops', ['NAME', 'STOPID', 'SHAPE@'], aQuery) as aCursor:
    for aRow in aCursor:
        stopid = aRow[1]
        dataDict[stopid] = aRow[2].buffer(400), aRow[0]

# Intersect census blocks and bus stop buffers
processedDataDict = {}
for i in dataDict.keys():
    blocksIntersected = []
    with arcpy.da.SearchCursor('CensusBlocks2010', ['BLOCKID10', 'POP10', 'SHAPE@']) as aCursor:
        for aRow in aCursor:
            if dataDict[i][0].overlaps(aRow[2]) == True:
                interPoly = dataDict[i][0].intersect(aRow[2], 4)
                data = aRow[0], aRow[1], interPoly, aRow[2]
                blocksIntersected.append(data)
    processedDataDict[i] = dataDict[stopid], blocksIntersected

# Create an average population for each bus stop 
dataList = []
for stopid in processedDataDict.keys():
    allValues = processedDataDict[stopid]
    popValues = []
    blocksIntersected = allValues[1]
    for blocks in blocksIntersected:
        pop = blocks[1]
        totalArea = blocks[-1].area
        interArea = blocks[-2].area
        finalPop = pop * (interArea/totalArea)
        popValues.append(finalPop)
    averagePop = round(sum(popValues)/len(popValues),2)
    busStopLine = allValues[0][1]
    busStopID = stopid
    finalData = busStopLine, busStopID, averagePop
    dataList.append(finalData)
