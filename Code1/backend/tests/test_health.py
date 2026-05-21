"""Test health endpoint."""
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "healthy"
    assert d["app"] == "CosmoPH"
