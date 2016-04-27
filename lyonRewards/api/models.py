import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Profile(models.Model):
    user = models.OneToOneField(User)  # La liaison OneToOne vers le modèle User
    globalPoints = models.PositiveIntegerField()
    currentPoints = models.PositiveIntegerField()

    def __str__(self):
        return "Profil de {0}".format(self.user.username)

    def __unicode__(self):
        return "Profil de {0}".format(self.user.username)


class CitizenAct(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    points = currentPoints = models.PositiveIntegerField()

    def __str__(self):
        return "{0}".format(self.title)

    def __unicode__(self):
        return "{0}".format(self.title)

class UserCitizenAct(models.Model):
    date = models.DateTimeField(default=now, verbose_name="Citizen act date")
    models.ForeignKey(Profile)
    models.ForeignKey(CitizenAct)

    def __str__(self):
        return "{0}".format(self.date)

    def __unicode__(self):
        return "{0}".format(self.date)

