import json
import uuid
import os
import time
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
import google.generativeai as genai

# Set up your Gemini API key as an environment variable (or hardcode here for local testing)
api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# Target URLs for Playwright
# We'll simulate fetching from a public forum using headless Chromium.
# For production 1point3acres/Blind or gated sites, you would inject tokens or cookies here.
TARGET_URLS = [
    {"url": "https://old.reddit.com/r/cscareerquestions/search?q=MLE+interview+experience&restrict_sr=on&sort=new", "source": "Reddit (cscareerquestions)"},
    {"url": "https://old.reddit.com/r/MachineLearning/search?q=interview+questions&restrict_sr=on&sort=new", "source": "Reddit (MachineLearning)"}
    # Future additions (requires authentication/cookies handled manually):
    # {"url": "https://www.1point3acres.com/bbs/forum-145-1.html", "source": "1point3acres"}
    # {"url": "https://www.teamblind.com/topics/Interviews", "source": "Blind"}
]

def parse_slang_and_structure_with_llm(raw_text, source_name, author="anonymous"):
    """
    Uses an LLM to deeply understand unstructured text, translate Chinese slang 
    ("狗家" -> Google, "麻" -> Amazon, "脸/meta" -> Meta), and format it into our strict JSON schema.
    """
    if not api_key:
        # Fallback if no LLM key is configured
        print("No GEMINI_API_KEY found. Falling back to simple heuristic extraction.")
        return simple_fallback_extraction(raw_text, source_name, author)

    system_prompt = """
    You are an expert technical interviewer and data extractor. You are analyzing community forum posts (often containing Chinese/English slang) about technical interviews.
    Your job is to extract the details and return them EXCLUSIVELY as a valid JSON object matching the exact schema below. Do not output markdown, do not output reasoning, only the JSON. 
    
    Slang mapping:
    - 狗家 / 狗厂 -> Google
    - 麻厂 / 亚麻 -> Amazon
    - 脸 / 脸家 -> Meta
    - 软 / 巨硬 -> Microsoft
    - 字节 / 抖 -> ByteDance
    - 果 / 苹果 -> Apple
    - O家 -> OpenAI
    - 虾皮 -> Shopee
    
    Target Schema:
    {
      "company": "Company Name (Standardized)",
      "role": "MLE or SWE etc",
      "level": "L3, L4, L5, E4, E5, Staff, etc (or 'Unknown')",
      "round": "phone_screen, coding, ml_coding, ml_theory, system_design, ml_system_design, behavioral",
      "domain": "fundamentals, deep_learning, nlp, cv, recsys, ranking, llm, mlops, or experimentation",
      "question": "A concise, technical summary of the actual interview question(s) asked",
      "answer": [
        "Provide a technical, structured answer/guide based on best practices for this question (3-5 succinct points). Do NOT just copy the user's rant if it's wrong.",
        "Include the original snippet context at the end."
      ],
      "follow_ups": ["Likely follow-up question 1", "Likely follow-up question 2"],
      "difficulty": "easy, medium, or hard",
      "tags": ["extracted_tag_1", "extracted_tag_2"]
    }
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        full_prompt = f"{system_prompt}\n\nTask:\nExtract the interview data from the following post:\n\n{raw_text}"
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.2,
            )
        )
        result_content = response.text.strip()
        
        # Clean up if the LLM wraps it in markdown code blocks
        if result_content.startswith("```json"):
            result_content = result_content[7:]
        if result_content.endswith("```"):
            result_content = result_content[:-3]
            
        json_data = json.loads(result_content.strip())
        
        # Hydrate necessary metadata
        json_data["id"] = f"auto_llm_{str(uuid.uuid4())[:8]}"
        json_data["tags"] = json_data.get("tags", []) + ["llm-processed", source_name, author]
        json_data["frequency"] = 1
        json_data["importance"] = 4
        json_data["common_mistakes"] = []
        json_data["year"] = datetime.now().year
        
        return json_data
        
    except Exception as e:
        print(f"LLM Parsing failed: {e}")
        return simple_fallback_extraction(raw_text, source_name, author)

def simple_fallback_extraction(raw_text, source_name, author):
    """Fallback if LLM API fails or isn't set."""
    company = "Community"
    companies = ["Google", "Meta", "Amazon", "Apple", "Netflix", "Snap", "ByteDance", "OpenAI"]
    for c in companies:
        if c.lower() in raw_text.lower():
            company = c
            break
            
    snippet = raw_text[:600] + f"...\n\n[View Full Source on {source_name}]"
    
    return {
        "id": f"auto_{str(uuid.uuid4())[:8]}",
        "company": company,
        "role": "MLE",
        "level": "Unknown",
        "round": "ml_theory",
        "domain": "fundamentals",
        "question": f"[{source_name}] Community Question",
        "answer": [snippet, f"Source Author: {author}"],
        "follow_ups": [],
        "difficulty": "medium",
        "frequency": 1,
        "importance": 3,
        "tags": ["community-scraped", source_name, author],
        "common_mistakes": [],
        "year": datetime.now().year
    }

def scrape_with_playwright():
    """Use Playwright to render JS-heavy pages or evade basic HTTP blocks."""
    new_questions = []
    
    with sync_playwright() as p:
        # We start Chromium in headless mode
        browser = p.chromium.launch(headless=True)
        # Using a convincing desktop viewport and locale
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
            locale='en-US'
        )
        
        page = context.new_page()
        
        for source_info in TARGET_URLS:
            url = source_info["url"]
            source_name = source_info["source"]
            print(f"Navigating to {url}...")
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                # Wait for the search results (specific to old.reddit layout for stability)
                page.wait_for_selector('.search-result', timeout=5000)
                
                # Extract all search result posts
                posts = page.query_selector_all('.search-result')
                
                for post in posts[:5]:  # Just grab top 5 latest to save LLM tokens/runtime
                    title_elem = post.query_selector('.search-title')
                    if not title_elem: continue
                    
                    title = title_elem.inner_text()
                    author_elem = post.query_selector('.author')
                    author = author_elem.inner_text() if author_elem else "anonymous"
                    
                    # For a real implementation, we would click into the post to get the full body.
                    # Here we might just grab the snippet, but let's emulate clicking.
                    post_link = title_elem.get_attribute('href')
                    if not post_link: continue
                    
                    post_page = context.new_page()
                    try:
                        post_page.goto(post_link, wait_until="domcontentloaded", timeout=10000)
                        # old.reddit body content
                        body_elem = post_page.query_selector('.usertext-body .md')
                        selftext = body_elem.inner_text() if body_elem else ""
                    except Exception as e:
                        print(f"Failed to load full post for: {title} - {e}")
                        selftext = ""
                    finally:
                        post_page.close()
                    
                    # If it's a substantive post
                    if len(selftext) > 200:
                        raw_combined = f"TITLE: {title}\n\nBODY:\n{selftext}"
                        print(f"Sending to LLM: '{title}'")
                        
                        structured_data = parse_slang_and_structure_with_llm(raw_combined, source_name, author)
                        if structured_data:
                            new_questions.append(structured_data)
                            
                time.sleep(2) # be polite between subreddits
                
            except Exception as e:
                print(f"Playwright error on {url}: {e}")
                
        browser.close()
        
    return new_questions

def update_json_file(new_questions):
    if not new_questions:
        print("No new LLM-processed questions generated today.")
        return
        
    json_path = Path(__file__).parent.parent / "data" / "interview_questions.json"
    
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # Fallback
        data = {"categories": {}, "metadata": {}, "questions": []}
        
    # Prevent exact duplicates by relying on the generated question text
    existing_titles = set(q['question'] for q in data.get('questions', []))
    
    added_count = 0
    for nq in new_questions:
        # The LLM outputs a standard question text; if we already have it, skip
        if nq.get('question', '') not in existing_titles:
            data['questions'].insert(0, nq)
            existing_titles.add(nq.get('question', ''))
            added_count += 1
            
    if added_count > 0:
        if 'metadata' in data:
            data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            data['metadata']['total_questions'] = len(data.get('questions', []))
            
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully integrated {added_count} new AI-formatted questions into the database.")
    else:
        print("No new unique LLM questions to add.")

if __name__ == "__main__":
    print("Starting Playwright + LLM scraper engine...")
    extracted_qs = scrape_with_playwright()
    update_json_file(extracted_qs)
    print("AI Extraction Pipeline complete.")
