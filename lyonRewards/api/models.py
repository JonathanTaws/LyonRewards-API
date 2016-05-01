# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from rest_framework.authtoken.models import Token

# TODO Citizen act transport
from lyonRewards import settings


class Tag(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return "{0}".format(self.title)

    def __unicode__(self):
        return u"{0}".format(self.title)

class Partner(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.TextField()
    image_url = models.CharField(max_length=400)


    def __str__(self):
        return "{0}".format(self.name)

    def __unicode__(self):
        return u"{0}".format(self.name)

class Event(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    publish_date = models.DateTimeField(default=now, verbose_name="Date of publication")
    start_date = models.DateTimeField(default=now, verbose_name="Start of the event")
    end_date = models.DateTimeField(default=now, verbose_name="End of the event")
    latitude = models.FloatField()
    longitude = models.FloatField()
    image_url = models.CharField(max_length=400)
    address = models.CharField(max_length=400)
    tags = models.ManyToManyField('Tag')
    partner = models.ForeignKey(Partner, blank=True, null=True)

    def progress(self, profile):
        qrCodes = CitizenActQRCode.objects.filter(treasure_hunt__event = self).count()
        if qrCodes == 0:
            return 0
        return (
            CitizenActQRCode.objects.
            filter(treasure_hunt__event = self).
            filter(usercitizenact__profile = profile).
            count()/float(qrCodes))



class Profile(models.Model):
    user = models.OneToOneField(User)  # One-to-One liaison, no inheritance
    global_points = models.PositiveIntegerField()
    current_points = models.PositiveIntegerField()
    group = models.ForeignKey(Group, blank=True, null=True)

    def __str__(self):
        return "Profil de {0}".format(self.user.username)

    def __unicode__(self):
        return u"Profil de {0}".format(self.user.username)

    @property
    def last_tfh_points(self):
        date_from = datetime.now() - timedelta(days=1)
        sum = (
            CitizenAct.objects
            .filter(usercitizenact__profile=self, usercitizenact__date__gte=date_from)
            .aggregate(last_tfh_points=models.Sum('points')))
        return sum.get('last_tfh_points') if sum.get('last_tfh_points') else 0

    @property
    def current_month_points(self):
        sum = (
            CitizenAct.objects
                .filter(usercitizenact__profile=self, usercitizenact__date__month = datetime.now().month)
                .aggregate(current_month_points=models.Sum('points')))
        return sum.get('current_month_points') if sum.get('current_month_points') else 0

    def month_points(self, month):
        sum = (
            CitizenAct.objects
                .filter(usercitizenact__profile=self, usercitizenact__date__month = month)
                .aggregate(month_points=models.Sum('points')))
        return sum.get('month_points') if sum.get('month_points') else 0

@receiver(post_delete, sender=Profile)
def delete_user(sender, instance, **kwargs):
    #we destroy the user before deleting the profile
    instance.user.delete()

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class CitizenAct(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    points = models.PositiveIntegerField()

    def __str__(self):
        return "{0}".format(self.title)

    def __unicode__(self):
        return u"{0}".format(self.title)


class TreasureHunt(models.Model):
    event = models.OneToOneField(Event)

    def __str__(self):
        return "TreasureHunt {0}".format(self.id)

    def __unicode__(self):
        return u"TreasureHunt {0}".format(self.id)


class CitizenActQRCode(CitizenAct):
    treasure_hunt = models.ForeignKey(TreasureHunt, blank=True)

    def __str__(self):
        return "CitizenActQRCode {0}".format(self.title)

    def __unicode__(self):
        return u"CitizenActQRCode {0}".format(self.title)


class UserCitizenAct(models.Model):
    date = models.DateTimeField(default=now, verbose_name="Citizen act date")
    profile = models.ForeignKey(Profile)
    citizen_act = models.ForeignKey(CitizenAct)

    def __str__(self):
        return "UserCitizenAct {0}".format(self.date)

    def __unicode__(self):
        return u"UserCitizenAct {0}".format(self.date)





class PartnerOffer(models.Model):
    description = models.TextField()
    title = models.CharField(max_length=100)
    points = models.PositiveIntegerField()
    partner = models.ForeignKey(Partner)

    def __str__(self):
        return "{0}".format(self.description)

    def __unicode__(self):
        return u"{0}".format(self.description)


class UserPartnerOffer(models.Model):
    date = models.DateTimeField(default=now, verbose_name="Date of transaction")
    profile = models.ForeignKey(Profile)
    partner_offer = models.ForeignKey(PartnerOffer)

    def __str__(self):
        return "UserPartnerOffer {0}".format(self.date)

    def __unicode__(self):
        return u"UserPartnerOffer {0}".format(self.date)


