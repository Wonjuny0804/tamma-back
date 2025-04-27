import json
from typing import Any, Dict

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda function handler that returns a greeting.

    :param event: The event data that triggers the function.
    :param context: The runtime information of the handler.
    :return: A dictionary with a status code and a greeting message.
    """
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }