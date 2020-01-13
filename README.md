# IBM_Budapest_Lab_HF
See [General coding task.pdf](General%20coding%20task.pdf) for a description of the task I received!
## Requirements
Created the application using Python 3.8.1. In order to run the application, the Cloudant Python library and all of its dependencies are needed. See [requirements.txt](requirements.txt)!

## Setup
Pip is recommended for installing the dependency libraries (use pip3 instead of pip if needed).
```
pip install -r requirements.txt
```
Or just install the Cloudant package, and pip will download all of the other dependencies as needed.
```
pip install cloudant
```
Note: if required, set up and use a separate virtual Python environment before installing packages with pip!

## Running the application
Run AirportApp.py! In command-line:
```
python AirportApp.py
```
Note: make sure to use the appropriate version of Python (as well as using the virtual environment mentioned above if needed).

## *Explaining the rectangle calculation used in the application
Let’s use a 2D analogy first! The user submits the origin coordinates (x,y), and a radius r. But instead of a circle, the format of the database query permits only a rectangle in the form of (x_min, x_max, y_min, y_max). Hence, if we want to get all points inside the circle, we have to calculate its enclosing rectangle first, which will be (x-r, x+r, y-r, y+r). The query will require these four coordinates!

Going back to the problem at hand: the Earth is a globe, and the coordinates are given in latitude and longitude (lat and lon). Instead of y-r and y+r, we will have lat-dlat (south), lat+dlat (north), and instead of x-r and x+r, we will have lon-dlon (west), and lon+dlon (east). 

To get dlat, we have to calculate how much “degrees” we have to go north or south to travel as much as the r radius (hint: traveling 360 degrees = the circumference of Earth). To get dlon, we have to calculate how much “degrees” we have to go west or east to travel as much as the r radius; traveling west or east a full 360 degrees would be usually a smaller distance than with dlat, because it depends on where we are: the Earth gets “narrower” on the x-axis as we get farther from the equator, i.e. the longitude circumference will be smaller. Let’s call it small circumference!

**1st edge-case:** the radius is so large that the circle encompasses the whole globe. We have to query the whole planet: -90, 90, -180, 180

**2nd edge-case:** when lat+dlat overflows the north pole (larger than 90), the area of the imaginary circle will be over the top part of the globe, which means the points there will have every possible longitude values for the query (-180 to 180). The same goes for when lat-dlat overflows the south pole (less than -90) Note, when lat is 90 or -90 the small circumference would be 0, and we would also need -180 to 180 longitude for the query. Note also, that the latitude values for the query will be adjusted to 90 or -90 as necessary, because latitude values must be between -90 and 90.

**3rd edge-case:** when 2*r is larger or equal to the small circumference, then again, we would need every longitude value (-180 to 180).

**4th edge-case:** a representative example would be when lon is 150 and dlon is 40. This would mean lon-dlon=110, lon+dlon=190, so we would need the values between 110 and 190. However, 190 longitude doesn’t exist, instead it is -170. Because the query doesn’t accept 110 to -170, we need two queries with 110 to 180, and then -180 to -170. That means two “rectangles” that share the same lwo latitude values, but different longitude values.
