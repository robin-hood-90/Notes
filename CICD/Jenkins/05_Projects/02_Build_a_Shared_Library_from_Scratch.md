---
tags: [jenkins, cicd, projects, shared-library, groovy, vars]
aliases: ["Build Shared Library Project", "Create Jenkins Shared Library"]
status: stable
updated: 2026-05-03
---

# Project: Build a Shared Library from Scratch

> [!summary] Goal
> Create a version-controlled Jenkins Shared Library with `vars/` steps, `src/` classes, and automated tests — then consume it from a Pipeline.

## Step 1: Scaffold the Repository

```bash
mkdir pipeline-library && cd pipeline-library
git init

# Create directory structure
mkdir -p vars src/com/example resources test/vars test/src
```

```
pipeline-library/
├── vars/
├── src/com/example/
├── resources/
├── test/vars/
├── test/src/
├── Jenkinsfile
└── README.md
```

## Step 2: Create a Global Variable (`vars/`)

```groovy
// vars/buildNode.groovy
def call(Map config = [:]) {
    def nodeVersion = config.nodeVersion ?: '20'
    return {
        stage('Build') {
            sh """
                echo "Node version: ${nodeVersion}"
                node --version
                ${config.buildCmd ?: 'npm ci && npm run build'}
            """
        }
    }
}
```

## Step 3: Create a Class (`src/`)

```groovy
// src/com/example/DockerHelper.groovy
package com.example

class DockerHelper implements Serializable {
    private String registry
    private String credentialsId

    DockerHelper(String registry, String credentialsId) {
        this.registry = registry
        this.credentialsId = credentialsId
    }

    def build(String name, String tag) {
        return {
            stage('Docker Build') {
                sh "docker build -t ${registry}/${name}:${tag} ."
            }
        }
    }

    def push(String name, String tag) {
        return {
            stage('Docker Push') {
                withDockerRegistry([credentialsId: credentialsId, url: registry]) {
                    sh "docker push ${registry}/${name}:${tag}"
                }
            }
        }
    }
}
```

## Step 4: Configure in Jenkins

```
Manage Jenkins → Configure System → Global Pipeline Libraries
  Name: pipeline-library
  Default version: main
  Source: Git → https://github.com/org/pipeline-library.git
  Credentials: (if private)
  Load implicitly: ❌ (use @Library annotation instead)
```

## Step 5: Consume in a Pipeline

```groovy
// Application Jenkinsfile
@Library('pipeline-library@v1.0') _
import com.example.DockerHelper

pipeline {
    agent any
    environment {
        dockerHelper = new DockerHelper('https://ghcr.io', 'ghcr-token')
    }
    stages {
        stage('CI') {
            steps {
                script {
                    buildNode(nodeVersion: '20', buildCmd: 'npm ci && npm test')
                }
            }
        }
        stage('Docker') {
            steps {
                script {
                    dockerHelper.build('my-app', "${BUILD_NUMBER}")
                    dockerHelper.push('my-app', "${BUILD_NUMBER}")
                }
            }
        }
    }
}
```

---

## Cross-Links

- [[CICD/Jenkins/02_Core/01_Shared_Libraries_Basics]] for library syntax
- [[CICD/Jenkins/03_Advanced/04_Docker_Kubernetes_Integration_with_Pipeline]] for Docker steps
- [[CICD/Jenkins/05_Projects/03_Deploy_a_Microservice_to_Kubernetes]] for full deployment pipeline
