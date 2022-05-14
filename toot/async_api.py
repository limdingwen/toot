import asyncio

from toot import config
from toot.asynch import api


async def async_main():
    user, app = config.get_active_user_app()

    # response = await api.get_instance("social.zlatko.dev")
    response = await api.timeline(app, user)
    # response = await api.get_status(app, user, 108302558833681902)
    print(response.body)
    # text = await response.text()
    # pprint(text)


def main():
    asyncio.run(async_main())
