from google.cloud import firestore
import google.auth
import os

def check_firestore():
    _, project_id = google.auth.default()
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", project_id)
    db = firestore.Client(project=project_id)

    print(f"Checking project: {project_id}")
    
    print("\nPersona Tiers:")
    docs = db.collection("persona_tiers").stream()
    for doc in docs:
        print(f"  {doc.id}: {doc.to_dict()}")

    print("\nUsers:")
    docs = db.collection("users").stream()
    for doc in docs:
        print(f"  {doc.id}: {doc.to_dict()}")

if __name__ == "__main__":
    check_firestore()