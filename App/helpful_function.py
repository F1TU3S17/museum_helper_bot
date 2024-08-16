from globals import events_data
import pyshorteners

def shorten_url(url):
    return pyshorteners.Shortener().clckru.short(url)

def counter_future_event():
    from handlers import event_isnt_going_now
    keys = list(events_data.keys())
    counter = 0
    for i in range(len(keys)):
        if event_isnt_going_now(i):
            counter += 1
            break;
    return counter


