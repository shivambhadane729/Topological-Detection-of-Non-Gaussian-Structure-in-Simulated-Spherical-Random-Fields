import json
import os
from backend.configs import settings

class ResultService:
    @staticmethod
    def get_job_status(job_id: str) -> dict:
        \"\"\"
        Retrieves the status of a Celery job.
        In a real scenario, this queries the Celery Redis backend via AsyncResult.
        \"\"\"
        from celery.result import AsyncResult
        from backend.workers.celery_worker import celery_app
        
        result = AsyncResult(job_id, app=celery_app)
        
        response = {
            "job_id": job_id,
            "status": result.state
        }
        
        if result.state == "SUCCESS":
            response["result"] = result.result
        elif result.state == "FAILURE":
            response["error"] = str(result.info)
            
        return response

    @staticmethod
    def get_topology_result(map_id: str) -> dict:
        \"\"\"
        Retrieves saved topology results from storage.
        \"\"\"
        result_file = os.path.join(settings.TOPOLOGY_RESULT_STORAGE, f"{map_id}_result.json")
        if not os.path.exists(result_file):
            raise FileNotFoundError("Results not found for this map.")
            
        with open(result_file, "r") as f:
            return json.load(f)
