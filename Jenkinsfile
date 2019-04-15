#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block()
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t
    }
    finally {
        if (tearDown) {
            tearDown()
        }
    }
}


node {
    stage("Checkout") {
        checkout scm
    }

    stage('Test') {
        tryStep "test", {
            sh "api/deploy/test/test.sh &&" +
               "scrape_api/deploy/test/test.sh"
        }
    }

    stage("Build dockers") {
        tryStep "build", {
            docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
            def importer = docker.build("datapunt/afvalcontainers_importer:${env.BUILD_NUMBER}", "--build-arg http_proxy=${JENKINS_HTTP_PROXY_STRING} --build-arg https_proxy=${JENKINS_HTTP_PROXY_STRING} scrape_api")
                importer.push()
                importer.push("acceptance")
            def api = docker.build("datapunt/afvalcontainers:${env.BUILD_NUMBER}", "--build-arg http_proxy=${JENKINS_HTTP_PROXY_STRING} --build-arg https_proxy=${JENKINS_HTTP_PROXY_STRING} api")
                api.push()
                api.push("acceptance")
            }
        }
    }
}


String BRANCH = "${env.BRANCH_NAME}"

if (BRANCH == "master") {

    node {
        stage('Push acceptance image') {
            tryStep "image tagging", {
                docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
                    def image = docker.image("datapunt/afvalcontainers:${env.BUILD_NUMBER}")
                    image.pull()
                    image.push("acceptance")
                }
            }
        }
    }

    node {
        stage("Deploy to ACC") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-afvalcontainers.yml'],
                ]
            }
        }
    }

    stage('Waiting for approval') {
        slackSend channel: '#ci-channel', color: 'warning', message: 'Afval Container API Waiting for Production Release - please confirm'
        input "Deploy to Production?"
    }

    node {
        stage('Push production image') {
            tryStep "image tagging", {
                docker.withRegistry('https://repo.data.amsterdam.nl','docker-registry') {
                def api = docker.image("datapunt/afvalcontainers:${env.BUILD_NUMBER}")
                def importer = docker.image("datapunt/afvalcontainers_importer:${env.BUILD_NUMBER}")

                importer.push("production")
                importer.push("latest")

                api.push("production")
                api.push("latest")
            }
        }
    }

    node {
        stage("Deploy") {
            tryStep "deployment", {
                build job: 'Subtask_Openstack_Playbook',
                parameters: [
                    [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                    [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-afvalcontainers.yml'],
                ]
            }
        }
    }
}
}