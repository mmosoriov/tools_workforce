# app.py
import os
import json
from flask import Flask, jsonify, render_template_string
from diagnostics import collect_report

CONFIG_PATH = "config.json"

def load_config(path: str = CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

app = Flask(__name__)

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

@app.get("/api/report")
def report():
    config = load_config()
    return jsonify(collect_report(config))

@app.get("/")
def home():
    config = load_config()
    report_data = collect_report(config)
    html = """
    <h1>{{ app_name }}</h1>
    <p>Focus: {{ focus }}</p>
    <pre>{{ report }}</pre>
    <p>Try: <a href="/api/report">/api/report</a></p>
    """
    return render_template_string(
        html,
        app_name=config.get("app_name", "portfolio-flask-starter"),
        focus=config.get("focus", "A"),
        report=report_data,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
