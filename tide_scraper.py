import httplib2
from bs4 import BeautifulSoup

http = httplib2.Http()
main = 'https://tidesandcurrents.noaa.gov/stations.html'
status, response = http.request(main)


def get_tide_data(value):
    times = list()
    tide_http = httplib2.Http()
    tide_data = value
    tide_status, tide_response = tide_http.request(tide_data)
    soup = BeautifulSoup(tide_response, 'html.parser')
    table = soup.find("table", attrs={'class': 'table-condensed'}).findAll("tr", attrs={'class': None})
    for tag in table:
        times.append(tag.text)  

    return times


def get_regions():
    soup = BeautifulSoup(response, 'html.parser')
    regions = soup.findAll("span", attrs={'class': None})
    regions.remove(regions[len(regions) - 1])
    return regions


def get_water_level():
    soup = BeautifulSoup(response, 'html.parser')
    areas = soup.findAll("div", attrs={'class': 'span4'})
    return areas


def get_stations_dict():
    soup = BeautifulSoup(response, 'html.parser')
    stations_dict = dict()
    regions = soup.findAll("div", attrs={'class': 'span12 areaheader'})
    keys = []

    for region in regions:
        keys.append(region.get('id'))
    for key in keys:
        stations_dict[key] = []
    for key in stations_dict:
        temp = list()
        for region in regions:
            if key in region.get('id'):
                sub_regions = region.findAll("div", attrs={'class': lambda l: l and l.startswith('span4')})
                for sub_region in sub_regions:
                    value = "%s" % sub_region.find('a').text
                    temp.append(value)
            stations_dict[key] = temp
    return stations_dict


# Might want to consider implementing this cleaner approach
def get_station_by_region(region):
    stations_dict = get_stations_dict()
    local_stations = stations_dict.get(region)
    print(local_stations)
    return local_stations


def get_lunar_data(station):
    tide_data = list()
    trimmed_data = list()
    tide_http = httplib2.Http()
    lunar_url = "https://tidesandcurrents.noaa.gov/harcon.html?id=%s" % (station,)
    lunar_status, lunar_response = tide_http.request(lunar_url)
    soup = BeautifulSoup(lunar_response, 'html.parser')
    lunar_table = soup.find("table", attrs={'class': 'table-striped'}).findAll("td", attrs={'class': None})

    for tag in lunar_table:
        lunar_data.append(tag.text)
    for i in range(3, len(lunar_data), 6):
        trimmed_data.append(lunar_data[i])

    return trimmed_data

# Get Hawaii Wave Heights
def get_wave_data():
    wave_data = list()
    trimmed_data = list()
    wave_http = httplib2.Http()
    # wave_url = "http://www.pacioos.hawaii.edu/"
    wave_url = "https://www.ndbc.noaa.gov/station_page.php?station=51211"
    wave_status, wave_response = wave_http.request(wave_url)
    soup = BeautifulSoup(wave_response, 'html.parser')
    
    # wave_table = soup.find("table", attrs={'class': 'dataTable'}).findAll("tr")[3].findAll("td")[6]
    # wave_data.append(wave_table.text)

    wave_table = soup.find("table", attrs={'id': 'contenttable'}).findAll('table')[1].findAll('tr')[1:]
    # for tag in wave_table:
    #     wave_data.append(tag.text)

    return wave_table
