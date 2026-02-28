import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from data.supabase_client import is_supabase_configured, learning_store

def run_migration():
    if not is_supabase_configured():
        print("❌ Supabase is not configured. Please add SUPABASE_URL and SUPABASE_KEY to your .env file.")
        return

    print("🚀 Starting data migration from local JSON to Supabase...")
    data_dir = Path("data")

    # 1. Migrate Learning Plans
    plans_file = data_dir / "user_study_plans.json"
    if plans_file.exists():
        print("Migrating Learning Plans...")
        with open(plans_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                plans = data.get("plans", {})
                for user_id, plan in plans.items():
                    success = learning_store.save_user_plan(plan)
                    if success:
                        print(f"  ✅ Migrated plan for user: {user_id}")
                    else:
                        print(f"  ❌ Failed to migrate plan for user: {user_id}")
            except Exception as e:
                print(f"Error reading {plans_file}: {e}")
    else:
        print("No local user_study_plans.json found.")

    # 2. Migrate Daily Learning Profiles
    daily_file = data_dir / "user_daily_plans.json"
    if daily_file.exists():
        print("Migrating Daily Learning Profiles...")
        with open(daily_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                users = data.get("users", {})
                for user_id, udata in users.items():
                    success = learning_store.save_daily_profile(
                        user_id,
                        udata.get("profile", {}),
                        udata.get("progress", {}),
                        udata.get("daily_plans", {})
                    )
                    if success:
                        print(f"  ✅ Migrated daily profile for user: {user_id}")
                    else:
                        print(f"  ❌ Failed to migrate daily profile for user: {user_id}")
            except Exception as e:
                print(f"Error reading {daily_file}: {e}")
    else:
        print("No local user_daily_plans.json found.")

    # 3. Migrate Review Records
    reviews_file = data_dir / "review_records.json"
    if reviews_file.exists():
        print("Migrating Review Records...")
        with open(reviews_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                reviews = data.get("reviews", {})
                for user_id, user_records in reviews.items():
                    success = learning_store.save_review_records(user_id, user_records)
                    if success:
                        print(f"  ✅ Migrated review records for user: {user_id}")
                    else:
                        print(f"  ❌ Failed to migrate review records for user: {user_id}")
            except Exception as e:
                print(f"Error reading {reviews_file}: {e}")
    else:
        print("No local review_records.json found.")

    print("🎉 Migration complete!")

if __name__ == "__main__":
    run_migration()
