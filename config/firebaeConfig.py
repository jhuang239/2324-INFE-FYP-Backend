from firebase_admin import credentials
from firebase_admin import storage, initialize_app

cred = credentials.Certificate("./fyp-file-storage-firebase-adminsdk-ogzdb-3264c14fc4.json")

initialize_app(cred, {'storageBucket': 'fyp-file-storage.appspot.com'})
bucket = storage.bucket()