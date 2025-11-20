import io
import os
from PIL import Image

from src.mongodb.conf_loader import MongoConfLoader
from src.mongodb.utils import MongoUtils

import torch
from torchvision import models


resnet50 = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
output_file = os.path.join("models", "resnet50-weights.pth")

torch.save(resnet50.state_dict(), output_file)

"""
conf_loader = MongoConfLoader()
with MongoUtils(conf_loader=conf_loader) as mongo:
    X_test_cleaned = mongo.db["X_test_cleaned"]
    print("Taille de la collection X_test_cleaned :", X_test_cleaned.count_documents({}))
    result = X_test_cleaned.aggregate([{"$sample": {"size": 5}}])
    for doc in result:
        print("Document ID:", doc["id"])
        #        print("prdtypecode:", doc["prdtypecode"])
        print("Designation:", doc["designation"])
        print("Description:", doc["description"][:100], "...")
        img_bytes = doc["image_binary"]
        img_byte_arr = io.BytesIO(img_bytes)
        img = Image.open(img_byte_arr)
        img.show()
"""
