'''
Brief:
    File to help get git info in a git/hg style format from the given repo

Author(s):
    Charles Machalow
'''
import argparse
import subprocess
import os

REPLACE_STR = '<C_GIT_INFO>'

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
    output = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True)
    return output.strip().decode()
    
def getListOfCommits(branch='master'):
    '''
    Brief:
        Returns list of commits on given branch. 0th is most recent.
    '''
    commits = subprocess.check_output('git log --pretty=format:%%h --full-history %s' % branch, shell=True).decode().splitlines()
    return commits
    
def getCurrentCommitId(branch='master'):
    '''
    Brief:
        Gets the hash of the current commit and appenda a "+" if there are staged changes
    '''
    commit = getListOfCommits(branch)[0] # first is newest
    if hasChanges():
        return commit + "+"
    return commit
    
def getHgStyleIdNum(branch='master'):
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
    return subprocess.check_output('git config --get remote.origin.url', shell=True).decode().splitlines()[0]

def getRepoRevisionSetInfo(repoPath='.'):
    '''
    Brief:
        Returns a string of information about the current repository commits/changesets
    '''
    oldCwd = os.getcwd()
    os.chdir(repoPath)
    try:
        branch = getCurrentBranch()
        hgIdNum = getHgStyleIdNum(branch)
        commitId = getCurrentCommitId(branch)
        repoName = getRepoNameFromCurrentFolder()
        origin = getOriginUrl()
        return "%s - %s (hg:%s) - %s - %s" % (repoName, commitId, hgIdNum, branch, origin)
    finally:
        os.chdir(oldCwd)
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-input_file", "-i", help="File path. This is generic file with %s somewhere to replace." % REPLACE_STR, type=str, required=True)
    parser.add_argument("-output_file", "-o", help="Output file path (with replaced %s)" % REPLACE_STR, type=str, required=True)
    parser.add_argument("-repo_directory", "-r", help="Repository directory", type=str, required=False, default='.')
    args = parser.parse_args()

    with open(args.input_file, 'r') as f:
        txt = f.read()
        
    txt = txt.replace(REPLACE_STR, getRepoRevisionSetInfo(args.repo_directory))
    
    with open(args.output_file, 'r') as f:
        currentText = f.read()
        
    if txt == currentText:
        print ("Not updating. File matches!")
    else:
        with open(args.output_file, 'w') as f:
            f.write(txt)
        print ("Updated changset info!")
    
    