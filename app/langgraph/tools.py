from langchain.tools import tool
from app.supabase import supabase
import os, subprocess, tarfile, tempfile, json, uuid, datetime as dt
import boto3
from app.services.generate_handler_py import generate_handler_py
from openai import OpenAI
from pydantic import BaseModel, Field

ecr = boto3.client("ecr")
lambda_client = boto3.client("lambda")
events_client = boto3.client("events")

client = OpenAI()

class GenArgs(BaseModel):
    spec: str = Field(description="Specification of the code to generate")


@tool("generate_code", args_schema=GenArgs)
def generate_code(spec: str) -> str:
    """
    Generate a code based on the spec
    """
    prompt = f"Generate a code based on the spec: {spec}"
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )
        print(response)
        return response
    except Exception as e:
        return f"Error: {e}"

class LintAndTestInputSchema(BaseModel):
    """
    Lint and test the code and return the results
    """
    code: str = Field(description="The code to lint and test.")


@tool(args_schema=LintAndTestInputSchema)
def lint_and_test(code: str) -> str:
    """
    Lint and test the code
    """
    prompt = f"Lint and test the code: {code}"
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
    )
    return response

class WriteFileArgs(BaseModel):
    file_path: str = Field(description="Destination path, e.g. workspace/handler.py")
    content:   str = Field(description="Full text to write")

@tool(args_schema=WriteFileArgs)
def write_file(file_path: str, content: str):
    """
    Write a file
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"✅ Wrote {file_path} ({len(content)} bytes)"



class DeployArgs(BaseModel):
    handler_path:   str = Field(...,description="Path to handler.py")
    function_name:  str = Field(...,description="Lambda function name")
    cron:           str = Field(...,description="6-field EventBridge cron expr")
    aws_region:     str = Field("us-east-1", description="AWS region")

def _zip_single_file(path:str) -> bytes:
    buf = tempfile.SpooledTemporaryFile()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(path, arcname="handler.py")
    buf.seek(0)
    return buf.read()

def _acct() -> str:
    return boto3.client("sts").get_caller_identity()["Account"]


@tool(args_schema=DeployArgs)
def deploy_to_lambda(handler_path: str, function_name: str, cron: str, aws_region: str)  :
    """
    Zip `handler_path`, create/update Lambda, add/update an EventBridge schedule.
    Returns the Lambda ARN.
    """
    lambda_client = boto3.client("lambda", region_name=aws_region)
    events        = boto3.client("events", region_name=aws_region)
    role_arn = "arn:aws:iam::711556655801:role/lambda-automation-exec"

    # 1) build ZIP
    zip_bytes = _zip_single_file(handler_path)

    # 2) create or update Lambda
    try:
        lambda_client.get_function(FunctionName=function_name)
        lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_bytes
        )
    except lambda_client.exceptions.ResourceNotFoundException:
        lambda_client.create_function(
            FunctionName=function_name,
            Role=role_arn,
            Runtime="python3.11",
            Handler="handler.handler",
            Code={"ZipFile": zip_bytes},
            Timeout=300,
            MemorySize=256,
            Environment={"Variables": {
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "")
            }}
        )

    # 3) (re)create EventBridge rule
    if cron:
        rule_name = f"{function_name}-schedule"
        events.put_rule(
            Name=rule_name,
            ScheduleExpression=f"cron({cron})",
            State="ENABLED",
        )
        events.put_targets(
            Rule=rule_name,
            Targets=[{
                "Id": "t1",
                "Arn": f"arn:aws:lambda:{aws_region}:{_acct()}:function:{function_name}"
            }]
        )
        lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=f"{rule_name}-perm",
            Action="lambda:InvokeFunction",
            Principal="events.amazonaws.com",
            SourceArn=f"arn:aws:events:{aws_region}:{_acct()}:rule/{rule_name}",
            Qualifier=None,
        )

    arn = f"arn:aws:lambda:{aws_region}:{_acct()}:function:{function_name}"
    return f"✅ Deployed Lambda {arn}"

tools = [generate_code, write_file, lint_and_test, deploy_to_lambda]