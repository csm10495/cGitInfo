<#
Brief:
    File to help get git info in a git/hg style format from the given repo
        ... this is c_git_info.py... written in Powershell instead of Python!
            One difference is for params, we need to use commas between repo_directories
                instead of spaces in Python

Author(s):
    Charles Machalow
#>

Param(
    [string]$input_file=$FALSE,
    [string]$output_file=$FALSE,
    [string[]]$repo_directories="."
    )

$ErrorActionPreference = "Stop" # Stop on first error
$REPLACE_STR = [regex]"<C_GIT_INFO>"

function Has-changes(){
    <#
    Brief:
        Returns True if changes are staged locally
    #>
    $output = git status -s -uno
    return $output.length -gt 0 # True if output from this command
}

function Get-Current-Branch(){
    <#
    Brief:
        Returns the name of the current branch
    #>
    $output = git rev-parse --abbrev-ref HEAD
    $output = $output.trim()
    if ($output -eq "HEAD") {
        $output = git log -n 1 --pretty=%d HEAD
        $output = $output.split(',')[-1].split(')')[0].split('/', 1)[-1]
    }
    return $output.trim()
}

function Get-List-Of-Commits($branch='master'){
    <#
    Brief:
        Returns list of commits on given branch. 0th is most recent.
    #>
    $output = (git log --pretty=format:%h --full-history $branch)
    return $output.split('\n')
}

function Get-Current-Commit-Id($branch='master'){
    <#
    Brief:
        Gets the hash of the current commit and appenda a "+" if there are staged changes
    #>
    $commit = (Get-List-Of-Commits $branch)[0] # first is newest
    if (Has-Changes){
        return ($commit + "+")
    }
    return ($commit)
}

function Get-Hg-Style-Id-Num($branch='master'){
    <#
    Brief:
        Gets an hg-style id number for the current commit
    #>
    $commits = Get-List-Of-Commits $branch
    $start = [string]$commits.length
    if (Has-Changes){
        return ($start + "+")
    }
    return ($start)
}

function Get-Repo-Name-From-Current-Folder() {
    <#
    Brief:
        Gets the name of the repo from the current folder. Assumes the folder name was not changed
    #>
    $p = Get-Item -Path "./"
    return $p.Name
}

function Get-Origin-Url($repoPath='.'){
    <#
    Brief:
        Gets the url of the origin.
    #>
    pushd $repoPath
    $result = git config --get remote.origin.url
    popd
    return $result.trim()
}

function Get-Last-Commit-Authors-Name($repoPath='.'){
    <#
    Brief:
        Returns a string of the last committer's name
    #>
    pushd $repoPath
    $result = git log --format="%an"
    popd
    return $result.split("\n")[0].trim()
}

function Get-Last-Commit-Authors-Email($repoPath='.'){
    <#
    Brief:
        Returns a string of the last committer's email address
    #>
    pushd $repoPath
    $result = git log --format="%ae"
    popd
    return $result.split("\n")[0].trim()
}

function Get-Repo-Revision-Set-Info($repoPath='.'){
    <#
    Brief:
        Returns a string of information about the current repository commits/changesets
    #>
    pushd $repoPath
    $branch = Get-Current-Branch
    $hgIdNum = Get-Hg-Style-Id-Num $branch
    $commitId = Get-Current-Commit-Id $branch
    $repoName = Get-Repo-Name-From-Current-Folder
    $origin = Get-Origin-Url
    popd
    return "$repoName - $commitId (hg:$hgIdNum) - $branch - $origin"
}

if ($repo_directories -ne $false -and $input_file -ne $false -and $output_file -ne $false) {
    $txt = Get-Content $input_file -Raw
    for ($i=0; $i -lt $repo_directories.length; $i++) {
        $repoInfo = Get-Repo-Revision-Set-Info $repo_directories[$i]
        Write-Host $repoInfo
        $txt = $REPLACE_STR.Replace($txt, $repoInfo, 1)
    }
    if (Test-Path $output_file) {
        $out = Get-Content $output_file -Raw
    } else {
        $out = ""
    }

    if ($out.trim() -eq $txt.trim()) {
        Write-Host "Not updating. File matches!"
    } else {
        Set-Content -Path $output_file -Value $txt
        Write-Host "Updated changset info!"
    }
}