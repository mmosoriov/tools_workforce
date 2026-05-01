pipeline {
    agent any

    environment {
        // The port mapped to the host machine in docker-compose.yml
        HOST_PORT = '8080'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh """
                    # Pull down any existing environment from a previous failure
                    docker compose down -v 2>/dev/null || true
                    
                    # Explicitly build the Docker images defined in docker-compose.yml
                    docker compose build
                """
            }
        }

        stage('Run') {
            steps {
                sh """
                    docker compose up -d
                """
            }
        }

        stage('Verify') {
            steps {
                sh """
                    set -e
                    echo "Waiting for app health..."
                    ok=0
                    
                    # API health endpoint
                    for i in \$(seq 1 15); do
                      if curl -fsS http://localhost:${env.HOST_PORT}/api/health >/dev/null 2>&1; then
                        ok=1
                        break
                      fi
                      sleep 2
                    done
                    
                    if [ "\$ok" -ne 1 ]; then
                      echo "GET /api/health smoke check failed"
                      docker compose logs  # Print logs to help troubleshoot if it failed
                      exit 1
                    fi
                    
                    # Final confirmation curl
                    curl -fsS http://localhost:${env.HOST_PORT}/api/health
                    echo "\\nVerification passed."
                """
            }
        }
    }

    post {
        always {
            // destroy test environment (containers, networks, and volumes) 
            sh "docker compose down -v 2>/dev/null || true"
        }
    }
}
