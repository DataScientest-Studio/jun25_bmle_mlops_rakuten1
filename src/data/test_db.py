from pymongo import MongoClient
import os

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_ADMIN_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_ADMIN_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "changeme")
MONGO_DB_NAME = os.getenv("MONGO_INITDB_DATABASE", "mlops_rakuten")

print("Host : ", MONGO_HOST)
print("Port : ", MONGO_PORT)
print("User : ", MONGO_ADMIN_USER)
print("Password : ", MONGO_ADMIN_PASSWORD)
print("DB Name : ", MONGO_DB_NAME)

print("Connecting to MongoDB...")
connection_string = f"mongodb://{MONGO_ADMIN_USER}:{MONGO_ADMIN_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/admin"
client = MongoClient(connection_string)
print("Connected.")
databases = client.list_database_names()
print("Databases available:")
print(databases)
db = client[MONGO_DB_NAME]

collections = db.list_collection_names()
print("Collections in database:")
print(collections)

