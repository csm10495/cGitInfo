import os
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

def test_current_branch():
    '''
    makes sure we can get a valid current branch
    '''
    assert c_git_info.getCurrentBranch() != 'HEAD'

def test_flow():
    '''
    tests the input->output flow
    '''
    with open('_input.txt', 'w') as f:
        # write it twice
        f.write(c_git_info.REPLACE_STR + "\n")
        f.write(c_git_info.REPLACE_STR)

    # same repo twice
    runLine = 'python c_git_info.py -i _input.txt -o _output.txt -r "." "."'
    c_git_info.subprocess.check_output(runLine, shell=True)
    repoStr = c_git_info.getRepoRevisionSetInfo('.')
    with open('_output.txt', 'r') as f:
        outputText = f.read()

    assert outputText.count(repoStr) == 2

def test_flow_powershell():
    '''
    tests the input->output flow
    '''
    with open('_input.txt', 'w') as f:
        # write it twice
        f.write(c_git_info.REPLACE_STR + "\n")
        f.write(c_git_info.REPLACE_STR)

    POWERSHELL = 'powershell'
    if os.name != 'nt':
        POWERSHELL = 'pwsh'

    # same repo twice
    runLine = '%s -ExecutionPolicy ByPass ./c_git_info.ps1 -input_file _input.txt -output_file _output.txt -repo_directories ".", "."' % (POWERSHELL)
    c_git_info.subprocess.check_output(runLine, shell=True)
    repoStr = c_git_info.getRepoRevisionSetInfo('.')
    with open('_output.txt', 'r') as f:
        outputText = f.read()

    assert outputText.count(repoStr) == 2

def test_see_changes():
    '''
    tests that we get a + when changes are in the repo
    '''
    with open(__file__, 'r') as f:
        backupText = f.read()

    with open(__file__, 'a+') as f:
        f.write("\n\npass")
    assert '+' in c_git_info.getRepoRevisionSetInfo('.')

    # back to correct text
    with open(__file__, 'w') as f:
        f.write(backupText)