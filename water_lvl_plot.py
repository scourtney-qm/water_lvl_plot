import requests
import datetime
import matplotlib.pyplot as plt

from ipywidgets import widgets
from IPython.display import display, clear_output

def all_stations():
    response = requests.get('http://environment.data.gov.uk/flood-monitoring/id/stations')
    f = {i["stationReference"]:i['label'] if i['label'][0] !=' ' else i['label'][1:] for i in response.json()['items']}
    return sorted([f[k]+' ({})'.format(k) for k in f])

def from_json_to_datetime(dt):
    date_list = dt.split('T')[0].split('-')
    time_list = dt.split('T')[1][:-1].split(':')

    date = datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2]))
    time = datetime.time(int(time_list[0]),int(time_list[1]),int(time_list[2]))

    return datetime.datetime.combine(date, time)


def from_datetime_to_json(dt):
    return str(dt).replace(' ', 'T')+'Z'


def plot_station(station):
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
    
    
    fig = plt.figure(figsize=(10,6))
    ax = fig.add_subplot(1, 1, 1)

    ax.set_title(station.split('(')[0][:-1] + 
                 ' (now=' + 
                 str(datetime.datetime.now().date()) + 
                 ' ' + 
                 str(datetime.datetime.now().hour) + 
                 ":" + 
                 str(datetime.datetime.now().minute) + ')')

    ax.plot(times, values)

    ax.set_xlabel('hours')
    ax.set_ylabel('Water Level / $m$')

    ax.set_xlim([-hr_diff,0])
    
    ax.set_xticks(list(range(0,-hr_diff-3,-3)))
    ax.set_xticklabels(['Now']+list(range(-3,-hr_diff-3,-3)))

    plt.show()
    
    
    
def widget():
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
