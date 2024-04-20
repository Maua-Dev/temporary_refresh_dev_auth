import os
from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    CfnOutput, 
    aws_iam as iam,
    SecretValue
)
from constructs import Construct
from aws_cdk.aws_cloudwatch import ComparisonOperator
from aws_cdk.aws_sns import Topic

from aws_cdk.aws_cloudwatch_actions import SnsAction


class IacStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.project_name = os.environ.get("PROJECT_NAME")
        self.aws_account_id = os.environ.get("AWS_ACCOUNT_ID")
        userpool_arn_dev  = os.environ.get("AUTH_DEV_SYSTEM_USERPOOL_ARN_DEV")
        userpool_arn_prod = os.environ.get("AUTH_DEV_SYSTEM_USERPOOL_ARN_PROD")

        cognito_policy = iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["cognito-idp:InitiateAuth",
                     "cognito-idp:ListUserPoolClients"],
            resources=[userpool_arn_dev, userpool_arn_prod]
        )

        lambda_fn = _lambda.Function(
            self,
            "SimpleFastAPILambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("../src"),
            environment={
                "STAGE":"TEST",
                "AUTH_DEV_SYSTEM_USERPOOL_ARN_DEV": userpool_arn_dev,
                "AUTH_DEV_SYSTEM_USERPOOL_ARN_PROD": userpool_arn_prod
                         },
            handler="app.main.handler",
            initialPolicy=[
                cognito_policy
            ],

            timeout=Duration.seconds(15),
        )

        lambda_url = lambda_fn.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE,
            cors=_lambda.FunctionUrlCorsOptions(
            allowed_origins=["*"],
            allowed_headers=["*"],
            exposed_headers=["*"],
            allowed_methods=[_lambda.HttpMethod.ALL],
            max_age=Duration.seconds(5),
            ),
        )

        lambda_fn.add_to_role_policy(cognito_policy)

        CfnOutput(self, self.stack_name + "Url",
                  value=lambda_url.url,
                  export_name= self.stack_name + 'UrlValue')    
        
        CfnOutput(self, self.stack_name + "LambdaConsole",
                    value="https://" + self.region + ".console.aws.amazon.com/lambda/home?region=" + self.region + "#/functions/" + lambda_fn.function_name + "?tab=code",
                    export_name= self.stack_name + 'LambdaConsoleValue'
                    )
        

