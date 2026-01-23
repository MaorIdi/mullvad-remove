pipeline {
    agent {
        docker {
            image 'docker:27-cli'
            args '-v /var/run/docker.sock:/var/run/docker.sock --user server'
        }
    }

    stages {
        stage('Restart Application') {
            steps {
                script {
                    echo 'Stopping existing container...'
                    sh 'docker compose down || true'
                    
                    echo 'Starting container with latest code...'
                    sh 'docker compose up -d --build'
                    
                    // Wait and verify container is running
                    sh '''
                        sleep 3
                        if docker compose ps | grep -q "Up"; then
                            echo "✓ Application restarted successfully"
                            docker compose logs --tail=20
                        else
                            echo "✗ Application failed to start"
                            docker compose logs
                            exit 1
                        fi
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo '✓ Deployment successful!'
        }
        failure {
            echo '✗ Deployment failed!'
            sh 'docker compose logs || true'
        }
    }
}