import os
import uuid
import random
import string
import boto3
from botocore.exceptions import ClientError
access_key = 'AKIA22NJ22FDHXMX2GXF'
access_secret = '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'
bucket_name = 'azurcams-storage'

randomString = ''.join((random.choice(string.ascii_lowercase) for x in range(20))) # run loop until the define length
print(randomString)

client_s3 = boto3.client(
    's3',
    aws_access_key_id = access_key,
    aws_secret_access_key = access_secret
)

"""
Upload Files to S3 Bucket
"""

try:
    client_s3.upload_file(
        "black.jpg",
        bucket_name,
        str(uuid.getnode()) + "-" + randomString + ".jpg"
    )
    print(uuid.getnode())

except ClientError as e:
    print('Credential is incorrect')
    print(e)
