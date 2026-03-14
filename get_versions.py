import re

import requests
from bs4 import BeautifulSoup

reversion = re.compile(r'\d+\.\d+(?:\.\d+)?/$')


def main():
    downloads = requests.get('https://www.python.org/downloads/')
    downloads.raise_for_status()

    wanted = []
    soup = BeautifulSoup(downloads.content, 'html.parser')
    version_rows = soup.find('div', class_='active-release-list-widget').find('ol', class_='list-row-container')
    for row in version_rows.find_all('li'):
        branch = row.find('span', class_='release-version').text
        status = row.find('span', class_='release-status').text
        if status in ('bugfix', 'security'):
            wanted.append(tuple(map(int, branch.split('.'))))

    ftp = requests.get('https://www.python.org/ftp/python/')
    ftp.raise_for_status()

    soup = BeautifulSoup(ftp.content, 'html.parser')

    releases = {}
    for version in soup.find_all('a'):
        href = version['href']
        if reversion.match(href):
            release = tuple(map(int, href.rstrip('/').split('.')))
            branch = (release[0], release[1])
            if branch in wanted:
                if branch in releases:
                    releases[branch] = max(releases[branch], release)
                else:
                    releases[branch] = release

    for _, release in sorted(releases.items()):
        print('.'.join(map(str, release)))


if __name__ == '__main__':
    main()
