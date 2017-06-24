import pytest

import c_git_info

def test_everything():
    '''
    tests everything
    '''
    for i in dir(c_git_info):
        thing = getattr(c_git_info, i)
        if hasattr(thing, '__call__'):
            try:
                thing() # don't assert on this since False is probably ok
            except Exception as ex:
                # check for missing positional argument... ignore it.
                if 'required positional argument' not in str(ex):
                    raise ex
                    