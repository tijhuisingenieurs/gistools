# functions for list manupulation

def all_same(items):
    """
    function to check if all items in list are the same. Input is list
    """
    return all(x == items[0] for x in items)


def closest(lst, K):
    """
    Find closest K value in a list
    """
    return lst[min(range(len(lst)), key=lambda i: abs(lst[i] - K))]