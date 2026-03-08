from backend.workers.celery_worker import celery_app
from backend.models.schemas import TDARequest

class TDAService:
    @staticmethod
    def enqueue_tda_computation(request: TDARequest) -> str:
        \"\"\"
        Pushes a Persistent Homology Computation and Topology Feature Extraction job 
        to the Celery Worker queue.
        \"\"\"
        job = celery_app.send_task(
            "backend.workers.celery_worker.compute_tda",
            kwargs={
                "map_id": request.map_id,
                "max_dimension": request.max_dimension,
                "threshold": request.threshold,
            }
        )
        return job.id
