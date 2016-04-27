from django.shortcuts import render
from rest_framework import viewsets
from api.models import Tag, Event
from api.serializers import TagSerializer, EventSerializer


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()


