import argparse
import os

import google.auth
from google.cloud import firestore


def seed_firestore(project_id):
    db = firestore.Client(project=project_id)

    # 1. Seed persona_tiers
    # Standard: Rick, Yoda, Donald, Jack
    # Supporter: Yasmin, Dazbo
    persona_tiers = {
        "rick": "standard",
        "yoda": "standard",
        "donald": "standard",
        "jack": "standard",
        "yasmin": "standard",
        "dazbo": "supporter"
    }

    print("Seeding persona_tiers collection...")
    for persona_id, required_role in persona_tiers.items():
        doc_ref = db.collection("persona_tiers").document(persona_id)
        doc_ref.set({"required_role": required_role})
        print(f"  Set {persona_id} -> {required_role}")

    # 2. Seed users (for testing)
    # Using readable document ID format: {name}:{provider}:{id}
    users = [
        {
            "id": "derailed-dash",
            "provider": "github",
            "name": "Dazbo",
            "role": "supporter",
            "email": "dazbo@example.com"
        },
        {
            "id": "837482910475839201847",
            "provider": "google",
            "name": "Darren Lester",
            "role": "supporter",
            "email": "dazbo@google.com"
        },
        {
            "id": "test-standard-user",
            "provider": "mock",
            "name": "StandardUser",
            "role": "standard",
            "email": "standard@example.com"
        }
    ]

    print("\nSeeding users collection...")
    for user in users:
        safe_name = "".join(c for c in user["name"] if c.isalnum()) or f"user-{user['id'][:8]}"
        doc_id = f"{safe_name}:{user['provider']}:{user['id']}"
        doc_ref = db.collection("users").document(doc_id)
        doc_ref.set({
            "id": user["id"],
            "provider": user["provider"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "last_logged_in": firestore.SERVER_TIMESTAMP
        })
        print(f"  Set user doc {doc_id} -> {user['role']}")

    print("\nFirestore seeding complete.")

if __name__ == "__main__":
    _, default_project_id = google.auth.default()
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", default_project_id)

    parser = argparse.ArgumentParser(description="Seed Firestore with persona tiers and test users.")
    parser.add_argument("--project", default=project_id, help="Google Cloud Project ID")
    args = parser.parse_args()

    if not args.project:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable not set and --project not provided.")
        exit(1)

    seed_firestore(args.project)
