"""

This module contains the database client and the functions that are
the backbone of the whole application.
"""


class AirportDbClient:
    """

    Class to connect to the world readable Cloudant database.
    """
    pass


def calculate_distance(lat1, lon1, lat2, lon2):
    """

    Function to calculate the distance between two points
    on the surface of Earth, based on the Haversine formula.

    Args:
        lat1 (float): Latitude of the first point.
        lon1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lon2 (float): Longitude of the second point.

    Returns:
       float: The Haversine distance of the two points in km.
    """
    pass


def enclosing_rectangle(radius, origin_lat, origin_lon):
    """

    Calculates the enclosing rectangle of a circle on the surface of Earth,
    keeping in mind all of the edge cases that are due to the format of the
    search query we will use afterwards.

    Args:
        radius (float): Input radius.
        origin_lat (float): Input latitude.
        origin_lon (float): Input  longitude.

    Returns:
        list: List of 4 values, the two latitudes and two longitudes of the rectangle.
        Or list of 6 values, two rectangles with the same two latitudes and 2-2 longitudes.
    """
    pass


def filter_and_sort(search_results, radius, origin_lat, origin_lon):
    """

    For each airport in the list of search results, the function calculates
    the distance from the origin point, then filters out the airports that
    are farther than the given radius. Lastly, the remaining airports are
    sorted by the distance from the origin point.

    Args:
        search_results (list of dict): The airports from the search query.
        radius (float): Input radius.
        origin_lat (float): Input latitude.
        origin_lon (float): Input  longitude.

    Returns:
        list: The list of the sorted (and filtered) airports.
    """

    pass

