import pyproj


def convert_latlon_proj(x, y, origin, destination):
    """
    :param x: Longitude coordinate
    :param y: Latitude coordinate
    :param origin: origin projection. i.e: '+init=EPSG:27700'
    :param destination: destination projection. i.e: '+init=EPSG:27700'
    :return: a tuple or lat long coordinate
    """
    proj_origin = pyproj.Proj(origin) if origin.startswith("+") else pyproj.Proj(proj="latlong", datum=origin)

    proj_dest = pyproj.Proj(destination) if destination.startswith('+') else pyproj.Proj(proj="latlong",
                                                                                         datum=destination)
    return pyproj.transform(proj_origin, proj_dest, x, y)