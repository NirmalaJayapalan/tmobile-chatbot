from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__)

# ---------------------------
# Set your OpenAI API key
# ---------------------------
openai.api_key = os.getenv("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")  # or set your key directly like "sk-XXXX"

# ---------------------------
# T-Mobile structured data
# ---------------------------
telecom_data = {
    "devices": [
        {"model": "Samsung Galaxy A12", "type": "Android", "price": 180, "budget": "low", "screen": "6.5 inch", "storage": "64GB"},
        {"model": "iPhone 13", "type": "iOS", "price": 799, "budget": "high", "screen": "6.1 inch", "storage": "128GB"},
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

# ---------------------------
# Route to serve frontend
# ---------------------------
@app.route("/")
def index():
    return render_template("index.html")


# ---------------------------
# Route to handle user queries
# ---------------------------
@app.route("/ask", methods=["POST"])
def ask():
    user_query = request.json.get("query", "")

    # Build context string for OpenAI
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

    # Add plans
    context += "\nPlans:\n"
    for p in telecom_data["plans"]:
        plan_info = f"- {p['name']}: ${p['price_per_month']}/month, {p['lines']} line(s), data: {p['data']}, features: {', '.join(p['features'])}"
        context += plan_info + "\n"

    # Add promotions
    context += "\nPromotions:\n"
    for promo in telecom_data["promotions"]:
        context += f"- {promo['description']}\n"

    # Instruction for JSON output
    context += """
Answer user queries using only this data. 
Output structured JSON in this format:
{
  "devices": [],
  "plans": [],
  "promotions": []
}
"""

    # Combine context with user query
    prompt = context + f"\nUser query: {user_query}\n"

    # Call OpenAI GPT
    try:
        response = openai.Completion.create(
            model="text-davinci-003",  # You can replace with your fine-tuned model
            prompt=prompt,
            max_tokens=400,
            temperature=0
        )

        # Parse response
        answer_text = response.choices[0].text.strip()
        try:
            # Evaluate JSON safely
            answer_json = eval(answer_text)
        except:
            answer_json = {"devices": [], "plans": [], "promotions": []}

    except Exception as e:
        print("OpenAI API error:", e)
        answer_json = {"devices": [], "plans": [], "promotions": []}

    return jsonify(answer_json)


# ---------------------------
# Run the Flask app
# ---------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

