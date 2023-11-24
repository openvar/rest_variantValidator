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
        stage("Install Docker Compose") {
            steps {
                sh 'apt update && apt install -y docker-compose'
            }
        }

        stage("Clone Repository Remove dangling docker components and Create Docker Network") {
            steps {
                checkout scm
                sh 'docker system prune --all --volumes --force'
                sh 'docker network create $DOCKER_NETWORK'
            }
        }

        stage("Switch to Git Branch") {
            steps {
                sh "git checkout ${BRANCH_NAME}"
            }
        }

        stage("Build and Run Services with Docker Compose") {
            steps {
                script {
                    // Build and run services using docker-compose with container names including the build number
                    sh 'docker-compose build --no-cache rv-vvta rv-vdb rv-seqrepo rest-variantvalidator'
                    sh 'docker-compose up -d --build --force-recreate rv-vvta-${CONTAINER_SUFFIX} rv-vdb-${CONTAINER_SUFFIX} rv-seqrepo-${CONTAINER_SUFFIX} rest-variantvalidator-${CONTAINER_SUFFIX}'

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
