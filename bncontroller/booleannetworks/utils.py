
def check_to_json_existence(value):
    if hasattr(value, 'to_json') and callable(value.to_json):
        return value.to_json() 
    else:
        return value