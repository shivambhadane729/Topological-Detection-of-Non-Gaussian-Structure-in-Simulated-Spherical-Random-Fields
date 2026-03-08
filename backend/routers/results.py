from fastapi import APIRouter

router = APIRouter(prefix="/results", tags=["Results"])

@router.get("/")
def get_results():
    return {
        "betti_curve": [1, 3, 2],
        "persistence_diagram": [[0.1, 0.3], [0.2, 0.5]]
    }