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

        stage('Build image') {
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

        stage('Run and smoke') {
            steps {
                sh """
                    set -e
                    docker network inspect ${env.CI_NETWORK} >/dev/null 2>&1 || docker network create ${env.CI_NETWORK}
                    docker rm -f ${env.APP_CTR} ${env.MONGO_CTR} 2>/dev/null || true

                    docker run -d --name ${env.MONGO_CTR} --network ${env.CI_NETWORK} mongo:7

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

                    docker run -d --name ${env.APP_CTR} --network ${env.CI_NETWORK} \\
                      -e MONGO_URI=mongodb://${env.MONGO_CTR}:27017/worldcup \\
                      -e MONGO_COLLECTION=teams \\
                      -e PORT=8080 \\
                      -p ${env.HOST_PORT}:8080 \\
                      ${env.IMAGE_NAME}:${env.IMAGE_TAG}

                    echo "Waiting for app health..."
                    ok=0
                    for i in \$(seq 1 60); do
                      if curl -fsS http://127.0.0.1:${env.HOST_PORT}/api/health >/dev/null 2>&1; then
                        ok=1
                        break
                      fi
                      sleep 2
                    done
                    if [ "\$ok" -ne 1 ]; then
                      echo "GET /api/health smoke check failed"
                      exit 1
                    fi
                    curl -fsS http://127.0.0.1:${env.HOST_PORT}/api/health
                    echo "Smoke check passed."
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
