"""
Skill Extractor Module
Extracts skills from text using keyword matching against a taxonomy
"""
import re
from typing import List, Dict, Set


def extract_skills(text: str, taxonomy: Dict) -> List[str]:
    """
    Extract skills from text by matching against the skills taxonomy.
    
    Args:
        text: The text to extract skills from (resume or JD)
        taxonomy: The skills taxonomy dictionary
    
    Returns:
        List of extracted skill names
    """
    if not text or not taxonomy:
        return []
    
    # Normalize text
    text_lower = text.lower()
    
    # Build a set of all skills from taxonomy
    all_skills: Set[str] = set()
    skill_patterns: Dict[str, str] = {}  # lowercase -> original case
    
    for category_id, category_data in taxonomy.get("categories", {}).items():
        for skill in category_data.get("skills", []):
            all_skills.add(skill)
            skill_patterns[skill.lower()] = skill
    
    # Also add some common variations and aliases
    aliases = {
        "pytorch": "PyTorch",
        "tensorflow": "TensorFlow",
        "scikit-learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "huggingface": "HuggingFace Transformers",
        "hugging face": "HuggingFace Transformers",
        "llm": "LLM",
        "llms": "LLM",
        "large language model": "LLM",
        "large language models": "LLM",
        "rlhf": "RLHF",
        "reinforcement learning from human feedback": "RLHF",
        "bert": "BERT",
        "gpt": "GPT",
        "cnn": "CNN",
        "convolutional neural network": "CNN",
        "rnn": "RNN",
        "recurrent neural network": "RNN",
        "lstm": "LSTM",
        "transformer": "Transformer",
        "transformers": "Transformer",
        "attention": "Attention Mechanism",
        "attention mechanism": "Attention Mechanism",
        "gan": "GAN",
        "generative adversarial network": "GAN",
        "vae": "VAE",
        "variational autoencoder": "VAE",
        "cv": "Computer Vision",
        "computer vision": "Computer Vision",
        "nlp": "Natural Language Processing",
        "natural language processing": "Natural Language Processing",
        "object detection": "Object Detection",
        "yolo": "YOLO",
        "resnet": "ResNet",
        "vit": "ViT",
        "vision transformer": "ViT",
        "recommendation system": "Recommendation Systems",
        "recommendation systems": "Recommendation Systems",
        "recommender system": "Recommendation Systems",
        "recsys": "Recommendation Systems",
        "ranking": "Ranking",
        "retrieval": "Retrieval",
        "a/b testing": "A/B Testing",
        "ab testing": "A/B Testing",
        "a/b test": "A/B Testing",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "k8s": "Kubernetes",
        "mlflow": "MLflow",
        "kubeflow": "Kubeflow",
        "airflow": "Airflow",
        "aws": "AWS",
        "amazon web services": "AWS",
        "gcp": "GCP",
        "google cloud": "GCP",
        "google cloud platform": "GCP",
        "azure": "Azure",
        "sagemaker": "SageMaker",
        "vertex ai": "Vertex AI",
        "bigquery": "BigQuery",
        "distributed training": "Distributed Training",
        "data parallelism": "Data Parallelism",
        "model parallelism": "Model Parallelism",
        "horovod": "Horovod",
        "ray": "Ray",
        "spark": "Spark",
        "apache spark": "Spark",
        "hadoop": "Hadoop",
        "kafka": "Kafka",
        "redis": "Redis",
        "python": "Python",
        "c++": "C++",
        "cpp": "C++",
        "java": "Java",
        "scala": "Scala",
        "sql": "SQL",
        "git": "Git",
        "linear algebra": "Linear Algebra",
        "probability": "Probability",
        "statistics": "Statistics",
        "bayesian": "Bayesian Methods",
        "causal inference": "Causal Inference",
        "experimental design": "Experimental Design",
        "xgboost": "XGBoost",
        "lightgbm": "LightGBM",
        "feature store": "Feature Store",
        "ci/cd": "CI/CD",
        "cicd": "CI/CD",
        "ner": "NER",
        "named entity recognition": "NER",
        "sentiment analysis": "Sentiment Analysis",
        "machine translation": "Machine Translation",
        "question answering": "Question Answering",
        "qa": "Question Answering",
        "rag": "RAG",
        "retrieval augmented generation": "RAG",
        "prompt engineering": "Prompt Engineering",
        "fine-tuning": "Fine-tuning",
        "finetuning": "Fine-tuning",
        "fine tuning": "Fine-tuning",
        "ocr": "OCR",
        "face recognition": "Face Recognition",
        "facial recognition": "Face Recognition",
        "video understanding": "Video Understanding",
        "3d vision": "3D Vision",
        "collaborative filtering": "Collaborative Filtering",
        "matrix factorization": "Matrix Factorization",
        "two-tower": "Two-Tower Model",
        "two tower": "Two-Tower Model",
        "wide and deep": "Wide & Deep",
        "wide & deep": "Wide & Deep",
        "multi-task": "Multi-task Learning",
        "multitask": "Multi-task Learning",
        "real-time": "Real-time Recommendation",
        "diffusion": "Diffusion Models",
        "diffusion model": "Diffusion Models",
        "diffusion models": "Diffusion Models",
        "nas": "Neural Architecture Search",
        "neural architecture search": "Neural Architecture Search",
    }
    
    # Find matches
    found_skills: Set[str] = set()
    
    # Check direct matches from taxonomy
    for skill_lower, skill_original in skill_patterns.items():
        # Use word boundary matching for better accuracy
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill_original)
    
    # Check aliases
    for alias_lower, skill_original in aliases.items():
        pattern = r'\b' + re.escape(alias_lower) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.add(skill_original)
    
    return sorted(list(found_skills))


def categorize_skills(skills: List[str], taxonomy: Dict) -> Dict[str, List[str]]:
    """
    Categorize a list of skills according to the taxonomy.
    
    Args:
        skills: List of skill names
        taxonomy: The skills taxonomy dictionary
    
    Returns:
        Dictionary mapping category names to lists of skills
    """
    categorized = {}
    skill_set = set(skills)
    
    for category_id, category_data in taxonomy.get("categories", {}).items():
        category_name = category_data.get("name", category_id)
        category_skills = set(category_data.get("skills", []))
        
        matching = skill_set & category_skills
        if matching:
            categorized[category_name] = sorted(list(matching))
    
    return categorized


def get_skill_importance(skill: str, jd_text: str) -> str:
    """
    Determine the importance level of a skill based on JD context.
    
    Args:
        skill: The skill name
        jd_text: The job description text
    
    Returns:
        "required", "preferred", or "mentioned"
    """
    jd_lower = jd_text.lower()
    skill_lower = skill.lower()
    
    # Check for required indicators
    required_patterns = [
        rf"required.*{re.escape(skill_lower)}",
        rf"must have.*{re.escape(skill_lower)}",
        rf"{re.escape(skill_lower)}.*required",
        rf"{re.escape(skill_lower)}.*must",
        rf"experience with {re.escape(skill_lower)}",
        rf"proficiency in {re.escape(skill_lower)}",
    ]
    
    for pattern in required_patterns:
        if re.search(pattern, jd_lower):
            return "required"
    
    # Check for preferred indicators
    preferred_patterns = [
        rf"preferred.*{re.escape(skill_lower)}",
        rf"nice to have.*{re.escape(skill_lower)}",
        rf"{re.escape(skill_lower)}.*preferred",
        rf"{re.escape(skill_lower)}.*bonus",
        rf"familiarity with {re.escape(skill_lower)}",
    ]
    
    for pattern in preferred_patterns:
        if re.search(pattern, jd_lower):
            return "preferred"
    
    return "mentioned"
