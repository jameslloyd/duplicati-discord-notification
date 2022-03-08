from pymongo import MongoClient
from google.cloud import secretmanager

def access_secret_version(secret_id, PROJECT_ID, version_id="latest"):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()
    # Build the resource name of the secret version.
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    # Access the secret version.
    response = client.access_secret_version(name=name)
    # Return the decoded payload.
    return response.payload.data.decode('UTF-8')

PROJECTID = 'duplicati-notifications'
client = MongoClient(access_secret_version('mongodburl',PROJECTID))
db = client.duplicati
collection = db.duplicati

myquery = {"name": "Home_Backup_to_BackBlaze"}
newvalues = {"$set": {"name":"Home_Backup_to_Backblaze"}}
x = collection.update_many(myquery, newvalues)

print(x.modified_count, "documents updated.")