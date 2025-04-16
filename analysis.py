import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def fetch_firebase_data():
    """Fetch matches and commentary data from Firestore"""
    print("Fetching data from Firestore...")
    
    # Get all matches
    matches_ref = db.collection('matches')
    matches = []
    for doc in matches_ref.stream():
        match_data = doc.to_dict()
        match_data['doc_id'] = doc.id  # Add document ID
        matches.append(match_data)
    matches_df = pd.DataFrame(matches)
    
    # Get all commentary (assuming it's a top-level collection)
    commentary_ref = db.collection('commentary')
    commentary = [doc.to_dict() for doc in commentary_ref.stream()]
    commentary_df = pd.DataFrame(commentary)
    
    return matches_df, commentary_df

if __name__ == "__main__":
    matches_df, commentary_df = fetch_firebase_data()
    
    print("\nMatches DataFrame:")
    print(matches_df.head())
    print("\nCommentary DataFrame:")
    print(commentary_df.head())