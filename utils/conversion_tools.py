

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


def get_string(value, default=None):
    if value is None:
        return default
    elif value == '':
        return default
    else:
        return str(value)


def get_int(value, default=None):
    if value is None:
        return default
    elif type(value) == float:
        return int(value)
    elif type(value) == str:
        if value == '':
            return default
        else:
            try:
                return int(value)
            except ValueError:
                return default
    else:
        print('unknown type! type: {type}, value: {value}.'.format(
            **{'type': type(value), 'value': value}))
        return default