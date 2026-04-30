# tools_workforce

IDEA:
# Flask World Cup App - Shows the Remaining teams 
 
 GitHub → Jenkins → Docker

• A minimal Flask app with a list of National teams and their flags (add/delete items)

• Docker builds and runs it

• Jenkins pipeline: Checkout → Build Docker image → Run container

• MongoDB persists teams (Compose service + volume)


## Usage

### 1. Start the Application
Build and run the application using Docker Compose in detached mode:
```bash
docker compose up --build -d
```

### 2. Check Health
Verify the application is running via the API health endpoint:
```bash
curl http://localhost:8080/api/health
```

### 3. Add a Team
You can add a team by sending a POST request with form data:
```bash
curl -X POST http://localhost:8080/add -d "name=Germany" -d "flag=🇩🇪"
```

### 4. Remove a Team
You can remove a team by sending a POST request to the delete endpoint along with the team's ID (e.g., ID 1 for Argentina):
```bash
curl -X POST http://localhost:8080/delete/1
```

### 5. Stop the Application
To stop and remove the container when you're finished:
```bash
docker compose down
```

## Remaining Tasks (to reach end product)

### Jenkins / Delivery pipeline
- **Add `Jenkinsfile`** implementing: Checkout → Build Docker image → Run container (optionally smoke-check `GET /api/health`)
- **Define Docker image naming/tagging** (e.g. `worldcup-teams:${GIT_COMMIT}`) and container cleanup strategy (stop/remove old container before running new one)
- **Document Jenkins setup** in this README (job type, required Jenkins agent w/ Docker, any credentials if needed)

### MongoDB persistence (done)
- **`docker-compose.yml`**: `mongo` service (`mongo:7`), named volume `mongo_data`, app `depends_on` Mongo until healthy; app env `MONGO_URI`, `MONGO_COLLECTION`.
- **`app.py`**: PyMongo reads/writes; stable integer `id` per team; seed Argentina/France/Brazil (`id` 1–3) when the collection is empty.
- **`requirements.txt`**: `pymongo`.

Environment for the app:
- **`MONGO_URI`**: e.g. `mongodb://mongo:27017/worldcup` in Compose; default for local runs without Compose is `mongodb://localhost:27017/worldcup`.
- **`MONGO_COLLECTION`**: collection name (default `teams`).

To wipe DB data and re-seed: `docker compose down -v`, then `docker compose up --build -d`.

### Product completeness / behavior
- **Validation + edge cases**
  - decide and implement duplicate handling
  - deletion of non-existent ID should be a no-op (or return an error—pick one and document it)
- **Confirm routes and docs stay in sync**
  - if Mongo changes IDs or endpoints, update curl examples accordingly

### Quality (recommended)
- **Add a basic smoke test plan** (script or tests)
  - health ok, add team, delete team, and persistence across container restart
- **Add ops notes**
  - how to reset the DB volume, view logs, and run locally
- **(Optional) Add a `.dockerignore`** to speed up Docker builds
