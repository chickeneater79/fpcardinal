from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cardinal import Cardinal

from bs4 import BeautifulSoup
from FunPayAPI.account import Account

import telebot
from tg_bot import utils


NAME = "List Old Orders Plugin"
VERSION = "0.0.2"
DESCRIPTION = "Данный плагин добавляет команду /old_orders, " \
              "благодаря которой можно получить список открытых заказов, которым более 24 часов."
CREDITS = "@woopertail"
UUID = "a31cfa24-5ac8-4efb-8c61-7dec3544aa32"
SETTINGS_PAGE = False


def get_orders(acc: Account) -> list[str]:
    """
    Получает список ордеров на аккаунте.

    :return: Список с заказами.
    """
    orders = acc.get_sales(state="paid")[1]
    old_orders = []
    for i in orders:
        parser = BeautifulSoup(i.html, "html.parser")

        time = parser.find("div", {"class": "tc-date-left"}).text
        if any(map(time.__contains__, ["сек", "мин", "час", "тол"])):
            continue
        old_orders.append(parser.find("div", {"class": "tc-order"}).text)
    return old_orders


def init_commands(cardinal: Cardinal, *args):
    if not cardinal.telegram:
        return
    tg = cardinal.telegram
    bot = tg.bot
    acc = cardinal.account

    def send_orders(m: telebot.types.Message):
        try:
            orders = get_orders(acc)
        except:
            bot.send_message(m.chat.id, "❌ Не удалось получить список заказов.")
            return

        if not orders:
            bot.send_message(m.chat.id, "❌ Просроченных заказов нет.")
            return

        orders_text = ", ".join(orders)
        text = f"Здравствуйте!\n\nПрошу подтвердить выполнение следующих заказов:\n{orders_text}"
        bot.send_message(m.chat.id, f"<code>{utils.escape(text)}</code>")

    tg.msg_handler(send_orders, commands=["old_orders"])
    cardinal.add_telegram_commands(UUID, [
        ("old_orders", "отправляет список открытых заказов, которым более 24 часов", True)
    ])


BIND_TO_PRE_INIT = [init_commands]
BIND_TO_DELETE = None
