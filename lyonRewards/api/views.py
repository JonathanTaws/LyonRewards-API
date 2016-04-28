import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import detail_route, api_view
from rest_framework.response import Response

from api.models import Tag, Event, Profile, PartnerOffer, Partner, CitizenAct, CitizenActQRCode, TreasureHunt, \
    UserPartnerOffer
from api.serializers import (
    TagSerializer, EventSerializer, ProfileSerializer, PartnerOfferSerializer, PartnerSerializer,
    CitizenActSerializer, CitizenActQRCodeSerializer)



class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()

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



@api_view(['POST'])
def debit(request, userId, offerId):
    '''
    Create an UserPartnerOffer and debit the user acount
    '''
    try:
        profile = Profile.objects.get(id=userId)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    try:
        offer = PartnerOffer.objects.get(id=offerId)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # we save it in database
    user_partner_offer = UserPartnerOffer(profile=profile, partner_offer=offer, date=datetime.now())
    user_partner_offer.save()

    # we deduce the corresponding amount of money from the user
    if profile.current_points > offer.points:
        profile.current_points -= offer.points
        profile.save()

        # we return the new user if we deduced the correct amount of points
        return Response(ProfileSerializer(profile).data)

    return Response(status=status.HTTP_403_FORBIDDEN)
