import os
import numpy as np
import requests


# Import client library
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import qdrant_client.models as models
from qdrant_client.http.models.models import Filter
from PIL import Image

from embeddings import Embeddings

class Qdrant:
    def __init__(
        self,
        host="localhost", 
        port=6333,
        embeddings = Embeddings()
    ):
        self.client = QdrantClient(host=host, port=port)
        self.host = host
        self.port = port
        self.embeddings = embeddings     

    def create_collection(self, vector_size, collection_name):
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    def upload_to_collection_from_file_path(self, vectors_path, images, collection_name, batch_size=256):
        vectors = np.load(vectors_path)
        payload = self.get_payload(images)
        self.client.upload_collection(
            collection_name=collection_name,
            vectors=vectors,
            payload=payload,
            ids=None,
            batch_size=batch_size,
            parallel=2,
        )

    def upload_to_collection_from_image_stream(self, images, collection_name, batch_size=256):
        points_list = self.embeddings.get_embeddings_across_imgs(images)
        vectors = np.array(points_list)
        payload = self.get_payload(images)
        self.client.upload_collection(
            collection_name=collection_name,
            vectors=vectors,
            payload=payload,
            ids=None,
            batch_size=batch_size,
            parallel=2,
        )
    
    def delete_collection(self, collection_name):
        self.client.delete_collection(collection_name=collection_name)

    def get_collection_count(self, collection_name):
        url = f"http://{self.host}:{self.port}/collections/{collection_name}"
        count = requests.get(url=url).json()['result']['vectors_count']
        return count

    def get_payload(self, img_path):
        payload = {}
        payload["image path"] = img_path
        return payload


    def add_points(self, img_path, img, collection_name, id):
        vector = self.embeddings.get_embedding(img)
        payload = self.get_payload(img_path)
        self.client.upsert(
            collection_name=collection_name,
            points= [
                models.PointStruct(
                id=id,
                payload=payload,
                vector=vector
            ),
         ]
        )

    def retrieve_points(self, collection_name, ids):
        return self.client.retrieve(
    collection_name=collection_name,
    ids=ids,
        )
    
    def delete_points(self, collection_name, points):
        self.client.delete(
    collection_name=collection_name,
    points_selector=models.PointIdsList(
        points=[0, 2],
    ),
)

    def delete_filtered_points(self, collection_name, filter_value):
        self.client.delete(
    collection_name=collection_name,
    points_selector=models.FilterSelector(
        filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="image path",
                    match=models.MatchValue(value=filter_value),
                ),
            ],
        )
    ),
)


    def retrieve_filtered_count(self, collection_name, key, value):
        result = self.client.scroll(
            collection_name=collection_name, 
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key=key, 
                        match=models.MatchValue(value=value)
                    ),
                ]
            ),
            # limit=1,
            # with_payload=True,
        )
        count = len(result[0])
        return count

    def search(self, img, collection_name, limit=5, offset=0, threshold=0, filter: dict = None):
        results = []
        # Convert image into vector
        vector = self.embeddings.get_embedding(img)

        # Use `vector` for search for closest vectors in the collection
        search_result = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            query_filter=Filter(**filter) if filter else None,
            limit=limit+offset,
            score_threshold=threshold*0.1
        )
        # return image paths and corresponding scores
        for result in search_result[offset:]:
            results.append((result.payload['image path'], result.score*10))

        return results


    def filter(self, collection_name, key, value):
        self.client.scroll(
            collection_name=collection_name, 
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key=key, 
                        match=models.MatchValue(value=value),
                    ),
                ]
            ),
        )

#############################################################################################


# img_path = (
#      "/Users/zeeshan/Desktop/Qdrant/Qdrant/test-images/00000146.jpg"
# )
# host = "localhost"
# port = 6333
# COLLECTION_NAME = "images"
# embeddings = Embeddings()
# my_collection = Qdrant(host, port, embeddings)

# my_collection.create_collection(4096, 'images')

# img = Image.open(img_path)
# my_collection.add_points(img_path, img, COLLECTION_NAME, 1001)

# print(my_collection.retrieve_points('images',[1001]))
# img = Image.open(img_path)
# print(my_collection.search(img,'images'))

