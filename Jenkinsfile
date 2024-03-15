Sure, I can help you modify your `Jenkinsfile` to include some additional steps. Here's a step-by-step plan:

1. Add a step to check if the directory `/root/variantvalidator_data/seqdata` exists. If it doesn't, create it.
2. Add a step to check if the directory `/root/variantvalidator_data/logs` exists. If it doesn't, create it.
3. Add a step to list the contents of the `/root/variantvalidator_data/` directory to verify that the directories were created successfully.
4. Continue with the existing steps to build and run the Docker containers.

Here's the modified `Jenkinsfile`:

```groovy
pipeline {
    agent {
        docker {
            image 'docker:24.0.6-git'
        }
    }

    environment {
        CODECOV_TOKEN = credentials('CODECOV_TOKEN_rest_variantvalidator')
        CONTAINER_SUFFIX = "${BUILD_NUMBER}"
        DATA_VOLUME = "/root/variantvalidator_data/"
    }

    stages {
        stage("Clone Repository Remove dangling docker components and Create Docker Network") {
            steps {
                checkout scm
                sh 'docker system prune --all --volumes --force'
            }
        }
        stage("Switch to Git Branch") {
            steps {
                sh "git checkout ${BRANCH_NAME}"
                sh "git pull"
            }
        }
        stage("Install Docker Compose") {
            steps {
                sh 'apk update && apk add docker-compose'
            }
        }
        stage("Check and Create Directories") {
            steps {
                script {
                    sh """
                        if [ ! -d "${DATA_VOLUME}seqdata" ]; then
                            mkdir -p ${DATA_VOLUME}seqdata
                        fi

                        if [ ! -d "${DATA_VOLUME}logs" ]; then
                            mkdir -p ${DATA_VOLUME}logs
                        fi

                        ls -l ${DATA_VOLUME}
                    """
                }
            }
        }
        stage("Build and Run containers") {
            steps {
                script {
                    sh """
                        docker-compose --project-name rest-variantvalidator-ci build --no-cache rv-vvta rv-vdb rv-seqrepo rest-variantvalidator
                        docker-compose --project-name rest-variantvalidator-ci up -d rv-vvta && docker-compose --project-name rest-variantvalidator-ci up -d rv-vdb && docker-compose --project-name rest-variantvalidator-ci up -d rv-seqrepo && docker-compose --project-name rest-variantvalidator-ci up -d rest-variantvalidator
                    """
                }
            }
        }
        stage("Connect and run Pytest") {
            steps {
                script {
                    def connectionSuccessful = false
                    for (int attempt = 1; attempt <= 5; attempt++) {
                        echo "Attempt $attempt to connect to the database..."
                        def exitCode = sh(script: '''
                            docker-compose exec -e PGPASSWORD=uta_admin rest-variantvalidator-${CONTAINER_SUFFIX} psql -U uta_admin -d vvta -h rv-vvta-${CONTAINER_SUFFIX} -p 54321
                        ''', returnStatus: true)

                        if (exitCode == 0) {
                            connectionSuccessful = true
                            echo "Connected successfully! Running tests..."
                            break
                        }

                        echo "Connection failed. Waiting for 60 seconds before the next attempt..."
                        sleep 60
                    }

                    if (!connectionSuccessful) {
                        error "All connection attempts failed. Exiting..."
                    }
                }
            }
        }
        stage("Run Pytest and Codecov") {
            steps {
                script {
                    sh 'docker-compose exec rest-variantvalidator-${CONTAINER_SUFFIX} pytest --cov=rest_VariantValidator --cov-report=term tests/'
                    sh 'docker-compose exec rest-variantvalidator-${CONTAINER_SUFFIX} codecov -t $CODECOV_TOKEN -b ${BRANCH_NAME}'
                }
            }
        }
    }

    post {
        always {
            script {
                sh 'docker-compose down -v'
                sh 'docker network rm $DOCKER_NETWORK'
                sh 'docker system prune --all --volumes --force'
            }
        }
    }
}
```

This script checks if the directories exist and creates them if they don't. It then lists the contents of the `/root/variantvalidator_data/` directory to verify that the directories were created successfully. The rest of the script is the same as your original script.