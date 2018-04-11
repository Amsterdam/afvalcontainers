"""
Exctract login information
"""
import os
import logging
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


def get_login_cookies(session, baseUrl):
    """Get PHPSESSID cookie to use the API
    """
    log.info("start login")
    loginPage = session.get(baseUrl + '/login')
    soup = BeautifulSoup(loginPage.text, "html.parser")
    csrf = soup.find("input", type="hidden")

    payload = {
        '_username': os.environ['BAMMENS_API_USERNAME'],
        '_password': os.environ['BAMMENS_API_PASSWORD'],
        '_csrf_token': csrf['value'],
    }

    # Fake browser header
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36"  # noqa
    }
    loginCheck = session.post(
        baseUrl + '/login_check',
        data=payload,
        headers=headers,
        cookies=loginPage.cookies)
    # Response ok or not?
    if loginCheck.status_code == 200:
        soup = BeautifulSoup(loginCheck.text, "html.parser")
        # Check for name in html page which is only visible after login
        if 'dashboard' in soup.title.string.lower():
            log.info("Login succeeded!")
            return loginCheck.cookies
    if loginCheck.status_code == 401 or loginCheck == 403:
        log.info('login failed!')
