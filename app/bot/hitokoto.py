from typing import Optional
from random import choice
import httpx
from nonebot import CommandSession, on_command

__plugin_name__ = "一言"
__plugin_usage__ = r"""给你回复一句话
""".strip()

defaults = [
    "这里有嬉笑怒骂，柴米油盐，人间戏梦，滚滚红尘。",
    "这温热的跳动，就是活着。",
    "那就祝你早安，午安，晚安吧。",
]


@on_command("hitokoto", aliases=("一言", "hi"), only_to_me=False)
async def _(session: CommandSession):
    _hitokoto = await hitokoto()
    if _hitokoto:
        await session.finish(_hitokoto["hitokoto"].strip())
    await session.finish(choice(defaults))


async def hitokoto() -> Optional[dict]:
    # https://hitokoto.cn/api
    hitokoto_url = "https://v1.hitokoto.cn/"
    async with httpx.AsyncClient() as client:
        r: httpx.Response = await client.get(hitokoto_url)
        res = r.json()
    return res
