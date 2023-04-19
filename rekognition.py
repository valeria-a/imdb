import boto3

client = boto3.client('rekognition')
response = client.recognize_celebrities(Image={
        'S3Object': {
            'Bucket': 'edulabs-public',
            'Name': 'profile_imgs/9a8f33b6-de19-11ed-bc48-16bb156c947f.jpeg',
        }
    })
print(response)