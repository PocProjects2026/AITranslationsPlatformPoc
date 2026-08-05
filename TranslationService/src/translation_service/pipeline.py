import re
from typing import List, Dict, Any

_PLACEHOLDER_RE = re.compile(r"(\{\{[^{}]+\}\}|\{[^{}]+\}|%\([a-zA-Z_][a-zA-Z0-9_]*\)[sd]|%\d*\$?[sd]|<[^>]+>)")

def extract_placeholders(text: str) -> List[str]:
    return _PLACEHOLDER_RE.findall(text)

def validate_candidate(source: str, target: str, glossary: Dict[str, str] = None) -> float:
    score = 100.0
    
    # 1. Placeholder integrity
    src_ph = extract_placeholders(source)
    tgt_ph = extract_placeholders(target)
    for ph in src_ph:
        if ph not in tgt_ph:
            score -= 30.0 # penalty for missing placeholder
    for ph in tgt_ph:
        if ph not in src_ph:
            score -= 30.0 # penalty for hallucinatory placeholder
            
    # 2. Glossary compliance
    if glossary:
        for k, v in glossary.items():
            if k in source and v not in target:
                score -= 20.0
                
    # 3. Length variation
    len_src = len(source.strip())
    len_tgt = len(target.strip())
    if len_src > 0:
        ratio = len_tgt / len_src
        if ratio > 3.0 or ratio < 0.3:
            score -= 15.0
            
    # 4. Similarity evidence (simple heuristic based on punctuation/structure)
    if source.endswith('.') and not target.endswith('.'):
        score -= 5.0
    if source.endswith('?') and not target.endswith('?'):
        score -= 5.0
        
    return max(0.0, score)

def rank_candidates(source: str, candidates: List[str], glossary: Dict[str, str] = None) -> List[Dict[str, Any]]:
    ranked = []
    for c in candidates:
        score = validate_candidate(source, c, glossary)
        ranked.append({"text": c, "score": score})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked
