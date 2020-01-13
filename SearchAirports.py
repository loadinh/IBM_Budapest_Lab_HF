"""
This module contains the database client and the functions that are
necessary for the search for airports.
"""
from cloudant.client import Cloudant
from cloudant.database import CloudantDatabase
from math import sin, cos, asin, radians, sqrt, pi, isclose

EARTH_RADIUS = 6371.0088  # average Earth radius in km


class AirportDbClient:
    """
    Class to connect to the world readable Cloudant database. The class is a
    context manager, and must be used inside a with() statement.

    List of airports can be pulled from the database with a rectangle search query.

    Attributes:
        url (str): The url of the Cloudant account.
        db_name (str): Name of the Cloudant database.
        design_doc (str): Name of the design document.
        search_index (str): The search index used.
        client (Cloudant): Cloudant client instance.
        db (CloudantDatabase): Cloudant database instance.
    """

    def __init__(self, url, db_name, design_doc, search_index):
        self.url = url
        self.db_name = db_name
        self.design_doc = design_doc
        self.search_index = search_index

    def __enter__(self):
        """
        Runs when the control flow enters the with() statement.
        Creates the Cloudant client instant and the Cloudant database instant.

        To connect to the world readable database, I had to use the 'admin_party' flag.
        """
        self.client = Cloudant(" ", " ", admin_party=True,
                               url=self.url,
                               connect=True)

        self.db = CloudantDatabase(self.client, self.db_name)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Runs when the control flow leaves the with() statement.
        """
        self.client.disconnect()

    @staticmethod
    def _format_query(rect):
        """
        Formats the query in the format of 'lat:[X TO Y] AND lon:[V TO Z]'.
        Creates one or two queries, depending on its input.

        Args:
            rect (list): List of 4 (lat1, lat2, lon1, lon2) floats or
                    list of 6 (lat1, lat2, lon1, lon2, lon3, lon4) floats.

        Returns:
            list: List of one query string, or two query strings.
        """

        if len(rect) == 4:
            query = f"lat:[{rect[0]} TO {rect[1]}] AND lon:[{rect[2]} TO {rect[3]}]"
            return [query]

        qr1 = f"lat:[{rect[0]} TO {rect[1]}] AND lon:[{rect[2]} TO {rect[3]}]"
        qr2 = f"lat:[{rect[0]} TO {rect[1]}] AND lon:[{rect[4]} TO {rect[5]}]"

        return [qr1, qr2]

    def get_search_results(self, rectangles):
        """
        Getting all of the search results from the database based on the queries submitted.

        Args:
            rectangles (list): Rectangle data for the query.
                Or data for two rectangles if 2 query is present.

        Returns:
            list: The list of airports from the database.

        Raises:
            AirportDbException: Every problem with the database and its connection (e.g.
                no internet, or wrong url and name etc.)
                No errors occur when the Cloudant client and database instance are created,
                therefore errors are only raised here, when the search method is called,
                because this is where the Cloudant database is actively used.
        """

        queries = self._format_query(rectangles)
        total_number = 0
        results = []

        try:
            for qr in queries:  # 1 or 2 queries

                # The max limit of results pulled at once for a request is 200.
                # Hence, when there are more than 200 results, multiple requests
                # must be sent.

                q_result = self.db.get_search_result(self.design_doc,
                                                     self.search_index,
                                                     query=qr, limit=200)

                # NOTE: when 0 airports match the query, q_result will
                # look like {"total_rows":0,"bookmark":"g2o","rows":[]}

                # NOTE: the 'total_rows' field contains the total number of results,
                # not the number of results in the current query result.

                total_number = total_number + q_result['total_rows']
                results.extend([r['fields'] for r in q_result['rows']])

                while len(results) < total_number:  # Paging through all the results

                    # To get to the next page of results, the bookmark
                    # field of the previous request is used.
                    bookmark = q_result['bookmark']

                    q_result = self.db.get_search_result(self.design_doc,
                                                         self.search_index,
                                                         query=qr, limit=200,
                                                         bookmark=bookmark)

                    results.extend([r['fields'] for r in q_result['rows']])

        except Exception as ex:  # Any problem when trying to connect to and use the database
            raise AirportDbException(ex)

        return results


class AirportDbException(Exception):
    """
    Exception class that wraps the database connection errors.

    Attributes:
        ex (Exception): The caught exception.
    """
    def __init__(self, ex):
        self.exception = ex

    def print_exception_msg(self):
        # print(type(self.exception))
        print(self.exception)


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
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat1 - lat2
    dlon = lon1 - lon2

    h = sin(dlat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(dlon * 0.5) ** 2

    return EARTH_RADIUS * 2 * asin(sqrt(h))


def enclosing_rectangle(radius, origin_lat, origin_lon):
    """
    Calculates the enclosing rectangle of a circle on the surface of Earth,
    keeping in mind all of the edge cases that are due to the format of the
    search query we will use afterwards.

    For further explanations on the whole idea and the edge-cases,
    see in the README file!

    Args:
        radius (float): Input radius.
        origin_lat (float): Input latitude.
        origin_lon (float): Input longitude.

    Returns:
        list: List of 4 values, the two latitudes and two longitudes of the rectangle.
        Or list of 6 values, two rectangles with the same two latitudes and 2-2 longitudes.
    """
    circum_earth = 2 * pi * EARTH_RADIUS  # The circumference of Earth

    # 1st edge-case
    if radius >= circum_earth * 0.5:
        return [-90.0, 90.0, -180.0, 180.0]
    #

    # Traveling 'dlat' amount of latitude would mean traveling
    # a distance equal to the radius.
    dlat = (radius / circum_earth) * 360

    lat_S = origin_lat - dlat  # south
    lat_N = origin_lat + dlat  # north

    # 2nd edge-case
    # if lat_S or lat_N 'overflows' to the other side of the globe
    # i.e. south or north pole was reached
    pole_reached = False
    if lat_S < -90.0 or isclose(lat_S, -90.0):
        pole_reached = True
        lat_S = -90.0

    if lat_N > 90.0 or isclose(lat_N, 90.0):
        pole_reached = True
        lat_N = 90.0

    if pole_reached:
        return [lat_S, lat_N, -180.0, 180.0]
    #

    # Now onto the longitude part!
    circum_small = 2 * pi * cos(radians(origin_lat)) * EARTH_RADIUS

    # 3rd edge-case
    if radius >= circum_small / 2:
        return [lat_S, lat_N, -180.0, 180.0]
    #

    # Traveling 'dlon' amount of longitude would mean traveling
    # a distance equal to the radius.
    dlon = (radius / circum_small) * 360

    lon_W = origin_lon - dlon  # west
    lon_E = origin_lon + dlon  # east

    # 4th edge-case
    # Two rectangles are needed when lon_W < -180.0 or lon_E > 180.0
    # NOTE: only one of them can be true, because we already checked
    # for (radius >= circum_small / 2)
    if lon_W < -180.0:
        lon_W = 360.0 + lon_W
        return [lat_S, lat_N, lon_W, 180.0, -180.0, lon_E]

    if lon_E > 180.0:
        lon_E = lon_E - 360.0
        return [lat_S, lat_N, lon_W, 180.0, -180.0, lon_E]
    #

    # Finally, the normal case
    return [lat_S, lat_N, lon_W, lon_E]


def filter_and_sort(search_results, radius, origin_lat, origin_lon):
    """
    For each airport in the list of search results, the function calculates
    the distance from the origin point, then filters out the airports that
    are farther than the given radius (because instead of a circle, a rectangle
    was used in the query). Lastly, the remaining airports are sorted by
    the distance from the origin point (closest first).

    Args:
        search_results (list of dict): The airports from the search query result.
        radius (float): Input radius.
        origin_lat (float): Input latitude.
        origin_lon (float): Input  longitude.

    Returns:
        list: The list of the sorted (and filtered) airports.
    """
    airport_list = []

    for airport in search_results:
        distance = calculate_distance(origin_lat,
                                      origin_lon,
                                      airport['lat'],
                                      airport['lon'])

        if distance <= radius:
            airport['distance'] = distance
            airport_list.append(airport)

    airport_list.sort(key=lambda x: x['distance'])  # works fine even if list is empty

    return airport_list
