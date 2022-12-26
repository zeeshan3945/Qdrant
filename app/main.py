import os
import random
from io import BytesIO
from PIL import Image
import requests
import base64


print("Which option in the following would you like to use?")
print("1 - Create a new collection")
print("2 - Delete a collection")
print("3 - Add images to collection")
print("4 - Delete image from collection")
print("5 - Search image in the Image Search Vector")
print("6 - Display count of images in the collection")

choice = int(input("Choice: "))


def img_to_byte_stream(img_path):
    buffered = BytesIO()
    img = Image.open(img_path)
    #img.show()
    img.save(buffered, format="JPEG")
    temp_payload = buffered.getvalue()
    payload = base64.b64encode(temp_payload).decode("utf-8")
    return payload


def create_collection(COLLECTION_NAME, vector_size=4096):
    url = "https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/create_index"

    data = {"collection name": COLLECTION_NAME, "vector size": vector_size}
    response = requests.post(url=url, json=data)
    if response.status_code==200:
        return 'Collection successfuly created'
    else:
        return 'Something went wrong'


def delete_collection(COLLECTION_NAME):
    url = "https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/delete_index"

    data = {"collection name": COLLECTION_NAME,}
    response = requests.post(url=url, json=data)
    if response.status_code==200:
        return 'Collection deleted'
    else:
        return 'Something went wrong'


def add_vector_points(dir_name, COLLECTION_NAME):
    url = "https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/add_point"
    # Add images to the collection from your directory. 
    if('.jpg' not in dir_name):
        dir_list = os.listdir(dir_name)
        count=0
        for i in dir_list:
            img_bytes = img_to_byte_stream(dir_name+'/'+i)
            data = {
                "collection name": COLLECTION_NAME,
                "image path": i,
                "img_bytes": img_bytes,
            }
            response = requests.post(url=url, json=data)
            if response.status_code==200:
                print(f"{dir_name+'/'+i} has been added to {COLLECTION_NAME} collection. ({count+1})")
                count+=1
            else:
                return 'Something went wrong'
    else:
        img_bytes = img_to_byte_stream(dir_name)
        data = {
            "collection name": COLLECTION_NAME,
            "image path": dir_name,
            "img_bytes": img_bytes,
        }
        response = requests.post(url=url, json=data)
        if response.status_code==200:
            print(f"{dir_name} has been added to {COLLECTION_NAME} collection.")
        else:
            return 'Something went wrong'
        
        
        
def delete_vector_point(vector_path, COLLECTION_NAME):
    url = "https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/delete_point"
    data = {
        "collection name": COLLECTION_NAME,
        "image path": vector_path,
    }
    response = requests.post(url=url, json=data)
    if response.status_code==200:
        print(f"{vector_path} has been deleted from {COLLECTION_NAME} collection.")
    else:
        return 'Something went wrong'



def search_vector_point(vector_path,COLLECTION_NAME,threshold, offset,limit):
    url = "https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/search"
    img = Image.open(search_img_path)
    img.show()
    payload = img_to_byte_stream(search_img_path)
    data = {
        "collection name": COLLECTION_NAME,
        "payload": payload,
        "limit": limit,
        "offset": offset,
        "threshold": threshold,
    }
    response = requests.post(url=url, json=data)
    if response.status_code==200:
        return response.text
    else:
        return 'Something went wrong'



def vectors_count(COLLECTION_NAME):
    url = "https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/count"
    data = {
        "collection name": COLLECTION_NAME,
    }
    response = requests.post(url=url, json=data)
    if response.status_code==200:
        print(response.text)
    else:
        print(f'"{COLLECTION_NAME}" collection does not exist or Something went wrong')




if __name__ == "__main__":
    
    if(choice==1):
        COLLECTION_NAME = input("Collection Name:")
        response = create_collection(COLLECTION_NAME)
        print(f"Create Collection Function Response: {response}")
        
        
        '''data='{"collection name": "test", "vector size": 4096}'
        curl -X POST https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/create_index -H "Content-Type: application/json" -d "$data"'''


    elif(choice==2):
        COLLECTION_NAME = input("Collection Name:")
        response = delete_collection(COLLECTION_NAME)
        print(f"Delete Collection response: {response}")
        
        
        '''data='{"collection name": "test"}'
        curl -X POST https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/delete_index -H "Content-Type: application/json" -d "$data"'''


    elif(choice==3):
        COLLECTION_NAME = input("Collection Name:")
        dir_name=input("Enter the path of the directory or image: ")
        add_vector_points(dir_name, COLLECTION_NAME)
        
        
        '''data='{"collection name": "test", "image path": path, "img_bytes":img_bytes}'
        curl -X POST https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/add_point -H "Content-Type: application/json" -d "$data"'''
        

    elif(choice==4):
        COLLECTION_NAME = input("Collection Name:")
        delete_image_path=input("Enter the path of the image you want to delete: ")
        delete_vector_point(delete_image_path,COLLECTION_NAME)
        
        
        '''data='{"collection name": "test", "image path": path}'
        curl -X POST https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/delete_point -H "Content-Type: application/json" -d "$data"'''


    elif(choice==5):
        COLLECTION_NAME = input("Collection Name:")
        search_img_path=input("Enter the path of the image you want to search: ")
        limit = int(input("limit: ") or 10)
        offset = int(input("offset: ") or 0)
        threshold = int(input("threshold: ") or 0)
        
        response=search_vector_point(search_img_path, COLLECTION_NAME,threshold,offset,limit)
        
        
        print(f"Search function response: {response}")
        '''data='{"collection name": "test", "payload": payload, "limit":5, "offset":0, "threshold":0}'
        curl -X POST https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/search -H "Content-Type: application/json" -d "$data"'''


    elif(choice==6):
        COLLECTION_NAME = input("Collection Name:")
        vectors_count(COLLECTION_NAME)
        
        
        '''data='{"collection name": "test"}'
        curl -X POST https://mzul3mezie.execute-api.us-west-2.amazonaws.com/Prod/count -H "Content-Type: application/json" -d "$data"'''
        

    else:
        print("Please retry with an correct option")