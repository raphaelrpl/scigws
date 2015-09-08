from collections import defaultdict
from apps.swe.swe import SWEMeta
from apps.ows.base import XMLEncoder
from apps.wcs.base import ImageEncoder
from utils import WCS_MAKER, WCSEO_MAKER
from apps.ows.ows import OWSMeta
from apps.wcs.wcs import WCS
from apps.gml.utils import GML_MAKER, GMLCOV_MAKER, namespace_gml
from apps.geo.models import GeoArrayTimeLine, GeoArray
from apps.ows.base import Operation

from scidbpy import connect
import numpy as np


class WCSOperation(Operation):
    """

    _scidb: It's instance of SciDBShimInterface
    :params: It is OWSDict that contains request params

    """
    _scidb = None
    params = None

    def __init__(self, params, encoder_type):
        super(WCSOperation, self).__init__(encoder_type)
        self.params = params
        self._scidb = connect()


class GetCapabilities(WCSOperation):
    _operation_name = "getcapabilities"

    def __init__(self, params, encoding="utf-8"):
        super(GetCapabilities, self).__init__(params, XMLEncoder(encoding=encoding))

    def process(self, request):
        nodes = []

        ows = OWSMeta(url=request.build_absolute_uri().split('?')[0] + "?")

        nodes.append(ows.root_identification)
        nodes.append(ows.root_provider)
        nodes.append(ows.root_operations)

        root_service_metadata = WCS_MAKER("ServiceMetadata")

        # Supported formats
        formats = [WCS_MAKER("formatSupported", f.content_type) for f in type.__subclasses__(ImageEncoder)]
        formats.append(WCS_MAKER('formatSupported', 'application/xml'))
        root_service_metadata.extend(formats)

        nodes.append(root_service_metadata)

        # Get Coverage Summary
        root_coverages_summary = WCS_MAKER("Contents")
        root_coverages_summary.extend([
            WCS_MAKER(
                "CoverageSummary",
                WCS_MAKER(
                    "CoverageId",
                    coverage.name
                ),
                WCS_MAKER(
                    "CoverageSubtype",
                    "GridCoverage"
                )
            )
            for coverage in GeoArray.objects.all()
        ])

        # Get Times
        arrays_time = GeoArrayTimeLine.objects.all().order_by('id')

        times = defaultdict(list)
        for time in arrays_time:
            times[time.array.name].append(time)

        wcseo_times = [
            WCSEO_MAKER(
                "DatasetSeriesSummary",
                WCSEO_MAKER("DatasetSeriesId", geo_array),
                GML_MAKER(
                    "TimePeriod",
                    GML_MAKER(
                        "beginPosition",
                        times[geo_array][0].date.strftime("%Y-%m-%dT%H:%M:%S")
                    ),
                    GML_MAKER(
                        "endPosition",
                        times[geo_array][-1].date.strftime("%Y-%m-%dT%H:%M:%S")
                    ),
                    GML_MAKER("timeInterval", str(times[geo_array][0].array.t_resolution)),
                    **{namespace_gml('id'): geo_array}
                )
            )
            for geo_array in times
        ]

        extension = WCS_MAKER("Extension")
        extension.extend(wcseo_times)

        contents = root_coverages_summary
        contents.append(extension)

        nodes.append(contents)
        root = WCS_MAKER("Capabilities", version="2.0.1")
        root.extend(nodes)

        self._encoder.set_root(root)


class DescribeCoverage(WCSOperation):
    """
    DescribeCoverage operation: It has XMLEncoder by default
    """

    _operation_name = "describecoverage"

    def __init__(self, params, encoding="utf-8"):
        super(DescribeCoverage, self).__init__(params, XMLEncoder(encoding=encoding))

    def process(self, request):
        wcs = WCS()
        wcs.describe_coverage(self.params)

        coverages = []

        for coverage in wcs.geo_arrays:
            # geo = wcs.get_geo_array(coverage)
            time_periods = coverage.get_min_max_time()
            coverage_description = WCS_MAKER(
                "CoverageDescription",
                GML_MAKER(
                    "boundedBy",
                    GML_MAKER(
                        "Envelope",
                        GML_MAKER(
                            "lowerCorner",
                            coverage.get_lower()
                        ),
                        GML_MAKER(
                            "upperCorner",
                            coverage.get_upper()
                        ),
                        axisLabels=coverage.get_axis_labels(),
                        srsDimension="3",
                        srsName="http://www.opengis.net/def/crs/EPSG/0/4326"
                    )
                ),
                WCS_MAKER("CoverageId", coverage.name),
                GML_MAKER(
                    "domainSet",
                    GML_MAKER(
                        "Grid",
                        GML_MAKER(
                            "limits",
                            GML_MAKER(
                                "GridEnvelope",
                                GML_MAKER("low", coverage.get_lower()),
                                GML_MAKER("high", coverage.get_upper())
                            )
                        ),
                        dimension="3"
                    )
                ),
                GML_MAKER(
                    "TimePeriod",
                    GML_MAKER("beginPosition", time_periods[0]),
                    GML_MAKER("endPosition", time_periods[-1]),
                    GML_MAKER("timeInterval", str(coverage.t_resolution))
                ),
                GMLCOV_MAKER(
                    "rangeType",
                    SWEMeta.get_data_record(coverage)
                ),
                id=coverage.name
            )
            coverages.append(coverage_description)
        root = WCS_MAKER("CoverageDescriptions", version="2.0.1")
        root.extend(coverages)
        self._encoder.set_root(root)


class GetCoverage(WCSOperation):
    _operation_name = "getcoverage"

    def __init__(self, params):
        # Check if it has image response or xml response
        default_format = "application/xml"
        fmt = params.get('format', ' ')[0].lower()
        if fmt == default_format:
            encoder = XMLEncoder()
        else:
            for klass in type.__subclasses__(ImageEncoder):
                if klass.content_type == fmt:
                    encoder = klass()
                    break
            else:
                raise TypeError("Invalid wcs format input")

        super(GetCoverage, self).__init__(params, encoder)

    def process(self, request):
        wcs = WCS()
        wcs.get_coverage(**self.params)
        if isinstance(self._encoder, ImageEncoder):
            # It should be an image

            # Get X and Y
            col_id = wcs.col_id
            row_id = wcs.row_id
            x = col_id[1] - col_id[0] + 1
            y = row_id[1] - row_id[0] + 1

            # Calculate the factor if there are 3d dimension. Multiply Y axis by default
            fact = wcs.time_id[-1] - wcs.time_id[0] + 1

            # Let parallel reshape save
            self._encoder.process_data(wcs, x, y, fact)

            # Bands size
            # band_size = len(wcs.bands)

            # Generate image and save temporarily
            # self._encoder.generate_image_on_disk(wcs.geo_array, enc, x=x, y=y, band_size=band_size)
        else:
            nodes = []
            col_id = wcs.col_id
            row_id = wcs.row_id
            time_id = wcs.time_id
            geo = wcs.get_geo_array()
            bounded_by = GML_MAKER(
                "boundedBy",
                GML_MAKER(
                    "Envelope",
                    GML_MAKER(
                        "lowerCorner",
                        geo.get_lower(xmin=col_id[0], ymin=row_id[0], tmin=time_id[0])
                    ),
                    GML_MAKER(
                        "upperCorner",
                        geo.get_upper(xmax=col_id[1], ymax=row_id[1], tmax=time_id[1])
                    ),
                    axisLabels=geo.get_axis_labels(),
                    srsDimension="3",
                    srsName="http://www.opengis.net/def/crs/EPSG/0/4326"
                )
            )

            nodes.append(bounded_by)

            domain_set = GML_MAKER(
                "domainSet",
                GML_MAKER(
                    "Grid",
                    GML_MAKER(
                        "limits",
                        GML_MAKER(
                            "GridEnvelope",
                            GML_MAKER(
                                "low",
                                geo.get_lower()
                            ),
                            GML_MAKER(
                                "high",
                                geo.get_upper()
                            ),
                        )
                    ),
                    dimension="3"
                )
            )

            nodes.append(domain_set)

            # SciDB data
            time_series = []

            # a = [" ".join(x.tolist()) for x in np.hstack((wcs.data.T.real, wcs.data.T.imag)).flat]

            # Stack array splitting by z dimension and then, uses flat to iterate over all
            for i in np.hstack(wcs.data.T.real).T.flat:
                time_series.append(" ".join(map(str, i.tolist())))

            range_set = GML_MAKER(
                "rangeSet",
                GML_MAKER(
                    "DataBlock",
                    GML_MAKER(
                        "tupleList",
                        ",".join(time_series),
                        cs=" ",
                        ts=","
                    )
                )
            )

            nodes.append(range_set)

            range_type = GMLCOV_MAKER("rangeType", SWEMeta.get_data_record(geo))

            nodes.append(range_type)

            root = GMLCOV_MAKER("GridCoverage", *nodes, version="2.0.1")
            self._encoder.set_root(root)