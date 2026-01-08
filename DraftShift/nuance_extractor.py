from typing import Dict
try:
    import spacy
    _nlp = spacy.load('en_core_web_sm')
except Exception:
    _nlp = None


def extract_nuance(text: str) -> Dict[str, object]:
    """Return syntactic/semantic cues using spaCy where available.

    Returns keys: subject, object, verb, modals, hedges, is_question
    """
    s = text.strip()
    out = {
        'subject': None,
        'object': None,
        'verb': None,
        'modals': [],
        'hedges': [],
        'is_question': s.endswith('?'),
    }
    hedges = set(['maybe', 'might', 'could', 'perhaps', 'seems', 'appears'])

    try:
        if _nlp is None:
            return out
        doc = _nlp(s)
        for token in doc:
            if token.dep_ in ('nsubj', 'nsubjpass') and out['subject'] is None:
                out['subject'] = token.lemma_
            if token.dep_ in ('dobj', 'pobj') and out['object'] is None:
                out['object'] = token.lemma_
            if token.pos_ == 'VERB' and out['verb'] is None:
                out['verb'] = token.lemma_
            if token.tag_ == 'MD':
                out['modals'].append(token.lemma_)
            if token.lower_ in hedges:
                out['hedges'].append(token.lower_)
    except Exception:
        pass
    return out
