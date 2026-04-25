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

                sh 'bash ci/build.sh'
            }
        }

        stage('Test') {
            steps {
                echo '=== Test Stage: Running automated pytest suite ==='

                withCredentials([string(credentialsId: 'openai-api-key', variable: 'OPENAI_API_KEY')]) {
                    sh 'bash ci/test.sh'
                }
            }
        }

        stage('Code Quality') {
            steps {
                echo '=== Code Quality Stage: Ruff static analysis and SonarCloud scan ==='
                echo 'This stage currently runs in non-blocking mode so the full pipeline can continue.'

                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
                        sh 'bash ci/code_quality.sh'
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
                    sh 'bash ci/security_scan.sh'
                }

                echo 'Security stage finished. Findings should be reviewed, fixed, mitigated, or documented in the next hardening pass.'
            }
        }

        stage('Deploy') {
            steps {
                echo '=== Deploy Stage: Deploying tagged image to testing environment ==='

                withCredentials([string(credentialsId: 'openai-api-key', variable: 'OPENAI_API_KEY')]) {
                    sh 'bash ci/deploy_test.sh'
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
                    sh 'bash ci/release_prod.sh'
                }
            }
        }

        stage('Monitoring and Alerting') {
            steps {
                echo '=== Monitoring and Alerting Stage: Production health, status, logs, and alert simulation ==='

                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh 'bash ci/monitoring.sh'
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
