import arrow
import regex as re
from typing import List

from nonebot import (
    CommandSession,
    IntentCommand,
    NLPSession,
    on_command,
    on_natural_language,
)
from requests import Response
from time_converter import StringPreHandler, TimeNormalizer

from app.bot.constants.config import api_url
from log import IS_LOGGER
from utils.aio import requests
from utils.tools import bot_hash

from .parse import get_week, parse_course_by_date, str_int_wday_dict, week_course

__plugin_name__ = "查询课表(缩写cs)"
__plugin_usage__ = r"""输入 查询课课表
或者加上时间限定：
    - 今天课表
    - 明天有什么课
    - 九月十五号有什么课
查询课表短语：cs

    - 更新课表
更新课表短语：uc
""".strip()

tn = TimeNormalizer()


@on_command("cs", aliases=("查询课表", "课表", "课程表", "课程"))
async def course_schedule(session: CommandSession):
    sender_qq = session.ctx.get("user_id")

    # 从更新课表中传过来的值
    if session.state.get("course_schedule"):
        resp = session.state.get("course_schedule")
    else:
        r: Response = await requests.get(
            api_url + "api/v1/course/getCourse",
            params={
                "qq": sender_qq,
                "token": bot_hash(sender_qq)
            },
        )
        if r:
            resp = await r.json()
        else:
            await session.finish("查询出错")
            return

    IS_LOGGER.debug(f"查询课表结果：{str(resp)}")
    if resp["code"] == 200:
        body = resp["data"]["body"]
        week = session.state.get("week")
        wday = session.state.get("wday")
        is_today = session.state.get("today")
        if is_today:
            IS_LOGGER.info("发送当天课表")
            now = arrow.now("Asia/Shanghai")
            week = get_week(now.timestamp)
            wday = str(now.isoweekday())
            course = parse_course_by_date(body, week, wday)
            await session.finish(course)
        elif week and wday:
            IS_LOGGER.info(f"检测到时间意图：{str(session.state)}")
            course = parse_course_by_date(body, week, wday)
            await session.finish(course)
        elif week:
            IS_LOGGER.info(f"检测到时间意图：{str(session.state)}")
            course_dict: List[str] = week_course(body, int(week))
            for i in course_dict:
                await session.send(i)
        else:
            # 所有课表
            course_dict: List[str] = week_course(body)
            for i in course_dict:
                await session.send(i)

        if body['errMsg']:
            await session.finish(f"错误信息：{body['errMsg']}")

        if body['updateTime']:
            await session.finish(f"课表抓取时间：{body['updateTime']}")
        return

    elif resp["code"] == -1:
        await session.finish("未绑定！")
        return
    await session.finish("查询出错")


@on_natural_language("课")
async def process_accu_date(session: NLPSession):
    msg = session.ctx.get("raw_message")
    now = arrow.now("Asia/Shanghai")

    week_re = re.search(r"下周", msg)
    if week_re:
        IS_LOGGER.info(f"获取下周课表")
        week = get_week(now.timestamp)
        args = {"week": week + 1}
        await session.send(f"下周课表（第{week + 1}周）：")
        return IntentCommand(90.0, "cs", args=args)

    res = tn.parse(target=msg, timeBase=now)
    IS_LOGGER.debug(f"课程时间意图分析结果: {str(msg)} -> {str(res)}")
    tn_type: str = res.get("type")
    if tn_type == "timestamp":
        date = arrow.get(res.get(tn_type), "YYYY-MM-DD HH:mm:ss")
        wday = str(date.isoweekday())
        week = get_week(date.timestamp)
        await session.send(
            f"{res.get(tn_type)[:10]}，第{week}周，星期{str_int_wday_dict.get(wday,wday)}"
        )
        IS_LOGGER.info(f"第{str(week)}周，星期{str_int_wday_dict.get(wday,wday)}")
        args = {"wday": wday, "week": week}
        return IntentCommand(90.0, "cs", args=args)

    # 周数匹配
    text = StringPreHandler.numberTranslator(msg)
    week_re = re.search(r"第(\d+)周", text)
    if week_re and week_re.group(1):
        await session.send(f"{week_re.group(0)}课表：")
        IS_LOGGER.info(f"周数分析结果:{week_re.group(1)}")
        args = {"week": week_re.group(1)}
        return IntentCommand(90.0, "cs", args=args)

    return IntentCommand(90.0, "cs")
