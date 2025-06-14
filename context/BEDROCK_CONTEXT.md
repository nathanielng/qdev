# Bedrock Context

## Bedrock Model IDs

Bedrock Model IDs for cross-region inference profiles can be found at https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-support.html. For example:

```
us.amazon.nova-micro-v1:0
us.amazon.nova-lite-v1:0
us.amazon.nova-pro-v1:0
us.anthropic.claude-3-5-haiku-20241022-v1:0
us.anthropic.claude-3-5-sonnet-20241022-v2:0
us.anthropic.claude-3-7-sonnet-20250219-v1:0
us.anthropic.claude-sonnet-4-20250514-v1:0
```


## Amazon Bedrock Converse API

Use the Amazon Bedrock Converse API.
For example:

```python
import boto3

# Load AWS Credentials from the environment
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', None)
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', None)
AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', None)
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'us.amazon.nova-lite-v1:0')

if AWS_ACCESS_KEY and AWS_SECRET_ACCESS_KEY and AWS_SESSION_TOKEN:
    session = boto3.Session(
        aws_access_key_id = AWS_ACCESS_KEY,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
        aws_session_token = AWS_SESSION_TOKEN,
        region_name = AWS_DEFAULT_REGION
        # profile_name = 'your-profile'
    )
else:
    session = boto3.Session()

def get_bedrock_runtime_client(region='us-west-2'):
    return boto3.client(
        service_name = 'bedrock-runtime',
        region_name=region,
        boto_session=session
    )

def invoke_bedrock_model(prompt, model_id='us.amazon.nova-lite-v1:0', region='us-west-2', max_tokens=1000, temperature=0.1):
    try:       
        bedrock_runtime = get_bedrock_runtime_client(region)
        messages = [{ "role": "user", "content": [{"text": prompt}] }]
        response = bedrock_runtime.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig={"temperature": temperature}
        )
        output = response.get('output', {}).get('message', None)
        # logging.info(json.dumps(output, default=str))
        return output.get('content')[0].get('text', '')
    
    except Exception as e:
        print(f'Error invoking Bedrock model: {e}')
        return f'Error invoking Bedrock model: {e}'
```
