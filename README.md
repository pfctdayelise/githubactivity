githubactivity
--------------

*githubactivity* is a script generates a summary report of activity happening on a Github repository. It makes use of the [PyGithub][1] library to read the [Github API][2].

    [1]: http://vincent-jacques.net/PyGithub/
    [2]: http://developer.github.com/v3/

Run via the command line:

    python githubactivity.py -o ORG -r REPO

By default this will generate a report for the last 7 days.

To see all the options:

    python githubactivity.py --help


This script is provided under the MIT License; see *LICENSE* for details.