import datetime

def dict_from_row(row):
    return dict(zip(row.keys(), row))   

def json_addons(obj):
    if isinstance(obj, datetime.datetime):
        return obj.__str__()
    if isinstance(obj, datetime.date):
        return obj.__str__()
    raise TypeError ("Type %s not serializable" % type(obj))