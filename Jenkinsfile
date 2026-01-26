pipeline {
    agent any
    environment {
        // Updated naming convention
        IMAGE = 'maoridi/mullvad-remove'
        // You will create this ID in Jenkins UI later
        REGISTRY_CREDS = 'docker-hub-creds'
        // Mullvad account number from Jenkins credentials
        MULLVAD_ACCOUNT_NUMBER = credentials('mullvad-account-number')
    }
    stages {
        stage('Build & Push') {
            steps {
                script {
                    docker.withRegistry('', REGISTRY_CREDS) {
                        // Builds using the Dockerfile in root
                        def app = docker.build("${IMAGE}:${env.BUILD_NUMBER}")
                        app.push()
                        app.push('latest')
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                // Deploys the chart from the charts/worker folder
                // We disable serviceAccount creation to keep it simple
                sh """
                  helm upgrade --install mullvad-remove ./charts/worker \
                  --set image.repository=${IMAGE} \
                  --set image.tag=${env.BUILD_NUMBER} \
                  --set serviceAccount.create=false
                """
            }
        }
    }
}