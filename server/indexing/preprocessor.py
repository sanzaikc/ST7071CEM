import re
from typing import List
import nltk
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

def preprocess_text(text: str) -> List[str]:
    """Preprocess text for indexing"""
    if not text:
        return []
    
    # Convert to lowercase
    text = text.lower()
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Clean tokens - remove non-alphanumeric characters
    tokens = [re.sub(r'\W+', '', token) for token in tokens if token.isalnum()]
    
    # Remove empty tokens
    tokens = [t for t in tokens if t]
    
    return tokens

def create_search_text(title: str, abstract: str, keywords: List[str]) -> str:
    """Create combined search text from publication fields"""
    parts = []
    
    if title:
        parts.append(title)
    
    if abstract:
        parts.append(abstract)
    
    if keywords:
        parts.extend(keywords)
    
    return ' '.join(parts)
