import pytest

class TestAuth:
    def test_register(self, client):
        res = client.post("/api/register", json={"email": "new@example.com", "username": "newuser", "password": "Password123"})
        assert res.status_code == 201
        assert "access_token" in res.json()

    def test_login(self, client, auth_token):
        res = client.post("/api/login", json={"email": "test@example.com", "password": "Password123"})
        assert res.status_code == 200

    def test_login_wrong_password(self, client, auth_token):
        res = client.post("/api/login", json={"email": "test@example.com", "password": "Wrong"})
        assert res.status_code == 401

class TestBREAD:
    def test_add(self, client):
        res = client.post("/api/calculations", json={"operation": "add", "operand_a": 10, "operand_b": 5})
        assert res.status_code == 201
        assert res.json()["result"] == 15

    def test_browse(self, client):
        client.post("/api/calculations", json={"operation": "add", "operand_a": 1, "operand_b": 1})
        res = client.get("/api/calculations")
        assert res.status_code == 200
        assert res.json()["total"] >= 1

    def test_read(self, client):
        create = client.post("/api/calculations", json={"operation": "multiply", "operand_a": 6, "operand_b": 7})
        id = create.json()["id"]
        res = client.get(f"/api/calculations/{id}")
        assert res.status_code == 200
        assert res.json()["result"] == 42

    def test_edit(self, client):
        create = client.post("/api/calculations", json={"operation": "add", "operand_a": 1, "operand_b": 1})
        id = create.json()["id"]
        res = client.put(f"/api/calculations/{id}", json={"operation": "subtract", "operand_a": 10, "operand_b": 3})
        assert res.status_code == 200
        assert res.json()["result"] == 7

    def test_delete(self, client):
        create = client.post("/api/calculations", json={"operation": "add", "operand_a": 1, "operand_b": 1})
        id = create.json()["id"]
        res = client.delete(f"/api/calculations/{id}")
        assert res.status_code == 204

    def test_division_by_zero(self, client):
        res = client.post("/api/calculations", json={"operation": "divide", "operand_a": 10, "operand_b": 0})
        assert res.status_code == 422

    def test_health(self, client):
        res = client.get("/health")
        assert res.status_code == 200
