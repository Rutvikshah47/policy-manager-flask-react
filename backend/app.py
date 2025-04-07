from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import os, datetime, cloudinary.uploader
import io, csv
from dotenv import load_dotenv
import cloudinary
from dotenv import load_dotenv; load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
load_dotenv()

print("Mongo URI:", os.getenv("MONGO_URI"))
print("Cloud Name:", os.getenv("CLOUDINARY_CLOUD_NAME"))

print("Connecting to MongoDB...")
client = MongoClient(os.getenv("MONGO_URI"))
db = client["policy_db"]
policies = db["policies"]

CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
API_KEY = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
print("Configuring Cloudinary...")
cloudinary.config(cloud_name=CLOUD_NAME, api_key=API_KEY, api_secret=API_SECRET)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    print("Login attempt with:", data)
    if data["username"] == "ramya" and data["password"] == "ramya.123":
        print("Login successful")
        return jsonify({"status": "success"})
    print("Login failed")
    return jsonify({"status": "fail"}), 401

@app.route("/add_policy", methods=["POST"])
def add_policy():
    data = request.form.to_dict()
    print("Received policy data:", data)

    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.content_type.startswith("image/"):
        return jsonify({"error": "Invalid file type. Only images are allowed."}), 400

    try:
        print("Uploading file to Cloudinary...")
        upload_result = cloudinary.uploader.upload(file)
        print("Upload result:", upload_result)
    except Exception as e:
        print("Upload failed:", str(e))
        return jsonify({"error": str(e)}), 500

    data['file_url'] = upload_result['secure_url']
    data['created_at'] = datetime.datetime.utcnow()
    policies.insert_one(data)
    print("Policy added to database.")
    return jsonify({"status": "added"})


@app.route("/get_policies", methods=["GET"])
def get_policies():
    search = request.args.get("search", "")
    status_filter = request.args.get("status", "all")
    print(f"Fetching policies. Search='{search}', Status='{status_filter}'")
    results = []
    for p in policies.find():
        match = any(search.lower() in str(p.get(k, '')).lower() for k in ["customer_name", "car_number", "policy_name"])
        if not match:
            continue
        if status_filter != "all":
            expired = datetime.datetime.strptime(p.get("expiry_date", "9999-12-31"), "%Y-%m-%d") < datetime.datetime.utcnow()
            if status_filter == "active" and expired:
                continue
            if status_filter == "expired" and not expired:
                continue
        p["_id"] = str(p["_id"])
        results.append(p)
    print(f"Returning {len(results)} policies")
    return jsonify(results)

@app.route("/export", methods=["GET"])
def export():
    print("Exporting policies to CSV...")
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Customer Name", "Car Number", "Policy Name", "Expiry Date", "Premium Amount"])
    for p in policies.find():
        writer.writerow([
            p.get("customer_name", ""),
            p.get("car_number", ""),
            p.get("policy_name", ""),
            p.get("expiry_date", ""),
            p.get("premium_amount", "")
        ])
    output.seek(0)
    print("CSV export complete.")
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='policies.csv')

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True)
