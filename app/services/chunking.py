from typing import List

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split a given text into overlapping chunks limit defined by sizes.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        
        if end == text_length:
            break
            
        start += chunk_size - chunk_overlap
        
    return chunks
