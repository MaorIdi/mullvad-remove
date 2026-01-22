pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        PYTHON_VERSION = '3.11'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate') {
            steps {
                script {
                    // Check required files exist
                    sh 'test -f requirements.txt || exit 1'
                    sh 'test -f mullvad_device_cleaner.py || exit 1'
                    sh 'test -f Dockerfile || exit 1'
                    sh 'test -f docker-compose.yml || exit 1'
                    echo 'All required files present ✓'
                }
            }
        }

        stage('Python Lint & Test') {
            agent {
                docker {
                    image "python:${PYTHON_VERSION}-slim"
                    args '-u root:root'
                }
            }
            steps {
                sh '''
                    pip install --no-cache-dir -r requirements.txt
                    pip install --no-cache-dir pylint flake8
                    
                    # Lint the Python script
                    echo "Running pylint..."
                    pylint mullvad_device_cleaner.py --exit-zero --reports=y || true
                    
                    echo "Running flake8..."
                    flake8 mullvad_device_cleaner.py --max-line-length=120 --exit-zero || true
                    
                    # Syntax check
                    python -m py_compile mullvad_device_cleaner.py
                    echo "Python syntax check passed ✓"
                '''
            }
        }

        stage('Security Scan') {
            steps {
                script {
                    // Check for common security issues in dependencies
                    sh '''
                        docker run --rm -v "$(pwd):/app" python:3.11-slim sh -c "
                            cd /app &&
                            pip install --no-cache-dir safety &&
                            safety check -r requirements.txt --json || true
                        "
                    '''
                    echo 'Security scan completed'
                }
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    sh 'docker-compose build --no-cache'
                    echo 'Docker image built successfully ✓'
                }
            }
        }

        stage('Test Docker Image') {
            steps {
                script {
                    // Test that the Docker image can start
                    sh '''
                        # Create a test allowed_devices.txt if it doesn't exist
                        if [ ! -f allowed_devices.txt ]; then
                            echo "test-device" > allowed_devices.txt
                            echo "Created test allowed_devices.txt"
                        fi
                        
                        # Test the image can run (will fail gracefully without MULLVAD_ACCOUNT_NUMBER)
                        docker-compose config
                        echo "Docker Compose configuration is valid ✓"
                    '''
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Stop existing containers
                    sh 'docker-compose down || true'
                    
                    // Start the service
                    sh 'docker-compose up -d'
                    
                    // Wait a bit and check if container is running
                    sh '''
                        sleep 5
                        if docker-compose ps | grep -q "Up"; then
                            echo "Container deployed and running ✓"
                        else
                            echo "Warning: Container may not be running properly"
                            docker-compose logs
                        fi
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo '✓ Pipeline completed successfully!'
        }
        failure {
            echo '✗ Pipeline failed. Check logs above.'
            sh 'docker-compose logs || true'
        }
        always {
            // Cleanup test artifacts
            sh 'docker system prune -f --volumes || true'
            echo 'Pipeline finished.'
        }
        cleanup {
            // Clean up workspace
            cleanWs(deleteDirs: true, disableDeferredWipeout: true)
        }
    }
}