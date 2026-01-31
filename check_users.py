import os
os.chdir('d:/Interview')
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
result = client.table('users').select('*').execute()

print(f"Total users: {len(result.data)}")
print("-" * 40)
for i, u in enumerate(result.data):
    print(f"{i+1}. Username: {u.get('username')}")
    print(f"   Points: {u.get('points')}, Level: {u.get('level')}")
    print(f"   Joined: {u.get('joined_at')}")
    print()
