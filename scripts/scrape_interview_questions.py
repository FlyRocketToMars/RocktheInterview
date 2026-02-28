import json
import uuid
import requests
from pathlib import Path
from datetime import datetime

# Target sources: Reddit JSON APIs for public data
SOURCES = [
    "https://www.reddit.com/r/cscareerquestions/search.json?q=MLE+interview+experience&restrict_sr=1&sort=new",
    "https://www.reddit.com/r/MachineLearning/search.json?q=interview+questions&restrict_sr=1&sort=new"
]

COMPANIES = [
    "Google", "Meta", "Amazon", "Apple", "Netflix", 
    "Snap", "ByteDance", "Tiktok", "OpenAI", 
    "Anthropic", "Tesla", "Nvidia", "Microsoft"
]

def extract_company(text):
    """Simple extraction to guess company from text."""
    for company in COMPANIES:
        if company.lower() in text.lower():
            return "ByteDance" if company.lower() == "tiktok" else company
    return "Community"

def scrape_questions():
    """Fetch new interview questions from community forums."""
    new_questions = []
    
    # Needs a generic user-agent to bypass basic Reddit JSON blocks
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for url in SOURCES:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])
                
                # Process the top recent relevant results
                for post in posts[:15]: 
                    post_data = post.get('data', {})
                    title = post_data.get('title', '')
                    selftext = post_data.get('selftext', '')
                    author = post_data.get('author', 'anonymous')
                    
                    text_lower = title.lower() + " " + selftext.lower()
                    # Filter for MLE/AI related interviews
                    if 'interview' in text_lower and ('mle' in text_lower or 'machine learning' in text_lower or 'ai' in text_lower):
                        
                        # Only grab substantive posts
                        if len(selftext) > 200:
                            company = extract_company(title + " " + selftext)
                            
                            question_id = f"auto_{str(uuid.uuid4())[:8]}"
                            snippet = selftext[:600] + "...\n\n[View Full Source on Reddit]"
                            
                            question_entry = {
                                "id": question_id,
                                "company": company,
                                "role": "MLE",
                                "level": "Unknown",
                                "round": "behavioral" if "behavioral" in text_lower else "ml_theory",
                                "domain": "fundamentals",
                                "question": f"[Auto-Scraped] {title}",
                                "answer": [snippet, f"Source Author: u/{author}"],
                                "follow_ups": [],
                                "difficulty": "medium",
                                "frequency": 1,
                                "importance": 3,
                                "tags": ["community-scraped", "reddit", author],
                                "common_mistakes": [],
                                "year": datetime.now().year
                            }
                            new_questions.append(question_entry)
            else:
                print(f"Failed to fetch {url}: {response.status_code}")
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            
    return new_questions

def update_json_file(new_questions):
    if not new_questions:
        print("No new questions found today.")
        return
        
    json_path = Path(__file__).parent.parent / "data" / "interview_questions.json"
    
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # Fallback
        data = {"categories": {}, "metadata": {}, "questions": []}
        
    # Prevent exact duplicates by title/question
    existing_titles = set(q['question'] for q in data.get('questions', []))
    
    added_count = 0
    for nq in new_questions:
        if nq['question'] not in existing_titles:
            # Insert Auto-scraped at the beginning for visibility
            data['questions'].insert(0, nq)
            existing_titles.add(nq['question'])
            added_count += 1
            
    if added_count > 0:
        if 'metadata' in data:
            data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            data['metadata']['total_questions'] = len(data.get('questions', []))
            
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully added {added_count} new questions.")
    else:
        print("No new unique questions to add.")

if __name__ == "__main__":
    print("Starting daily interview question scraper...")
    new_qs = scrape_questions()
    update_json_file(new_qs)
    print("Scraping complete.")
