pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {
        IMAGE_NAME = 'ai-agent-network-model'
        TEST_URL = 'http://localhost:8001/health'
        PROD_URL = 'http://localhost:8002/health'
    }

    stages {

        stage('Build') {
            steps {
                echo '=== Build Stage: Checkout, dependency setup, and Docker image artifact build ==='

                checkout scm

                script {
                    env.SHORT_COMMIT = sh(
                        script: "git rev-parse --short HEAD",
                        returnStdout: true
                    ).trim()

                    env.APP_VERSION = "${env.BUILD_NUMBER}-${env.SHORT_COMMIT}"
                }

                sh '''
                    echo "Building application version: $APP_VERSION"

                    echo "Creating Python virtual environment..."
                    python3 -m venv .venv

                    echo "Installing Python dependencies..."
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt

                    echo "Building Docker image artifact..."
                    docker build \
                      -t $IMAGE_NAME:$APP_VERSION \
                      -t $IMAGE_NAME:latest .

                    echo "Build stage completed successfully."
                    echo "Created Docker image artifact: $IMAGE_NAME:$APP_VERSION"
                '''
            }
        }

        stage('Test') {
            steps {
                echo '=== Test Stage: Running automated pytest suite ==='

                withCredentials([string(credentialsId: 'openai-api-key', variable: 'OPENAI_API_KEY')]) {
                    sh '''
                        . .venv/bin/activate
                        export OPENAI_API_KEY="$OPENAI_API_KEY"

                        echo "Running automated tests..."
                        pytest tests -v

                        echo "Test stage completed successfully."
                    '''
                }
            }
        }

        stage('Code Quality') {
    steps {
        echo '=== Code Quality Stage: Running Ruff static analysis in non-blocking mode ==='
        echo 'This stage reports maintainability/style issues but does not stop the pipeline yet.'

        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
            sh '''
                . .venv/bin/activate

                echo "Installing Ruff..."
                pip install ruff

                echo "Running Ruff code quality checks..."
                ruff check . \
                  --exclude .venv \
                  --exclude __pycache__ \
                  --exclude .git

                echo "Code Quality stage completed without findings."
            '''
        }

        echo 'Code Quality stage finished. Any Ruff findings above should be reviewed and fixed in the improvement pass.'
    }
}

        stage('Security') {
            steps {
                echo '=== Security Stage: Placeholder / baseline only ==='
                echo 'Security scanning has not been fully implemented yet.'
                echo 'Planned improvement: add pip-audit for dependency vulnerabilities.'
                echo 'Planned improvement: add Bandit for Python source-code security scanning.'
                echo 'Planned improvement: add Trivy for Docker image/container scanning.'
                echo 'This stage is currently non-blocking and only documents the planned security work.'
            }
        }

        stage('Deploy') {
            steps {
                echo '=== Deploy Stage: Deploying tagged image to testing environment ==='

                withCredentials([string(credentialsId: 'openai-api-key', variable: 'OPENAI_API_KEY')]) {
                    sh '''
                        echo "Creating testing environment file..."

                        cat > .env.test <<EOF
OPENAI_API_KEY=$OPENAI_API_KEY
OPENAI_MODEL=gpt-5.4-mini
APP_ENV=test
DEBUG=true
EOF

                        echo "Deploying Docker image to testing environment: $IMAGE_NAME:$APP_VERSION"

                        APP_VERSION=$APP_VERSION docker compose -f docker-compose.test.yml down || true
                        APP_VERSION=$APP_VERSION docker compose -f docker-compose.test.yml up -d

                        echo "Validating testing environment health..."

                        for i in 1 2 3 4 5 6 7 8 9 10; do
                            if curl --fail $TEST_URL; then
                                echo "Testing environment is healthy."
                                echo "Deploy stage completed successfully."
                                exit 0
                            fi

                            echo "Waiting for testing environment to become ready..."
                            sleep 3
                        done

                        echo "Testing environment failed to become healthy."
                        docker logs ai-agent-test || true
                        exit 1
                    '''
                }
            }
        }

        stage('Release') {
            steps {
                echo '=== Release Stage: Manual approval before production deployment ==='

                input message: 'Approve release to production environment?', ok: 'Release to Production'

                echo 'Manual approval received. Promoting the same tagged image to production...'

                withCredentials([string(credentialsId: 'openai-api-key', variable: 'OPENAI_API_KEY')]) {
                    sh '''
                        echo "Creating production environment file..."

                        cat > .env.production <<EOF
OPENAI_API_KEY=$OPENAI_API_KEY
OPENAI_MODEL=gpt-5.4-mini
APP_ENV=production
DEBUG=false
EOF

                        echo "Releasing Docker image to production environment: $IMAGE_NAME:$APP_VERSION"

                        APP_VERSION=$APP_VERSION docker compose -f docker-compose.prod.yml down || true
                        APP_VERSION=$APP_VERSION docker compose -f docker-compose.prod.yml up -d

                        echo "Validating production environment health..."

                        for i in 1 2 3 4 5 6 7 8 9 10; do
                            if curl --fail $PROD_URL; then
                                echo "Production environment is healthy."
                                echo "Release stage completed successfully."
                                exit 0
                            fi

                            echo "Waiting for production environment to become ready..."
                            sleep 3
                        done

                        echo "Production release failed health validation."
                        docker logs ai-agent-prod || true
                        exit 1
                    '''
                }
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo '=== Monitoring and Alerting Stage: Placeholder / baseline only ==='
                echo 'Monitoring has not been fully implemented yet.'
                echo 'Current baseline: production health endpoint can be checked at http://localhost:8002/health.'
                echo 'Planned improvement: add Prometheus/Grafana or another monitoring dashboard.'
                echo 'Planned improvement: add alert simulation or meaningful alert rules.'
                echo 'This stage is currently non-blocking and only documents the planned monitoring work.'

                sh '''
                    echo "Baseline production health check:"
                    curl --fail $PROD_URL || true

                    echo "Current production container status:"
                    docker ps --filter "name=ai-agent-prod" || true

                    echo "Image used by production container:"
                    docker inspect ai-agent-prod --format='{{.Config.Image}}' || true
                '''
            }
        }
    }

    post {
        always {
            echo '=== Pipeline Summary ==='
            sh '''
                echo "Pipeline finished."
                echo "Build number: $BUILD_NUMBER"
                echo "Application version: $APP_VERSION"
                echo "Current AI agent containers:"
                docker ps --filter "name=ai-agent" || true

                echo "Available AI agent Docker images:"
                docker images | grep ai-agent-network-model || true
            '''
        }

        success {
            echo 'Pipeline completed successfully.'
        }

        failure {
            echo 'Pipeline failed. Review the failed stage output above.'
        }
    }
}
