pipeline {
    agent any
    options { disableConcurrentBuilds() }
    stages {
        stage('Stage 0: Clone Repo') {
            steps {
                echo 'Cloning..'
		git branch: 'main', credentialsId: '3464aa34-c94d-42d6-9cd7-fdfec72319ab', url: 'https://github.com/Logan-Chayet/Lab11PoC.git'
            }
        }
        stage('Stage 1: Install Packages') {
            steps {
                echo 'Installing..'
		sh 'pip3 install --upgrade ncclient pandas netaddr prettytable'
            }
        }
	stage('Stage 3: Run the Application') {
            steps {
                echo 'Running..'
		sh 'python3 /var/lib/jenkins/workspace/Lab11PoC@2/ANSIBLE/playbookCreation.py'
            }
        }
    }
    post {
	always {
		emailext body: '$DEFAULT_CONTENT', 
		recipientProviders: [
		    [$class: 'CulpritsRecipientProvider'],
		    [$class: 'DevelopersRecipientProvider'],
		    [$class: 'RequesterRecipientProvider']
		], 
		replyTo: '$DEFAULT_REPLYTO', 
		subject: '$DEFAULT_SUBJECT',
		to: '$DEFAULT_RECIPIENTS'
	}
    }
}
