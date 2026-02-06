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
        "yasmin": "supporter",
        "dazbo": "supporter"
    }

    print("Seeding persona_tiers collection...")
    for persona_id, required_role in persona_tiers.items():
        doc_ref = db.collection("persona_tiers").document(persona_id)
        doc_ref.set({"required_role": required_role})
        print(f"  Set {persona_id} -> {required_role}")

    # 2. Seed users (for testing)
    # We'll seed the current user as a supporter for testing
    # In a real app, users would be created during signup/login
    users = [
        {"id": "derailed-dash", "role": "supporter"}, # GitHub handle from GEMINI.md
        {"id": "test-standard-user", "role": "standard"}
    ]

    print("\nSeeding users collection...")
    for user in users:
        doc_ref = db.collection("users").document(user["id"])
        doc_ref.set({"role": user["role"]})
        print(f"  Set user {user['id']} -> {user['role']}")

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
