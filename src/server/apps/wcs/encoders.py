from apps.ows.encoders import OWSEncoder
from apps.ows.utils import OWS_MAKER
from apps.ows.ows import OWSMeta
from apps.ows.exception import MissingParameterValue
from utils import WCS_MAKER, wcs_set, WCSEO_MAKER
from apps.wcs.wcs import WCS
from apps.gml.utils import GML_MAKER
from apps.geo.models import GeoArrayTimeLine
from collections import defaultdict


class WCSEncoder(OWSEncoder):
    def __init__(self, params):
        self.params = params

    def get_schema_locations(self):
        return wcs_set.schema_locations


class GetCapabilitiesEncoder(WCSEncoder):
    def encode(self, request, url="http://127.0.0.1:8000/ows?"):
        nodes = []
        ows = OWSMeta()

        nodes.append(ows.root_identification)
        nodes.append(ows.root_provider)
        nodes.append(ows.root_operations)

        wcs = WCS(formats=ows.formats)

        root_service_metadata = WCS_MAKER("ServiceMetadata")
        formats = [WCS_MAKER("formatSupported", f.get('name')) for f in ows.formats]
        root_service_metadata.extend(formats)

        nodes.append(root_service_metadata)

        times = GeoArrayTimeLine.objects.all().order_by('id')

        output_dict = defaultdict(list)
        for time in times:
            output_dict[time.array.pk].append(time)


        wcseo_times = [
            WCSEO_MAKER(
                "DatasetSeriesSummary",
                GML_MAKER(
                    "TimePeriod",
                    GML_MAKER(
                        "beginPosition",
                        output_dict[geo_array][0].date.strftime("%Y-%m-%dT%H:%M:%S")
                    ),
                    GML_MAKER(
                        "endPosition",
                        output_dict[geo_array][-1].date.strftime("%Y-%m-%dT%H:%M:%S")
                    ),
                    id=output_dict[geo_array][0].array.name
                )
            )
            for geo_array in output_dict
        ]

        extension = WCS_MAKER("Extension")
        extension.extend(wcseo_times)

        contents = wcs.root_coverages_summary
        contents.append(extension)

        nodes.append(contents)

        # nodes.append(extension)

        root = WCS_MAKER("Capabilities", *nodes, version="2.0.1")

        return root


class DescribeCoverageEncoder(WCSEncoder):
    def __init__(self, params):
        super(DescribeCoverageEncoder, self).__init__(params)
        if not params.get('coverageid'):
            raise MissingParameterValue("Missing parameter coverageID", locator="coverageID")

    def encode(self, request, url="http://127.0.0.1:8000/ows?"):
        nodes = []

        root = WCS_MAKER("CoverageDescriptions", *nodes, version="2.0.1")

        return root