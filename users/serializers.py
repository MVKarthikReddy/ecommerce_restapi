from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'name', 'phone', 'address', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', '')
        )
        return user

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.address = validated_data.get('address', instance.address)

        if validated_data.get('password'):
            instance.set_password(validated_data['password'])
        instance.save()

        return instance
