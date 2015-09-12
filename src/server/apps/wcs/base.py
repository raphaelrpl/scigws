from xml.etree import ElementTree
from exception import WCSException
from json import loads
from apps.ows.base import ImageEncoder
from datetime import datetime

import abc
import h5py
import osgeo.gdal as gdal


class HDFEncoder(ImageEncoder):
    content_type = "image/hdf"

    def generate_image_on_disk(self, metadata, data, x, y, band_size):
        times = metadata.get_min_max_time()
        self.file_name = "{}_mod09q1_{}_{}.h5".format(datetime.now().strftime("%d-%M-%Y"),
                                                       times[0][:10],
                                                       times[1][:10])
        h5f = h5py.File(self.file_name, 'w')

        for i in xrange(band_size):
            band_name, band_values = data.get()
            h5f.create_dataset('dataset_{}'.format(band_name), data=band_values)
        h5f.close()


class TIFFEncoder(ImageEncoder):
    content_type = "image/tiff"

    def generate_image_on_disk(self, metadata, data, x, y, band_size):
        driver = gdal.GetDriverByName('GTiff')
        times = metadata.get_min_max_time()
        self.file_name = "{}_mod09q1_{}_{}.tif".format(datetime.now().strftime("%d-%M-%Y"),
                                                  times[0][:10],
                                                  times[1][:10])
        dataset = driver.Create(self.file_name, y, x, band_size, gdal.GDT_UInt16)
        # TODO: Should have another way
        for i in xrange(band_size):
            band_name, band_values = data.get()
            dataset.GetRasterBand(i + 1).WriteArray(band_values)


class WCSBase(object):
    __metaclass__ = abc.ABCMeta
    geo_arrays = None

    def __init__(self, db_path="config/db.config.json", meta="config/geo_arrays.json"):
        super(WCSBase, self).__init__()
        self.ns_dict = self._initialize_namespaces()
        self.dom = self._create_dom()
        self._register_namespaces()
        try:
            with open(meta) as data:
                self.geo_arrays = loads(data.read())
            with open(db_path) as data:
                self.config = loads(data.read())
        except StandardError as e:
            raise WCSException(e)

    @classmethod
    def _initialize_namespaces(cls):
        return {
            "gml": "http://www.opengis.net/gml/3.2",
            "gmlcov": "http://www.opengis.net/gmlcov/1.0",
            "swe": "http://www.opengis.net/swe/2.0",
            "ows": "http://www.opengis.net/ows/2.0",
            "wcs": "http://www.opengis.net/wcs/2.0"
        }

    @abc.abstractmethod
    def _create_dom(self):
        """
        :return:
        """""

    def _register_namespaces(self):
        for namespace in self.ns_dict:
            ElementTree.register_namespace(namespace, self.ns_dict[namespace])