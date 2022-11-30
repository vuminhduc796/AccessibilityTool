import collections

import xmltodict
import glob
import json
import os
import sys


def addLinkToDict(schemeName, activityName, linkCount, thisDict, pkName, action):
    deeplinks = 'deeplinks'
    params = 'params'
    if activityName in thisDict[pkName].keys():
        thisDict[pkName][activityName].get(deeplinks).append(
            [schemeName + '://' + activityName + str(linkCount), action])
    else:
        item = {deeplinks: [[schemeName + '://' + activityName + str(linkCount), action]], params: []}
        thisDict[pkName][activityName] = item
    return thisDict

def addLink(scheme, host, prefix, activityName, thisDict):

    newLink = {
                "scheme": scheme,
                "host": host,
                "pathPrefix": prefix,
                "action": "android.intent.action.VIEW"
            }
    if activityName in thisDict.keys():
        thisDict[activityName].append(newLink)
    else:
        thisDict[activityName] = [newLink]
    return thisDict

def addComponent(activityName, thisDict, pkName, action, category):
    newComponent = {
                "component": pkName + "/" + activityName,
                "action": action,
                "category": category
            }
    if activityName in thisDict.keys():
        thisDict[activityName].append(newComponent)
    else:
        thisDict[activityName] = [newComponent]
    return thisDict
def extractComponent(currentIntentFilter, activityName, pkName, thisDict):
    categories = []
    # skip if no action
    if 'action' not in currentIntentFilter.keys():
        return
    if 'category' in currentIntentFilter.keys():

        if type(currentIntentFilter['category']) == list:

            for j in range(0, len(currentIntentFilter['category'])):
                currentCategory = currentIntentFilter['category'][j]
                categories.append(currentCategory["@android:name"])
        else:
            categories.append(currentIntentFilter['category']["@android:name"])
    # components
    if type(currentIntentFilter['action']) == list:
        for ac in currentIntentFilter['action']:
            # actions.append(ac['@android:name'])
            for category in categories:
                thisDict = addComponent(activityName, thisDict, pkName, ac['@android:name'], category)
    else:
        for category in categories:
            thisDict = addComponent(activityName, thisDict, pkName, currentIntentFilter['action']['@android:name'], category)

    return thisDict

def extractLink(dataField, thisDict, activityName):
    if type(dataField) == list:
        schemeList = []
        hostList = []
        prefixList = [""]
        for field in dataField:
            if '@android:scheme' in field and field['@android:scheme'] not in schemeList:
                schemeList.append(field['@android:scheme'])
            if '@android:host' in field and field['@android:host'] not in hostList:
                hostList.append(field['@android:host'])
            if '@android:path' in field and field['@android:path'] not in prefixList:
                prefixList.append(field['@android:path'])
            if '@android:pathPrefix' in field and field['@android:pathPrefix'] not in prefixList:
                prefixList.append(field['@android:pathPrefix'])

        for scheme in schemeList:
            for host in hostList:
                for prefix in prefixList:
                    thisDict = addLink(scheme, host, prefix, activityName, thisDict)

    elif '@android:host' in dataField:
        deeplink = {'@android:host': dataField['@android:host'], '@android:path': "", '@android:scheme': ""}
        if '@android:scheme' in dataField:
            deeplink['@android:scheme'] = dataField['@android:scheme']
        if '@android:path' in dataField:
            deeplink['@android:path'] = dataField['@android:path']
        elif '@android:pathPrefix' in dataField:
            deeplink['@android:path'] = dataField['@android:pathPrefix']
        thisDict = addLink(deeplink['@android:scheme'], deeplink['@android:host'], deeplink['@android:path'],
                           activityName, thisDict)

    return thisDict

def extractIntent(folderName, deeplinks=r'deeplinks.json'):
    # get packageName
    xmlDir = os.path.join(folderName, 'AndroidManifest.xml')

    try:
        with open(xmlDir, 'r') as fd:
            doc = xmltodict.parse(fd.read())
            pkName = doc['manifest']['@package']
            thisDict = {}

            # get activity
            schemeName = pkName.replace('.', '_')
            initialExported = False
            if 'exported' in doc['manifest']['application'].keys() and doc['manifest']['application']['exported'] == "true":
                initialExported = True
            if 'activity' in doc['manifest']['application'].keys():
                for activity in doc['manifest']['application']['activity']:
                    isActivityExported = initialExported
                    if '@android:exported' in activity and activity['@android:exported'] == "true":
                        isActivityExported = True

                    activityName = activity['@android:name']
                    # start inject
                    if 'intent-filter' in activity.keys():

                        if type(activity['intent-filter']) == list:
                            for i in range(0, len(activity['intent-filter'])):
                                currentIntentFilter = activity['intent-filter'][i]
                                if isActivityExported:
                                    thisDict = extractComponent(currentIntentFilter, activityName, pkName, thisDict)
                                # deep link
                                if 'data' in currentIntentFilter.keys():
                                    dataField = currentIntentFilter['data']
                                    thisDict = extractLink(dataField,thisDict,activityName)

                        else:
                            if isActivityExported:
                                thisDict = extractComponent(activity['intent-filter'], activityName, pkName, thisDict)

                            if 'data' in activity['intent-filter'].keys():
                                dataField = activity['intent-filter']['data']
                                thisDict = extractLink(dataField,thisDict,activityName)


    except FileNotFoundError as e:
        print(e)
        return
    except TypeError as e:
        print(e)
        return
    except KeyError as e:
        print(e)
        return e

    print(thisDict)

    with open(deeplinks, 'w') as fd:
        print("dsds")
        json.dump( thisDict, fd, indent=4)

def extractDeepLinkField():
    pass

if __name__ == '__main__':
    # get sys args
    args = sys.argv
    # folderName = args[1]
    folderName = r'/Users/hhuu0025/PycharmProjects/uiautomator2/activityMining/data/ess_41_reflexis_one_v4.1..apk'
    # folderName = 'Amazon Prime Video by Amazon Mobile LLC - com.amazon.avod.thirdpartyclient'
    deeplinks = r'data/ebay/deeplinks.json'
    extractIntent(folderName, deeplinks)
