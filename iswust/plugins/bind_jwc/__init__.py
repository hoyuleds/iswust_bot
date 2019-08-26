from nonebot import on_command, CommandSession
from iswust.utils.tools import xor_encrypt, tcn
from iswust.constants.config import login_url

__plugin_name__ = '绑定教务处'
__plugin_usage__ = r"""对我发以下关键词开始绑定：
绑定、绑定教务处、bind"""


@on_command('bind', aliases=('绑定', '绑定教务处'))
async def bind(session: CommandSession):
    await session.send(f'开始请求绑定~ 请等待')

    sender = session.ctx.get('sender', {})
    sender_qq = sender.get('user_id')
    nickname = sender.get('nickname')
    verify_code = xor_encrypt(sender_qq)

    # 检查用户名和密码的长度
    url_ = f'{login_url}?qq={sender_qq}&nickname={nickname}&verifycode={verify_code}'
    shorten_url_ = tcn(url_)
    if shorten_url_:
        await session.send(f'请点击链接绑定：{shorten_url_}')
    else:
        await session.send(f'请点击链接绑定：{url_}')
