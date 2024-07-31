pipeline {
    agent {
        docker {
            image 'docker:24.0.6-git'
        }
    }

    environment {
        CODECOV_TOKEN = credentials('CODECOV_TOKEN_rest_variantvalidator')
        CONTAINER_SUFFIX = "${BUILD_NUMBER}"
        HOME = "/home/jenkins"
        DATA_VOLUME = "${HOME}/variantvalidator_data/"
    }

    stages {
        stage("Clone Repository and Clean Up Docker") {
            steps {
                checkout scm
                sh 'docker system prune --all --volumes --force'
            }
        }
        stage("Set Safe Directory for Git") {
            steps {
                script {
                    sh """
                        git config --global --add safe.directory "${env.WORKSPACE}"
                    """
                }
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
                    def dataVolume = "${env.DATA_VOLUME}"
                    sh """
                        echo "Ensuring data directories exist and have correct permissions..."
                        mkdir -p ${dataVolume}seqdata ${dataVolume}logs
                        chmod -R 775 ${dataVolume}
                        if id -u jenkins > /dev/null 2>&1; then
                            chown -R jenkins:jenkins ${dataVolume}
                        else
                            echo "Jenkins user does not exist. Skipping chown."
                        fi
                        ls -l ${dataVolume}
                    """
                }
            }
        }
        stage("Build and Run Containers") {
            steps {
                script {
                    sh """
                        docker-compose --project-name rest-variantvalidator-ci build --no-cache rv-vvta rv-vdb rv-seqrepo rest-variantvalidator
                        docker-compose --project-name rest-variantvalidator-ci up -d rv-vvta && docker-compose --project-name rest-variantvalidator-ci up -d rv-vdb && docker-compose --project-name rest-variantvalidator-ci up -d rv-seqrepo && docker-compose --project-name rest-variantvalidator-ci up -d rest-variantvalidator
                    """
                }
            }
        }
        stage("Connect and Run Pytest") {
            steps {
                script {
                    def connectionSuccessful = false
                    for (int attempt = 1; attempt <= 5; attempt++) {
                        echo "Attempt $attempt to connect to the database..."
                        def exitCode = sh(script: '''
                            docker-compose exec -e PGPASSWORD=uta_admin rest-variantvalidator-${CONTAINER_SUFFIX} psql -U uta_admin -d vvta -h rv-vvta-${CONTAINER_SUFFIX} -p 54321 -c "SELECT 1;"
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
                sh 'docker system prune --all --volumes --force'
            }
        }
    }
}
