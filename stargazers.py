import argparse
import pandas as pd
import re

from github_stargazers.github import GitHub as GitHubStargazer
from github import Github


def main(repos, login, password, output_file):
    output = []
    g = Github(login, password)
    prefix = 'https://github.com/'
    for repo in repos:
        gs = GitHubStargazer(re.sub(prefix, '', repo))
        stargazers = gs.get_all_stargazers()
        for stargazer in stargazers:
            user = g.get_user(stargazer)
            output.append({
                'name': user.name,
                'email': user.email,
                'company': user.company,
                'location': user.location
            })
    pd.DataFrame.from_records(output).to_csv(output_file, sep='\t')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--repos', dest='repos', nargs='+', required=True,
                        help='GitHub repositories URLs separated by whitespace')
    parser.add_argument('--login', dest='login', required=True,
                        help='Your GitHub login')
    parser.add_argument('--password', dest='password', required=True,
                        help='Your GitHub password')
    parser.add_argument('--output-file', dest='output_file', default='output.tsv',
                        help='Output file in TSV format')

    args = parser.parse_args()

    main(args.repos, args.login, args.password, args.output_file)
