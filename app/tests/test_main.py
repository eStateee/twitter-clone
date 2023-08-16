
def test_main(test_client):
    response = test_client.get("/api/test")
    assert response.status_code == 200
    assert response.json() == {"result": 'True'}
