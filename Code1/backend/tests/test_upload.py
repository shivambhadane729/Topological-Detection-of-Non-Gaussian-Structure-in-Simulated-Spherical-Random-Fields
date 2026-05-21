"""Test upload endpoint."""
import io
def test_upload_invalid_type(client):
    f = io.BytesIO(b"not a fits file")
    r = client.post("/api/upload", files={"file": ("test.txt", f, "text/plain")})
    assert r.status_code == 400

def test_datasets_list(client):
    r = client.get("/api/datasets")
    assert r.status_code == 200
    d = r.json()
    assert "datasets" in d
    assert d["total"] > 0
