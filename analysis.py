import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from tqdm import tqdm

# Initialize Firebase
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def fetch_combined_data():
    """Fetch all data in one go with match details included in each commentary entry"""
    print("Fetching combined match and commentary data from Firestore...")
    
    combined_data = []
    matches_ref = db.collection('matches')
    
    # First get all match documents
    matches = {doc.id: doc.to_dict() for doc in matches_ref.stream()}
    
    # Then get all commentary subcollections
    for match_id, match_data in tqdm(matches.items(), desc="Processing matches"):
        commentary_ref = matches_ref.document(match_id).collection('commentary')
        for comm_doc in commentary_ref.stream():
            comm_data = comm_doc.to_dict()
            # Merge match data with commentary
            combined_entry = {
                **match_data,  # All match fields
                **comm_data,   # All commentary fields
                'commentary_id': comm_doc.id  # Keep commentary document ID
            }
            combined_data.append(combined_entry)
    
    return pd.DataFrame(combined_data)

if __name__ == "__main__":
    df = fetch_combined_data()
    print(df.head())