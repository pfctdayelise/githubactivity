githubactivity
--------------

*githubactivity* is a script generates a summary report of activity happening on a Github repository. It makes use of the [PyGithub](http://vincent-jacques.net/PyGithub/) library to read the [Github API](http://developer.github.com/v3/).

To see an example of the output, have a look at *example-bootstrap.html*.

Run via the command line:

    python githubactivity.py -o ORG -r REPO

By default this will generate a report for the last 7 days.

To see all the options:

    python githubactivity.py --help


One-liner to send it as an email:

   (echo -e "To: alice@foo.com\nFrom: bob@foo.com\nSubject: Github activity summary\nContent-Type: text/html\n\n"; python githubactivity.py -o ORG -r REPO) | sendmail alice@foo.com



This script is provided under the MIT License; see *LICENSE* for details.