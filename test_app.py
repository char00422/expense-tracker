from app import app, expenses, calculate_total, category_totals

client = app.test_client()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_calculate_total():
    items = [{"amount": 100.5, "category": "Food"}, {"amount": 49.5, "category": "Travel"}]
    assert calculate_total(items) == 150.0


def test_category_totals():
    items = [
        {"amount": 100, "category": "Food"},
        {"amount": 50, "category": "Food"},
        {"amount": 30, "category": "Travel"},
    ]
    assert category_totals(items) == {"Food": 150, "Travel": 30}


def test_add_expense_via_api():
    expenses.clear()
    r = client.post("/api/expenses", json={"title": "Lunch", "amount": 120, "category": "Food"})
    assert r.status_code == 201
    data = client.get("/api/expenses").get_json()
    assert data["total"] == 120


def test_invalid_amount_rejected():
    r = client.post("/api/expenses", json={"title": "Bad", "amount": -5})
    assert r.status_code == 400
