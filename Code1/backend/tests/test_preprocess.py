"""Test preprocessing service."""
import numpy as np
from app.services.preprocessor import preprocess_pipeline, normalize_patch, apply_map_mask

def test_normalize_zscore():
    data = np.random.normal(5, 2, (64, 64))
    normed = normalize_patch(data, "zscore")
    assert abs(np.mean(normed)) < 0.01
    assert abs(np.std(normed) - 1.0) < 0.01

def test_preprocess_pipeline():
    data = np.random.normal(0, 1e-5, (128, 128))
    result = preprocess_pipeline(data, apply_mask=True, patch_size=64)
    assert result["patch"].shape == (64, 64)
    assert "min" in result["stats"]

def test_mask():
    data = np.ones((64, 64))
    masked = apply_map_mask(data)
    assert np.any(np.isnan(masked))
