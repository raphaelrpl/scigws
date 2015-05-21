#
# Copyright (C) 2014-2015 National Institute For Space Research (INPE) - Brazil.
#
# This file is part of the SciWMS.
#
# SciWMS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# SciWMS is distributed  "AS-IS" in the hope that it will be useful,
# but WITHOUT ANY WARRANTY OF ANY KIND; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with SciWMS. See COPYING. If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
#

from django.http.response import HttpResponse
from django.views.generic.base import View
from wms import WMS


class WMSView(View):
    def get(self, request):
        service = request.GET.get('SERVICE', '')
        req = request.GET.get('REQUEST', '')
        x = WMS()
        if service.lower() == 'wms':
            if req.lower() == 'getcapabilities':
                return HttpResponse(x.capabilities(), content_type='application/xml')
            elif req.lower() == 'getmap':
                x = WMS()
                return HttpResponse(x.map(), content_type='application/xml')
            elif req.lower() == 'getfeatureinfo':
                x = WMS()
                return HttpResponse(x.feature_info(), content_type='application/xml')
            else:
                x = WMS()
                return HttpResponse(x.feature_info(), content_type='application/xml')
        return HttpResponse()
