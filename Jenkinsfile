pipeline {
    agent any

    environment {
        CI_NETWORK = 'worldcup-ci-net'
        MONGO_CTR = 'worldcup-mongo-ci'
        APP_CTR = 'worldcup-app-ci'
        HOST_PORT = '18080'
        IMAGE_NAME = 'worldcup-teams'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                script {
                    def commit = env.GIT_COMMIT?.trim()
                    env.IMAGE_TAG = (commit && commit.length() > 0) ? commit : sh(
                        returnStdout: true,
                        script: 'git rev-parse HEAD'
                    ).trim()
                }
                sh "docker build -t ${env.IMAGE_NAME}:${env.IMAGE_TAG} ."
            }
        }

        stage('Run') {
            steps {
                sh """
                    set -e
                    # 1. Setup isolated CI Network
                    docker network inspect ${env.CI_NETWORK} >/dev/null 2>&1 || docker network create ${env.CI_NETWORK}
                    docker rm -f ${env.APP_CTR} ${env.MONGO_CTR} 2>/dev/null || true

                    # 2. Run Database
                    docker run -d --name ${env.MONGO_CTR} --network ${env.CI_NETWORK} mongo:7

                    # 3. Wait for Mongo 
                    echo "Waiting for MongoDB..."
                    mongo_ok=0
                    for i in \$(seq 1 30); do
                      if docker exec ${env.MONGO_CTR} mongosh --quiet --eval "db.adminCommand({ ping: 1 })" >/dev/null 2>&1; then
                        mongo_ok=1
                        break
                      fi
                      sleep 2
                    done
                    if [ "\$mongo_ok" -ne 1 ]; then
                      echo "MongoDB did not become ready in time"
                      exit 1
                    fi

                    # 4. Run App Container on the same network
                    docker run -d --name ${env.APP_CTR} --network ${env.CI_NETWORK} \\
                      -e MONGO_URI=mongodb://${env.MONGO_CTR}:27017/worldcup \\
                      -e MONGO_COLLECTION=teams \\
                      -e PORT=8080 \\
                      -p ${env.HOST_PORT}:8080 \\
                      ${env.IMAGE_NAME}:${env.IMAGE_TAG}
                """
            }
        }

        stage('Verify') {
            steps {
                sh """
                    set -e
                    echo "Waiting for app health..."
                    ok=0
                    
                    # Ping the app using a temporary curl container ON THE SAME NETWORK
                    for i in \$(seq 1 60); do
                      if docker run --rm --network ${env.CI_NETWORK} curlimages/curl -fsS http://${env.APP_CTR}:8080/api/health >/dev/null 2>&1; then
                        ok=1
                        break
                      fi
                      sleep 2
                    done
                    
                    if [ "\$ok" -ne 1 ]; then
                      echo "GET /api/health check failed"
                      exit 1
                    fi
                    
                    # Final confirmation print
                    docker run --rm --network ${env.CI_NETWORK} curlimages/curl -fsS http://${env.APP_CTR}:8080/api/health
                    echo "\\n check passed."
                """
            }
        }
    }

    post {
        always {
            sh """
                docker rm -f ${env.APP_CTR} ${env.MONGO_CTR} 2>/dev/null || true
                docker network rm ${env.CI_NETWORK} 2>/dev/null || true
            """
        }
    }
}
