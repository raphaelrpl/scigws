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
        return "<GeoArray %s>" % self.name

    def get_axis_labels(self):
        return "%s %s %s" % (self.x_dim_name, self.y_dim_name, self.t_dim_name)

    def get_x_dimension(self):
        return [self.x_min, self.x_max]

    def get_y_dimension(self):
        return [self.y_min, self.y_max]

    def get_lower(self):
        return "%s %s %s" % (self.x_min, self.y_min, self.geoarraytimeline_set.all().aggregate(
            time_point=models.Min('time_point')).get('time_point', 0))

    def get_upper(self):
        return "%s %s %s" % (self.x_max, self.y_max, self.geoarraytimeline_set.all().aggregate(
            time_point=models.Max('time_point')).get('time_point', 0))

    def get_min_max_time(self):
        return (self.geoarraytimeline_set.all().aggregate(models.Min('date')).get('date__min').strftime("%Y-%m-%dT%H:%M:%S"),
                self.geoarraytimeline_set.all().aggregate(models.Max('date')).get('date__max').strftime("%Y-%m-%dT%H:%M:%S"))


class GeoArrayAttribute(models.Model):
    array = models.ForeignKey(GeoArray)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    range_min = models.IntegerField()
    range_max = models.IntegerField()
    scale = models.FloatField()
    missing_value = models.IntegerField()

    def __str__(self):
        return "<GeoArrayAttribute %s>" % self.name

    def get_interval(self):
        return "%s %s" % (self.range_min, self.range_max)


class GeoArrayTimeLine(models.Model):
    array = models.ForeignKey(GeoArray)
    time_point = models.IntegerField()
    date = models.DateTimeField()

    def __str__(self):
        return "<GeoArrayTimeLine array=%s, time_point=%s>" % (self.array.name, self.time_point)


class GeoArrayDataFile(models.Model):
    array = models.ForeignKey(GeoArray)
    time_point = models.ForeignKey(GeoArrayTimeLine)
    data_file = models.CharField(max_length=250)
    start_load_time = models.DateTimeField()
    end_load_time = models.DateTimeField()


class GeoArrayTimeUnit(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return "<GeoArrayTimeUnit %s>" % self.name


