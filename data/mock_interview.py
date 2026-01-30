"""
AI Mock Interview Engine
Handles interview sessions, AI persona, and feedback generation
"""
import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class InterviewSession:
    """Represents a single interview session."""
    def __init__(self, interview_type: str, target_company: str, level: str):
        self.id = str(uuid.uuid4())
        self.interview_type = interview_type  # behavioral, technical, system_design
        self.target_company = target_company
        self.level = level
        self.messages = []  # List of {"role": "user"|"model", "content": "..."}
        self.created_at = datetime.now().isoformat()
        self.status = "active"  # active, completed
        self.feedback = None
        
        # Initialize context based on company style
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        """Generate system prompt based on company and type."""
        
        base_prompt = f"""You are a senior {self.interview_type} interviewer at {self.target_company}. 
Your goal is to assess a candidate for a {self.level} position.
"""
        
        if self.interview_type == "behavioral":
            style_guide = ""
            if "Amazon" in self.target_company:
                style_guide = "Focus heavily on Amazon Leadership Principles. Ask probing questions about specific situations. Be skeptical and dig into details."
            elif "Google" in self.target_company:
                style_guide = "Focus on 'Googleyness', ambiguity navigation, and collaborative problem solving."
            else:
                style_guide = "Use the STAR method (Situation, Task, Action, Result) to evaluate answers."
            
            return f"""{base_prompt}
{style_guide}

INSTRUCTIONS:
1. Start by welcoming the candidate and asking a brief introduction.
2. Then, ask ONE behavioral question at a time.
3. If the answer is vague, ask follow-up questions (e.g., "What was your specific role?", "What was the outcome?").
4. Do not provide feedback during the interview. Stay in character as a professional interviewer.
5. Keep your responses concise (under 100 words) unless explaining a complex question.
"""
        return base_prompt

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "interview_type": self.interview_type,
            "target_company": self.target_company,
            "level": self.level,
            "messages": self.messages,
            "created_at": self.created_at,
            "status": self.status,
            "feedback": self.feedback
        }

class MockInterviewManager:
    """Manages interview sessions and AI interaction."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}"

    def create_session(self, interview_type: str, target_company: str, level: str) -> InterviewSession:
        return InterviewSession(interview_type, target_company, level)

    def send_message(self, session: InterviewSession, user_message: str = None) -> str:
        """Send message to AI and get response."""
        
        # Prepare context
        messages_payload = []
        
        # Add system instruction as the first part of context if possible, 
        # but for Gemini Pro API simple usage, we insert it into the first message or history.
        # We will reconstruct the chat history.
        
        history = []
        
        # Add system prompt as context context for the AI
        history.append({"role": "user", "parts": [{"text": f"System Instruction: {session.system_prompt}\n\nPlease start the interview now."}]})
        history.append({"role": "model", "parts": [{"text": "Understood. I am ready to conduct the interview."}]})

        # Append session history
        for msg in session.messages:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        # Append current user message if exists
        if user_message:
            session.messages.append({"role": "user", "content": user_message})
            history.append({"role": "user", "parts": [{"text": user_message}]})
        
        # Call API
        try:
            response = requests.post(
                self.api_url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": history,
                    "generationConfig": {
                        "temperature": 0.7, 
                        "maxOutputTokens": 800
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Add AI response to session history
                session.messages.append({"role": "model", "content": ai_text})
                return ai_text
            else:
                return f"Error: {response.text}"
        except Exception as e:
            return f"Connection Error: {e}"

    def generate_feedback(self, session: InterviewSession) -> Dict:
        """Generate final feedback for the session."""
        
        conversation_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in session.messages])
        
        prompt = f"""
Analyze the following behavioral interview transcript for a {session.level} role at {session.target_company}.

TRANSCRIPT:
{conversation_text}

Provide detailed feedback in JSON format with the following keys:
1. "score": Integrity score (1-10)
2. "strengths": List of 3 key strengths
3. "improvements": List of 3 areas for improvement
4. "star_analysis": How well did they use the STAR method?
5. "verdict": "Strong Hire", "Hire", "Lean Hire", "No Hire"
"""
        # Call API for feedback
        try:
            response = requests.post(
                self.api_url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.5}
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                feedback_text = result["candidates"][0]["content"]["parts"][0]["text"]
                # Clean up markdown code blocks if present
                if "```json" in feedback_text:
                    feedback_text = feedback_text.replace("```json", "").replace("```", "")
                
                try:
                    return json.loads(feedback_text)
                except:
                    return {"raw_feedback": feedback_text}
            
        except Exception as e:
            return {"error": str(e)}
        
        return {}

# Global instance
mock_interview_manager = MockInterviewManager()
