from django.db import models


class GeoArray(models.Model):
    name = models.CharField(max_length=100)


class GeoArrayAttribute(models.Model):
    pass


class GeoArrayTimeLine(models.Model):
    pass


class GeoArrayDataFile(models.Model):
    pass


class GeoArrayTimeUnit(models.Model):
    pass


