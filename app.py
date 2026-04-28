# app.py
import os
from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

# 1. In-Memory Data Storage

teams = [
    {"id": 1, "name": "Argentina", "flag": "🇦🇷"},
    {"id": 2, "name": "France", "flag": "🇫🇷"},
    {"id": 3, "name": "Brazil", "flag": "🇧🇷"}
]
next_team_id = 4

# HTML Template with Bootstrap for styling
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>World Cup Teams</title>
    <!-- Using Bootstrap for a quick, clean UI -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .flag-icon { font-size: 4rem; text-align: center; }
        .team-card { transition: transform 0.2s; }
        .team-card:hover { transform: scale(1.05); }
    </style>
</head>
<body>
<div class="container py-5">
    
    <header class="pb-3 mb-4 border-bottom">
        <h1 class="display-5 fw-bold text-center">🏆 World Cup Teams</h1>
    </header>

    <!-- Form to Add a New Team -->
    <div class="card mb-5 shadow-sm max-w-md mx-auto" style="max-width: 500px;">
        <div class="card-body">
            <h5 class="card-title">Add National Team</h5>
            <form action="{{ url_for('add_team') }}" method="POST">
                <div class="mb-3">
                    <label for="name" class="form-label">Country Name</label>
                    <input type="text" class="form-control" name="name" required placeholder="e.g. Spain">
                </div>
                <div class="mb-3">
                    <label for="flag" class="form-label">Flag Emoji</label>
                    <input type="text" class="form-control" name="flag" required placeholder="e.g. 🇪🇸">
                </div>
                <button type="submit" class="btn btn-primary w-100">Add Team</button>
            </form>
        </div>
    </div>

    <!-- Grid displaying all Teams -->
    <div class="row row-cols-1 row-cols-md-3 row-cols-lg-4 g-4">
        {% for team in teams %}
        <div class="col">
            <div class="card h-100 shadow-sm team-card">
                <div class="card-body d-flex flex-column align-items-center">
                    <div class="flag-icon mb-2">{{ team.flag }}</div>
                    <h5 class="card-title text-center">{{ team.name }}</h5>
                    
                    <!-- Form to Delete a Team -->
                    <form action="{{ url_for('delete_team', team_id=team.id) }}" method="POST" class="mt-auto w-100">
                        <button type="submit" class="btn btn-outline-danger w-100 btn-sm">Remove</button>
                    </form>
                </div>
            </div>
        </div>
        {% else %}
        <div class="col-12 text-center text-muted">
            <p>No teams available. Add one above!</p>
        </div>
        {% endfor %}
    </div>

</div>
</body>
</html>
"""

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.route("/", methods=["GET"])
def home():
    # Render the HTML template and pass the teams list
    return render_template_string(HTML_TEMPLATE, teams=teams)

@app.route("/add", methods=["POST"])
def add_team():
    global next_team_id
    
    # Grab data from the traditional HTML form
    name = request.form.get("name")
    flag = request.form.get("flag")
    
    if name and flag:
        teams.append({"id": next_team_id, "name": name, "flag": flag})
        next_team_id += 1
        
    # Redirect back to the home page to see the new data
    return redirect(url_for("home"))

@app.route("/delete/<int:team_id>", methods=["POST"])
def delete_team(team_id):
    global teams
    # Filter out the team with the matching ID
    teams = [team for team in teams if team["id"] != team_id]
    
    # Redirect back to the home page
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
