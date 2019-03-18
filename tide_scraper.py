import httplib2
from bs4 import BeautifulSoup, SoupStrainer

http = httplib2.Http()
status, response = http.request('https://tidesandcurrents.noaa.gov/stations.html')


def get_regions():
    soup = BeautifulSoup(response, 'html.parser')
    regions = soup.findAll("span", attrs={'class': None})
    regions.remove(regions[len(regions) - 1])
    return regions


def get_stations():
    soup = BeautifulSoup(response, 'html.parser')
    stations = soup.findAll("div", attrs={'class': 'span4 station'})

    # For checking the values...
    # for station in stations:
    #      print(station.text)
    return stations
