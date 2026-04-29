# tools_workforce

IDEA:
# Flask World Cup App - Shows the Remaining teams 
 
 GitHub → Jenkins → Docker

• A minimal Flask app with a list of National teams and their flags (add/delete items)

• Docker builds and runs it

• Jenkins pipeline: Checkout → Build Docker image → Run container

• Add MongoDB for persistence


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

### MongoDB persistence
- **Add MongoDB to `docker-compose.yml`**
  - add a `mongo` service
  - add a named volume for DB persistence
  - add environment wiring so the app can reach Mongo by service name
- **Update `app.py` to persist teams in MongoDB**
  - replace in-memory `teams` list with Mongo reads/writes
  - ensure IDs are stable (Mongo `_id` or your own `id`)
  - ensure add/delete operate on the persisted records
- **Add configuration via environment variables**
  - `MONGO_URI` (and optionally DB/collection names) provided via Compose
- **Update dependencies**
  - add a MongoDB driver (e.g. `pymongo`) to `requirements.txt`

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
