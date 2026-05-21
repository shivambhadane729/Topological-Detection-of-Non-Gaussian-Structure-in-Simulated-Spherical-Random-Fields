"""
CosmoPH - ML Classifier Service
================================
Inflation model classification using a trained Random Forest on TDA features.

If a trained model exists at  app/models/inflation_classifier.joblib  it is
loaded and used for genuine inference.  Otherwise, a graceful fallback
returns mock probabilities (the original MVP behaviour) so the rest of the
pipeline never breaks.

The training script lives at  scripts/train_classifier.py.
"""

import os
import numpy as np
from pathlib import Path
from typing import Optional

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import SVC
    SKLEARN = True
except ImportError:
    SKLEARN = False

try:
    import joblib
    JOBLIB = True
except ImportError:
    JOBLIB = False

# ---------------------------------------------------------------------------
# Labels  (must match the training script)
# ---------------------------------------------------------------------------
MODEL_LABELS = {0: "Single-field slow-roll", 1: "Multi-field", 2: "Non-Bunch-Davies"}

# ---------------------------------------------------------------------------
# Model loading — done once at module import time
# ---------------------------------------------------------------------------
_MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
_MODEL_PATH = _MODEL_DIR / "inflation_classifier.joblib"
_trained_model: Optional[RandomForestClassifier] = None

if SKLEARN and JOBLIB and _MODEL_PATH.exists():
    try:
        _trained_model = joblib.load(str(_MODEL_PATH))
        print(f"[OK] Loaded trained classifier from {_MODEL_PATH}")
    except Exception as e:
        print(f"[WARN] Failed to load classifier ({e}). Falling back to mock.")
        _trained_model = None
else:
    if not _MODEL_PATH.exists():
        print(
            f"[INFO] No trained model at {_MODEL_PATH}. "
            "Run  python scripts/train_classifier.py  to train one."
        )


def is_model_trained() -> bool:
    """Return True if a real trained model is loaded."""
    return _trained_model is not None


# ---------------------------------------------------------------------------
# Feature extraction  (12-D vector — must stay in sync with train script)
# ---------------------------------------------------------------------------

FEATURE_NAMES = [
    "total_features",
    "max_persistence",
    "mean_persistence",
    "std_persistence",
    "H0_max_betti",
    "H0_mean_betti",
    "H0_std_betti",
    "H1_max_betti",
    "H1_mean_betti",
    "H1_std_betti",
    "wasserstein_H0",
    "wasserstein_H1",
]


def extract_features(tda_result: dict) -> np.ndarray:
    """Extract a 12-D feature vector from TDA results for classification.

    Features
    --------
    0-3   summary statistics (total features, max/mean/std persistence)
    4-6   H0 Betti curve stats  (max, mean, std)
    7-9   H1 Betti curve stats  (max, mean, std)
    10-11 Wasserstein distances  (H0, H1)
    """
    features = []

    # Summary statistics
    s = tda_result.get("summary", {})
    features.append(s.get("total_features", 0))
    features.append(s.get("max_persistence", 0))
    features.append(s.get("mean_persistence", 0))
    features.append(s.get("std_persistence", 0))

    # Betti curve statistics
    bc = tda_result.get("betti_curves", {})
    for dim in ["H0", "H1"]:
        if dim in bc:
            counts = bc[dim].get("counts", [0])
            features.extend([max(counts), float(np.mean(counts)), float(np.std(counts))])
        else:
            features.extend([0, 0, 0])

    # Gaussian comparison — Wasserstein distances
    gc = tda_result.get("gaussian_comparison", {})
    wd = gc.get("wasserstein_distances", {})
    for dim in ["H0", "H1"]:
        if dim in wd:
            features.append(wd[dim].get("mean", 0))
        else:
            features.append(0)

    return np.array(features, dtype=np.float64)


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_inflation_model(tda_result: dict) -> dict:
    """Classify the inflation model based on TDA features.

    If a trained model is available, runs genuine Random Forest inference.
    Otherwise, returns mock probabilities with a note.
    """
    feats = extract_features(tda_result)
    # Safety: replace NaN/Inf
    feats = np.nan_to_num(feats, nan=0.0, posinf=0.0, neginf=0.0)

    if _trained_model is not None:
        # ── Real inference ──────────────────────────────────────────
        X = feats.reshape(1, -1)
        probs = _trained_model.predict_proba(X)[0]
        predicted = int(np.argmax(probs))
        return {
            "predicted_model": MODEL_LABELS[predicted],
            "probabilities": {
                MODEL_LABELS[i]: round(float(p), 4) for i, p in enumerate(probs)
            },
            "confidence": round(float(max(probs)), 4),
            "note": "Prediction from trained Random Forest classifier.",
            "model_type": "RandomForest",
            "model_trained": True,
        }
    else:
        # ── Mock fallback ───────────────────────────────────────────
        np.random.seed(int(abs(feats.sum()) * 1000) % 2**31)
        probs = np.random.dirichlet([3, 1.5, 0.5])
        predicted = int(np.argmax(probs))
        return {
            "predicted_model": MODEL_LABELS[predicted],
            "probabilities": {
                MODEL_LABELS[i]: round(float(p), 4) for i, p in enumerate(probs)
            },
            "confidence": round(float(max(probs)), 4),
            "note": (
                "Mock classifier (no trained model found). "
                "Run  python scripts/train_classifier.py  to train a real model."
            ),
            "model_type": "MockDirichlet",
            "model_trained": False,
        }
