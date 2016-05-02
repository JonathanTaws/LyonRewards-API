# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import detail_route, list_route, api_view
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token

from api.models import (
    Tag, Event, Profile, PartnerOffer, Partner, CitizenAct, CitizenActQRCode, TreasureHunt,
    UserPartnerOffer, UserCitizenAct, CitizenActTravel)
from api.serializers import (
    TagSerializer, EventSerializer, ProfileSerializer, PartnerOfferSerializer, PartnerSerializer,
    CitizenActSerializer, CitizenActQRCodeSerializer, GroupSerializer, TreasureHuntSerializer,
    UserCitizenActSerializer, CitizenActTravelSerializer)


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()


class TreasureHuntViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TreasureHuntSerializer
    queryset = TreasureHunt.objects.all()


class UserCitizenActViewSet(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    serializer_class = UserCitizenActSerializer
    queryset = UserCitizenAct.objects.all()


class EventViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def list(self, request):
        events = None

        if 'type' in request.query_params:
            type = request.query_params['type']
            if type == 'past':
                events = Event.objects.filter(end_date__lt=datetime.now())
            elif type == 'ongoing':
                events = Event.objects.filter(start_date__lt=datetime.now(), end_date__gt=datetime.now())
            elif type == 'future':
                events = Event.objects.filter(start_date__gt=datetime.now())
            else:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
        else:
            events = Event.objects.all()

        show_progress = False
        if 'userId' in request.query_params:
            show_progress = True
            if 'participatedOnly' in request.query_params:
                if request.query_params['participatedOnly'] == "true":
                    events = events.filter(
                        treasurehunt__citizenactqrcode__usercitizenact__profile__id=request.query_params[
                            'userId']).distinct()

        # sorting is done after all others operation on events
        if 'sort' in request.query_params:
            sort_type = request.query_params['sort']
            if sort_type == 'startDate':
                events = events.order_by('start_date')

        # serialization
        serializer = EventSerializer(events, many=True)

        # Extra attributes are added to the data after serialization
        if show_progress:
            for s_event in serializer.data:
                s_event['progress'] = Event.objects.get(id=s_event['id']).progress(request.query_params['userId'])

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        serializer = EventSerializer(self.get_object())
        if 'userId' in request.query_params:
            s_dict = dict(serializer.data)
            s_dict['progress'] = Event.objects.get(id=serializer.data['id']).progress(request.query_params['userId'])
            return Response(s_dict, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def hunt(self, request, *args, **kwargs):
        serializer = TreasureHuntSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['get'])
    def qrcodes(self, request, *args, **kwargs):
        citizenActQRCode = CitizenActQRCode.objects.filter(treasure_hunt__event=self.get_object())
        serializer = CitizenActQRCodeSerializer(citizenActQRCode, many=True)
        if 'userId' in request.query_params:
            for s_qrCodes in serializer.data:
                try:
                    completion = (
                        UserCitizenAct.objects.get(
                            citizen_act__id=s_qrCodes.get('id'),
                            profile__id=request.query_params.get('userId')))
                    s_qrCodes['completed'] = True
                    s_qrCodes['date'] = completion.date
                except ObjectDoesNotExist:
                    s_qrCodes['completed'] = False
        return Response(serializer.data)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    # permission_classes = (IsAuthenticatedOrReadOnly,)

    @list_route()
    def ranking(self, request):
        profiles = None

        # filtering on existing property
        if 'time' in request.query_params:
            time = request.query_params['time']
            if time == 'lastTfh':
                profiles = sorted(Profile.objects.all(), key=lambda m: m.last_tfh_points, reverse=True)
            elif time == 'currentMonth':
                profiles = sorted(Profile.objects.all(), key=lambda m: m.current_month_points, reverse=True)
            else:
                return Response({'error': '{0} is not a acceptable time parameter'.format(time)},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

        # filtering on parameter
        elif 'month' in request.query_params:
            month = int(request.query_params['month'])
            if 1 < month > 12:
                return Response({'error': 'Month should be in range 1-12 (included)'.format(month)},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
            profiles = sorted(Profile.objects.all(), key=lambda m: m.month_points(month), reverse=True)

        # no filtering
        else:
            profiles = Profile.objects.all().order_by('-global_points')

        # Returned set limitation
        if 'limit' in request.query_params:
            profiles = profiles[:int(request.query_params['limit'])]

        # serialization
        serializer = ProfileSerializer(profiles, many=True)

        if 'userId' in request.query_params:
            for index, profile in enumerate(profiles):
                if profile.id == int(request.query_params['userId']):
                    return Response(
                        {'ranking': serializer.data, 'specified_user_rank': index + 1},
                        status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @detail_route()
    def history(self, request):
        pass

    @detail_route(methods=['post'])
    def travel(self, request, *args, **kwargs):
        def number_times_step_passed(step, current_distance, total_distance):
            '''
            :return the number of times the step is passed
            '''
            return int((total_distance % step + current_distance) / step)

        def create_citizen_act_travel(number_passed, citizen_acts, profile, citizen_act_travel):
            '''
            Create user citizen
            '''
            for i in range(number_passed):
                user_citizen_act_travel = UserCitizenAct(profile=profile, citizen_act=citizen_act_travel,
                                                         date=datetime.now())
                user_citizen_act_travel.save()
                citizen_acts.append(CitizenActTravelSerializer(citizen_act_travel).data)

        # we retrieve the json given by the mobile user, and give it to random forest
        profile = self.get_object()
        data = request.data

        #####give it to random forest######
        transports = ["bike", "walk", "tram", "bus"]

        from random import randint
        dico_random_forest = {"type": "bike", "distance": 120}

        citizen_act_travel = CitizenActTravel.objects.get(type=dico_random_forest['type'])

        if citizen_act_travel == None:
            return Response({"Error": "Please create in database the act travel"}, status=status.HTTP_400_BAD_REQUEST)


        # we create the citizen acts if needed
        newTotalKm = 0
        citizen_acts = []
        number_passed = 0

        if dico_random_forest['type'] == "bike":
            # if we passed at least one time the step
            print(number_passed)
            number_passed = number_times_step_passed(citizen_act_travel.distance_step, dico_random_forest['distance'],
                                                     profile.bike_distance)

            print(number_passed)

            if number_passed > 0:
                create_citizen_act_travel(number_passed, citizen_acts, profile, citizen_act_travel)

            profile.bike_distance += dico_random_forest['distance']
            newTotalKm = profile.bike_distance

        elif dico_random_forest['type'] == "walk":
            number_passed = number_times_step_passed(citizen_act_travel.distance_step, dico_random_forest['distance'],
                                                     profile.walk_distance)
            if number_passed > 0:
                create_citizen_act_travel(number_passed, citizen_acts, profile, citizen_act_travel)

            profile.bike_walk += dico_random_forest['distance']
            newTotalKm = profile.walk_distance

        elif dico_random_forest['type'] == "tram":
            number_passed = number_times_step_passed(citizen_act_travel.distance_step, dico_random_forest['distance'],
                                                     profile.tram_distance)
            if number_passed > 0:
                create_citizen_act_travel(number_passed, citizen_acts, profile, citizen_act_travel)

            profile.bike_tram += dico_random_forest['distance']
            newTotalKm = profile.tram_distance

        elif dico_random_forest['type'] == "bus":
            number_passed = number_times_step_passed(citizen_act_travel.distance_step, dico_random_forest['distance'],
                                                     profile.tram_distance)
            if number_passed > 0:
                create_citizen_act_travel(number_passed, citizen_acts, profile, citizen_act_travel)

            profile.bike_bus += dico_random_forest['distance']
            newTotalKm = profile.bus_distance
        else:
            return Response({"Error": "Type from random forest incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        points_granted = 0

        for citizen_act in citizen_acts:
            points_granted = number_passed * citizen_act['points']

        profile.global_points += points_granted
        profile.current_points += points_granted

        dict_return = {
            "mode": dico_random_forest['type'],
            "new_total_km": newTotalKm,
            "step_success": citizen_act_travel.distance_step,
            "points_granted": points_granted,
            "citizen_acts": citizen_acts
        }

        profile.save()
        return Response(dict_return)


class PartnerOfferViewSet(viewsets.ModelViewSet):
    serializer_class = PartnerOfferSerializer
    queryset = PartnerOffer.objects.all()

    def retrieve(self, request, pk=None):
        # we define a custom get in order to return a representation which is flatten
        # we find the corresponding partner_offer
        partner_offer = get_object_or_404(PartnerOffer.objects.all(), pk=pk)

        # we find the corresponding partner
        partner = get_object_or_404(Partner.objects.all(), pk=partner_offer.partner.pk)

        # we serialize the partner and include it into the representation of partner_offer
        serializer_partner = PartnerSerializer(partner)
        serializer_offer = PartnerOfferSerializer(partner_offer)

        # mixing the two dico
        data_offer = dict(serializer_offer.data)
        data_partner = dict(serializer_partner.data)

        data_offer['partner'] = data_partner

        return Response(data_offer)

    def list(self, request):
        # we define a custom list in order to get the flatten partner as a representation
        partner_offers = PartnerOffer.objects.all()
        list_return = []

        # we use retrieve !
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
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    serializer_class = CitizenActSerializer
    queryset = CitizenAct.objects.all()

    def retrieve(self, request, pk=None, *args, **kwargs):
        serializer = None

        # type parameter
        if 'type' in request.query_params:
            type = request.query_params['type']

            # type CitizenActQRCode
            if type == 'qrcode':
                try:
                    serializer = CitizenActQRCodeSerializer(self.get_object().citizenactqrcode)
                except CitizenActQRCode.DoesNotExist:
                    return Response({'Error': 'The requested CitizenAct is not of the specified type'},
                                    status=status.HTTP_400_BAD_REQUEST)
                s_dict = dict(serializer.data)

                # add completion if userId specified
                if 'userId' in request.query_params:

                    try:
                        completion = (
                            UserCitizenAct.objects.get(
                                citizen_act__id=serializer.data['id'],
                                profile__id=request.query_params['userId']))
                        s_dict['completed'] = True
                        s_dict['date'] = completion.date
                    except ObjectDoesNotExist:
                        s_dict['completed'] = False
                return Response(s_dict, status=status.HTTP_200_OK)

            # CitizenActTravel type
            if type == 'travel':
                try:
                    serializer = CitizenActTravelSerializer(self.get_object().citizenacttravel)
                except CitizenActTravel.DoesNotExist:
                    return Response({'Error': 'The requested CitizenAct is not of the specified type'},
                                    status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'Error': 'Specified type does not exist'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        else:
            return Response(CitizenActSerializer(self.get_object()).data, status=status.HTTP_200_OK)

    def create(self, request):
        try:
            type = request.query_params['type']
        except KeyError:
            return Response({'Error': 'type specification missing'}, status=status.HTTP_428_PRECONDITION_REQUIRED)
        if type == 'qrcode':
            serializer = CitizenActQRCodeSerializer(data=request.data)
        elif type == 'travel':
            serializer = CitizenActTravelSerializer(data=request.data)
        else:
            return Response({'Error': 'Specified type does not exist'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

    def update(self, request, pk=None):
        try:
            type = request.query_params['type']
            try:
                if type == 'qrcode':
                    serializer = CitizenActQRCodeSerializer(self.get_object().citizenactqrcode, data=request.data)
                elif type == 'travel':
                    serializer = CitizenActTravelSerializer(self.get_object().citizenacttravel, data=request.data)
                else:
                    return Response({'Error': 'Specified type does not exist'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            except ObjectDoesNotExist:
                return Response({'Error': 'The CitizenAct is not of the specified type'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            serializer = CitizenActSerializer(self.get_object(), data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

    @detail_route(methods=['get'])
    def event(self, request, *args, **kwargs):
        try:
            event = self.get_object().citizenactqrcode.treasure_hunt.event
            serializer = EventSerializer(event)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
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

    # we deduce the corresponding amount of money from the user
    if profile.current_points >= offer.points:
        profile.current_points -= offer.points
        profile.save()

        # we save it in database
        user_partner_offer = UserPartnerOffer(profile=profile, partner_offer=offer, date=datetime.now())
        user_partner_offer.save()


        # we call the google service to send a notification
        # we first retireve the token given in paramaters
        token_mobile = request.query_params.get('token_mobile')

        headers = {"Authorization": "key=AIzaSyDTDxOSbGp9vNX7dWc5PLmzKz55S_0Z_M8", 'Content-type': 'application/json',
                   'Accept': 'text/plain'}
        data = {
            "data": {
                "score": u"{}".format(offer.points),
                "time": u"{}".format(datetime.now()),
                "id_offer": u"{}".format(offerId),
                "new_score": u"{}".format(profile.current_points),
                "title": u"{}".format(offer.title)
            },
            "to": token_mobile
        }

        try:
            request_google_gcm = requests.post('https://gcm-http.googleapis.com/gcm/send', data=json.dumps(data),
                                               headers=headers)
        except:
            return Response(status=status.HTTP_503_SERVICE_UNAVAILABLE)

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
        act = CitizenAct.objects.get(id=actId)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # we check if we are talking about an citizenQRCode or a regularQrCode
    try:
        CitizenAct.citizenactqrcode
        qrCode = True
    except:
        qrCode = False

    # we check if the user has already scanned this QR Code
    if qrCode and UserCitizenAct.objects.filter(profile=profile, citizen_act=act).count() != 0:
        return Response(status=status.HTTP_403_FORBIDDEN)

    user_citizen_act = UserCitizenAct(profile=profile, citizen_act=act, date=datetime.now())
    user_citizen_act.save()

    # we add the point to the user acount
    profile.global_points += act.points
    profile.current_points += act.points

    profile.save()

    return Response(ProfileSerializer(profile).data)
