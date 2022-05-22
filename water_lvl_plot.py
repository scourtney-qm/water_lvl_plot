import requests
import datetime
import matplotlib.pyplot as plt

from ipywidgets import widgets
from IPython.display import display, clear_output

def all_stations():
    """Returns list of all stations in http://environment.data.gov.uk/flood-monitoring/id/stations in alphabetical order"""
    response = requests.get('http://environment.data.gov.uk/flood-monitoring/id/stations')
    f = {i["stationReference"]:i['label'] if i['label'][0] !=' ' else i['label'][1:] for i in response.json()['items']}
    return sorted([f[k]+' ({})'.format(k) for k in f])

def from_json_to_datetime(dt):
    """Takes the datetime string as formatted in th json, dt, and returns the corresponding to a datetime object"""
    date_list = dt.split('T')[0].split('-')
    time_list = dt.split('T')[1][:-1].split(':')

    date = datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2]))
    time = datetime.time(int(time_list[0]),int(time_list[1]),int(time_list[2]))

    return datetime.datetime.combine(date, time)


def from_datetime_to_json(dt):
    """Takes the datetime object, dt, and returns the corresponding datetime string as formatted in the json"""
    return str(dt).replace(' ', 'T')+'Z'


def plot_station(station):
    """Makes a 24 hour water level plot and table for the given station"""
    hr_diff = 24
    param = 'level'
    id_num = station.split('(')[1][:-1]

    diff = datetime.timedelta(hours=hr_diff)

    since_time = str(datetime.datetime.now() - diff).replace(' ', 'T')+'Z'

    station_response = requests.get(
        'http://environment.data.gov.uk/flood-monitoring/id/stations/{}/readings?since={}&parameter={}'.format(
            id_num, from_datetime_to_json(datetime.datetime.now()-diff), param))
    results = station_response.json()['items']
    
    values = [r['value'] for r in results]
    times = [(from_json_to_datetime(r['dateTime'])-datetime.datetime.now()).total_seconds()/3600 for r in results]

    values = [v for _, v in sorted(zip(times, values))]
    times = sorted(times)
    
    
    fig = plt.figure(figsize=(11,5))
    ax = fig.add_subplot(1, 1, 1)

    ax.set_title(station.split('(')[0][:-1] + 
                 ' (now=' + 
                 str(datetime.datetime.now().date()) + 
                 ' ' + 
                 str(datetime.datetime.now().hour).zfill(2) + 
                 ":" + 
                 str(datetime.datetime.now().minute).zfill(2) + ')')

    ax.plot(times, values)

    ax.set_xlabel('hours')
    ax.set_ylabel('Water Level / $m$')

    ax.set_xlim([-hr_diff,0])
    
    ax.set_xticks(list(range(0,-hr_diff-3,-3)))
    ax.set_xticklabels(['Now']+list(range(-3,-hr_diff-3,-3)))

    plt.show()
    
    table_values = [r['value'] for r in results]
    table_times = [str(from_json_to_datetime(r['dateTime'])) for r in results]

    table_values = [v for _, v in sorted(zip(table_times, table_values))]
    table_times = sorted(table_times)
    print(tabulate([[t,v] for t,v in zip(table_times,table_values)], headers=['Time', 'Water Level/m']))
    
    
    
def widget():
    """Creates a widget to switch between plots of stations. 
    A dropdown is used to switch stations and the searchbar can refine your options."""
    options = all_stations()

    def select_station(search):
        stW.options = [st for st in options if search.lower() in st.lower()]

    searchW = widgets.Text(value='',
                       placeholder='Type something',
                       description='Search:',
                       disabled=False)

    stW = widgets.Dropdown(options=options)

    j = widgets.interactive(plot_station, station=stW)
    i = widgets.interactive(select_station, search=searchW)

    display(i)
    display(j)
