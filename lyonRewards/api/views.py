from datetime import datetime
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route, api_view
from rest_framework.response import Response
from api.models import Tag, Event, Profile, PartnerOffer, Partner, UserPartnerOffer
from api.serializers import TagSerializer, EventSerializer, ProfileSerializer, PartnerOfferSerializer, \
    PartnerSerializer, \
    UserPartnerOfferSerializer


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
