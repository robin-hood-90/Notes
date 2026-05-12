---
tags: [aws, project, serverless, lambda, api-gateway, dynamodb, cognito, cloudfront, waf]
aliases: ["Serverless API Project", "Lambda + API Gateway + DynamoDB", "Full Serverless App"]
status: stable
updated: 2026-05-11
---

# Project: Serverless REST API with Lambda, API Gateway, DynamoDB

> [!summary] Goal
> Build a full serverless REST API: API Gateway REST → Cognito authorizer → Lambda handler → DynamoDB. Add CloudFront distribution, WAF rate-based rule, API usage plan, and CloudWatch dashboard.

## Architecture

```text
CloudFront (CDN)
  → WAF (rate-based rule)
    → API Gateway REST (custom domain, usage plan)
      → Cognito Authorizer (JWT)
        → Lambda handler (CRUD)
          → DynamoDB (data storage)
```

### Resources

```yaml
# SAM template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Resources:
  UserTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub ${AWS::StackName}-users
      AttributeDefinitions:
        - AttributeName: userId, AttributeType: S
      KeySchema:
        - AttributeName: userId, KeyType: HASH
      BillingMode: PAY_PER_REQUEST

  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: index.handler
      Runtime: nodejs20.x
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref UserTable
      Events:
        Api:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
            Auth:
              Authorizer: CognitoAuthorizer

  CognitoAuthorizer:
    Type: AWS::ApiGateway::Authorizer
    Properties:
      Name: CognitoAuthorizer
      RestApiId: !Ref ApiGatewayRestApi
      Type: COGNITO_USER_POOLS
      ProviderARNs: [!GetAtt UserPool.Arn]
      IdentitySource: method.request.header.Authorization
```

---

## Cross-Links

- [[CICD/AWS/01_Foundations/07_Lambda_Functions_Events_and_Best_Practices]] for Lambda configuration
- [[CICD/AWS/01_Foundations/10_API_Gateway_REST_HTTP_WebSocket]] for API Gateway REST APIs
- [[CICD/AWS/01_Foundations/06_DynamoDB_NoSQL]] for DynamoDB tables and GSIs
- [[CICD/AWS/01_Foundations/08_Route53_and_CloudFront]] for CloudFront distribution
