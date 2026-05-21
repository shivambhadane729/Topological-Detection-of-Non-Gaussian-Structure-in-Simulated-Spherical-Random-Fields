"""
CosmoPH - TDA Engine Service
# Core Topological Data Analysis: persistence diagrams, Betti curves,
# persistence images, and Wasserstein distance comparison.
"""

import numpy as np
from typing import Optional
from app.config import get_settings

try:
    from ripser import ripser
    RIPSER_AVAILABLE = True
except ImportError:
    RIPSER_AVAILABLE = False
    print("⚠️  ripser not available. Using simplified TDA.")

try:
    from persim import PersistenceImager, wasserstein
    PERSIM_AVAILABLE = True
except ImportError:
    PERSIM_AVAILABLE = False
    print("⚠️  persim not available. Using simplified comparison.")


def _subsample_points(data_2d: np.ndarray, max_points: int = 1000) -> np.ndarray:
    """
    Convert a 2D image patch into a point cloud for TDA.
    Uses superlevel set filtration: points are (x, y, value) where value > threshold.
    Subsamples to max_points if needed.
    
    Args:
        data_2d: 2D numpy array (image patch)
        max_points: Maximum number of points
    
    Returns:
        2D array of shape (n_points, 2) or (n_points, 3)
    """
    h, w = data_2d.shape
    
    # Create coordinate grid
    rows, cols = np.where(~np.isnan(data_2d))
    values = data_2d[rows, cols]
    
    # Create point cloud: (normalized_x, normalized_y) weighted by value
    points = np.column_stack([
        cols / w,  # normalized x
        rows / h,  # normalized y
    ])
    
    # Subsample if too many points
    if len(points) > max_points:
        # Prefer points with extreme values (features)
        importance = np.abs(values - np.mean(values))
        prob = importance / importance.sum() if importance.sum() > 0 else np.ones(len(importance)) / len(importance)
        indices = np.random.choice(len(points), size=max_points, replace=False, p=prob)
        points = points[indices]
    
    return points


def compute_persistence_diagram(
    data_2d: np.ndarray,
    max_dimension: int = 1,
    max_edge_length: float = 2.0,
    max_points: int = 1000,
) -> dict:
    """
    Compute the persistence diagram of a 2D data patch.
    
    Uses Vietoris-Rips filtration on the point cloud extracted from the image.
    
    Args:
        data_2d: 2D numpy array (preprocessed CMB patch)
        max_dimension: Maximum homology dimension (0 or 1)
        max_edge_length: Maximum edge length for Rips complex
        max_points: Maximum points to use
    
    Returns:
        Dictionary with 'diagrams' (list of (birth, death, dim) tuples),
        'raw_diagrams' (list of numpy arrays per dimension)
    """
    points = _subsample_points(data_2d, max_points)
    
    if RIPSER_AVAILABLE:
        result = ripser(points, maxdim=max_dimension, thresh=max_edge_length)
        diagrams = result['dgms']
    else:
        # Simplified fallback: compute pairwise distances and extract features
        diagrams = _simplified_persistence(points, max_dimension)
    
    # Convert to serializable format
    pairs = []
    for dim, dgm in enumerate(diagrams):
        for birth, death in dgm:
            if np.isfinite(death):  # Skip infinite persistence
                pairs.append({
                    "birth": float(birth),
                    "death": float(death),
                    "dimension": dim,
                })
    
    return {
        "pairs": pairs,
        "raw_diagrams": [dgm[np.isfinite(dgm[:, 1])] if len(dgm) > 0 else np.array([]).reshape(0, 2) for dgm in diagrams],
        "n_features": {f"H{dim}": int(np.sum(np.isfinite(dgm[:, 1]))) if len(dgm) > 0 else 0 for dim, dgm in enumerate(diagrams)},
    }


def _simplified_persistence(points: np.ndarray, max_dim: int = 1) -> list:
    """
    Simplified persistence computation when ripser is not available.
    Uses distance-based heuristic to generate approximate persistence pairs.
    """
    from scipy.spatial.distance import pdist, squareform
    
    n = len(points)
    if n < 3:
        return [np.array([[0, 0.1]]), np.array([[0, 0.05]])]
    
    dists = squareform(pdist(points))
    
    # H0: connected components (simplified via minimum spanning tree heuristic)
    sorted_edges = np.sort(dists[np.triu_indices(n, k=1)])
    n_h0 = min(50, len(sorted_edges))
    h0_births = np.zeros(n_h0)
    h0_deaths = sorted_edges[:n_h0]
    h0_dgm = np.column_stack([h0_births, h0_deaths])
    
    diagrams = [h0_dgm]
    
    if max_dim >= 1:
        # H1: loops (very simplified)
        n_h1 = min(20, n // 5)
        if n_h1 > 0:
            h1_births = np.sort(sorted_edges)[:n_h1] * 0.5
            h1_deaths = h1_births + np.random.exponential(0.1, n_h1)
            h1_dgm = np.column_stack([h1_births, h1_deaths])
        else:
            h1_dgm = np.array([]).reshape(0, 2)
        diagrams.append(h1_dgm)
    
    return diagrams


def compute_betti_curves(diagrams: list, n_thresholds: int = 100) -> dict:
    """
    Compute Betti curves from persistence diagrams.
    
    Betti number β_k(ε) = number of features in dimension k alive at threshold ε.
    
    Args:
        diagrams: List of persistence diagrams (one per dimension)
        n_thresholds: Number of threshold values
    
    Returns:
        Dict mapping dimension to {'thresholds': [...], 'counts': [...]}
    """
    betti_curves = {}
    
    for dim, dgm in enumerate(diagrams):
        if len(dgm) == 0:
            betti_curves[f"H{dim}"] = {
                "thresholds": [0.0],
                "counts": [0],
            }
            continue
        
        # Determine range
        all_values = dgm[np.isfinite(dgm)].flatten()
        if len(all_values) == 0:
            continue
        
        t_min = 0.0
        t_max = float(np.max(all_values)) * 1.1
        thresholds = np.linspace(t_min, t_max, n_thresholds)
        
        counts = []
        for t in thresholds:
            # Count features alive at threshold t
            alive = np.sum((dgm[:, 0] <= t) & (dgm[:, 1] > t) & np.isfinite(dgm[:, 1]))
            counts.append(int(alive))
        
        betti_curves[f"H{dim}"] = {
            "thresholds": thresholds.tolist(),
            "counts": counts,
        }
    
    return betti_curves


def compute_persistence_image(
    diagram: np.ndarray,
    resolution: tuple = (20, 20),
    sigma: float = 0.1,
) -> np.ndarray:
    """
    Compute a persistence image from a persistence diagram.
    
    Args:
        diagram: Persistence diagram as (N, 2) array of (birth, death)
        resolution: Output image resolution
        sigma: Gaussian kernel bandwidth
    
    Returns:
        2D numpy array (persistence image)
    """
    if PERSIM_AVAILABLE:
        try:
            pimgr = PersistenceImager(
                pixel_size=1.0 / resolution[0],
                birth_range=(0, 1),
                pers_range=(0, 1),
            )
            # Transform to (birth, persistence) format
            if len(diagram) > 0:
                pers = diagram[:, 1] - diagram[:, 0]
                valid = np.isfinite(pers) & (pers > 0)
                if np.any(valid):
                    birth_pers = np.column_stack([diagram[valid, 0], pers[valid]])
                    img = pimgr.transform(birth_pers)
                    return img
            return np.zeros(resolution)
        except Exception:
            pass
    
    # Fallback: manual persistence image
    if len(diagram) == 0:
        return np.zeros(resolution)
    
    # Filter finite persistence
    pers = diagram[:, 1] - diagram[:, 0]
    valid = np.isfinite(pers) & (pers > 0)
    if not np.any(valid):
        return np.zeros(resolution)
    
    births = diagram[valid, 0]
    deaths = diagram[valid, 1]
    persistences = deaths - births
    
    # Normalize
    b_min, b_max = births.min(), births.max()
    p_min, p_max = persistences.min(), persistences.max()
    
    if b_max == b_min:
        b_max = b_min + 1
    if p_max == p_min:
        p_max = p_min + 1
    
    img = np.zeros(resolution)
    h, w = resolution
    
    for b, p in zip(births, persistences):
        bx = int((b - b_min) / (b_max - b_min) * (w - 1))
        py = int((p - p_min) / (p_max - p_min) * (h - 1))
        bx = np.clip(bx, 0, w - 1)
        py = np.clip(py, 0, h - 1)
        img[py, bx] += p  # Weight by persistence
    
    # Smooth
    try:
        from scipy.ndimage import gaussian_filter
        img = gaussian_filter(img, sigma=sigma * min(resolution))
    except ImportError:
        pass
    
    return img


def compute_wasserstein_distance(dgm1: np.ndarray, dgm2: np.ndarray) -> float:
    """
    Compute the Wasserstein distance between two persistence diagrams.
    
    Args:
        dgm1: First persistence diagram (N, 2)
        dgm2: Second persistence diagram (M, 2)
    
    Returns:
        Wasserstein distance (float)
    """
    if PERSIM_AVAILABLE:
        try:
            return float(wasserstein(dgm1, dgm2))
        except Exception:
            pass
    
    # Simplified fallback: compare persistence distributions
    if len(dgm1) == 0 or len(dgm2) == 0:
        return 0.0
    
    pers1 = dgm1[:, 1] - dgm1[:, 0]
    pers2 = dgm2[:, 1] - dgm2[:, 0]
    
    pers1 = np.sort(pers1[np.isfinite(pers1)])
    pers2 = np.sort(pers2[np.isfinite(pers2)])
    
    # Interpolate to same length
    n = max(len(pers1), len(pers2))
    p1_interp = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(pers1)), pers1)
    p2_interp = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(pers2)), pers2)
    
    return float(np.mean(np.abs(p1_interp - p2_interp)))


def run_tda_pipeline(
    patch: np.ndarray,
    max_dimension: int = 1,
    max_edge_length: float = 2.0,
    max_points: int = 1000,
    compute_betti: bool = True,
    compute_pi: bool = True,
    compare_gaussian: bool = True,
    n_gaussian_samples: int = 5,
) -> dict:
    """
    Run the full TDA analysis pipeline on a preprocessed patch.
    
    Args:
        patch: 2D preprocessed CMB patch
        max_dimension: Max homology dimension
        max_edge_length: Max edge length for Rips
        max_points: Max points for subsampling
        compute_betti: Whether to compute Betti curves
        compute_pi: Whether to compute persistence images
        compare_gaussian: Whether to compare against Gaussian null
        n_gaussian_samples: Number of Gaussian comparison samples
    
    Returns:
        Comprehensive TDA results dictionary
    """
    results = {}
    
    # 1. Persistence diagram
    pd_result = compute_persistence_diagram(patch, max_dimension, max_edge_length, max_points)
    results["persistence_diagram"] = pd_result["pairs"]
    results["n_features"] = pd_result["n_features"]
    
    # 2. Betti curves
    if compute_betti:
        results["betti_curves"] = compute_betti_curves(pd_result["raw_diagrams"])
    
    # 3. Persistence image
    if compute_pi and len(pd_result["raw_diagrams"]) > 0:
        # Use H0 diagram for persistence image
        h0_dgm = pd_result["raw_diagrams"][0]
        if len(h0_dgm) > 0:
            pi = compute_persistence_image(h0_dgm, resolution=(20, 20))
            results["persistence_image"] = pi.tolist()
        else:
            results["persistence_image"] = np.zeros((20, 20)).tolist()
    
    # 4. Gaussian comparison
    if compare_gaussian:
        results["gaussian_comparison"] = _compare_with_gaussian(
            patch, pd_result["raw_diagrams"], n_gaussian_samples, max_dimension, max_edge_length, max_points
        )
    
    # 5. Summary statistics
    all_persistences = []
    for pair in pd_result["pairs"]:
        all_persistences.append(pair["death"] - pair["birth"])
    
    results["summary"] = {
        "total_features": len(pd_result["pairs"]),
        "max_persistence": float(max(all_persistences)) if all_persistences else 0.0,
        "mean_persistence": float(np.mean(all_persistences)) if all_persistences else 0.0,
        "std_persistence": float(np.std(all_persistences)) if all_persistences else 0.0,
        "features_by_dimension": pd_result["n_features"],
    }
    
    # 6. Map preview (downsampled for JSON transport)
    preview_size = min(64, patch.shape[0])
    if patch.shape[0] > preview_size:
        from scipy.ndimage import zoom
        factor = preview_size / patch.shape[0]
        preview = zoom(patch, factor)
    else:
        preview = patch
    results["map_preview"] = preview.tolist()
    
    return results


def _compare_with_gaussian(
    patch: np.ndarray,
    real_diagrams: list,
    n_samples: int,
    max_dimension: int,
    max_edge_length: float,
    max_points: int,
) -> dict:
    """
    Compare real TDA results against Gaussian null hypothesis.
    Generates Gaussian random fields with same statistics and computes
    Wasserstein distances.
    """
    h, w = patch.shape
    mean = float(np.nanmean(patch))
    std = float(np.nanstd(patch))
    
    wasserstein_distances = []
    gaussian_feature_counts = []
    
    for i in range(n_samples):
        # Generate Gaussian random field with same statistics
        np.random.seed(1000 + i)
        gaussian_patch = np.random.normal(mean, max(std, 1e-10), (h, w))
        
        # Smooth to approximate CMB correlations
        try:
            from scipy.ndimage import gaussian_filter
            gaussian_patch = gaussian_filter(gaussian_patch, sigma=2.0)
            # Re-normalize to match original stats
            gaussian_patch = (gaussian_patch - gaussian_patch.mean()) / max(gaussian_patch.std(), 1e-10) * std + mean
        except ImportError:
            pass
        
        # Compute persistence on Gaussian sample
        gauss_result = compute_persistence_diagram(gaussian_patch, max_dimension, max_edge_length, max_points)
        
        # Compute Wasserstein distances per dimension
        dists = {}
        for dim in range(min(len(real_diagrams), len(gauss_result["raw_diagrams"]))):
            d = compute_wasserstein_distance(
                real_diagrams[dim],
                gauss_result["raw_diagrams"][dim]
            )
            dists[f"H{dim}"] = d
        
        wasserstein_distances.append(dists)
        gaussian_feature_counts.append(gauss_result["n_features"])
    
    # Compute summary
    avg_distances = {}
    for key in wasserstein_distances[0]:
        values = [wd[key] for wd in wasserstein_distances]
        avg_distances[key] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "values": [float(v) for v in values],
        }
    
    # Simple non-Gaussianity test: is the average Wasserstein distance significant?
    is_non_gaussian = {}
    for key, dist_info in avg_distances.items():
        # If mean distance > 2*std, flag as potentially non-Gaussian
        threshold = dist_info["std"] * 2 if dist_info["std"] > 0 else dist_info["mean"] * 0.5
        is_non_gaussian[key] = dist_info["mean"] > threshold if threshold > 0 else False
    
    return {
        "wasserstein_distances": avg_distances,
        "is_non_gaussian": is_non_gaussian,
        "n_gaussian_samples": n_samples,
        "gaussian_feature_counts": gaussian_feature_counts,
    }
