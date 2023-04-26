from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator


class SignupSerializer(ModelSerializer):

    password = serializers.CharField(
        max_length=128, validators=[validate_password], write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'is_staff']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'read_only': True},
        }
        validators = [UniqueTogetherValidator(User.objects.all(), ['email'])]

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['email'],
                                   email=validated_data['email'],
                                   first_name=validated_data.get('first_name', ''),
                                   last_name=validated_data.get('last_name', ''))
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'is_staff')
        extra_kwargs = {
            'email': {'read_only': True},
            'is_staff': {'required': False}
        }

    def validate(self, attrs):
        if attrs.get('is_staff') is not None and not self.instance.is_staff:
            raise serializers.ValidationError('Only staff can update is_staff field')
        return attrs