pipeline {
    agent {
        docker {
            image 'docker:latest'
            // We mount the docker socket so this container can control the host's Docker
            // We run as root to avoid permission issues with the socket
            args '-v /var/run/docker.sock:/var/run/docker.sock --user root'
        }
    }

    environment {
        // Optional: Tells your scripts/compose that this is an automated build
        CI = 'true'
    }

    stages {
        stage('Deploy') {
            steps {
                script {
                    echo '--- 1. Teardown ---'
                    // "|| true" ensures the pipeline doesn't stop if containers are already down
                    sh 'docker compose down --remove-orphans || true'
                    
                    echo '--- 2. Build & Launch ---'
                    // -d: Detached mode
                    // --build: Forces a rebuild to include your latest code changes
                    sh 'docker compose up -d --build'
                    
                    echo '--- 3. Health Check ---'
                    // Wait 5 seconds for the container to stabilize
                    sh 'sleep 5'
                    
                    // Verify the specific container is actually running
                    // We verify that the "State" is running to be sure
                    sh '''
                        if docker compose ps --format json | grep -q "running"; then
                            echo "✓ SUCCESS: Container is up and running."
                            docker compose logs --tail=20
                        else
                            echo "✗ FAILURE: Container died or failed to start."
                            docker compose logs
                            exit 1
                        fi
                    '''
                }
            }
        }
    }
    
    post {
        failure {
            echo 'Deployment failed. Check the logs above.'
        }
        cleanup {
            // Optional: Clean up temporary docker images to save space
            sh 'docker image prune -f || true'
        }
    }
}