import json

def lambda_handler(event: dict, context) -> dict:
    """
    AWS Lambda function handler.

    Args:
        event (dict): The event data that triggered the function.
        context: The context object containing runtime information.

    Returns:
        dict: A dictionary containing the response status code and body.
    """
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }