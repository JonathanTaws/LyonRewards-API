from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from api.models import Tag, Event, Profile, PartnerOffer, Partner
from api.serializers import TagSerializer, EventSerializer, ProfileSerializer, PartnerOfferSerializer, PartnerSerializer


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()

class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

class PartnerOfferViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerOfferSerializer
    queryset = PartnerOffer.objects.all()

class PartnerViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerSerializer
    queryset = Partner.objects.all()





