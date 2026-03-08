from backend.workers.celery_worker import celery_app
from backend.models.schemas import PreprocessRequest

class PreprocessingService:
    @staticmethod
    def enqueue_preprocessing(request: PreprocessRequest) -> str:
        \"\"\"
        Pushes a CMB Array Preprocessing job to the Celery Worker Process.
        \"\"\"
        job = celery_app.send_task(
            "backend.workers.celery_worker.preprocess_cmb_map",
            kwargs={
                "map_id": request.map_id,
                "mask_galactic_plane": request.mask_galactic_plane,
                "mask_point_sources": request.mask_point_sources,
                "scale": request.scale,
            }
        )
        return job.id
