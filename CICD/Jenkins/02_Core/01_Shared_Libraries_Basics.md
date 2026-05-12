---
tags: [jenkins, cicd, core, shared-libraries, groovy, vars, src]
aliases: ["Shared Libraries", "Jenkins Shared Libraries", "Global Pipeline Libraries"]
status: stable
updated: 2026-05-03
---

# Shared Libraries

> [!summary] Goal
> Reuse pipeline logic across repositories using Shared Libraries — define global functions in `vars/`, classes in `src/`, and resources in `resources/`.

## Table of Contents

1. [Why Shared Libraries Matter](#why-shared-libraries-matter)
2. [Directory Structure](#directory-structure)
3. [Global Variables in `vars/`](#global-variables-in-vars)
4. [Classes in `src/`](#classes-in-src)
5. [Resources in `resources/`](#resources-in-resources)
6. [Loading Libraries](#loading-libraries)
7. [Testing Shared Libraries](#testing-shared-libraries)
8. [Versioning and Strategy](#versioning-and-strategy)
9. [Pitfalls](#pitfalls)

---

## Why Shared Libraries Matter

Without shared libraries, every Jenkinsfile repeats the same build, test, and deploy logic. A shared library centralizes this into a versioned Git repository.

```mermaid
flowchart LR
    A[Shared Library Git Repo] --> B[Pipeline A: loads @Library]
    A --> C[Pipeline B: loads @Library]
    A --> D[Pipeline C: loads @Library]
    B --> E[Same buildNode(), deployApp(), sendSlack()]
    C --> E
    D --> E
```

> [!tip] Definition
> **Shared Library**: a separate Git repository containing Groovy code that Jenkins pipelines load at runtime. It can define global pipeline steps (`vars/`), utility classes (`src/`), and static resource files (`resources/`).

---

## Directory Structure

```
pipeline-library/
├── vars/                     # Global variables (become pipeline steps)
│   ├── buildNode.groovy      → buildNode() step
│   ├── deployApp.groovy      → deployApp() step
│   ├── sendSlack.groovy       → sendSlack() step
│   └── logEnvInfo.groovy     → logEnvInfo() step
├── src/                      # Groovy classes (under package)
│   ├── com/example/
│   │   ├── PipelineHelper.groovy
│   │   ├── DockerHelper.groovy
│   │   └── SlackNotifier.groovy
├── resources/                # Static files accessed via libraryResource
│   ├── templates/
│   │   └── deploy.yaml
│   └── scripts/
│       └── cleanup.sh
├── test/                     # Unit tests (JenkinsPipelineUnit)
│   ├── vars/
│   │   └── buildNodeTest.groovy
│   └── src/
│       └── DockerHelperTest.groovy
├── Jenkinsfile               # Pipeline to test the library itself
└── README.md
```

---

## Global Variables in `vars/`

A file `vars/buildNode.groovy` becomes the pipeline step `buildNode(...)`:

```groovy
// vars/buildNode.groovy
def call(Map config = [:]) {
    def nodeVersion = config.nodeVersion ?: '20'
    def buildCmd = config.buildCmd ?: 'npm ci && npm run build'

    return {
        stage('Build') {
            sh """
                echo "Building with Node ${nodeVersion}"
                node --version
                ${buildCmd}
            """
        }
    }
}
```

```groovy
// Pipeline consuming the library
@Library('my-library') _

pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // Calls buildNode.groovy::call([nodeVersion: '20', buildCmd: 'npm ci --production && npm run build'])
                script {
                    buildNode(nodeVersion: '20', buildCmd: 'npm ci && npm run build')
                }
            }
        }
    }
}
```

### Common `vars/` patterns

```groovy
// Simple step — just a call()
def call() {
    echo "Hello from shared library"
}

// Step with parameters
def call(String message, String level = 'info') {
    echo "[${level.toUpperCase()}] ${message}"
}

// Step with closure (wraps execution)
def call(Closure body) {
    echo "Before execution"
    body()
    echo "After execution"
}
```

---

## Classes in `src/`

Classes follow standard Groovy/Java package structure and must be `Serializable`:

```groovy
// src/com/example/DockerHelper.groovy
package com.example

import groovy.transform.Synchronized

class DockerHelper implements Serializable {
    private String registry
    private String credentialsId

    DockerHelper(String registry, String credentialsId) {
        this.registry = registry
        this.credentialsId = credentialsId
    }

    def build(String imageName, String tag) {
        return {
            stage('Docker Build') {
                sh "docker build -t ${registry}/${imageName}:${tag} ."
            }
        }
    }

    def push(String imageName, String tag) {
        return {
            stage('Docker Push') {
                withDockerRegistry([credentialsId: credentialsId, url: registry]) {
                    sh "docker push ${registry}/${imageName}:${tag}"
                }
            }
        }
    }

    @Synchronized
    def login() {
        sh "echo ${registry} | docker login --username ... "
    }
}
```

```groovy
// Pipeline consuming the class
@Library('my-library')
import com.example.DockerHelper

pipeline {
    agent any
    environment {
        dockerHelper = new DockerHelper('https://ghcr.io', 'ghcr-token')
    }
    stages {
        stage('Build') {
            steps {
                script {
                    dockerHelper.build('my-app', "${BUILD_NUMBER}")
                }
            }
        }
        stage('Push') {
            steps {
                script {
                    dockerHelper.push('my-app', "${BUILD_NUMBER}")
                }
            }
        }
    }
}
```

---

## Resources in `resources/`

Access files from the library's `resources/` directory:

```groovy
// resources/templates/deploy.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${APP_NAME}
spec:
  replicas: 3
```

```groovy
// vars/deployFromTemplate.groovy
def call(String appName) {
    def template = libraryResource 'templates/deploy.yaml'
    writeFile file: 'deploy.yaml', text: template.replace('${APP_NAME}', appName)
    sh "kubectl apply -f deploy.yaml"
}
```

---

## Loading Libraries

### Global configuration (Jenkins → Manage → Configure System → Global Pipeline Libraries)

```groovy
// No @Library annotation needed — library is globally available
pipeline {
    stages {
        stage('Build') {
            steps {
                buildNode()  // From globally configured library
            }
        }
    }
}
```

### `@Library` annotation

```groovy
// Load specific version
@Library('my-library@v1.2') _

// Load multiple libraries
@Library(['my-library@main', 'other-lib@v2']) _

// Load with import
@Library('my-library@main')
import com.example.PipelineHelper

// Load specific class without making all vars global
@Library('my-library@main') _
import static com.example.PipelineHelper.*
```

### `library()` step (Scripted Pipeline)

```groovy
library 'my-library@main'
library identifier: 'my-library@v1.2', retriever: modernSCM(
    [$class: 'GitSCMSource',
     remote: 'https://github.com/org/pipeline-library.git',
     credentialsId: 'github-token']
)
```

---

## Testing Shared Libraries

Use the `JenkinsPipelineUnit` framework:

```groovy
// test/vars/buildNodeTest.groovy
class BuildNodeTest extends BasePipelineTest {

    @Override
    void setUp() throws Exception {
        super.setUp()
        helper.registerAllowedMethod('sh', [Map.class], null)
        helper.registerAllowedMethod('echo', [String.class], null)
    }

    void testBuildNodeDefault() {
        def result = loadScript('vars/buildNode.groovy')
        result.call(nodeVersion: '20', buildCmd: 'npm test')

        assertThat(helper.callStack.find { it.methodName == 'sh' }).isNotNull()
    }
}
```

```bash
# Run tests
gradle test
```

---

## Versioning and Strategy

| Strategy | How | Pros | Cons |
|----------|-----|------|------|
| **Git tags** | `@Library('lib@v1.2')`, `@Library('lib@v2.0')` | Stable, immutable | Must tag on every change |
| **Branch** | `@Library('lib@main')` | Always latest | Breaking changes break consumers |
| **SemVer with auto-promotion** | `@Library('lib@v1')` → patch updates auto-promoted | Stability + updates | Requires CI to manage tags |

### Recommendation

- Use `@Library('lib@v1.x')` for production projects
- Use `@Library('lib@main')` for testing/experimental
- Run library tests in CI before tagging new versions

---

## Pitfalls

### `@NonCPS` annotation

Groovy closures and non-Serializable classes break pipeline persistence. Use `@NonCPS` on methods that cannot be serialized:

```groovy
@NonCPS
def parseJson(String json) {
    new groovy.json.JsonSlurperClassic().parseText(json)
}
```

### Not marking classes `Serializable`

Pipeline state must be serialized (saved to disk) between steps. Classes must implement `Serializable`:

```groovy
class MyHelper implements Serializable {
    // All instance fields must be Serializable too
}
```

### `this` binding in `vars/`

Inside a `vars/` function, `this` refers to the global variable context, not the class. Use `getClass().getMethod('call', ...)` for reflection.

### Overriding built-in steps

If your `vars/` function has the same name as a built-in step (e.g., `docker`), it replaces the built-in one.

**Fix**: Prefix custom step names with a convention: `myDocker`, `customDocker`.

---

> [!question]- Interview Questions
>
> **Q: What is the directory structure of a Jenkins Shared Library?**
> A: `vars/` for global pipeline steps, `src/` for Groovy classes under packages, `resources/` for static files. The library is loaded via `@Library('name@version')` annotation.
>
> **Q: What is the difference between `vars/` and `src/`?**
> A: `vars/` files define global variables that become pipeline steps (e.g., `buildNode()`). `src/` files define standard Groovy classes that must be imported explicitly.
>
> **Q: How do you test a Shared Library?**
> A: Use the `JenkinsPipelineUnit` test framework. Register allowed methods with `helper.registerAllowedMethod` and assert expected calls on the `helper.callStack`.

---

## Cross-Links

- [[CICD/Jenkins/01_Foundations/01_Jenkinsfile_Pipeline_Basics]] for Jenkinsfile syntax
- [[CICD/Jenkins/01_Foundations/03_Credentials_and_Secrets]] for credentials in shared libraries
- [[CICD/Jenkins/05_Projects/02_Build_a_Shared_Library_from_Scratch]] for hands-on project

---

## References

- [Shared Libraries](https://www.jenkins.io/doc/book/pipeline/shared-libraries/)
- [JenkinsPipelineUnit](https://github.com/jenkinsci/JenkinsPipelineUnit)
- [@NonCPS](https://www.jenkins.io/doc/book/pipeline/persistence/#noncps)
