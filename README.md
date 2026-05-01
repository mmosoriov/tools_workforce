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

The repo includes a Declarative [`Jenkinsfile`](Jenkinsfile) organized into 4 stages: 
**Checkout** → **Build** (Docker image via commit hash) → **Run** (creates an isolated CI network and starts MongoDB + App) → **Verify** (polls the `/api/health` endpoint). A `post { always }` block ensures the test network and containers are destroyed after every run.

**Requirements to run this pipeline:**
- **Job type:** Pipeline (or Multibranch Pipeline) from SCM.
- **Agent:** Linux agent with the **Docker CLI** and `curl` installed, usually with the host `/var/run/docker.sock` mounted.
- **Ports:** The CI pipeline automatically maps the app to host port **18080** to prevent clashes with Jenkins or other local services.



#### Run Jenkins locally with Docker Desktop 

##### 1) Install Docker Desktop
Ensure Docker Desktop is downloaded, installed, and currently running on your Mac.

##### 2) Start Jenkins
Because our pipeline requires running Docker commands (`docker build`, `docker run`), we need a custom Jenkins image that has the Docker CLI installed. This approach is not recommended to use in production, where a more robust approach should be taken to install Docker. Using the docker convenience script is a security vulnerability. (https://get.docker.com)

1. Open the **Terminal** app.
2. Create a custom image by running this command:

```bash
docker build -t my-jenkins-with-docker - <<EOF
FROM jenkins/jenkins:lts
USER root

# Install Docker CLI using the official installation script
RUN curl -fsSL https://get.docker.com | sh
USER jenkins
EOF
```

3. Start the container:
```bash
docker run -d --name jenkins \
  -p 8081:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -u root \
  my-jenkins-with-docker
```

##### 3) Open Jenkins in your browser
Open Chrome or Safari and go to: `http://localhost:8081`

##### 4) Unlock Jenkins
In Terminal, run this to print your one-time unlock password:
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
Then:
- Copy the password from your Terminal.
- Paste it into the Jenkins web page.
- Click **Install suggested plugins**.
- Skip creating an admin user (or create one if you prefer).

##### 5) Set up the Pipeline Job
1. Click on **New Item** in the Jenkins dashboard.
2. Enter a name, select **Pipeline**, and click **OK**.
3. Scroll down to the **Pipeline** section and change "Definition" to **Pipeline script from SCM**.
4. Set "SCM" to **Git**.
5. Set "Repository URL" to `https://github.com/mmosoriov/tools_workforce`.
6. Ensure the "Branch Specifier" is set to `*/main`.
7. Click **Save** and then click **Build Now**.

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

