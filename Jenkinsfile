pipeline {
    agent {
        docker {
            image 'docker:24.0.6-git'
        }
    }

    environment {
        CODECOV_TOKEN = credentials('CODECOV_TOKEN_rest_variantvalidator')
        CONTAINER_SUFFIX = "${BUILD_NUMBER}"
        DOCKER_NETWORK = "rest-variantvalidator_docker_network-${CONTAINER_SUFFIX}"
        DATA_VOLUME = "docker-shared-space"
    }
    stages {
        stage("Clone Repository Remove dangling docker components and Create Docker Network") {
            steps {
                checkout scm // Checkout the source code from the configured source code management system
                sh 'docker system prune --all --volumes --force' // Remove unused Docker resources
                sh 'docker network create $DOCKER_NETWORK' // Create a Docker network for containers
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
        stage("Build and Run containers") {
            steps {
                // Build and run services using docker-compose with container names including the build number
                sh "docker-compose build --no-cache rv-vvta${CONTAINER_SUFFIX} rv-vdb${CONTAINER_SUFFIX} rv-seqrepo${CONTAINER_SUFFIX} rest-variantvalidator${CONTAINER_SUFFIX}"
                sh "docker-compose up -d rv-vvta${CONTAINER_SUFFIX} && docker-compose up -d rv-vdb${CONTAINER_SUFFIX} && docker-compose up -d rv-seqrepo${CONTAINER_SUFFIX} && docker-compose up -d rest-variantvalidator${CONTAINER_SUFFIX}"
            }
        }
        stage("Connect and run Pytest") {
            steps {
                script {
                    // Wait for the PostgreSQL container to be ready
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
                    // Run pytest && Run Codecov with the provided token and branch name
                    sh 'docker-compose exec rest-variantvalidator-${CONTAINER_SUFFIX} pytest -n 3 --cov=VariantValidator --cov=VariantFormatter --cov-report=term tests/'

                    // Send coverage report to Codecov
                    sh 'docker-compose exec rest-variantvalidator-${CONTAINER_SUFFIX} codecov -t $CODECOV_TOKEN -b ${BRANCH_NAME}'
                }
            }
        }
    }

    post {
        always {
            script {
                // Cleanup Docker and Docker Compose
                sh 'docker-compose down -v'
                sh 'docker network rm $DOCKER_NETWORK'
            }
        }
    }
}
