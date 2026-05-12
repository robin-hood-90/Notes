---
tags: [jenkins, cicd, projects, migration, freestyle, pipeline-conversion]
aliases: ["Migrate Freestyle to Pipeline Project", "Pipeline Migration Guide"]
status: stable
updated: 2026-05-03
---

# Project: Migrate a Freestyle Job to Pipeline

> [!summary] Goal
> Convert a click-configured Freestyle job into a version-controlled Jenkinsfile Pipeline — with before/after comparison, step-by-step migration, and verification.

## Step 1: Analyze the Existing Freestyle Job

Open the Freestyle job in Jenkins and document:

```
Job: my-app-legacy
Source Control: Git → https://github.com/org/my-app.git (branch */main)
Build Triggers: Poll SCM (H/5 * * * *)
Environment Variables: NODE_ENV=production
Build Steps:
  1. Execute shell: npm ci
  2. Execute shell: npm run build
  3. Execute shell: npm run test
  4. Execute shell: ./deploy.sh
Post-build Actions:
  1. Archive artifacts: dist/**/*.zip
  2. Publish JUnit test result: reports/**/*.xml
  3. Email: team@example.com
```

## Step 2: Create the Jenkinsfile

```groovy
pipeline {
    agent any
    triggers { pollSCM('H/5 * * * *') }
    environment {
        NODE_ENV = 'production'
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Install') {
            steps { sh 'npm ci' }
        }
        stage('Build') {
            steps { sh 'npm run build' }
        }
        stage('Test') {
            steps {
                sh 'npm run test'
                junit 'reports/**/*.xml'
            }
        }
        stage('Deploy') {
            when { branch 'main' }
            steps { sh './deploy.sh' }
        }
    }
    post {
        success { archiveArtifacts artifacts: 'dist/**/*.zip' }
        always { emailext(to: 'team@example.com', subject: "${env.JOB_NAME} - ${currentBuild.currentResult}", body: "Build ${env.BUILD_URL}") }
    }
}
```

## Step 3: Test the Pipeline

```
1. Create a Multibranch Pipeline job pointing to the same Git repo
2. Run the pipeline on a feature branch
3. Verify all stages pass with same outputs as Freestyle
4. Compare artifacts, test results, notifications
```

## Step 4: Archive and Delete

```bash
# Save the old Freestyle config for reference
cp $JENKINS_HOME/jobs/my-app-legacy/config.xml /backup/freestyle-configs/

# Disable the old job (don't delete immediately)
# Disable → OK → verify Pipeline runs for 1 week
# Then delete

# Via CLI:
java -jar jenkins-cli.jar -s https://jenkins.example.com/ disable-job my-app-legacy
```

## Step 5: Migration Check List

- [ ] All build steps mapped to pipeline stages
- [ ] All post-build actions mapped to `post` blocks
- [ ] Credentials moved to Jenkins credential store and referenced with `credentials()`
- [ ] Environment variables moved to `environment` block
- [ ] Build triggers mapped to `triggers` block
- [ ] SCM polling configured identically
- [ ] Pipeline runs for 1 week without issues
- [ ] Old Freestyle job disabled and archived

---

## Cross-Links

- [[CICD/Jenkins/02_Core/04_Freestyle_vs_Pipeline_and_Migration]] for detailed mapping table
- [[CICD/Jenkins/01_Foundations/01_Jenkinsfile_Pipeline_Basics]] for pipeline syntax
- [[CICD/Jenkins/01_Foundations/03_Credentials_and_Secrets]] for credential migration
