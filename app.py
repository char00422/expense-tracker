from flask import Flask, request, jsonify, redirect, render_template_string

app = Flask(__name__)
expenses = []


def calculate_total(items):
    return round(sum(e["amount"] for e in items), 2)


def category_totals(items):
    totals = {}
    for e in items:
        totals[e["category"]] = round(totals.get(e["category"], 0) + e["amount"], 2)
    return totals


PAGE = """
<!doctype html>
<title>Expense Tracker</title>
<body style="font-family:sans-serif;max-width:560px;margin:40px auto;padding:0 12px">
<h2>Expense Tracker</h2>
<form method="post" action="/add">
  <input name="title" placeholder="What for?" required>
  <input name="amount" type="number" step="0.01" min="0.01" placeholder="Amount" required>
  <select name="category">
    <option>Food</option><option>Travel</option><option>Study</option><option>Other</option>
  </select>
  <button>Add</button>
</form>
<h3>Total: Rs. {{ total }}</h3>
<table border="1" cellpadding="6" style="border-collapse:collapse;width:100%">
  <tr><th>Title</th><th>Category</th><th>Amount</th></tr>
  {% for e in expenses %}
  <tr><td>{{ e.title }}</td><td>{{ e.category }}</td><td>{{ e.amount }}</td></tr>
  {% endfor %}
</table>
<h4>By category</h4>
<ul>{% for c, t in cats.items() %}<li>{{ c }}: Rs. {{ t }}</li>{% endfor %}</ul>
<small>Running in a Docker container, deployed via CI/CD</small>
</body>
"""


@app.route("/")
def home():
    return render_template_string(
        PAGE, expenses=expenses, total=calculate_total(expenses), cats=category_totals(expenses)
    )


@app.route("/add", methods=["POST"])
def add():
    try:
        amount = float(request.form.get("amount", ""))
    except ValueError:
        return redirect("/")
    title = request.form.get("title", "").strip()
    if title and amount > 0:
        expenses.append({"title": title, "amount": amount,
                         "category": request.form.get("category", "Other")})
    return redirect("/")


@app.route("/api/expenses", methods=["GET", "POST"])
def api_expenses():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        title = str(data.get("title", "")).strip()
        try:
            amount = float(data.get("amount"))
        except (TypeError, ValueError):
            return jsonify(error="amount must be a number"), 400
        if not title or amount <= 0:
            return jsonify(error="title and positive amount required"), 400
        item = {"title": title, "amount": amount, "category": data.get("category", "Other")}
        expenses.append(item)
        return jsonify(item), 201
    return jsonify(expenses=expenses, total=calculate_total(expenses))


@app.route("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
