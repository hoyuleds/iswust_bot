import pickle

from loguru import logger
from nonebot import get_bot
from sqlalchemy import Column

from app.constants.dean import API
from app.libs.aio import run_sync_func
from app.libs.cache import cache
from app.libs.gino import db
from app.utils.bot import qq2event
from app.config import Config

from .base import Base


class User(Base, db.Model):
    """用户表 Model
    """

    __tablename__ = "user"

    qq = Column(db.String(16), primary_key=True)
    student_id = Column(db.String(32), unique=True)
    password = Column(db.String(64), nullable=False)
    cookies = Column(db.LargeBinary)

    @classmethod
    async def add(cls, *, qq: int, student_id: int, password: str, cookies):
        user = User(
            student_id=str(student_id), qq=str(qq), password=password, cookies=cookies,
        )
        await user.create()
        return user

    @classmethod
    async def unbind(cls, qq: int):
        user = await User.query.where(User.qq == str(qq)).gino.first()
        await user.delete()
        return True

    @classmethod
    async def check(cls, qq: int):
        user = await cls.get(str(qq))
        if user:
            return user
        _bot = get_bot()
        await _bot.send(qq2event(qq), "未绑定，试试对我发送 `绑定`")
        return False

    @classmethod
    async def get_cookies(cls, user: "User"):
        from auth_swust import Login
        from auth_swust import request as login_request

        cookies = pickle.loads(user.cookies)
        sess = login_request.Session(cookies)
        res = await run_sync_func(
            sess.get, API.jwc_index, allow_redirects=False, verify=False
        )

        # 302重定向了，session 失效，重新获取session
        if res.status_code == 302 or res.status_code == 301:
            u_ = Login(user.student_id, user.password)
            is_log, _ = await run_sync_func(u_.try_login)
            if is_log:
                cookies = pickle.dumps(u_.get_cookies())
                await user.update(cookies=cookies).apply()
                logger.info(f"更新qq: {user.qq} 的 session")
                return u_.get_cookies()
        else:
            return cookies

    @classmethod
    async def get_session(cls, user: "User"):
        from auth_swust import request as login_request

        key = f"cookies/{user.qq}"
        cookies = await cache.get(key)
        if not cookies:
            cookies = await cls.get_cookies(user)
            await cache.set(key, cookies, ttl=Config.CACHE_SESSION_TIMEOUT)
        sess = login_request.Session(cookies)
        return sess
