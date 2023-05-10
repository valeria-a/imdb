import jwt
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

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


class UsersGenericView(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]



class UpdateUserPermission(BasePermission):

    def has_permission(self, request, view):
        return True

    # Note, validation that if is_staff field is sent - it can only
    # be changed by the staff user is done in the serializer
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id or request.user.is_staff


class UpdateUserGenericView(UpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [UpdateUserPermission]

    # Treat PUT as PATCH
    def put(self, request, *args, **kwargs):
        return self.patch(request, *args, *kwargs)

from google.oauth2 import id_token
from google.auth.transport import requests

@api_view(['POST'])
def google_auth(request):
    CLIENT_ID = "872794659630-ehu55i6a7fbglef45mjno5pgjv7qeab9.apps.googleusercontent.com"
    google_token = request.headers['Authorization']
    print('auth header:', google_token)
    idinfo = id_token.verify_oauth2_token(google_token, requests.Request(), CLIENT_ID)
    print(idinfo)
    return Response()


# https://developers.google.com/identity/gsi/web/guides/verify-google-id-token
# from google.oauth2 import id_token
# from google.auth.transport import requests
#
# # (Receive token by HTTPS POST)
# # ...
#
# try:
#     # Specify the CLIENT_ID of the app that accesses the backend:
#     idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
#
#     # Or, if multiple clients access the backend server:
#     # idinfo = id_token.verify_oauth2_token(token, requests.Request())
#     # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
#     #     raise ValueError('Could not verify audience.')
#
#     # If auth request is from a G Suite domain:
#     # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
#     #     raise ValueError('Wrong hosted domain.')
#
#     # ID token is valid. Get the user's Google Account ID from the decoded token.
#     userid = idinfo['sub']
# except ValueError:
#     # Invalid token
#     pass