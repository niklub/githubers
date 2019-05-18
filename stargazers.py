import argparse
import pandas as pd
import re

from github_stargazers.github import GitHub as GitHubStargazer
from github import Github


def main(args):
    output = []
    g = Github(args.login, args.password)
    prefix = 'https://github.com/'
    for repo in args.repos:
        reponame = re.sub(prefix, '', repo)
        print(f'Start processing {reponame}...')
        gs = GitHubStargazer(reponame)
        stargazers = gs.get_all_stargazers()
        for stargazer in stargazers:
            user = g.get_user(stargazer)
            if args.email_required and not user.email:
                continue
            if args.company_required and not user.company:
                continue
            if args.location_required and not user.location:
                continue
            output.append({
                'name': user.name,
                'email': user.email,
                'company': user.company,
                'location': user.location
            })
    pd.DataFrame.from_records(output).to_csv(args.output_file, sep='\t', index=False)


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
    parser.add_argument('--email-required', dest='email_required', action='store_true')
    parser.add_argument('--company-required', dest='company_required', action='store_true')
    parser.add_argument('--location-required', dest='location_required', action='store_true')

    args = parser.parse_args()

    main(args)
