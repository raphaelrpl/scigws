from apps.ows.encoders import OWSEncoder
from apps.ows.ows import OWSMeta
from apps.ows.exception import MissingParameterValue
from utils import WCS_MAKER, wcs_set, WCSEO_MAKER, SWE_MAKER
from apps.wcs.wcs import WCS
from apps.gml.utils import GML_MAKER, GMLCOV_MAKER


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
        if not params.get('coverageid', []):
            raise MissingParameterValue("Missing parameter coverageID", locator="coverageID")
        super(DescribeCoverageEncoder, self).__init__(params)

    def encode(self, request):
        nodes = []

        wcs = WCS()
        wcs.describe_coverage(self.params)

        coverages = []

        for coverage in self.params.get('coverageid'):
            geo = wcs.get_geo_array(coverage)
            time_periods = geo.get_min_max_time()
            swe_datarecord = SWE_MAKER("DataRecord")
            swe_fields = [
                SWE_MAKER(
                    "field",
                    SWE_MAKER(
                        "Quantity",
                        SWE_MAKER("description", attr.description),
                        SWE_MAKER("uom", "NVDI"),
                        SWE_MAKER(
                            "constraint",
                            SWE_MAKER(
                                "AllowedValues",
                                SWE_MAKER("interval", attr.get_interval())
                            )
                        )
                    ),
                    name=attr.name
                )
                for attr in geo.geoarrayattribute_set.all()
            ]
            swe_datarecord.extend(swe_fields)
            coverage_description = WCS_MAKER(
                "CoverageDescription",
                GML_MAKER(
                    "boundedBy",
                    GML_MAKER(
                        "Envelope",
                        GML_MAKER(
                            "lowerCorner",
                            geo.get_lower()
                        ),
                        GML_MAKER(
                            "upperCorner",
                            geo.get_upper()
                        ),
                        axisLabels=geo.get_axis_labels(),
                        srsDimension="3",
                        srsName="http://www.opengis.net/def/crs/EPSG/0/4326"
                    )
                ),
                WCS_MAKER("CoverageId", geo.name),
                GML_MAKER(
                    "domainSet",
                    GML_MAKER(
                        "Grid",
                        GML_MAKER(
                            "limits",
                            GML_MAKER(
                                "GridEnvelope",
                                GML_MAKER("low", geo.get_lower()),
                                GML_MAKER("high", geo.get_upper())
                            )
                        ),
                        dimension="3"
                    )
                ),
                GML_MAKER(
                    "TimePeriod",
                    GML_MAKER("beginPosition", time_periods[0]),
                    GML_MAKER("endPosition", time_periods[-1])
                ),
                GMLCOV_MAKER(
                    "rangeType",
                    swe_datarecord
                ),
                id=coverage
            )
            coverages.append(coverage_description)

        root = WCS_MAKER("CoverageDescriptions", *nodes, version="2.0.1")
        root.extend(coverages)

        return root