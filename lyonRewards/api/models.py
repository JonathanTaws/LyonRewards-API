import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


# TODO Citizen act transport
class Tag(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return "{0}".format(self.title)

    def __unicode__(self):
        return "{0}".format(self.title)


class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=100)
    publish_date = models.DateTimeField(default=now, verbose_name="Date of publication")
    start_date = models.DateTimeField(default=now, verbose_name="Start of the event")
    end_date = models.DateTimeField(default=now, verbose_name="End of the event")
    latitude = models.FloatField()
    longitude = models.FloatField()
    image_url = models.URLField()
    tags = models.ManyToManyField('Tag')


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One-to-One liaison, no inheritance
    global_points = models.PositiveIntegerField()
    current_points = models.PositiveIntegerField()

    def __str__(self):
        return "Profil de {0}".format(self.user.username)

    def __unicode__(self):
        return "Profil de {0}".format(self.user.username)


class CitizenAct(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    points = models.PositiveIntegerField()

    def __str__(self):
        return "{0}".format(self.title)

    def __unicode__(self):
        return "{0}".format(self.title)


class TreasureHunt(models.Model):
    event = models.OneToOneField(Event)

    def __str__(self):
        return "TreasureHunt {0}".format(self.id)

    def __unicode__(self):
        return "TreasureHunt {0}".format(self.id)


class CitizenActQRCode(CitizenAct):
    treasure_hunt = models.ForeignKey(TreasureHunt, blank=True)

    def __str__(self):
        return "CitizenActQRCode {0}".format(self.title)

    def __unicode__(self):
        return "CitizenActQRCode {0}".format(self.title)


class UserCitizenAct(models.Model):
    date = models.DateTimeField(default=now, verbose_name="Citizen act date")
    profile = models.ForeignKey(Profile)
    citizen_act = models.ForeignKey(CitizenAct)

    def __str__(self):
        return "UserCitizenAct {0}".format(self.date)

    def __unicode__(self):
        return "UserCitizenAct {0}".format(self.date)


class Partner(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    adress = models.TextField()
    image_url = models.URLField()

    def __str__(self):
        return "{0}".format(self.name)

    def __unicode__(self):
        return "{0}".format(self.name)


class PartnerOffer(models.Model):
    description = models.TextField()
    title = models.CharField()
    points = models.PositiveIntegerField()
    partner = models.ForeignKey(Partner)

    def __str__(self):
        return "{0}".format(self.description)

    def __unicode__(self):
        return "{0}".format(self.description)


class UserPartnerOffer(models.Model):
    date = models.DateTimeField(default=now, verbose_name="Date of transaction")
    profile = models.ForeignKey(Profile)
    partner_offer = models.ForeignKey(PartnerOffer)

    def __str__(self):
        return "UserPartnerOffer {0}".format(self.date)

    def __unicode__(self):
        return "UserPartnerOffer {0}".format(self.date)


