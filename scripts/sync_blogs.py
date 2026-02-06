"""
Manual sync script to fetch latest blogs and update question bank
Run this periodically or set up as a cron job
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.knowledge_evolver import knowledge_evolver

def sync_blogs():
    """Sync latest blog posts and generate questions."""
    print("🔄 Starting blog sync...")
    print("=" * 60)
    
    try:
        new_count = knowledge_evolver.sync_from_blogs()
        print(f"\n✅ Sync complete! Generated {new_count} new questions.")
        
        # Show latest questions
        print("\n📚 Latest questions in bank:")
        print("-" * 60)
        latest = knowledge_evolver.get_latest_questions(limit=10)
        for i, q in enumerate(latest, 1):
            print(f"\n{i}. [{q.get('type')}] {q.get('title')}")
            print(f"   Source: {q.get('source', 'Unknown')}")
            print(f"   Added: {q.get('added_at', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sync_blogs()
