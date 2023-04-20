import os
import uuid

import boto3
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from imdb_app.models import UserProfile
from imdb_app.serializers.auth import SignupSerializer, UserSerializer


@api_view(['POST'])
def signup(request):
    signup_serializer = SignupSerializer(data=request.data, many=False)
    if signup_serializer.is_valid(raise_exception=True):

        # only staff can create staff
        if signup_serializer.validated_data['is_staff']:
            if not (request.user.is_authenticated and request.user.is_staff):
                return Response(status=status.HTTP_401_UNAUTHORIZED,
                                data={'is_staff': ['Only staff member can create staff user']})

        new_user = signup_serializer.create(signup_serializer.validated_data)
        user_serializer = UserSerializer(instance=new_user, many=False)
        return Response(data=user_serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    # you will get here only if the user is already authenticated!
    user_serializer = UserSerializer(instance=request.user, many=False)
    return Response(data=user_serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_img(request):
    # if request.data['file'].size > 3 * 1024 * 1024:
    #     return Response(status=400)
    #
    # jpeg_header = request.data['file'].file.read(1024)
    # request.data['file'].file.seek(0)

    # with open() as f:
    #     pass

    # generate unique id
    # bucket_name/uuid.jpeg
    random_uuid = uuid.uuid1()
    file, ext = os.path.splitext(request.data['file'].name)
    bucket_name = 'edulabs-public'
    obj_key = f"profile_imgs/{random_uuid}{ext}"

    s3 = boto3.client('s3')
    s3.upload_fileobj(request.data['file'].file, bucket_name, obj_key)

    print(f'Successfully uploaded!')

    url = f"https://{bucket_name}.s3.amazonaws.com/{obj_key}"
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)
    profile.profile_pic_url = url
    profile.save()

    return Response()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_presigned_url(request):
    # go to db and get bucket_name and obj_key according to video_id
    s3_client = boto3.client('s3')
    response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': 'edulabs-private',
                                                        'Key': 'panda.jpeg'},
                                                ExpiresIn=600)

    # response = s3_client.generate_presigned_post(bucket_name,
    #                                              object_name,
    #                                              # Fields=fields,
    #                                              # Conditions=conditions,
    #                                              ExpiresIn=expiration)
    return Response(data={'presigned_url': response})