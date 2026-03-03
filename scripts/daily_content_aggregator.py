"""
Daily Content Aggregator
Runs blog fetcher + knowledge evolver to generate new questions from blogs/papers.
Used by GitHub Actions for automated daily content updates.
"""
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

def run():
    print(f"{'='*60}")
    print(f"Daily Content Aggregator - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    
    # 1. Fetch blogs
    print("\n[1/3] Fetching tech blogs (ByteByteGo, Netflix, Google AI, etc.)...")
    try:
        from data.blog_fetcher import blog_fetcher
        posts = blog_fetcher.get_latest_posts(force_refresh=True)
        total_posts = sum(len(p) for p in posts.values())
        print(f"  Got {total_posts} blog posts from {len(posts)} sources")
        for source, source_posts in posts.items():
            print(f"    {source}: {len(source_posts)} posts")
    except Exception as e:
        print(f"  [ERROR] Blog fetch failed: {e}")
        posts = {}
    
    # 2. Generate questions from blog content
    print("\n[2/3] Generating interview questions from blog content...")
    try:
        from data.knowledge_evolver import knowledge_evolver
        new_q_count = knowledge_evolver.sync_from_blogs()
        print(f"  Generated {new_q_count} new questions")
    except Exception as e:
        print(f"  [ERROR] Question generation failed: {e}")
    
    # 3. Also update hot_papers.json if fetch_hot_papers exists
    print("\n[3/3] Checking for hot papers update...")
    try:
        hot_papers_file = Path(__file__).parent.parent / "data" / "hot_papers.json"
        if hot_papers_file.exists():
            data = json.loads(hot_papers_file.read_text(encoding='utf-8'))
            paper_count = len(data.get("top_papers", []) or data.get("papers", []))
            print(f"  Hot papers file exists with {paper_count} papers")
        else:
            print("  No hot_papers.json found, running fetcher...")
            from scripts.fetch_hot_papers import main as fetch_papers
            fetch_papers()
    except Exception as e:
        print(f"  [ERROR] Papers check failed: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("Daily content aggregation complete!")
    
    # Check totals
    try:
        iq_file = Path(__file__).parent.parent / "data" / "interview_questions.json"
        if iq_file.exists():
            iq_data = json.loads(iq_file.read_text(encoding='utf-8'))
            print(f"  Total interview questions: {len(iq_data.get('questions', []))}")
        
        dq_file = Path(__file__).parent.parent / "data" / "dynamic_question_bank.json"
        if dq_file.exists():
            dq_data = json.loads(dq_file.read_text(encoding='utf-8'))
            total_dq = sum(len(v) for v in dq_data.get("questions", {}).values())
            print(f"  Dynamic question bank: {total_dq}")
        
        blog_cache = Path(__file__).parent.parent / "data" / "blog_cache.json"
        if blog_cache.exists():
            bc_data = json.loads(blog_cache.read_text(encoding='utf-8'))
            total_blogs = sum(len(v) for v in bc_data.get("posts", {}).values() if isinstance(v, list))
            print(f"  Cached blog posts: {total_blogs}")
    except:
        pass
    
    print(f"{'='*60}")


if __name__ == "__main__":
    run()
