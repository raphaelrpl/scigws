from exception import SWEException
from utils import SWE_MAKER


class SWEMeta(object):
    def __init__(self, identifier, meta):
        if not meta:
            raise SWEException("Metadata for \"identifier\" is none. <{0}>".format(meta))
        self.identifier = identifier
        self.meta = meta

    @classmethod
    def get_data_record(cls, geo_array):
        """
        Get fields based SWE Specification
        :return: root node with all children nodes
        """
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
            for attr in geo_array.geoarrayattribute_set.all().reverse()
        ]
        swe_datarecord.extend(swe_fields)
        return swe_datarecord