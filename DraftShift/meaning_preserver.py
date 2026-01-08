from typing import Tuple, Dict
try:
    import spacy
    _nlp = spacy.load('en_core_web_sm')
except Exception:
    _nlp = None


def preserve_meaning(original: str, transformed: str) -> Tuple[bool, Dict[str, object]]:
    """Best-effort checks whether subject and main verb are preserved.

    Returns (passed, details)
    """
    details = {
        'subject_match': False,
        'verb_match': False,
        'object_match': False,
        'similarity': 0.0,
    }
    try:
        if _nlp is None:
            # conservative fallback: ensure key lemmas of original appear in transformed
            import re
            orig_lemmas = set(re.findall(r"\w+", original.lower()))
            trans_lemmas = set(re.findall(r"\w+", transformed.lower()))
            common = orig_lemmas.intersection(trans_lemmas)
            details['similarity'] = len(common) / max(1, len(orig_lemmas))
            passed = details['similarity'] > 0.4
            return passed, details

        doc_o = _nlp(original)
        doc_t = _nlp(transformed)
        # main subject/verb/object
        subj_o = next((tok.lemma_ for tok in doc_o if tok.dep_ in ('nsubj', 'nsubjpass')), None)
        subj_t = next((tok.lemma_ for tok in doc_t if tok.dep_ in ('nsubj', 'nsubjpass')), None)
        verb_o = next((tok.lemma_ for tok in doc_o if tok.pos_ == 'VERB'), None)
        verb_t = next((tok.lemma_ for tok in doc_t if tok.pos_ == 'VERB'), None)
        obj_o = next((tok.lemma_ for tok in doc_o if tok.dep_ in ('dobj', 'pobj')), None)
        obj_t = next((tok.lemma_ for tok in doc_t if tok.dep_ in ('dobj', 'pobj')), None)

        details['subject_o'] = subj_o
        details['subject_t'] = subj_t
        details['verb_o'] = verb_o
        details['verb_t'] = verb_t
        details['object_o'] = obj_o
        details['object_t'] = obj_t

        if subj_o and subj_t and subj_o == subj_t:
            details['subject_match'] = True
        if verb_o and verb_t and verb_o == verb_t:
            details['verb_match'] = True
        if obj_o and obj_t and obj_o == obj_t:
            details['object_match'] = True

        # similarity using spaCy vector similarity if available
        try:
            sim = doc_o.similarity(doc_t)
            details['similarity'] = float(sim)
        except Exception:
            details['similarity'] = 0.0

        # pass if subject and verb preserved or similarity reasonably high
        passed = (details['subject_match'] and details['verb_match']) or details['similarity'] > 0.6
        return passed, details
    except Exception:
        return False, details
