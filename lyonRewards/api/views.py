from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.utils.six import BytesIO
from rest_framework import viewsets, status, mixins, generics
from rest_framework.parsers import JSONParser
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from api.models import Tag, Event, Profile, PartnerOffer, Partner, CitizenAct, CitizenActQRCode, TreasureHunt
from api.serializers import (
    TagSerializer, EventSerializer, ProfileSerializer, PartnerOfferSerializer, PartnerSerializer,
    CitizenActSerializer, CitizenActQRCodeSerializer)



class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class EventViewSet(mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def list(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        for s_event in serializer.data:
            print(s_event['id'])
            print(Event.objects.get(id=s_event['id']))
            s_event['progress'] = Event.objects.get(id=s_event['id']).progress(request.query_params['userid'])
        return Response(serializer.data)


    @detail_route(methods=['post'])
    def hunt(self, request, *args, **kwargs):
        treasure_hunt = TreasureHunt(event=self.get_object())
        treasure_hunt.save()
        return Response(status=status.HTTP_201_CREATED)

    @detail_route(methods=['get'])
    def qrcodes(self, request, *args, **kwargs):
        citizenActQRCode = CitizenActQRCode.objects.filter(treasure_hunt__event = self.get_object())
        serializer = CitizenActQRCodeSerializer(citizenActQRCode, many=True)
        return Response(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

class PartnerOfferViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerOfferSerializer
    queryset = PartnerOffer.objects.all()

class PartnerViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerSerializer
    queryset = Partner.objects.all()

    @detail_route(methods=['get'])
    def offers(self, request, *args, **kwargs):
        #TODO : add exception in case id doesn't exist
        offers_list = self.get_object().partneroffer_set.all()
        serializer = PartnerOfferSerializer(offers_list, many=True)
        return Response(serializer.data)

class CitizenActViewSet(mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):

    serializer_class = CitizenActSerializer
    queryset = CitizenAct.objects.all()

    def create(self, request):
        type = request.query_params.get('type')
        if type == 'qrcode' :
            serializer = CitizenActQRCodeSerializer(data=request.data)
            if serializer.is_valid():
                citizenActQRCode = CitizenActQRCode(**serializer.validated_data)
                print(citizenActQRCode.treasure_hunt)
                citizenActQRCode.save()
                return Response(serializer.errors, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def update(self, request):
        pass

    @detail_route(methods=['get'])
    def event(self, request, *args, **kwargs):
        try:
            event = self.get_object().citizenactqrcode.treasure_hunt.event
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except(ObjectDoesNotExist):
            return Response(status=status.HTTP_204_NO_CONTENT)






