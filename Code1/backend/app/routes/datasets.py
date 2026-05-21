"""CosmoPH - Dataset Routes"""
from fastapi import APIRouter, HTTPException
from app.services.data_loader import get_dataset_registry, generate_demo_data, DATASET_REGISTRY

router = APIRouter()

@router.get("/datasets")
async def list_datasets():
    generate_demo_data()
    reg = get_dataset_registry()
    datasets = []
    for did, info in reg.items():
        datasets.append({
            "id": info["id"], "name": info["name"],
            "filename": info["filename"], "category": info["category"],
            "description": info["description"], "nside": info.get("nside"),
            "is_available": info["is_available"],
            "file_size_mb": info.get("file_size_mb"),
            "source_url": info.get("source_url"),
        })
    return {"datasets": datasets, "total": len(datasets)}

@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    reg = get_dataset_registry()
    if dataset_id not in reg:
        raise HTTPException(404, f"Dataset not found: {dataset_id}")
    return reg[dataset_id]
