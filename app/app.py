from flask_lambda import FlaskLambda
from flask import Flask, request
from PIL import Image
from io import BytesIO
from qdrant import Qdrant
from embeddings import Embeddings
import base64
import random
#
# from aws_lambda_wsgi import response

# def lambda_handler(event, context):
#     if 'httpMethod' not in event:
#         # If not, set the 'httpMethod' key to 'GET'
#         event['httpMethod'] = 'POST'

#     return response(app, event, context)

#app = FlaskLambda(__name__)

app = FlaskLambda(__name__)

host = "35.78.139.182"
port = 6333

embeddings = Embeddings()
collection = Qdrant(host, port, embeddings)


@app.route("/hello")
def hello():
    return "Hello from get"

@app.route("/hi", methods=["POST"])
def hi():
    return "Hi from Post"


@app.route("/create_index", methods=["POST"])
def create_index():
    data = request.json
    index_name = data["collection name"]
    vector_size = data["vector size"]
    result = collection.create_collection(vector_size, index_name)
    return f'"{data}" has been successfully created'


@app.route("/delete_index", methods=["POST"])
def delete_index():
    data = request.json
    index_name = data["collection name"]
    collection.delete_collection(index_name)
    return f'"{data}" has been successfully deleted'


@app.route("/add_point", methods=["POST"])
def add_point():
    data = request.json
    index_name = data["collection name"]
    img_path = data["image path"]
    img_utf = data["img_bytes"]
    img_bytes = bytes(img_utf, "utf-8")
    img_decoded = base64.b64decode(img_bytes)
    img = Image.open(BytesIO(img_decoded))
    id = random.getrandbits(64)
    #id=11334160272865621853
    try:
        collection.add_points(img_path, img, index_name, id)
        return img_path
    except:
        return f'"{index_name}" collection does not exist or Something went wrong'


@app.route("/delete_point", methods=["POST"])
def delete_point():
    data = request.json
    index_name = data["collection name"]
    img_path = data["image path"]
    try:
        collection.delete_filtered_points(index_name, img_path)
        return img_path
    except:
        return f'"{index_name}" collection does not exist or Something went wrong'


@app.route("/search", methods=["POST"])  # Search function using post (pass the image path in requests.post)
def search():
    data = request.json
    collection_name = data["collection name"]
    img_utf = data["payload"]
    limit=data['limit']
    offset=data['offset']
    threshold=data['threshold']
    img_bytes = bytes(img_utf, "utf-8")
    img_decoded = base64.b64decode(img_bytes)
    search_img_path = Image.open(BytesIO(img_decoded))
    try:
        results = collection.search(
            search_img_path, collection_name, limit=limit, offset=offset, threshold=threshold
        )
        return f"{results}"
    except:
        return f'"{collection_name}" collection does not exist or Something went wrong'


@app.route("/count", methods=["POST"])
def count():
    data = request.json
    collection_name = data["collection name"]
    try:
        vector_count = collection.get_collection_count(collection_name)
        return f"count of vectors in {collection_name}: {vector_count}"
    except:
        return f'"{collection_name}" collection does not exist or Something went wrong'


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
