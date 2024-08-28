from rest_framework import serializers
from ...models import User
from ...custom_response import APIException


class UserRegistrationSerializer(serializers.ModelSerializer):
    # we are writing this because we need confirm password field 
    # in our Registratin Request
    password2 = serializers.CharField(
        label='Confirm password',
        style={'input_type': 'password'},
        write_only=True
    )
    class Meta:
        model = User
        fields = [
            'name',
            'email',
            'password',
            'password2',
            'tc'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # validating password and confirm password field
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError(
                "Password and Confirm Password doesn't match",
        )
        tc = attrs.get('tc')
        if tc != True:
            raise serializers.ValidationError(
                "You must accept the terms and conditions",
        )
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'created_at']