def get_week_day(instance, week_index):
    week_mapping = {
        0: instance.mon,
        1: instance.tue,
        2: instance.wed,
        3: instance.thr,
        4: instance.fri,
        5: instance.sat,
        6: instance.sun,
    }

    return week_mapping[week_index]
