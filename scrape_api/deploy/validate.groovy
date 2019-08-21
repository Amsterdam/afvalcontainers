#!groovy

node {
    stage("Checkout") {
        checkout scm
    }

    stage("Check database") {
        OUTPUT = sh(
            script: 'import/validate.sh',
            returnStdout: true
        ).trim()
        slacksend(
            channel: '#niels-test', 
            color: 'warning', 
            message: "Something is wrong\nFoo\nBar\n${OUPUT}"
        )
    }
}
