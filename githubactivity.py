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


class PullRequest(object):
    def __init__(self, pull):
        self._pull = pull

    @property
    def closedTimestamp(self):
        return self._pull.closed_at.strftime(dateStamp)

    @property
    def closer(self):
        return '?'

    @property
    def author(self):
        return self._pull.user.login

    @property
    def title(self):
        return self._pull.title


class Issue(object):
    def __init__(self, issue):
        self._issue = issue

    @property
    def url(self):
        return self._issue.html_url

    @property
    def assignee(self):
        if self._issue.assignee:
            return self._issue.assignee.login
        return 'no'

    @property
    def author(self):
        return self._issue.user.login

    @property
    def number(self):
        return self._issue.number

    @property
    def title(self):
        return self._issue.title

    @property
    def timestamp(self):
        if self.created == self.updated:
            return 'new {}'.format(self.created)
        return 'updated {}'.format(self.updated)

    @property
    def created(self):
        return self._issue.created_at.strftime(dateStamp)

    @property
    def updated(self):
        return self._issue.updated_at.strftime(dateStamp)

    @property
    def closer(self):
        return self._issue.closed_by.login

    @property
    def closed(self):
        return self._issue.closed_at.strftime(dateStamp)

    @property
    def comments(self):
        return list(self._issue.get_comments())

    @property
    def commentSummary(self):
        totalComments = len(self.comments)
        if totalComments == 0:
            return 'No comments'
        if totalComments == 1:
            return '1 comment'
        else:
            return '{} comments'.format(totalComments)


def getRecentCommits(repo, start):
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
        # end might be specified, i.e. in the past
        recentCommits.append(Commit(commit))
    return recentCommits


def getPullRequestsOpen(repo):
    pulls = repo.get_pulls('open')
    pulls = [PullRequest(p) for p in pulls]
    return pulls


def getPullRequestsClosed(repo, start):
    pulls = repo.get_pulls('closed')
    pulls = [PullRequest(p) for p in pulls if start < p.closed_at]
    return pulls


def getIssuesUpdated(repo, start):
    if not repo.has_issues:
        return False
    issues = [Issue(i) for i in repo.get_issues(state='open', sort='updated', since=start)]
    return issues


def getIssuesClosed(repo, start):
    if not repo.has_issues:
        return False
    issues = [Issue(i) for i in repo.get_issues(state='closed', sort='updated', since=start)]
    return issues


def getRepoActivity(org, repo, days=None, reportNoActivity=None):
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
    if reportNoActivity is None:
        reportNoActivity = True
    end = datetime.datetime.today()
    period = datetime.timedelta(days=days)
    start = end - period

    g = Github()
    repository = g.get_organization(org).get_repo(repo)
    
    commits = getRecentCommits(repository, start)
    pullReqOpen = getPullRequestsOpen(repository)
    pullReqClosed = getPullRequestsClosed(repository, start)
    hasIssues = repository.has_issues

    contents = {
        'repo': repo,
        'org': org,
        'period': period.days,
        'end': end.strftime('%Y-%m-%d'),
        'commits': commits,
        'pullrequestsopen': pullReqOpen,
        'pullrequestsclosed': pullReqClosed,
        'hasIssues': hasIssues,
        'issuessubmitted': None,
        'issuesactivity': None,
        'issuesclosed': None,
    }
    if hasIssues:
        issuesUpdated = getIssuesUpdated(repository, start)
        issuesClosed = getIssuesClosed(repository, start)
        contents.update({
                'issuesupdated': issuesUpdated,
                'issuesclosed': issuesClosed
            })

    template = Template(filename='template.txt')
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
#    parser.add_argument("-e", dest="end", default=None, type=dateObject, help="End date (in format '{}'".format(dateStamp))
    parser.add_argument("-n", dest="reportNoActivity", default=None, type=bool, help="Report explicitly if there is no activity")
    args = parser.parse_args()
    r = getRepoActivity(**vars(args))
    print r
