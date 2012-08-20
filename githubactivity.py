import datetime
import argparse
from github import Github
from mako.template import Template

dateStamp = '%Y-%m-%d'

class Commit(object):
    def __init__(self, commit):
        self._commit = commit

    @property
    def author(self):
        if self._commit.author is None:
            return 'None?'
        return self._commit.author.login

    @property
    def message(self):
        lines = [l.strip() for l in self._commit.commit.message.split('\n')]
        lines = [l for l in lines if l]
        return lines[0]

    @property
    def timestamp(self):
        return self._commit.commit.author.date.strftime(dateStamp)

    @classmethod
    def strList(cls, commits, reportNoActivity):
        if not commits and reportNoActivity:
            return "No recent commits!"
        return '\n'.join('{0.timestamp} {0.author}: {0.message}'.format(c) for c in commits)


def getRecentCommits(repo, start, end, reportNoActivity):
    """
    @param repo: a GitRepo object
    @return: string
    """
    commits = repo.get_commits()
    recentCommits = []

    for commit in commits:
        # I think we're iterating through these basically backwards??
        ts = commit.commit.author.date
        if ts < start:
            break
        if ts < end:
            # end might be specified, i.e. in the past
            recentCommits.append(Commit(commit))
    s = Commit.strList(recentCommits, reportNoActivity)
    return s


def getPullRequestsOpen(repo, reportNoActivity):
    if reportNoActivity:
        return 'No open pull requests.'
    return ''


def getPullRequestsClosed(repo, reportNoActivity):
    if reportNoActivity:
        return 'No closed pull requests.'
    return ''


def getIssuesSubmitted(repo, reportNoActivity):
    if reportNoActivity:
        return 'No issues submitted.'
    return ''


def getIssuesActivity(repo, reportNoActivity):
    if reportNoActivity:
        return 'No activity on issues.'
    return ''


def getIssuesClosed(repo, reportNoActivity):
    if reportNoActivity:
        return 'No issues closed.'
    return ''


def getWikiActivity(repo, reportNoActivity):
    if reportNoActivity:
        return 'No wiki activity.'
    return ''


def getRepoActivity(org, repo, days=None, end=None, reportNoActivity=True):
    """
    @param org: a string representing an organization
    @param repo: a string representing a repo
    @param days: optional, int
    @param end: optional, datetime object
    @param reportNoActivity: bool, explicitly report when there has been no activity?
    @return: string
    """
    if not days:
        days = 7
    if not end:
        end = datetime.datetime.today()
    period = datetime.timedelta(days=days)
    start = end - period

    g = Github()
    repository = g.get_organization(org).get_repo(repo)
    
    commits = getRecentCommits(repository, start, end, reportNoActivity)
    pullReqOpen = getPullRequestsOpen(repository, reportNoActivity)
    pullReqClosed = getPullRequestsClosed(repository, reportNoActivity)
    issuesSubmitted = getIssuesSubmitted(repository, reportNoActivity)
    issuesActivity = getIssuesActivity(repository, reportNoActivity)
    issuesClosed = getIssuesClosed(repository, reportNoActivity)
    wiki = getWikiActivity(repository, reportNoActivity)

    template = Template(filename='template.txt')
    contents = {
        'repo': repo,
        'org': org,
        'period': period.days,
        'end': end.strftime('%Y-%m-%d'),
        'commits': commits,
        'pullrequestsopen': pullReqOpen,
        'pullrequestsclosed': pullReqClosed,
        'issuessubmitted': issuesSubmitted,
        'issuesactivity': issuesActivity,
        'issuesclosed': issuesClosed,
        'wiki': wiki,
    }
    result = template.render(**contents)
    return result


def dateObject(s):
    try:
        d = datetime.datetime.strptime(s, dateStamp)
    except ValueError:
        msg = "'{}' is not a timestamp of the form '{}'".format(s, dateStamp)
        raise argparse.ArgumentTypeError(msg)
    return d

if __name__ ==  '__main__':
    parser = argparse.ArgumentParser(description="Print out a summary of Github activity")
    parser.add_argument("-o", dest="org", required=True, help="Name of an organization")
    parser.add_argument("-r", dest="repo", required=True, help="Name of a repository")
    parser.add_argument("-d", dest="days", default=None, type=int, help="Number of days to summarise")
    parser.add_argument("-e", dest="end", default=None, type=dateObject, help="End date (in format '{}'".format(dateStamp))
    parser.add_argument("-n", dest="reportNoActivity", default=None, type=bool, help="Report explicitly if there is no activity")
    args = parser.parse_args()
    r = getRepoActivity(**vars(args))
    print r
