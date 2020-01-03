#This module downloads files from a shared google drive folder

# !/usr/bin/python
from __future__ import print_function

import os
#import os.path
import re
import shutil
import sys
import tempfile
import requests
import six
import tqdm


def download_file_from_google_drive(id, destination, URL):
    session = requests.Session()
    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)
        
    #if not os.path.isfile(destination):
    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                
                
def check_nature(destination):
    myFile=open(destination)
    contents=myFile.read()
    myFile.close()
    for i,line in enumerate(contents.splitlines()):
        i=i+1
        if i> 9:
            return False
    return True
    
def is_drive_folder(source):
    statinfo = os.stat(source)
    if statinfo.st_size > 141:
        return False
    return True
    
def id_extractor(source,id_list):
    myFile=open(source, "r")
    contents=myFile.read()
    myFile.close()   
    lines=contents.splitlines()    
    for line in lines:
        #iterate for each found item
        for m in re.finditer(r"\\x5b\\x22", line):  #look for a pattern that comes before the id of the url 
            #get the id of the item
            item_id=line[m.end():m.end()+33]
            #get the name of the item
            n=re.search(r"\\x22\\x5d\\n,\\x22", line[m.end():])      
            if n!= None:
                o=re.search(r"\\x22,\\x22", line[m.end()+n.end():])
                if o!= None:
                    item_name=line[m.end()+n.end():m.end()+n.end()+o.start()] 
                    flag=False
                    for iterator in id_list:
                        if item_name in iterator:
                            flag=True
                    if not flag:
                        id_list.append([item_name,item_id])
    
if __name__ == '__main__':
    if len(sys.argv) < 2: 
        item_id=input("The id for the main folder ?")
    elif(sys.argv) == 2: 
        item_id=sys.argv[1]      
    else:  
        #sortie avec code d'erreur different de 0
        item_id='' #one needs to select drive folder ID Here
        sys.exit(10)
    
    count=0
    liste=[]
    identifiers=[]
    # create the session
    session = requests.Session()
    #set the first item which is url for the base folder
    if not os.path.isfile("dat.txt"):
        myFile= open("dat.txt","w+")
        myFile.write("%s;/;"% "base folder.temp")
        myFile.write("%s\n"% item_id)
        myFile.close()   
        
    myFile= open("dat.txt","r")
    content=myFile.read()
    myFile.close()
    
    lines=content.splitlines()   
    for line in lines:
        item=line.split(";/;")
        liste.append(item)
        
    while count < len(liste):   
        item_id=liste[count][1] 
        destination=liste[count][0]
        #set the link type then dowload the file/folder
        URL = 'https://docs.google.com/uc?export=download' # or "https://drive.google.com/uc?export=download" to download
         	
        print('Downloading file',destination)
        download_file_from_google_drive(item_id, destination, URL)
        
        if is_drive_folder(destination):
            URL = 'https://drive.google.com/open?' 
            download_file_from_google_drive(item_id, destination, URL)
            
            id_extractor(destination,liste)
            os.remove(destination)
            print("File ",destination," Removed!")            
        destination = liste[count][0]     #'image'+str(count)+'.jpg' 
        count=count+1 
    f= open("dat.txt","w+")
    for element in liste:
        f.write("%s;/;"% element[0])
        f.write("%s\n"% element[1])
    f.close()   

