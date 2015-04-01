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

from django.conf.urls import patterns, url
from views import Capabilities


urlpatterns = patterns('',
   url(r'^$', Capabilities.as_view()),
)
