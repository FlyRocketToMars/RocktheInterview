"""
Enhanced Interview Question Scraper v2
- 10+ Reddit/community sources
- Multi-page crawling (up to 3 pages per source)
- Top 15 posts per source
- Lower content threshold for short but valuable posts
- Dedup against existing DB
"""
import json
import uuid
import os
import time
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# ============ EXPANDED TARGET URLS ============
TARGET_URLS = [
    # ---- Reddit: ML/AI Interview focused ----
    {"url": "https://old.reddit.com/r/cscareerquestions/search?q=MLE+interview+experience&restrict_sr=on&sort=new&t=year", "source": "Reddit/cscareerquestions"},
    {"url": "https://old.reddit.com/r/cscareerquestions/search?q=machine+learning+interview&restrict_sr=on&sort=new&t=year", "source": "Reddit/cscareerquestions"},
    {"url": "https://old.reddit.com/r/cscareerquestions/search?q=system+design+interview&restrict_sr=on&sort=new&t=year", "source": "Reddit/cscareerquestions"},
    {"url": "https://old.reddit.com/r/MachineLearning/search?q=interview+questions&restrict_sr=on&sort=new&t=year", "source": "Reddit/MachineLearning"},
    {"url": "https://old.reddit.com/r/MachineLearning/search?q=MLE+onsite&restrict_sr=on&sort=new&t=year", "source": "Reddit/MachineLearning"},
    {"url": "https://old.reddit.com/r/MachineLearning/search?q=ML+system+design&restrict_sr=on&sort=new&t=year", "source": "Reddit/MachineLearning"},
    {"url": "https://old.reddit.com/r/datascience/search?q=MLE+interview&restrict_sr=on&sort=new&t=year", "source": "Reddit/datascience"},
    {"url": "https://old.reddit.com/r/datascience/search?q=machine+learning+engineer+interview&restrict_sr=on&sort=new&t=year", "source": "Reddit/datascience"},
    {"url": "https://old.reddit.com/r/leetcode/search?q=ML+interview+Google+Meta&restrict_sr=on&sort=new&t=year", "source": "Reddit/leetcode"},
    {"url": "https://old.reddit.com/r/experiencedDevs/search?q=machine+learning+interview&restrict_sr=on&sort=new&t=year", "source": "Reddit/experiencedDevs"},
    # ---- Reddit: Company-specific FAANG ----
    {"url": "https://old.reddit.com/r/cscareerquestions/search?q=Google+MLE+interview&restrict_sr=on&sort=new&t=year", "source": "Reddit/Google"},
    {"url": "https://old.reddit.com/r/cscareerquestions/search?q=Meta+machine+learning+interview&restrict_sr=on&sort=new&t=year", "source": "Reddit/Meta"},
    {"url": "https://old.reddit.com/r/cscareerquestions/search?q=Amazon+MLE+interview&restrict_sr=on&sort=new&t=year", "source": "Reddit/Amazon"},
    {"url": "https://old.reddit.com/r/cscareerquestions/search?q=Apple+ML+interview&restrict_sr=on&sort=new&t=year", "source": "Reddit/Apple"},
    # ---- Deep Learning / AI specific ----
    {"url": "https://old.reddit.com/r/deeplearning/search?q=interview&restrict_sr=on&sort=new&t=year", "source": "Reddit/deeplearning"},
    {"url": "https://old.reddit.com/r/artificial/search?q=interview+questions+ML&restrict_sr=on&sort=new&t=year", "source": "Reddit/artificial"},
]

POSTS_PER_SOURCE = 15
MIN_CONTENT_LENGTH = 100  # lowered from 200 to catch shorter valuable posts

def parse_slang_and_structure_with_llm(raw_text, source_name, author="anonymous"):
    """
    Uses Gemini to deeply understand unstructured text, translate slang, and format into strict JSON.
    """
    if not api_key:
        print("No GEMINI_API_KEY found. Falling back to simple heuristic extraction.")
        return simple_fallback_extraction(raw_text, source_name, author)

    system_prompt = """
    You are an expert technical interviewer and data extractor. You are analyzing community forum posts (often containing Chinese/English slang) about technical interviews.
    Your job is to extract the details and return them EXCLUSIVELY as a valid JSON object matching the exact schema below. Do not output markdown, do not output reasoning, only the JSON. 
    
    If the post contains MULTIPLE interview questions, return a JSON ARRAY of objects (one per question).
    If there's only one question, return a single JSON object.
    
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
        "Provide a technical, structured answer/guide based on best practices for this question (3-5 succinct points). Do NOT just copy the user's rant.",
        "Include original context at the end."
      ],
      "follow_ups": ["Likely follow-up question 1", "Likely follow-up question 2"],
      "difficulty": "easy, medium, or hard",
      "tags": ["extracted_tag_1", "extracted_tag_2"]
    }
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
            full_prompt = f"{system_prompt}\n\nTask:\nExtract the interview data from the following post:\n\n{raw_text[:3000]}"
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.GenerationConfig(temperature=0.2)
            )
            result_content = response.text.strip()
            
            # Clean up markdown wrapping
            if result_content.startswith("```json"):
                result_content = result_content[7:]
            if result_content.startswith("```"):
                result_content = result_content[3:]
            if result_content.endswith("```"):
                result_content = result_content[:-3]
                
            parsed = json.loads(result_content.strip())
            
            # Handle array of questions from a single post
            if isinstance(parsed, list):
                results = []
                for item in parsed:
                    item["id"] = f"auto_llm_{str(uuid.uuid4())[:8]}"
                    item["tags"] = item.get("tags", []) + ["community-scraped", source_name, author]
                    item["frequency"] = 1
                    item["importance"] = 4
                    item["common_mistakes"] = []
                    item["year"] = datetime.now().year
                    results.append(item)
                return results
            else:
                parsed["id"] = f"auto_llm_{str(uuid.uuid4())[:8]}"
                parsed["tags"] = parsed.get("tags", []) + ["community-scraped", source_name, author]
                parsed["frequency"] = 1
                parsed["importance"] = 4
                parsed["common_mistakes"] = []
                parsed["year"] = datetime.now().year
                return [parsed]
            
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "quota" in err_str.lower():
                wait = 20 * (attempt + 1)
                print(f"  [RATE LIMITED] Waiting {wait}s ... ({attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                print(f"LLM Parsing failed: {e}")
                return [simple_fallback_extraction(raw_text, source_name, author)]
    
    return [simple_fallback_extraction(raw_text, source_name, author)]


def simple_fallback_extraction(raw_text, source_name, author):
    """Fallback if LLM API fails or isn't set."""
    company = "Community"
    companies = ["Google", "Meta", "Amazon", "Apple", "Netflix", "Snap", "ByteDance", "OpenAI",
                 "Microsoft", "Uber", "Stripe", "Airbnb", "LinkedIn", "Twitter", "Nvidia"]
    for c in companies:
        if c.lower() in raw_text.lower():
            company = c
            break
            
    # Try to extract a question-like sentence
    lines = raw_text.split('\n')
    question_line = ""
    for line in lines:
        if '?' in line and len(line) > 20:
            question_line = line.strip()[:200]
            break
    if not question_line:
        question_line = f"[{source_name}] Community Interview Experience"
    
    snippet = raw_text[:800] + f"...\n\n[Source: {source_name}]"
    
    return {
        "id": f"auto_{str(uuid.uuid4())[:8]}",
        "company": company,
        "role": "MLE",
        "level": "Unknown",
        "round": "ml_theory",
        "domain": "fundamentals",
        "question": question_line,
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
    """Use Playwright to render JS-heavy pages and extract interview posts."""
    new_questions = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
            locale='en-US'
        )
        
        page = context.new_page()
        seen_titles = set()
        
        for source_info in TARGET_URLS:
            url = source_info["url"]
            source_name = source_info["source"]
            print(f"\n{'='*60}")
            print(f"[SOURCE] {source_name}: {url}")
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_selector('.search-result', timeout=5000)
                
                posts = page.query_selector_all('.search-result')
                post_count = 0
                
                for post in posts[:POSTS_PER_SOURCE]:
                    title_elem = post.query_selector('.search-title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.inner_text().strip()
                    
                    # Dedup by title
                    if title in seen_titles:
                        continue
                    seen_titles.add(title)
                    
                    author_elem = post.query_selector('.author')
                    author = author_elem.inner_text() if author_elem else "anonymous"
                    
                    post_link = title_elem.get_attribute('href')
                    if not post_link:
                        continue
                    
                    # Navigate into post to get full content
                    post_page = context.new_page()
                    try:
                        post_page.goto(post_link, wait_until="domcontentloaded", timeout=10000)
                        body_elem = post_page.query_selector('.usertext-body .md')
                        selftext = body_elem.inner_text() if body_elem else ""
                        
                        # Also grab top comments for extra context
                        comments = post_page.query_selector_all('.comment .usertext-body .md')
                        top_comments = []
                        for c in comments[:3]:
                            try:
                                top_comments.append(c.inner_text()[:500])
                            except:
                                pass
                        comment_text = "\n---COMMENT---\n".join(top_comments)
                        
                    except Exception as e:
                        print(f"  [WARN] Failed to load: {title[:50]}... - {e}")
                        selftext = ""
                        comment_text = ""
                    finally:
                        post_page.close()
                    
                    full_text = selftext + ("\n\nTOP COMMENTS:\n" + comment_text if comment_text else "")
                    
                    if len(full_text) > MIN_CONTENT_LENGTH:
                        raw_combined = f"TITLE: {title}\n\nBODY:\n{full_text}"
                        print(f"  [OK] Processing: {title[:60]}...")
                        
                        structured_list = parse_slang_and_structure_with_llm(raw_combined, source_name, author)
                        new_questions.extend(structured_list)
                        post_count += len(structured_list)
                        
                        time.sleep(2)  # rate limit LLM calls
                    else:
                        print(f"  [SKIP] Too short ({len(full_text)} chars): {title[:50]}...")
                
                print(f"  [DONE] Extracted {post_count} questions from {source_name}")
                time.sleep(3)  # be polite between sources
                
            except Exception as e:
                print(f"  [ERROR] Playwright error on {url}: {e}")
                
        browser.close()
        
    return new_questions

def update_json_file(new_questions):
    if not new_questions:
        print("\nNo new questions generated.")
        return
        
    json_path = Path(__file__).parent.parent / "data" / "interview_questions.json"
    
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"categories": {}, "metadata": {}, "questions": []}
        
    existing_titles = set(q['question'] for q in data.get('questions', []))
    
    added_count = 0
    for nq in new_questions:
        q_text = nq.get('question', '')
        if q_text and q_text not in existing_titles and len(q_text) > 10:
            data['questions'].insert(0, nq)
            existing_titles.add(q_text)
            added_count += 1
            
    if added_count > 0:
        if 'metadata' in data:
            data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            data['metadata']['total_questions'] = len(data.get('questions', []))
            
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\n{'='*60}")
        print(f"Successfully added {added_count} new questions!")
        print(f"Total questions in database: {len(data['questions'])}")
    else:
        print("\nNo new unique questions to add (all duplicates).")

if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"Enhanced Interview Scraper v2 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Sources: {len(TARGET_URLS)}")
    print(f"Max posts per source: {POSTS_PER_SOURCE}")
    print(f"{'='*60}")
    
    extracted_qs = scrape_with_playwright()
    print(f"\nRaw extraction: {len(extracted_qs)} questions")
    update_json_file(extracted_qs)
    print("Pipeline complete.")
