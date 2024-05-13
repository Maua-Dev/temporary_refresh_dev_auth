from fastapi import FastAPI, HTTPException
from mangum import Mangum
import boto3
import os
from botocore.exceptions import ClientError
from src.app.errors.controller_errors import WrongTypeParameters, MissingParameters
from src.app.errors.entity_errors import ParamNotValidated

app = FastAPI()

@app.post("/refresh_token")
def refresh_token(request: dict):
    try:
        if request.get("refresh_token") is None:
            raise MissingParameters("refresh_token")
        if request.get("stage") is None:
            raise MissingParameters("stage")
        
        if type(request.get("refresh_token")) != str:
            raise WrongTypeParameters("refresh_token", "str", type(request.get("refresh_token")).__name__)
        if type(request.get("stage")) != str:
            raise WrongTypeParameters("stage", "str", type(request.get("stage")).__name__)
        
        token = request.get("refresh_token")
        stage = request.get("stage")
        
        if len(token) == 0:
            raise ParamNotValidated("refresh_token", "refresh_token can't be empty")
        if len(stage) == 0:
            raise ParamNotValidated("stage", "stage can't be empty")
        
        if stage not in ["dev", "prod"]:
            raise ParamNotValidated("stage", "stage must be 'dev' or 'prod'")
        
        if stage == "dev":
            userpool_arn = os.getenv("AUTH_DEV_SYSTEM_USERPOOL_ARN_DEV")

        elif stage == "prod":
            userpool_arn = os.getenv("AUTH_DEV_SYSTEM_USERPOOL_ARN_PROD")

        print(f'userpool_arn: {userpool_arn}')
        
        # get client id based on userpool arn
        client = boto3.client("cognito-idp")
        response = client.list_user_pool_clients(UserPoolId=userpool_arn.split("/")[1])
        client_id = response["UserPoolClients"][0]["ClientId"]
    
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': token
            }
        )

        id_token = response["AuthenticationResult"]["IdToken"]
        access_token = response["AuthenticationResult"]["AccessToken"]

        return {"id_token": id_token, "access_token": access_token}
    except ClientError as e:
        errorCode = e.response.get('Error').get('Code')
        if errorCode == 'NotAuthorizedException':
            raise HTTPException(status_code=401, detail="Invalid token")
        else:
            print(f'error: {e}')
            raise HTTPException(status_code=500, detail="Internal server error")
    except MissingParameters as e:
        raise HTTPException(status_code=400, detail=str(e.message))
    except WrongTypeParameters as e:
        raise HTTPException(status_code=400, detail=str(e.message))
    except ParamNotValidated as e:
        raise HTTPException(status_code=400, detail=str(e.message))
        

handler = Mangum(app, lifespan="off")
