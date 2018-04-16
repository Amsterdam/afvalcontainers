"""
Exctract login information
"""
import os
import logging
from bs4 import BeautifulSoup
import settings

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


async def set_login_cookies(session):
    """Get PHPSESSID cookie to use the API
    """
    baseUrl = settings.API_URL
    log.debug("start login")
    loginPage = await session.get(baseUrl + '/login', ssl=False)
    text = await loginPage.text()
    soup = BeautifulSoup(text, "html.parser")
    csrf = soup.find("input", type="hidden")

    payload = {
        '_username': os.getenv('BAMMENS_API_USERNAME', ''),
        '_password': os.getenv('BAMMENS_API_PASSWORD', ''),
        '_csrf_token': csrf['value'],
    }

    # Fake browser header
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36"  # noqa
    }
    loginCheck = await session.post(
        baseUrl + '/login_check',
        data=payload,
        headers=headers,
    )
    # Response ok or not?
    if loginCheck.status == 200:
        text = await loginCheck.text()
        soup = BeautifulSoup(text, "html.parser")
        # Check for name in html page which is only visible after login
        if 'dashboard' in soup.title.string.lower():
            log.debug("Login succeeded!")
            # log.debug('COOKIES: %s', [c for c in session.cookie_jar])

    if loginCheck.status == 401 or loginCheck == 403:
        log.error('login failed!')
