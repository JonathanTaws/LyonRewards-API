from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Event, Tag, Profile, PartnerOffer, Partner, UserPartnerOffer, CitizenAct, CitizenActQRCode


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):
    # we use the userSerialiser in order to create a user at the same time we create a Profile
    id = serializers.IntegerField(source='pk', read_only=True)
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    class Meta:
        model = Profile
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'global_points', 'current_points')

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
        # we define how to update our profile

        user_data = validated_data.pop('user')

        instance.user.username = user_data['username']
        instance.user.set_password(user_data['password'])
        instance.user.first_name = user_data['first_name']
        instance.user.last_name = user_data['last_name']
        instance.user.email = user_data['email']
        instance.user.save()

        super(ProfileSerializer, self).update(instance, validated_data)

        return instance


class PartnerOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerOffer
        fields = '__all__'
        depth = 1




class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'


class UserPartnerOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPartnerOffer
        fields = "__all__"


class CitizenActSerializer(serializers.ModelSerializer):
    class Meta:
        model = CitizenAct
        fields = '__all__'


class CitizenActQRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CitizenActQRCode
        fields = '__all__'
