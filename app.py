from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Sample T-Mobile data
telecom_data = {
    "devices": [
        {"model": "Samsung Galaxy A12", "type": "Android", "price": 180, "multiline": True, "budget": "low", "screen": "6.5 inch", "storage": "64GB"},
        {"model": "iPhone 13", "type": "iOS", "price": 799, "multiline": True, "budget": "high", "screen": "6.1 inch", "storage": "128GB"},
        {"model": "Apple Watch SE", "type": "Watch", "price": 279, "budget": "medium", "features": ["Fitness Tracking","Heart Rate Monitor"]},
        {"model": "iPad Mini", "type": "Tablet", "price": 499, "budget": "high", "screen": "8.3 inch", "storage": "64GB"}
    ],
    "plans": [
        {"name": "Essentials", "price_per_month": 60, "lines": 1, "data": "unlimited", "features": ["5G included", "no hotspot"]},
        {"name": "Magenta Max", "price_per_month": 85, "lines": 1, "data": "unlimited", "features": ["5G included", "unlimited hotspot", "HD streaming"]}
    ],
    "promotions": [
        {"description": "Trade in any phone, get up to $500 credit."},
        {"description": "Free Apple Watch SE with Magenta Max plan on new line activation."}
    ]
}

def find_devices(query):
    query_lower = query.lower()
    results = []
    for d in telecom_data["devices"]:
        if "android" in query_lower and d["type"].lower() != "android": continue
        if "iphone" in query_lower and d["type"].lower() != "ios": continue
        if "watch" in query_lower and d["type"].lower() != "watch": continue
        if "tablet" in query_lower and d["type"].lower() != "tablet": continue
        if "low" in query_lower and d.get("budget", "") != "low": continue
        if "medium" in query_lower and d.get("budget", "") != "medium": continue
        if "high" in query_lower and d.get("budget", "") != "high": continue
        results.append(d)
    return results

def find_plans(query):
    query_lower = query.lower()
    return [p for p in telecom_data["plans"] if any(word in p["name"].lower() for word in query_lower.split())]

def find_promotions(query):
    query_lower = query.lower()
    return [promo for promo in telecom_data["promotions"] if any(word in promo["description"].lower() for word in query_lower.split())]

# Correct route to serve your HTML
@app.route("/")
def index():
    return render_template("index.html")  # ✅ Load your chatbot UI

@app.route("/ask", methods=["POST"])
def ask():
    user_query = request.json.get("query", "")
    return jsonify({
        "devices": find_devices(user_query),
        "plans": find_plans(user_query),
        "promotions": find_promotions(user_query)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
