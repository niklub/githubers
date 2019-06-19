import os
import urllib.request
from bs4 import BeautifulSoup
import time
import sys
import resource
import re
import io
import json
import pandas as pd
import argparse

from google import google
from github import Github
from github.GithubException import RateLimitExceededException

resource.setrlimit(resource.RLIMIT_STACK, [0x10000000, resource.RLIM_INFINITY])
sys.setrecursionlimit(0x100000)


n = 0


def get_users_from_stars(start_page, cache_dir):
    global n
    results = []

    ok = False
    while not ok:
        try:
            cache = cache_dir + '/' + str(n) + '.html'
            if os.path.exists(cache):
                page = open(cache).read()
                print('read from cache:', cache)
            else:
                page = urllib.request.urlopen(start_page).read()
                page = page.decode('utf-8')
                open(cache, 'w').write(page)

            n += 1
            ok = True
        except Exception as e:
            print('get_replies::urlopen error: ' + str(e))
            time.sleep(60)

    soup = BeautifulSoup(page, 'lxml')
    users = soup.select('span.css-truncate a')
    for user in users:
        results.append(user.text)

    soup = BeautifulSoup(page, 'html.parser')
    nexts = soup.select('a.btn')

    next_url = None
    for a in nexts:
        if a.text == 'Next':
            next_url = a['href']

    return results, next_url


def get_all_users_from_repo(start_url, output_file):
    """ Main function for start,
        start_url is like https://github.com/awslabs/amazon-sagemaker-examples/stargazers,
        output_file is output.json
    """

    users = []
    next_url = start_url
    cache_dir = os.path.splitext(output_file)[0]
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    while next_url is not None:
        print('Next url -->', next_url)
        batch, next_url = get_users_from_stars(next_url, cache_dir)
        users += batch
        if len(users) > 3: break

    with io.open(output_file, mode='w') as fout:
        json.dump(users, fout, indent=2)
    return users


def get_info_from_users_list(github_login, github_pass, all_users_file, json_formatted=True, use_google=False, output_file=None):
    if output_file is None:
        output_file = os.path.splitext(all_users_file)[0] + '.out.tsv'
    g = Github(github_login, github_pass)
    out = []
    if json_formatted:
        all_names = list(sorted(set(json.load(io.open(all_users_file)))))
    else:
        all_names = list(sorted(set(io.open(all_users_file).read().splitlines())))
    if len(all_names) == 0:
        print(f'Empty file {all_users_file}')
        return
    print(f'Start scraping info from {len(all_names)} users')
    for line in all_names:
        if use_google:
            req = f'github {line}'
            username = None
            try:
                for r in google.search(req):
                    username = re.match(r'https?://github.com/(\w+)(\?.*)?$', r.link)
                    if username:
                        username = username.group(1)
                        break
            except:
                print(line, ' --> Google ERROR')
                continue
        else:
            username = line
        if username:
            try:
                user = g.get_user(username)
                if user.email:
                    out.append({
                        'name': user.name,
                        'email': user.email,
                        'location': user.location,
                        'company': user.company,
                        'repos': user.repos_url,
                        'followers': user.followers,
                        'following': user.following,
                        'bio': user.bio,
                        'created_at': user.created_at,
                        'updated_at': user.updated_at,
                        'hireable': user.hireable,
                        'blog': user.blog,
                        'url': user.html_url or user.url
                    })
                    pd.DataFrame.from_records(out).to_csv(output_file, sep='\t', index=False)
                    print(line, ' --> OK!')
                else:
                    print(line, ' --> NO email!')
            except RateLimitExceededException:
                print('Rate limit...')
                time.sleep(1000)
            except Exception as exc:
                print(line, ' --> ', exc)
                continue
        else:
            print(line, ' --> skipped')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Example Heartex ML backend server with simple text classifier')
    parser.add_argument('--output-file', dest='output_file', help='Output file', default='output')
    parser.add_argument('--stargazer-page', dest='stargazer_page', help='URL to stargazer page', required=True)
    parser.add_argument('--login', dest='login', help='Github login', required=True)
    parser.add_argument('--password', dest='password', help='Github password', required=True)
    args = parser.parse_args()

    all_users_file = os.path.splitext(args.output_file)[0] + '.users.json'

    get_all_users_from_repo(args.stargazer_page, all_users_file)
    get_info_from_users_list(args.login, args.password, all_users_file)
