"""CosmoPH - Helper Utilities"""
import numpy as np

def array_to_list(arr):
    if isinstance(arr, np.ndarray): return arr.tolist()
    return arr

def safe_json(obj):
    if isinstance(obj, np.ndarray): return obj.tolist()
    if isinstance(obj, (np.float32, np.float64)): return float(obj)
    if isinstance(obj, (np.int32, np.int64)): return int(obj)
    if isinstance(obj, dict): return {k: safe_json(v) for k, v in obj.items()}
    if isinstance(obj, list): return [safe_json(v) for v in obj]
    return obj
