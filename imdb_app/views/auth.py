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
