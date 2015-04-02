from django.db import models


class GeoArray(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    detail = models.CharField(max_length=200)
    crs = models.CharField(max_length=200)
    x_dim_name = models.CharField(max_length=20)
    x_min = models.IntegerField()
    x_max = models.IntegerField()
    x_resolution = models.IntegerField()
    y_dim_name = models.CharField(max_length=20)
    y_min = models.IntegerField()
    y_max = models.IntegerField()
    y_resolution = models.IntegerField()
    t_dim_name = models.CharField(max_length=20)
    t_min = models.DateField()
    t_max = models.DateField()
    t_resolution = models.IntegerField()
    t_unit_id = models.SmallIntegerField()

    def __str__(self):
        return self.name


class GeoArrayAttribute(models.Model):
    array = models.ForeignKey(GeoArray)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    range_min = models.IntegerField()
    range_max = models.IntegerField()
    scale = models.FloatField()
    missing_value = models.IntegerField()

    def __str__(self):
        return self.name


class GeoArrayTimeLine(models.Model):
    array = models.ForeignKey(GeoArray)
    time_point = models.IntegerField()
    date = models.DateField()


class GeoArrayDataFile(models.Model):
    array = models.ForeignKey(GeoArray)
    time_point = models.ForeignKey(GeoArrayTimeLine)
    data_file = models.CharField(max_length=250)
    start_load_time = models.DateTimeField()
    end_load_time = models.DateTimeField()


class GeoArrayTimeUnit(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


