import os
import urllib.request
from bs4 import BeautifulSoup
import time
import sys
import resource

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
                page = open(cache).read().decode('utf-8')
                print('read from cache:', cache)
            else:
                page = urllib.request.urlopen(start_page).read().decode('utf-8')
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


def start(start_url, output_file):
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

    return users


if __name__ == '__main__':
    import json
    import sys

    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'start_github_page_with_stars output.json')

    users = start(sys.argv[1], sys.argv[2])
    open(sys.argv[2], 'w').write(json.dumps(users))

