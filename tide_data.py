from datetime import datetime
import time


def split_times_to_datetimes(split_times):
    tidal_datetimes = []
    for tides in split_times:
        today = datetime.today().strftime('%Y-%m-%d')
        today += " %s" % (tides[0],)
        print("HERE", today)
        d_time = datetime.strptime(today, '%Y-%m-%d %I:%M %p')
        tidal_datetimes.append(d_time)

    return tidal_datetimes


def get_data_points(current_time, tide_times):
    results = []
    last_item = None
    # Compare current time with tide times
    for tide in tide_times:
        if tide < current_time:
            last_item = tide
        else:
            prev_time = last_item
            next_time = tide
            results.extend([prev_time, current_time, next_time])
    return results


def get_light_intensity(data_points, ref_time):
    # Get fraction of tide
    current_time = datetime.now()
    next_time = data_points[2]

    ref_time_seconds = float(time.mktime(ref_time.timetuple()))
    current_time_seconds = float(time.mktime(current_time.timetuple()))
    next_time_seconds = float(time.mktime(next_time.timetuple()))

    numerator = next_time_seconds - current_time_seconds
    denominator = next_time_seconds - ref_time_seconds
    light_intensity = numerator / denominator

    return light_intensity
