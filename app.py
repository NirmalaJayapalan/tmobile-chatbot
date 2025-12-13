from flask import Flask, render_template, request, jsonify
import openai
import os
import json

app = Flask(__name__)

# ---------------------------
# Set your OpenAI API key
# ---------------------------
openai.api_key = os.getenv("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")  # or replace with your key

# ---------------------------
# T-Mobile structured data
# ---------------------------
telecom_data = {
    "devices": [
        {"model": "Samsung Galaxy A12", "type": "Android", "price": 180, "budget": "low", "screen": "6.5 inch", "storage": "64GB"},
        {"model": "iPhone 13", "type": "iOS", "price": 799, "budget": "high", "screen": "6.1 inch", "storage": "128GB"},
        {"model": "Apple Watch SE", "type": "Watch", "price": 279, "budget": "medium", "features": ["Fitness Tracking","Heart Rate Monitor"]},
        {"model": "iPad Mini", "type": "Tablet", "price": 499, "budget": "high", "screen": "8.3 inch", "storage": "64GB"},
        {"model": "iPhone 14 Pro", "type": "iOS", "price": 999, "budget": "high", "screen": "6.1 inch", "storage": "256GB"},
        {"model": "Samsung Galaxy S22", "type": "Android", "price": 899, "budget": "high", "screen": "6.2 inch", "storage": "128GB"}
    ],
    "plans": [
        {"name": "Essentials", "price_per_month": 60, "lines": 1, "data": "unlimited", "features": ["5G included", "no hotspot"]},
        {"name": "Magenta Max", "price_per_month": 85, "lines": 1, "data": "unlimited", "features": ["5G included", "unlimited hotspot", "HD streaming"]},
        {"name": "Magenta Plus", "price_per_month": 75, "lines": 1, "data": "unlimited", "features": ["5G included", "hotspot 10GB", "HD streaming"]}
    ],
    "promotions": [
        {"description": "Trade in any phone, get up to $500 credit."},
        {"description": "Free Apple Watch SE with Magenta Max plan on new line activation."},
        {"description": "Get 50% off second line on Essentials plan."}
    ],
    "services": [
        {"name": "Hotspot Add-on", "price_per_month": 15, "description": "Add mobile hotspot to any plan"},
        {"name": "International Roaming", "price_per_month": 10, "description": "Access data and calls while abroad"},
        {"name": "Premium Support", "price_per_month": 5, "description": "Priority customer support and faster service"}
    ]
}

# ---------------------------
# Serve Frontend
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------------------
# Handle User Queries
# ---------------------------
@app.route("/ask", methods=["POST"])
def ask():
    user_query = request.json.get("query", "").lower()

    # ---------------------------
    # Filter Devices
    # ---------------------------
    devices = []
    for d in telecom_data["devices"]:
        if "android" in user_query and d["type"].lower() != "android":
            continue
        if "ios" in user_query and d["type"].lower() != "ios":
            continue
        if "watch" in user_query and d["type"].lower() != "watch":
            continue
        if "tablet" in user_query and d["type"].lower() != "tablet":
            continue
        if "low" in user_query and d.get("budget", "") != "low":
            continue
        if "medium" in user_query and d.get("budget", "") != "medium":
            continue
        if "high" in user_query and d.get("budget", "") != "high":
            continue
        if "under $" in user_query:
            try:
                price_limit = int(user_query.split("under $")[1].split()[0])
                if d["price"] > price_limit:
                    continue
            except:
                pass
        if "over $" in user_query:
            try:
                price_limit = int(user_query.split("over $")[1].split()[0])
                if d["price"] < price_limit:
                    continue
            except:
                pass
        devices.append(d)

    # ---------------------------
    # Filter Plans
    # ---------------------------
    plans = []
    for p in telecom_data["plans"]:
        if any(word in p["name"].lower() for word in user_query.split()):
            plans.append(p)
        elif "unlimited" in user_query and p["data"] == "unlimited":
            plans.append(p)
        elif "hotspot" in user_query and any("hotspot" in f.lower() for f in p["features"]):
            plans.append(p)
        elif "family" in user_query and "family" in p["name"].lower():
            plans.append(p)

    # ---------------------------
    # Filter Promotions
    # ---------------------------
    promotions = []
    for promo in telecom_data["promotions"]:
        if any(word in promo["description"].lower() for word in user_query.split()):
            promotions.append(promo)

    # ---------------------------
    # Filter Services
    # ---------------------------
    services = []
    for s in telecom_data["services"]:
        if any(word in s["name"].lower() or word in s["description"].lower() for word in user_query.split()):
            services.append(s)

    # ---------------------------
    # Fallback to OpenAI if nothing matches
    # ---------------------------
    if not any([devices, plans, promotions, services]):
        context = "You are a T-Mobile assistant. Use the following data to answer user queries:\n\n"

        # Add devices
        context += "Devices:\n"
        for d in telecom_data["devices"]:
            device_info = f"- {d['model']}: {d['type']}, ${d['price']}, budget: {d.get('budget','')}"
            if 'screen' in d:
                device_info += f", {d['screen']}"
            if 'storage' in d:
                device_info += f", {d['storage']}"
            if 'features' in d:
                device_info += f", features: {', '.join(d['features'])}"
            context += device_info + "\n"

        # Plans
        context += "\nPlans:\n"
        for p in telecom_data["plans"]:
            plan_info = f"- {p['name']}: ${p['price_per_month']}/month, {p['lines']} line(s), data: {p['data']}, features: {', '.join(p['features'])}"
            context += plan_info + "\n"

        # Promotions
        context += "\nPromotions:\n"
        for promo in telecom_data["promotions"]:
            context += f"- {promo['description']}\n"

        # Services
        context += "\nServices:\n"
        for s in telecom_data["services"]:
            context += f"- {s['name']}: ${s['price_per_month']}/month, {s['description']}\n"

        context += """
Instructions:
1. ONLY use the data above.
2. Output valid JSON with keys: "devices", "plans", "promotions", "services".
3. Each key should have an array of matching entries or empty array.
"""

        prompt = context + f"\nUser query: {user_query}\n"

        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                max_tokens=500,
                temperature=0
            )
            answer_text = response.choices[0].text.strip()
            try:
                answer_json = json.loads(answer_text)
            except:
                answer_json = {"devices": [], "plans": [], "promotions": [], "services": []}
        except:
            answer_json = {"devices": [], "plans": [], "promotions": [], "services": []}

        return jsonify(answer_json)

    # ---------------------------
    # Return filtered results
    # ---------------------------
    return jsonify({
        "devices": devices,
        "plans": plans,
        "promotions": promotions,
        "services": services
    })


# ---------------------------
# Run the Flask app
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

