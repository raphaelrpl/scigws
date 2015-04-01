from django.db import models
from django.db.models.manager import Manager


class ServiceIdentification(models.Model):
    title = models.CharField(max_length=100)
    abstract = models.CharField(max_length=200)
    service_type = models.CharField(max_length=20, default="OGC WCS")
    service_type_version = models.CharField(max_length=10, default="2.0.1")

    def __str__(self):
        return "{}, {}".format(self.title, self.abstract)


class Profile(models.Model):
    profiles = models.ForeignKey(ServiceIdentification)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ServiceProvider(models.Model):
    name = models.CharField(max_length=100)
    site = models.URLField()

    def __str__(self):
        return "{}, {}".format(self.name, self.site)


class ServiceContact(models.Model):
    individual_name = models.CharField(max_length=30)
    position_name = models.CharField(max_length=20)
    provider = models.ForeignKey(ServiceProvider)

    def __str__(self):
        return "{}, {}".format(self.individual_name, self.position_name)