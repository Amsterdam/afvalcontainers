# utf-8
import requests
from bs4 import BeautifulSoup
from config import config
import argparse
import json
import tenacity


def get_login_cookies(session, baseUrl):
    """
        Get PHPSESSID cookie to use the API
    """
    print("start login")
    loginPage = session.get(baseUrl + '/login')
    soup = BeautifulSoup(loginPage.text, "html.parser")
    csrf = soup.find("input", type="hidden")

    # Get user and password from config.ini file
    credentials = config('loginCredentials')

    payload = {'_username': credentials['user'],
               '_password': credentials['password'],
               '_csrf_token': csrf['value'],
               }

    # Fake browser header
    headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36"}
    loginCheck = session.post(baseUrl + '/login_check',
                              data=payload,
                              headers=headers,
                              cookies=loginPage.cookies)
    # Response ok or not?
    if loginCheck.status_code == 200:
        soup = BeautifulSoup(loginCheck.text, "html.parser")
        # Check for name in html page which is only visible after login
        if 'dashboard' in soup.title.string.lower():
            print("login succeeded!")
            return loginCheck.cookies
    if loginCheck.status_code == 401 or loginCheck == 403:
        print('login failed!')


@tenacity.retry(wait=tenacity.wait_fixed(1),
                retry=tenacity.retry_if_exception_type(IOError))
def getContainer(session, cookies, endpoint, containerId):
    """
        Get The container date
    """
    url = baseUrl + '/api/' + endpoint + '/' + str(containerId) + '.json'
    print(url)
    containerURI = session.get(url, cookies=cookies)
    #print(containerURI.headers)
    #print(containerURI.text)
    if 'application/json' not in containerURI.headers["Content-Type"]:
        # DOES NOT WORK YET
        cookies = get_login_cookies(session, baseUrl)
        containerURI = session.get(url, cookies=cookies)
        containerData = containerURI.json()
        print("get login?")
    else:
        containerData = containerURI.json()
    return containerData


def main(baseUrl, endpoints, folder):
    """Get Containers."""
    with requests.Session() as session:
        cookies = get_login_cookies(session, baseUrl)
        for endpoint in endpoints:
            n = 1
            data = []
            ListURI = session.get(baseUrl + '/api/' + endpoint + '.json', cookies=cookies)
            List = ListURI.json()
            #print(containerList['containers'][0])
            arrayName = list(List.keys())[0]

            IdList = [item['id'] for item in List[arrayName]]
            #print(len(IdList), ' ', endpoint)
            for Id in IdList:
                item = getContainer(session, cookies, endpoint, Id)
                status = '{} of {}'.format(str(n), str(len(IdList)))
                print(status)
                data.append(item)
                n += 1
            with open(folder + '/' + endpoint + '.json', 'w') as outFile:
                json.dump(data, outFile, indent=2)
        print('Done with downloading!')


if __name__ == '__main__':
    desc = "download all containers from Bammens Api, for more info: https://bammensservice.nl/api/doc"
    parser = argparse.ArgumentParser(desc)
    parser.add_argument('datadir', type=str,
                        help='Local data directory.', nargs=1)
    args = parser.parse_args()

    baseUrl = 'https://bammensservice.nl'
    endpoints = ['containers', 'wells', 'containertypes']

    main(baseUrl, endpoints, args.datadir[0])
