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