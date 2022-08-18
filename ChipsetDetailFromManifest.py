import requests
import json
import argparse
from lxml import etree
from xml.etree import ElementTree
import xmltodict
import os

parser = argparse.ArgumentParser(description="help",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-manifestfile", action="store_true", help="archive mode")
parser.add_argument("manifestfile", help="manifestfilelocation")
args = parser.parse_args()
config = vars(args)

def GetChipsetDetails(BiosId):
    try:
        url = "https://cedcore-dev.azure-api.net/boss-dna-external-uat/api/boss/platform"
        apikey = "MjAxMGNkZmUtYjJhZS00ZTlmLTkyMWItNWJjMWVmNzQ1NDA3"

        headers = {
            'Cache-Control': 'no-cache',
            'ApiKey': apikey,
            'Content-Type': 'application/json'
        }

        page_no = 1

        try:
            while True:
                payload = json.dumps({
                    "pageNo": page_no,
                    "pageSize": 50,
                    "platformNames": [],
                    "vastPlatformNames": [],
                    "marketingModelNames": [],
                    "systemIds": [],
                    "pHs": [],
                    "types": [
                        "1"
                    ]
                })

                response = requests.request("POST", url, headers=headers, data=payload)
                # print(response.text)
                res_data = json.loads(response.text)
                return res_data["data"][0]["generalInfos"][0]["listChipsetGenerationName"]
        except Exception as e:
            return False
    except Exception as e:
        return False

def ParseXMLFiletoDictionary(XMLPath):
    try:
        if os.path.exists(XMLPath):
            # print(f"> Loading XML as JSON from '{XMLPath}'")
            try:
                encoding = etree.parse(XMLPath).docinfo.encoding
            except:
                encoding = ""
            try:
                with open(XMLPath, 'rt') as Filedetails:
                    #encoding = etree.parse(Filedetails).docinfo.encoding
                    xml = ElementTree.tostring(ElementTree.parse(Filedetails).getroot())
                    XMLDictionary=xmltodict.parse(xml, attr_prefix="", cdata_key="#text", dict_constructor=dict)
            except:
                xml = ElementTree.tostring(ElementTree.parse(XMLPath).getroot())
                XMLDictionary=xmltodict.parse(xml, attr_prefix="", cdata_key="#text", dict_constructor=dict)
            '''Json Formated Veiw'''

            #print(json.dumps(XMLDictionary, indent=2))
            XMLDictionary["Encoding"] = encoding
            return XMLDictionary
        else:
            print("Path not found :{}".format(XMLPath))
    except Exception as e:
        print("Failed to Parse XML : {}".format(e))
        return False


def fetch_biosdetails_from_manifest(xml_path):
    try:
        if os.path.exists(xml_path):
            Output_Dictionary = ParseXMLFiletoDictionary(xml_path)
            if Output_Dictionary:
                    Systems = Output_Dictionary["Catalog"]["System"]
                    if type(Systems) is not list:
                        Systems=[Systems]
                    Bios=[]
                    for BiosIds in Systems:
                        Bios.append(GetChipsetDetails(BiosIds['SystemID']))
                    return list(set(Bios))
            else:
                return False
        else:
            return False
    except Exception as e:
        print(e)
        return False

print(fetch_biosdetails_from_manifest(config['manifestfile']))
