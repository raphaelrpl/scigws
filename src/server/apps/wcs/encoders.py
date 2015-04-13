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
    def encode(self, request):
        nodes = []
        ows = OWSMeta(url=request.build_absolute_uri().split('?')[0] + "?")

        nodes.append(ows.root_identification)
        nodes.append(ows.root_provider)
        nodes.append(ows.root_operations)

        wcs = WCS(formats=ows.formats)

        root_service_metadata = WCS_MAKER("ServiceMetadata")
        formats = [WCS_MAKER("formatSupported", f.get('name')) for f in ows.formats]
        root_service_metadata.extend(formats)

        nodes.append(root_service_metadata)

        wcseo_times = [
            WCSEO_MAKER(
                "DatasetSeriesSummary",
                GML_MAKER(
                    "TimePeriod",
                    GML_MAKER(
                        "beginPosition",
                        wcs.times[geo_array][0].date.strftime("%Y-%m-%dT%H:%M:%S")
                    ),
                    GML_MAKER(
                        "endPosition",
                        wcs.times[geo_array][-1].date.strftime("%Y-%m-%dT%H:%M:%S")
                    ),
                    id=wcs.times[geo_array][0].array.name
                )
            )
            for geo_array in wcs.times
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

    def encode(self, request):
        nodes = []

        wcs = WCS()
        wcs.describe_coverage(self.params)

        coverages = []
        for coverage in self.params.get('coverageid'):
            coverage_description = WCS_MAKER(
                "CoverageDescription",
                WCS_MAKER(
                    "boundedBy",
                    WCS_MAKER(
                        "Envelope",
                        WCS_MAKER(
                            "lowerCorner",

                        ),
                        WCS_MAKER(
                            "upperCorner",

                        ),
                        axisLabels=""
                    )
                ),
                id=coverage
            )
            coverages.append(coverage_description)

        root = WCS_MAKER("CoverageDescriptions", *nodes, version="2.0.1")

        return root