import datetime
import json
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import detail_route, api_view
from rest_framework.response import Response

from api.models import Tag, Event, Profile, PartnerOffer, Partner, CitizenAct, CitizenActQRCode, TreasureHunt, \
    UserPartnerOffer, UserCitizenAct
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
        citizenActQRCode = CitizenActQRCode.objects.filter(treasure_hunt__event=self.get_object())
        serializer = CitizenActQRCodeSerializer(citizenActQRCode, many=True)
        return Response(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class PartnerOfferViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerOfferSerializer
    queryset = PartnerOffer.objects.all()


    def retrieve(self, request, pk=None):
        # we define a custom get in order to return a representation wich is flatten
        # we find the corresponding partner_offer
        partner_offer = get_object_or_404(PartnerOffer.objects.all(), pk=pk)

        # we find the corresponding partner
        partner = get_object_or_404(Partner.objects.all(), pk=partner_offer.partner.pk)

        # we serialize the partner and include it into the representation of partner_offer
        serializer_partner = PartnerSerializer(partner)
        serializer_offer = PartnerOfferSerializer(partner_offer)

        #mixing the two dico
        data_offer = dict(serializer_offer.data)
        data_partner = dict(serializer_partner.data)

        data_offer['partner'] = data_partner

        return Response(data_offer)

    def list(self, request):
        #we define a custom list in order to get the flatten partner as a representation
        partner_offers = PartnerOffer.objects.all()
        list_return = []

        #we use retrieve !
        for offer in partner_offers:
            resp = self.retrieve(request, offer.pk)
            list_return.append(resp.data)

        return Response(list_return)


class PartnerViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerSerializer
    queryset = Partner.objects.all()

    @detail_route(methods=['get'])
    def offers(self, request, *args, **kwargs):
        # TODO : add exception in case id doesn't exist
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
        if type == 'qrcode':
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


@api_view(['POST'])
def credit(request, userId, actId):
    '''
    Create an userCitizenAct and credit the user acount
    '''
    try:
        profile = Profile.objects.get(id=userId)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    try:
        act = PartnerOffer.objects.get(id=actId)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user_citizen_act = UserCitizenAct(profile=profile, citizen_act=act, date=datetime.now())
    user_citizen_act.save()

    # we add the point to the user acount
    profile.global_points += act.points
    profile.current_points += act.points

    return Response(ProfileSerializer(profile).data)
