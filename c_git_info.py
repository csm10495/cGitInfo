'''
Brief:
    File to help get git info in a git/hg style format from the given repo

Author(s):
    Charles Machalow
'''

import argparse
import contextlib
import subprocess
import os

# crappy backport of subprocess.check_output for Python 2.6...
if not hasattr(subprocess, 'check_output'):
    def check_output(cmd, shell=False):
        '''
        Brief:
            Backport of check_output, just to work for what I need here.
                Features are missing.
        '''
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=shell)
        stdout, stderr = process.communicate()
        ret = process.poll()
        if ret:
            error = subprocess.CalledProcessError(ret, cmd)
            error.output = stdout
            raise error
        return stdout
    subprocess.check_output = check_output
    del check_output

REPLACE_STR = '<C_GIT_INFO>'

@contextlib.contextmanager
def tempChDir(directory):
    '''
    Brief:
        Temporarily go to a directory, yield, then go back
    '''
    cwd = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(cwd)

def hasChanges():
    '''
    Brief:
        Returns True if changes are staged locally
    '''
    output = subprocess.check_output('git status -s -uno', shell=True)
    return bool(output.strip()) # True if output from this command

def getCurrentBranch():
    '''
    Brief:
        Returns the name of the current branch
    '''
    output = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True).decode().strip()
    if output == 'HEAD':
        output = subprocess.check_output('git log -n 1 --pretty=%d HEAD', shell=True).decode()
        output = output.split(',')[-1].split(')')[0].split('/', 1)[-1].split('->')[-1].strip()
        
        # handle if this is a tag that is checked out. Consider the tag as a branch.
        if output.startswith('tag: '):
            output = output.split('tag: ')[-1]
            
        if 'HEAD' in output:
            output = subprocess.check_output('git name-rev --name-only HEAD', shell=True).decode().strip()
            output = output.split('/', 1)[-1].split('^')[0].split('~')[0] # remove extra characters from branch name
    return output.strip()

def getListOfCommits(branch=None):
    '''
    Brief:
        Returns list of commits on given branch. 0th is most recent.
    '''
    if branch is None:
        branch = getCurrentBranch()

    commits = subprocess.check_output('git log --pretty=format:%%h --full-history %s' % branch, shell=True).decode().splitlines()
    return commits

def getCurrentCommitId(branch=None):
    '''
    Brief:
        Gets the hash of the current commit and appenda a "+" if there are staged changes
    '''
    if branch is None:
        branch = getCurrentBranch()

    commit = getListOfCommits(branch)[0] # first is newest
    if hasChanges():
        return commit + "+"
    return commit

def getHgStyleIdNum(branch=None):
    '''
    Brief:
        Gets an hg-style id number for the current commit
    '''
    commits = getListOfCommits(branch)
    start = str(len(commits))
    if hasChanges():
        return start + "+"
    return start

def getRepoNameFromCurrentFolder():
    '''
    Brief:
        Gets the name of the repo from the current folder. Assumes the folder name was not changed
    '''
    return os.path.basename(os.getcwd())

def getOriginUrl(repoPath='.'):
    '''
    Brief:
        Gets the url of the origin.
    '''
    with tempChDir(repoPath):
        return subprocess.check_output('git config --get remote.origin.url', shell=True).decode().splitlines()[0]

def getLastCommitAuthorName(repoPath='.'):
    '''
    Brief:
        Returns a string of the last committer's name
    '''
    with tempChDir(repoPath):
        return subprocess.check_output('git log --format="%an"', shell=True).decode().splitlines()[0]

def getLastCommitAuthorEmail(repoPath='.'):
    '''
    Brief:
        Returns a string of the last committer's email address
    '''
    with tempChDir(repoPath):
        return subprocess.check_output('git log --format="%ae"', shell=True).decode().splitlines()[0]

def getRepoRevisionSetInfo(repoPath='.'):
    '''
    Brief:
        Returns a string of information about the current repository commits/changesets
    '''
    with tempChDir(repoPath):
        branch = getCurrentBranch()
        hgIdNum = getHgStyleIdNum(branch)
        commitId = getCurrentCommitId(branch)
        repoName = getRepoNameFromCurrentFolder()
        origin = getOriginUrl()
        return "%s - %s (hg:%s) - %s - %s" % (repoName, commitId, hgIdNum, branch, origin)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-input_file", "-i", help="File path. This is generic file with %s somewhere to replace." % REPLACE_STR, type=str, required=True)
    parser.add_argument("-output_file", "-o", help="Output file path (with replaced %s)" % REPLACE_STR, type=str, required=True)
    parser.add_argument("-repo_directories", "-r", help="Repository directories", nargs='+', type=str, required=False, default='.')
    args = parser.parse_args()

    with open(args.input_file, 'r') as f:
        txt = f.read()

    for repoDir in args.repo_directories:
        repoInfo = getRepoRevisionSetInfo(repoDir)
        print (repoInfo)
        txt = txt.replace(REPLACE_STR, repoInfo, 1)

    if os.path.isfile(args.output_file):
        with open(args.output_file, 'r') as f:
            currentText = f.read()
    else:
        currentText = ""

    if txt == currentText:
        print ("Not updating. File matches!")
    else:
        with open(args.output_file, 'w') as f:
            f.write(txt)
        print ("Updated changset info!")
