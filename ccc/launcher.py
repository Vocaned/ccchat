import aiohttp
import typing

loginerrors = {
    'token': 'Internal error! Please try again.',
    'username': 'Invalid username!',
    'password': 'Invalid password!',
    'verification': 'User is not verified! Check your email',
    'login_code': '2FA authorization required. Check your email and log in using the ClassiCube launcher' # TODO: handle 2FA
}

async def _get(s, uri):
    async with s.get(uri) as r:
        return await r.json()
async def _post(s, uri, data=''):
    async with s.post(uri, data=data) as r:
        return await r.json()

async def login(username: str, password: str) -> typing.Tuple[str, str]:
    """Returns ((username, cookie_jar), error)"""
    async with aiohttp.ClientSession() as s:
        pre = await _get(s, 'https://www.classicube.net/api/login')
        token = pre['token']
        reallogin = await _post(s, 'https://www.classicube.net/api/login', data={'username': username, 'password': password, 'token': token})
        if reallogin['errors']:
            message = ', '.join(reallogin['errors'])
            for k,v in loginerrors.items():
                message = message.replace(k, v)
            return (None, message)

        if not reallogin['authenticated']:
            return (None, 'Could not authenticate. Please try again.')

        # TODO: Remember me

        return ((reallogin['username'], s.cookie_jar), None)

async def serverlist(cookie_jar):
    async with aiohttp.ClientSession(cookie_jar=cookie_jar) as s:
        # TODO: error handling
        servers = await _get(s, 'https://www.classicube.net/api/servers')
        servers = servers['servers']
        servers = sorted(servers, key=lambda k: k['players'], reverse=True)
        sList = []
        for _,s in enumerate(servers):
            col = ''
            if s['players'] > 0: col = '&a'
            display = f"{s['name']}&f | {col}{s['players']}/{s['maxplayers']}"
            if s['featured']:
                display = '&6' + display # TODO: background color
            sList.append((display, s))
        sList = sList[::-1]
        return sList
