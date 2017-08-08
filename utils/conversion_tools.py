

def get_float(value, default=None):

    if value is None:
        return default
    elif type(value) == float:
        return value
    elif type(value) == int:
        return float(value)
    elif type(value) == str:
        if value == '':
            return default
        else:
            try:
                return float(value)
            except ValueError:
                return default
    else:
        print('unknown type! type: {type}, value: {value}.'.format(
            **{'type': type(value), 'value': value}))
        return default
