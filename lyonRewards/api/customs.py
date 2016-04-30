# -*- coding: utf-8 -*-
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from api.models import Profile
from api.serializers import ProfileSerializer


class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        profil = Profile.objects.get(user=user)

        data_return = ProfileSerializer(profil).data
        return Response({'token': token.key, 'user': data_return})


obtain_auth_token = CustomObtainAuthToken.as_view()