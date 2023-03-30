import json
import sys
import requests
import time
import configparser
import os.path
from azureworker import post_data
from datetime import datetime, timezone

# Load settings
config = configparser.ConfigParser()
config.read('config.cfg')
# Assign Variables
URL = config.get('DEFAULT','authomizeURL')
token = config.get('DEFAULT','authomizeToken')
customer_id = config.get('DEFAULT','customer_id')
shared_key = config.get('DEFAULT','shared_key')
log_type = config.get('DEFAULT','sentinelLog')
DateFileCFG = config.get('DEFAULT','DateFileCFG')


MyNextPage = ""
currentDate = ""

# Setup the Data for the Search query

def GetJSONData(BooleanValue,nextPage,TheCurrentDateTime):
  if BooleanValue == True:
    JsonData = {
                "filter": {
                  "createdAt": {
                    "$lt": TheCurrentDateTime
                  },
                  "updatedAt": {
                  },
                  "severity": {
                    "$in": [
                      ]  
                  },
                  "status": {
                    "$in": [
                      "Open"
                      ]
                  },
                  "isResolved": {
                    "$eq": False
                  }
                },
                "pagination": {
                  "nextPage": nextPage,
                  "limit": 10
                },
                "expand": [
                  "policy"
                ],
                "sort": [
                  {
                    "fieldName": "createdAt",
                    "order": "DESC"
                  }
                ]
              }
  else:
    JsonData = {
              "filter": {
                "createdAt": {
                  "$gte": TheCurrentDateTime
                },
                "updatedAt": {
                },
                "severity": {
                  "$in": [
                    ]  
                },
                "status": {
                  "$in": [
                    "Open"
                    ]
                },
                "isResolved": {
                  "$eq": False
                }
              },
              "pagination": {
                "nextPage": nextPage,
                "limit": 10
              },
              "expand": [
                "policy"
              ],
              "sort": [
                {
                  "fieldName": "createdAt",
                  "order": "DESC"
                }
              ]
            }    
    
  return JsonData
    

def DateInZulu(currentDate):
  currentDate = datetime.now(timezone.utc).isoformat()
  return(currentDate)


def CheckFileExists(FileExistStatus):
  if os.path.exists(DateFileCFG):
    FileExistStatus = False
  else:
    FileExistStatus = True
  return bool(FileExistStatus)
    
def WriteFileContent(FileContent):
  f = open(DateFileCFG, "w")
  f.write(FileContent)
  f.close()
   
def ReadFileContent():
  f = open(DateFileCFG, "r")
  line = f.read()
  return line

def searchIncident():
  
    TheCurrentDateTime = DateInZulu(currentDate)
    FileState = CheckFileExists(True)

    if FileState:
      WriteFileContent(TheCurrentDateTime)
      JsonData = GetJSONData(FileState,'',TheCurrentDateTime)
      theData = json.dumps(JsonData)
    else:
      TheTime = ReadFileContent()
      TheCurrentDateTime = TheTime
      JsonData = GetJSONData(FileState,'',TheCurrentDateTime)
      theData = json.dumps(JsonData)

    theheaders = {
        'Authorization': token,
        'Content-Type': 'application/json'
        }
 
    # Enter while hasMore data
    hasMore = True
    # Setup for pulling data until hasMore is False 
    while hasMore:
      response = requests.post(url=URL,data=theData, headers=theheaders)      
      theresponse = response
      
      if (response.status_code >= 200 and response.status_code <= 299):
          getJSONdump = json.dumps(theresponse.json(), indent=2)
          jsonObj = json.loads(getJSONdump)
          
          # Lets test to see if there is any returned data
          if jsonObj['pagination']['hasMore'] == True:
            
            # Just for readability listing the hasMore field
            print("Has more data: ", jsonObj['pagination']['hasMore'])
            
            #access elements in the object
            limit = jsonObj['pagination']['limit']
            nextPage = jsonObj['pagination']['nextPage']
            # Not needed as we set the loop with True - Grab it only when its False
            # hasMore = jsonObj['pagination']['hasMore']
            
            #get the data from the object to send to Sentinel
            myAzureData = jsonObj['data']
            print("---",limit,"|", nextPage,"|", hasMore, "---")
            
            if myAzureData != []:
              body = json.dumps(myAzureData)
              # This sends to Azure (calls over to function in azureworker)
              post_data(customer_id, shared_key, body, log_type)
              # print(body)
            else:
              print("Empty Data String!!!")

            # Setup the request with new JSON data
            JsonData = GetJSONData(FileState,nextPage,TheCurrentDateTime)
            theData = json.dumps(JsonData)

            if hasMore == False:
              TheCurrentDateTime = DateInZulu(currentDate)
              WriteFileContent(TheCurrentDateTime)
          else:
            # hasMore is False so end the while loop and do nothing more
            # Data payload will be empty
            print("Checking if any more data as pagination has ended - hasMore returned: ", jsonObj['pagination']['hasMore'])
            hasMore = jsonObj['pagination']['hasMore']
            # print(jsonObj)
            # Try and get some data
            IfDataHere = jsonObj['data']
            
            # If no more data then we'll do nothing else we will send the last of the data
            if IfDataHere != []:
              print("Sending last bit of data...")
              body = json.dumps(IfDataHere)
              # This sends to Azure (calls over to function in azureworker)
              post_data(customer_id, shared_key, body, log_type)
              # print(body)
            else:
              print("empty data string not sending anything...")
            
            print("---------This is the end check above results---------")
            
            #This finishes the work
      else:
          print("Response code: {}".format(response.status_code))

searchIncident()