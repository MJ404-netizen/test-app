# utils/svm_predictor.py
"""
Loads the trained SVM pipeline and predicts stress type from session answers.
"""
import os
import json
import joblib
import numpy as np

# ---- Paths ----
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
MODEL_PATH = os.path.join(_PROJECT_ROOT, 'models', 'svm_stress_model.pkl')
META_PATH  = os.path.join(_PROJECT_ROOT, 'models', 'svm_model_metadata.json')

# ---- Cached loaders ----
_model = None
_meta  = None

def _load():
    global _model, _meta
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"SVM model not found at {MODEL_PATH}")
        if not os.path.exists(META_PATH):
            raise FileNotFoundError(f"Metadata not found at {META_PATH}")
        _model = joblib.load(MODEL_PATH)
        with open(META_PATH, 'r') as f:
            _meta = json.load(f)
    return _model, _meta

# ---- Column name -> question ID map ----
COLUMN_TO_QID = {
    'recent_stress':           3,
    'heart_palpitations':      4,
    'anxiety_severity':        5,
    'sleep_problems':          6,
    'anxiety_frequency':       7,
    'headaches':               8,
    'irritability':            9,
    'concentration_issues':   10,
    'sadness':                11,
    'health_issues':          12,
    'loneliness':             13,
    'academic_overwhelm':     14,
    'peer_competition':       15,
    'relationship_stress':    16,
    'professor_difficulties': 17,
    'work_environment_stress':18,
    'relaxation_time':        19,
    'home_stress':            20,
    'academic_confidence':    21,
    'subject_confidence':     22,
    'activity_conflict':      23,
    'class_attendance':       24,
    'weight_change':          25,
}

def _parse_score(raw):
    if raw is None:
        return 0
    try:
        return int(raw)
    except (ValueError, TypeError):
        pass
    try:
        return int(str(raw).split(" - ")[0].strip())
    except (ValueError, IndexError):
        return 0

def _parse_gender(raw):
    if raw is None:
        return 0
    if isinstance(raw, (int, float)):
        return int(raw)
    s = str(raw).strip().lower()
    if s in ('male', 'm', 'man'):
        return 0
    if s in ('female', 'f', 'woman'):
        return 1
    try:
        return int(s)
    except ValueError:
        return 0

def predict_stress_type(answers, gender_code, age):
    model, meta = _load()
    feature_cols = meta['feature_cols']
    expected_n = meta['n_features']

    features = []
    for col in feature_cols:
        if col == 'gender':
            features.append(_parse_gender(gender_code))
        elif col == 'age':
            try:
                features.append(int(age))
            except (ValueError, TypeError):
                features.append(0)
        else:
            q_id = COLUMN_TO_QID.get(col)
            if q_id is None:
                features.append(0)
            else:
                features.append(_parse_score(answers.get(q_id, 0)))

    if len(features) != expected_n:
        raise ValueError(f"Feature count mismatch: built {len(features)}, expects {expected_n}")

    X = np.array([features], dtype=float)
    pred = model.predict(X)[0]
    probs = model.predict_proba(X)[0]
    classes = list(model.classes_)

    return {
        'type': str(pred),
        'confidence': float(max(probs)),
        'probabilities': {str(c): float(p) for c, p in zip(classes, probs)},
        'feature_vector': features,
    }
