"""Test TDA engine."""
import numpy as np
from app.services.tda_engine import compute_persistence_diagram, compute_betti_curves, run_tda_pipeline

def test_persistence_diagram():
    patch = np.random.normal(0, 1, (32, 32))
    result = compute_persistence_diagram(patch, max_points=200)
    assert len(result["pairs"]) > 0
    assert all("birth" in p and "death" in p for p in result["pairs"])

def test_betti_curves():
    dgm = [np.array([[0, 0.1], [0, 0.2], [0, 0.5]]),
            np.array([[0.1, 0.3], [0.2, 0.4]])]
    bc = compute_betti_curves(dgm)
    assert "H0" in bc
    assert len(bc["H0"]["thresholds"]) > 0

def test_full_pipeline():
    patch = np.random.normal(0, 1, (32, 32))
    results = run_tda_pipeline(patch, max_points=200, n_gaussian_samples=2)
    assert "persistence_diagram" in results
    assert "betti_curves" in results
    assert "summary" in results
