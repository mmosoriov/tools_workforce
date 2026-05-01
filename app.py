# app.py
import os
import time

from flask import Flask, request, redirect, url_for, render_template_string
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)
# A starting list of teams as default
SEED_TEAMS = [
    {"id": 1, "name": "Argentina", "flag": "🇦🇷"},
    {"id": 2, "name": "France", "flag": "🇫🇷"},
    {"id": 3, "name": "Brazil", "flag": "🇧🇷"},
]

mongo_client: MongoClient | None = None
teams_coll = None


def _mongo_uri() -> str:
    return os.environ.get("MONGO_URI", "mongodb://localhost:27017/worldcup")


def _collection_name() -> str:
    return os.environ.get("MONGO_COLLECTION", "teams")

# Wait for database to start
def _wait_for_mongo(client: MongoClient, attempts: int = 30, delay_s: float = 1.0) -> None:
    last_err: Exception | None = None
    for _ in range(attempts):
        try:
            client.admin.command("ping")
            return
        except PyMongoError as e:
            last_err = e
            time.sleep(delay_s)
    raise RuntimeError(f"Could not connect to MongoDB after {attempts} attempts") from last_err


def init_db() -> None:
    global mongo_client, teams_coll

    uri = _mongo_uri()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    _wait_for_mongo(client)

    db = client.get_default_database()
    if db is None:
        db = client["worldcup"]

    coll = db[_collection_name()]
    coll.create_index("id", unique=True)

    if coll.count_documents({}) == 0:
        coll.insert_many(SEED_TEAMS)

    mongo_client = client
    teams_coll = coll


init_db()

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


def list_teams():
    assert teams_coll is not None
    return list(teams_coll.find({}, {"_id": 0}).sort("id", 1))


def next_team_id() -> int:
    assert teams_coll is not None
    doc = teams_coll.find_one(sort=[("id", -1)], projection={"id": 1})
    return (doc["id"] + 1) if doc else 1


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE, teams=list_teams())


@app.route("/add", methods=["POST"])
def add_team():
    assert teams_coll is not None
    name = request.form.get("name")
    flag = request.form.get("flag")

    if name and flag:
        teams_coll.insert_one(
            {"id": next_team_id(), "name": name.strip(), "flag": flag.strip()}
        )

    return redirect(url_for("home"))


@app.route("/delete/<int:team_id>", methods=["POST"])
def delete_team(team_id):
    assert teams_coll is not None
    teams_coll.delete_one({"id": team_id})
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)
