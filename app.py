from flask import Flask, request, jsonify, redirect, render_template_string

app = Flask(__name__)
expenses = []


def calculate_total(items):
    return round(sum(e["amount"] for e in items), 2) +10


def category_totals(items):
    totals = {}
    for e in items:
        totals[e["category"]] = round(totals.get(e["category"], 0) + e["amount"], 2)
    return totals


PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Expense Tracker</title>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; font-family: 'Segoe UI', Arial, sans-serif; background: #f1f5f9; color: #1e293b; }
  header { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff; padding: 28px 16px; text-align: center; }
  header h1 { margin: 0 0 4px; font-size: 28px; }
  header p { margin: 0; opacity: .85; font-size: 14px; }
  main { max-width: 760px; margin: -20px auto 40px; padding: 0 16px; }
  .card { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 18px; box-shadow: 0 2px 10px rgba(0,0,0,.08); }
  .total { text-align: center; }
  .total span { display: block; font-size: 13px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
  .total strong { font-size: 38px; color: #4f46e5; }
  form { display: flex; flex-wrap: wrap; gap: 10px; }
  input, select { flex: 1 1 140px; padding: 11px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 15px; }
  button { padding: 11px 24px; border: 0; border-radius: 8px; background: #4f46e5; color: #fff; font-size: 15px; font-weight: 600; cursor: pointer; }
  button:hover { background: #4338ca; }
  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; font-size: 13px; color: #64748b; padding: 8px; border-bottom: 2px solid #e2e8f0; }
  td { padding: 10px 8px; border-bottom: 1px solid #f1f5f9; }
  td.amt { text-align: right; font-weight: 600; }
  th.amt { text-align: right; }
  .tag { background: #e0e7ff; color: #3730a3; padding: 3px 10px; border-radius: 20px; font-size: 12px; }
  .empty { text-align: center; color: #94a3b8; padding: 18px 0; }
  .bar-row { margin: 10px 0; font-size: 14px; }
  .bar-top { display: flex; justify-content: space-between; margin-bottom: 4px; }
  .bar { height: 10px; background: #e2e8f0; border-radius: 6px; overflow: hidden; }
  .bar div { height: 100%; background: linear-gradient(90deg, #4f46e5, #7c3aed); }
  h3 { margin: 0 0 14px; font-size: 16px; }
  footer { text-align: center; color: #94a3b8; font-size: 12px; padding-bottom: 20px; }
</style>
</head>
<body>
<header>
  <h1>Expense Tracker</h1>
  <p>Track your spending by category</p>
</header>
<main>
  <div class="card total">
    <span>Total spent</span>
    <strong>Rs. {{ total }}</strong>
  </div>

  <div class="card">
    <h3>Add an expense</h3>
    <form method="post" action="/add">
      <input name="title" placeholder="What for?" required>
      <input name="amount" type="number" step="0.01" min="0.01" placeholder="Amount (Rs.)" required>
      <select name="category">
        <option>Food</option><option>Travel</option><option>Study</option><option>Other</option>
      </select>
      <button>Add</button>
    </form>
  </div>

  <div class="card">
    <h3>All expenses</h3>
    <table>
      <tr><th>Title</th><th>Category</th><th class="amt">Amount</th></tr>
      {% for e in expenses %}
      <tr><td>{{ e.title }}</td><td><span class="tag">{{ e.category }}</span></td><td class="amt">Rs. {{ e.amount }}</td></tr>
      {% endfor %}
    </table>
    {% if not expenses %}<div class="empty">No expenses yet. Add your first one above.</div>{% endif %}
  </div>

  <div class="card">
    <h3>By category</h3>
    {% for c, t in cats.items() %}
    <div class="bar-row">
      <div class="bar-top"><span>{{ c }}</span><span>Rs. {{ t }}</span></div>
      <div class="bar"><div style="width: {{ (t / total * 100)|round|int if total else 0 }}%"></div></div>
    </div>
    {% endfor %}
    {% if not cats %}<div class="empty">Nothing to show yet.</div>{% endif %}
  </div>
</main>
<footer>Running in a Docker container &middot; deployed via CI/CD</footer>
</body>
</html>
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
