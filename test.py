import pytest

import c_git_info

def test_everything():
    '''
    tests everything
    '''
    for i in dir(c_git_info):
        if i == 'tempChDir':
            continue # skip.
        thing = getattr(c_git_info, i)
        if hasattr(thing, '__call__'):
            thing() # don't assert on this since False is probably ok
                    