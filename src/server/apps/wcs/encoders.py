from apps.ows.encoders import OWSEncoder
from apps.ows.ows import OWSMeta
from apps.ows.exception import MissingParameterValue
from apps.swe.swe import SWEMeta
from utils import WCS_MAKER, wcs_set, WCSEO_MAKER
from apps.wcs.wcs import WCS
from apps.gml.utils import GML_MAKER, GMLCOV_MAKER, namespace_gml


class WCSEncoder(OWSEncoder):
    request = ""

    def __init__(self, params):
        self.params = params

    def get_schema_locations(self):
        return wcs_set.schema_locations


class GetCapabilitiesEncoder(WCSEncoder):
    request = "getcapabilities"

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
                WCSEO_MAKER("DatasetSeriesId", geo_array.name),
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
                    GML_MAKER("timeInterval", str(geo_array.t_resolution)),
                    **{namespace_gml('id'): geo_array.name}
                )
            )
            for geo_array in wcs.times
        ]

        extension = WCS_MAKER("Extension")
        extension.extend(wcseo_times)

        contents = wcs.root_coverages_summary
        contents.append(extension)

        nodes.append(contents)

        root = WCS_MAKER("Capabilities", *nodes, version="2.0.1")

        return root


class DescribeCoverageEncoder(WCSEncoder):
    request = "describecoverage"

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
                    GML_MAKER("endPosition", time_periods[-1]),
                    GML_MAKER("timeInterval", str(geo.t_resolution))
                ),
                GMLCOV_MAKER(
                    "rangeType",
                    SWEMeta.get_data_record(geo)
                ),
                id=coverage
            )
            coverages.append(coverage_description)

        root = WCS_MAKER("CoverageDescriptions", *nodes, version="2.0.1")
        root.extend(coverages)

        return root


class GetCoverageEncoder(WCSEncoder):
    request = "getcoverage"

    def encode(self, request):
        nodes = []
        wcs = WCS()
        wcs.get_coverage(**self.params)
        col_id = wcs.col_id
        row_id = wcs.row_id
        time_id = wcs.time_id
        geo = wcs.get_geo_array()
        if self.params.get('format', ['gml'])[0].lower() == 'gml':
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
            time_series = ""
            for i in xrange(len(wcs.data['values'].values()[0])):
                for attr_dict in wcs.bands:
                    time_series += " %i" % wcs.data['values'][attr_dict][i]
                time_series = time_series.rstrip(" ") + ","
            time_series = time_series.rstrip(',')

            range_set = GML_MAKER(
                "rangeSet",
                GML_MAKER(
                    "DataBlock",
                    GML_MAKER(
                        "tupleList",
                        time_series,
                        cs=" ",
                        ts=","
                    )
                )
            )

            nodes.append(range_set)

            range_type = GMLCOV_MAKER("rangeType", SWEMeta.get_data_record(geo))

            nodes.append(range_type)

            root = GMLCOV_MAKER("GridCoverage", *nodes, version="2.0.1")
            return root

        self.content_type = "application/tiff"
        first, last = wcs.data['limits']

        import osgeo.gdal as gdal
        import numpy as np

        x = last[1] + 1
        y = last[0] + 1
        # 127.0.0.1:8000/ows/?service=WCS&request=GetCoverage&coverageid=mod09q1&subset=col_id(43200,43300)&subset=row_id(33600,33700)&subset=time_id(2000-02-18,2000-02-18)

        band_quantity = len(wcs.bands)

        driver = gdal.GetDriverByName('GTiff')
        file_name = "bands_mod09q1.tif"
        dataset = driver.Create(file_name, x, y, band_quantity, gdal.GDT_UInt16)
        # TODO: Should have another way
        cont = 0
        for band_name, band_values in wcs.data['values'].iteritems():
            narray = np.array(band_values)
            data = np.resize(narray, (y, x))
            dataset.GetRasterBand(cont+1).WriteArray(data)
            cont += 1
            del data

        return file_name