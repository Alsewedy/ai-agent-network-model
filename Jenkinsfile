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
                echo '=== Code Quality Stage: Ruff static analysis and SonarCloud scan ==='
                echo 'This stage currently runs in non-blocking mode so the full pipeline can continue.'

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

                        echo "Ruff completed without findings."
                    '''
                }

                withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
                    catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                        sh '''
                            echo "Preparing SonarScanner CLI..."

                            SCANNER_VERSION=8.0.1.6346
                            SCANNER_DIR=$WORKSPACE/.sonar/sonar-scanner-$SCANNER_VERSION-linux-x64

                            mkdir -p $WORKSPACE/.sonar

                            if [ ! -d "$SCANNER_DIR" ]; then
                                echo "Downloading SonarScanner CLI..."
                                curl -sSLo $WORKSPACE/.sonar/sonar-scanner.zip https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-$SCANNER_VERSION-linux-x64.zip
                                unzip -o $WORKSPACE/.sonar/sonar-scanner.zip -d $WORKSPACE/.sonar
                            fi

                            echo "Running SonarCloud analysis..."
                            $SCANNER_DIR/bin/sonar-scanner -Dsonar.token=$SONAR_TOKEN

                            echo "SonarCloud analysis completed."
                        '''
                    }
                }

                echo 'Code Quality stage finished. Ruff findings and SonarCloud dashboard should be reviewed in the hardening pass.'
            }
        }
        stage('Security') {
            steps {
                echo '=== Security Stage: Dependency, source-code, and container image scanning ==='
                echo 'This stage runs in non-blocking mode so the full pipeline can continue during baseline hardening.'

                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '''
                        . .venv/bin/activate

                        echo "Installing Python security tools..."
                        pip install pip-audit bandit

                        echo "Running dependency vulnerability scan with pip-audit..."
                        pip-audit -r requirements.txt
                    '''
                }

                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '''
                        . .venv/bin/activate

                        echo "Running Python source-code security scan with Bandit..."
                        bandit -r . \
                          -x ./.venv,./tests,./__pycache__,./.git,./.sonar
                    '''
                }

                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '''
                        echo "Running Docker image vulnerability scan with Trivy..."
                        echo "Scanning image: $IMAGE_NAME:$APP_VERSION"

                        docker run --rm \
                          -v /var/run/docker.sock:/var/run/docker.sock \
                          aquasec/trivy:latest image \
                          --severity HIGH,CRITICAL \
                          --exit-code 1 \
                          $IMAGE_NAME:$APP_VERSION
                    '''
                }

                echo 'Security stage finished. Findings should be reviewed, fixed, mitigated, or documented in the next hardening pass.'
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

                withCredentials([
                    string(credentialsId: 'openai-api-key', variable: 'OPENAI_API_KEY'),
                    usernamePassword(credentialsId: 'github-token', usernameVariable: 'GIT_USERNAME', passwordVariable: 'GIT_TOKEN')
                ]) {
                    sh '''
                        echo "Creating production environment file..."

                        cat > .env.production <<EOF
OPENAI_API_KEY=$OPENAI_API_KEY
OPENAI_MODEL=gpt-5.4-mini
APP_ENV=production
DEBUG=false
EOF

                        echo "Releasing Docker image to production environment: $IMAGE_NAME:$APP_VERSION"

                        APP_VERSION=$APP_VERSION docker compose -p ai-agent-prod -f docker-compose.prod.yml down --remove-orphans || true
                        docker rm -f ai-agent-prod || true
                        APP_VERSION=$APP_VERSION docker compose -p ai-agent-prod -f docker-compose.prod.yml up -d --force-recreate

                        echo "Validating production environment health..."

                        HEALTHY=false

                        for i in 1 2 3 4 5 6 7 8 9 10; do
                            if curl --fail $PROD_URL; then
                                echo "Production environment is healthy."
                                HEALTHY=true
                                break
                            fi

                            echo "Waiting for production environment to become ready..."
                            sleep 3
                        done

                        if [ "$HEALTHY" != "true" ]; then
                            echo "Production release failed health validation."
                            docker logs ai-agent-prod || true
                            exit 1
                        fi

                        echo "Creating Git release tag..."

                        git config user.name "Jenkins CI"
                        git config user.email "jenkins-ci@example.local"

                        RELEASE_TAG="release-$APP_VERSION"

                        git fetch --tags || true

                        if git rev-parse "$RELEASE_TAG" >/dev/null 2>&1; then
                            echo "Git tag $RELEASE_TAG already exists locally."
                        else
                            git tag -a "$RELEASE_TAG" -m "Production release $APP_VERSION"
                        fi

                        echo "Pushing Git release tag to GitHub..."
                        git push "https://$GIT_USERNAME:$GIT_TOKEN@github.com/Alsewedy/ai-agent-network-model.git" "$RELEASE_TAG"

                        echo "Release stage completed successfully."
                        echo "Production release tag created: $RELEASE_TAG"
                    '''
                }
            }
        }
        stage('Monitoring and Alerting') {
            steps {
                echo '=== Monitoring and Alerting Stage: Production health, status, logs, and alert simulation ==='

                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '''
                        echo "Starting production monitoring checks..."

                        REPORT_FILE="monitoring_report.txt"

                        {
                            echo "=== AI Agent Production Monitoring Report ==="
                            echo "Build Number: $BUILD_NUMBER"
                            echo "Application Version: $APP_VERSION"
                            echo "Production URL: $PROD_URL"
                            echo "Generated At: $(date)"
                            echo ""
                        } > $REPORT_FILE

                        echo "Checking production container status..."
                        docker ps --filter "name=ai-agent-prod" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" | tee -a $REPORT_FILE

                        echo "" | tee -a $REPORT_FILE
                        echo "Checking production image version..." | tee -a $REPORT_FILE
                        docker inspect ai-agent-prod --format='Production image: {{.Config.Image}}' | tee -a $REPORT_FILE

                        echo "" | tee -a $REPORT_FILE
                        echo "Checking production health endpoint..." | tee -a $REPORT_FILE

                        if curl --fail --silent --show-error $PROD_URL | tee -a $REPORT_FILE; then
                            echo "" | tee -a $REPORT_FILE
                            echo "MONITORING STATUS: Production health check passed." | tee -a $REPORT_FILE
                        else
                            echo "" | tee -a $REPORT_FILE
                            echo "ALERT: Production health check failed." | tee -a $REPORT_FILE
                            echo "Collecting production logs for troubleshooting..." | tee -a $REPORT_FILE
                            docker logs --tail 50 ai-agent-prod | tee -a $REPORT_FILE || true
                            exit 1
                        fi

                        echo "" | tee -a $REPORT_FILE
                        echo "Collecting recent production logs..." | tee -a $REPORT_FILE
                        docker logs --tail 30 ai-agent-prod | tee -a $REPORT_FILE || true

                        echo "" | tee -a $REPORT_FILE
                        echo "Collecting production container resource usage..." | tee -a $REPORT_FILE
                        docker stats ai-agent-prod --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}" | tee -a $REPORT_FILE || true

                        echo "" | tee -a $REPORT_FILE
                        echo "Monitoring stage completed." | tee -a $REPORT_FILE
                    '''
                }

                archiveArtifacts artifacts: 'monitoring_report.txt', allowEmptyArchive: true

                echo 'Monitoring and Alerting stage finished. Review monitoring_report.txt for production status, logs, and health evidence.'
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
