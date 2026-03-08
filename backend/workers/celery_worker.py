import os
import time
import json
import warnings
from celery import Celery
from backend.configs import settings

# Suppress warnings from healpy/scikit for cleaner logs
warnings.filterwarnings("ignore")

celery_app = Celery(
    "cosmoph_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.task_routes = {
    "backend.workers.celery_worker.*": {"queue": "cosmoph"}
}
celery_app.conf.update(task_track_started=True)


@celery_app.task(bind=True, name="backend.workers.celery_worker.preprocess_cmb_map")
def preprocess_cmb_map(self, map_id: str, mask_galactic_plane: bool, mask_point_sources: bool, scale: float = None):
    # This is where the CMB Map Preprocessing pipeline runs
    print(f"Starting preprocessing for map_id: {map_id}")
    file_path = os.path.join(settings.CMB_FILE_STORAGE, f"{map_id}.fits")
    
    # Simulate processing time (importing healpy takes a bit, so we simulate real work here)
    time.sleep(2)
    
    # In a real implementation:
    # 1. import healpy as hp
    # 2. map_data = hp.read_map(file_path)
    # 3. apply masks and scales...
    # 4. save preprocessed output
    
    return {
        "status": "completed", 
        "map_id": map_id, 
        "message": "Preprocessing successful"
    }


@celery_app.task(bind=True, name="backend.workers.celery_worker.compute_tda")
def compute_tda(self, map_id: str, max_dimension: int = 2, threshold: float = None):
    # This is where Persistent Homology Computation & Topology Feature Extraction happens
    print(f"Starting TDA computation for map_id: {map_id}")
    
    # Simulate TDA processing 
    time.sleep(3)
    
    # In a real implementation:
    # 1. load preprocessed map data
    # 2. from ripser import ripser
    # 3. diagrams = ripser(map_data, maxdim=max_dimension)['dgms']
    # 4. Extract topological features and run through sklearn classifier
    
    # Mocking Results
    mock_result = {
        "diagrams": [
            {"dimension": 0, "birth": 0.0, "death": 1.5},
            {"dimension": 1, "birth": 1.2, "death": 2.4}
        ],
        "betti_curves": {
            0: [1, 2, 3, 2, 1],
            1: [0, 0, 1, 0, 0]
        },
        "fnl_prediction": 1.25,
        "classification": "Non-Gaussian",
        "confidence_score": 0.89
    }
    
    # Save results to Topology Result Storage
    result_path = os.path.join(settings.TOPOLOGY_RESULT_STORAGE, f"{map_id}_result.json")
    with open(result_path, "w") as f:
        json.dump(mock_result, f)
        
    return {
        "status": "completed", 
        "map_id": map_id,
        "result_path": result_path
    }
