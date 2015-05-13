from django.contrib import admin
from models import GeoArray, GeoArrayTimeLine, GeoArrayAttribute, GeoArrayTimeUnit, GeoArrayDataFile

admin.site.register(GeoArray)
admin.site.register(GeoArrayAttribute)
admin.site.register(GeoArrayTimeLine)
admin.site.register(GeoArrayTimeUnit)
admin.site.register(GeoArrayDataFile)
