
# Flask World Cup App 
 Tools:
 GitHub → Jenkins → Docker, persistance with MongoDB

Architecture: 
• A minimal Flask app with a list of National teams and their flags (add/delete items)

• Docker builds and runs it

• Jenkins pipeline: Checkout → Build Docker image → Run container → Verify → Destroy

• MongoDB persists list of teams 


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

### 3. View List of Teams
You can view the visual grid of all current teams by opening your web browser and navigating to:
`http://localhost:8080/`
*(Alternatively, from the terminal, you can run `curl http://localhost:8080/` to get the raw HTML string).*

### 4. Add a Team
You can add a team by sending a POST request with form data:
```bash
curl -X POST http://localhost:8080/add -d "name=Germany" -d "flag=🇩🇪"
```

### 5. Remove a Team
You can remove a team by sending a POST request to the delete endpoint along with the team's ID (e.g., 1 for Argentina):
```bash
curl -X POST http://localhost:8080/delete/1
```

### 6. Stop the Application
To stop and remove the container when you're finished:
```bash
docker compose down
```

### 7. Reset Database
To completely wipe out all saved data and restore the database to the original default seed teams:
```bash
docker compose down -v
```

### Jenkins (CI pipeline)

The repo includes a Declarative [`Jenkinsfile`](Jenkinsfile) at the root: **Checkout** → **build** Docker image **`worldcup-teams:${GIT_COMMIT}`** (falls back to `git rev-parse HEAD` when `GIT_COMMIT` is unset, e.g. some manual replays) → **stop/remove** prior CI containers **`worldcup-app-ci`** / **`worldcup-mongo-ci`** on shared network **`worldcup-ci-net`** → run **`mongo:7`** and the app → **`curl`** smoke test on **`GET http://127.0.0.1:18080/api/health`** → **`post { always }`** tears down those containers and the network.

The app connects to MongoDB at import time; the pipeline always starts Mongo alongside the app so the smoke check can succeed.

**Job type:** Create a **Pipeline** job (or **Multibranch Pipeline** for branches/PRs) with **Pipeline script from SCM**, script path **`Jenkinsfile`**.

**Agent:** A Linux agent with **Docker CLI** available and permission to talk to the Docker daemon (`docker build`, `docker run`, etc.). Typical setups use an agent where Docker is installed natively, or a container agent with the host **`/var/run/docker.sock`** mounted so builds use the host engine.

**Credentials:** None for a **public** Git remote. Use Jenkins **Git** credentials for **private** repositories. Add **registry** credentials in Jenkins only if you extend the pipeline to **push** images (not required by the current `Jenkinsfile`).

**Smoke check:** The agent needs **`curl`** on `PATH` for the health request. Local Compose still uses port **8080**; CI maps the app to host port **18080** to reduce clashes on shared builders.

#### Run Jenkins locally with Docker Desktop 

Jenkins is a web app that runs in the background. You **start Jenkins**, then you open it in your web browser (usually at `http://localhost:8080`) to click buttons and run jobs.

This is the easiest way to run Jenkins on a Mac: **Docker Desktop**.

##### 1) Install Docker Desktop

##### 2) Start Jenkins

Because our pipeline requires running Docker commands (`docker build`, `docker run`), we need a custom Jenkins image that has the Docker CLI installed.

1. Open the **Terminal** app (Command+Space → type “Terminal” → Enter)
2. Create a custom image by running this command:

```bash
docker build -t my-jenkins-with-docker - <<EOF
FROM jenkins/jenkins:lts
USER root

RUN ARCH=\$(uname -m) && \\
    if [ "\$ARCH" = "x86_64" ]; then DOCKER_ARCH="x86_64"; COMP_ARCH="x86_64"; \\
    elif [ "\$ARCH" = "aarch64" ] || [ "\$ARCH" = "arm64" ]; then DOCKER_ARCH="aarch64"; COMP_ARCH="aarch64"; \\
    else echo "Unsupported architecture: \$ARCH" && exit 1; fi && \\
    curl -fsSLO https://download.docker.com/linux/static/stable/\${DOCKER_ARCH}/docker-24.0.9.tgz && \\
    tar xzvf docker-24.0.9.tgz && \\
    mv docker/docker /usr/local/bin/ && \\
    rm -rf docker docker-24.0.9.tgz && \\
    mkdir -p /usr/local/lib/docker/cli-plugins && \\
    curl -SL https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-linux-\${COMP_ARCH} -o /usr/local/lib/docker/cli-plugins/docker-compose && \\
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

USER jenkins
EOF
```

```bash
docker run -d --name jenkins \
  -p 8081:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -u root \
  my-jenkins-with-docker
```
##### 3) Open Jenkins in your browser

Open Chrome/Safari and go to:
- `http://localhost:8081`

##### 4) Unlock Jenkins (get the one-time password)

In Terminal, run this to print the unlock password:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Then:
- Copy the password from Terminal
- Paste it into the Jenkins page
- Click **Install suggested plugins**
- skip creating admin user

##### 5) Create new job by clikcin on new item
##### 6) Pipeline script from SCM
##### 7) SCM as Git, repo = https://github.com/mmosoriov/tools_workforce
- branch specifier */main


##### Stop / start Jenkins later

- Stop Jenkins:

```bash
docker stop jenkins
```

- Start Jenkins again:

```bash
docker start jenkins
```

##### Remove Jenkins (only if you want to delete it)

- Remove the Jenkins container:

```bash
docker rm -f jenkins
```

- Remove Jenkins’s saved data (jobs, settings). Only run this if you truly want to wipe it:

```bash
docker volume rm jenkins_home
```

## Remaining Tasks (to reach end product)

### Jenkins / Delivery pipeline (done)
- **`Jenkinsfile`**: Checkout → build image `worldcup-teams:${GIT_COMMIT}` → remove old CI containers/network → run `mongo:7` + app on `worldcup-ci-net` → smoke `GET /api/health` on port **18080** → always cleanup.
- **Tagging / cleanup**: Image tag is the Git commit SHA; fixed container names are removed before each run and again in **`post { always }`**.
- **Documentation**: This README (job type, agent + Docker, credentials).

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
