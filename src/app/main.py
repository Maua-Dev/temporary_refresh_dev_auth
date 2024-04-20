from fastapi import FastAPI, HTTPException
from mangum import Mangum
import boto3
import os
from botocore.exceptions import ClientError



app = FastAPI()

@app.post("/refresh_token")
def refresh_token(request: dict):
    token = request.get("refresh_token")
    stage = request.get("stage")

    if not token:
        raise HTTPException(status_code=400, detail="Missing token")
    

    if not stage:
        raise HTTPException(status_code=400, detail="Missing stage")
    
    if stage not in ["dev", "prod"]:
        raise HTTPException(status_code=400, detail="Invalid stage")
    
    if stage == "dev":
        userpool_arn = os.getenv("AUTH_DEV_SYSTEM_USERPOOL_ARN_DEV")

    elif stage == "prod":
        userpool_arn = os.getenv("AUTH_DEV_SYSTEM_USERPOOL_ARN_PROD")


    # get client id based on userpool arn
    client = boto3.client("cognito-idp")
    response = client.list_user_pool_clients(UserPoolId=userpool_arn.split("/")[1])
    client_id = response["UserPoolClients"][0]["ClientId"]
    
    try:
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
            raise HTTPException(status_code=500, detail="Internal server error")

        

handler = Mangum(app, lifespan="off")
