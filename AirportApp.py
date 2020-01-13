"""
Module for the user interface of the application
(the main function and user inputs).
"""
from math import isclose
from SearchAirports import AirportDbClient, AirportDbException
from SearchAirports import enclosing_rectangle, filter_and_sort


def get_input():
    """
    Gets the input from the user in the form of: radius; latitude; longitude
    Checks the correctness of these inputs as well.

    Returns:
        list: Normally a list of three float values.
        list: Empty list if there was something wrong with the input.
        None: if the user typed 'quit' to exit application.
    """

    print("Enter input in the order of radius; latitude; longitude "
          "(e.g. 500; 20.5; -60), or type 'quit' to exit!")
    in_val = input('~ ')

    if in_val == 'quit':
        return None

    vals = in_val.split(';')

    if len(vals) != 3:
        print('Wrong number of parameters')
        return []

    try:
        vals = [float(v) for v in vals]
    except ValueError:
        print('Please use numbers only!')
        return []

    if vals[0] < 0 or isclose(vals[0], 0.0):
        print('Radius must be larger than zero')
        return []

    if vals[1] < -90.0 or vals[1] > 90.0:
        print('Latitude must be between -90 and 90')
        return []

    if vals[2] < -180.0 or vals[2] > 180.0:
        print('Longitude must be between -180 and 180')
        return []

    return vals


def main():
    """
    The application asks for user input (radius, lat, lon),
    calculates the appropriate query,
    searches the world readable Cloudant database,
    filters, sorts and prints the airport results.
    """
    url = "https://mikerhodes.cloudant.com"
    db_name = "airportdb"
    design_doc = "_design/view1"
    search_index = "geo"

    with AirportDbClient(url, db_name, design_doc, search_index) as db_client:
        print('\nGet the sorted list of airports from the database that are '
              'inside the radius (km) from a given point (latitude, longitude)! \n')
        while True:
            try:
                vals = get_input()
                if vals is None:
                    print('Exiting application!')
                    break
                if len(vals) == 0:
                    print('Please try again! \n')
                    continue

                radius = vals[0]
                lat = vals[1]
                lon = vals[2]

                rectangles_for_query = enclosing_rectangle(radius, lat, lon)

                search_results = db_client.get_search_results(rectangles_for_query)

                sorted_results = filter_and_sort(search_results, radius, lat, lon)

                print(f'\nThe airports less than {radius} km away from the specified '
                      f'point (lat: {lat}, lon: {lon})')

                print(f'Total number: {len(sorted_results)} (Note, that the database '
                      f'might contain duplicates!)')

                for res in sorted_results:
                    print(f"Name: {res['name']}, lat: {res['lat']}, lon: {res['lon']}, "
                          f"distance: {res['distance']}")
                print('')

            except AirportDbException as ex:
                print('\nAn error occurred, check database connection and parameters')
                ex.print_exception_msg()
                print('')


if __name__ == '__main__':
    main()
