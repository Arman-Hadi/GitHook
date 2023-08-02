import git

g = git.Repo('/Users/arman/w/GitHook')
g.remote('origin').pull()