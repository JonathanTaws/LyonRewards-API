from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Event, Tag, Profile, PartnerOffer, Partner, UserPartnerOffer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = "__all__"
        fields = ("id", "username", "password", "first_name", "last_name", "email")


class ProfileSerializer(serializers.ModelSerializer):
    # we use the userSerialiser in order to create a user at the same time we create a Profile
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ('id', 'user', 'globalPoints', 'currentPoints')

    def create(self, validated_data):
        # we define what the serializer must do when creating a profile

        # we first create a user (a django user)
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        user.save()

        # then we can create our profile, giving it our user
        profile = Profile.objects.create(user=user, **validated_data)

        return profile

    def update(self, instance, validated_data):
        # we define how to update our profile : not the best, we'd like to use **kwargs

        user_data = validated_data.pop('user')

        instance.user.set_password(user_data['password'])
        instance.user.username = user_data['username']
        instance.user.first_name = user_data['first_name']
        instance.user.last_name = user_data['last_name']
        instance.user.email = user_data['email']
        instance.user.save()

        instance.globalPoints = validated_data['globalPoints']
        instance.currentPoints = validated_data['currentPoints']
        instance.save()

        return instance


class PartnerOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerOffer
        fields = '__all__'


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'


class UserPartnerOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPartnerOffer
        fields = "__all__"
