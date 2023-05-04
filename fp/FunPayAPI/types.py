"""
В данном модуле описаны все объекты, используемые в пакете FunPayAPI.
"""
from __future__ import annotations
from typing import Literal, overload, Optional
from enum import Enum
from .common.utils import RegularExpressions


class MessageTypes(Enum):
    """
    В данном классе хранятся все типы сообщений.
    """
    NON_SYSTEM = 0
    """Несистемное сообщение."""

    ORDER_PURCHASED = 1
    """Покупатель X оплатил заказ #Y. Лот. X, не забудьте потом нажать кнопку «Подтвердить выполнение заказа»."""

    ORDER_CONFIRMED = 2
    """Покупатель X подтвердил успешное выполнение заказа #Y и отправил деньги продавцу Z."""

    NEW_FEEDBACK = 3
    """Покупатель X написал отзыв к заказу #Y."""

    FEEDBACK_CHANGED = 4
    """Покупатель X изменил отзыв к заказу #Y."""

    FEEDBACK_DELETED = 5
    """Покупатель X удалил отзыв к заказу #Y."""

    NEW_FEEDBACK_ANSWER = 6
    """Продавец Z ответил на отзыв к заказу #Y."""

    FEEDBACK_ANSWER_CHANGED = 7
    """Продавец Z изменил ответ на отзыв к заказу #Y."""

    FEEDBACK_ANSWER_DELETED = 8
    """Продавец Z удалил ответ на отзыв к заказу #Y."""

    ORDER_REOPENED = 9
    """Заказ #Y открыт повторно."""

    REFUND = 10
    """Продавец Z вернул деньги покупателю X по заказу #Y."""

    PARTIAL_REFUND = 11
    """Часть средств по заказу #Y возвращена покупателю."""

    ORDER_CONFIRMED_BY_ADMIN = 12
    """Администратор A подтвердил успешное выполнение заказа #Y и отправил деньги продавцу Z."""

    DISCORD = 13
    """Вы можете перейти в Discord. Внимание: общение за пределами сервера FunPay считается нарушением правил."""


class OrderStatuses(Enum):
    """
    Состояния заказов.

    OrderStatuses.PAID - ожидает выполнения.

    OrderStatuses.CLOSED - закрыт.

    OrderStatuses.REFUNDED - средства по заказу возвращены.
    """
    PAID = 0
    """Заказ оплачен и ожидает выполнения."""
    CLOSED = 1
    """Заказ закрыт."""
    REFUNDED = 2
    """Средства по заказу возвращены."""


class SubCategoryTypes(Enum):
    """
    Типы подкатегорий.

    SubCategoryTypes.COMMON - подкатегория со стандартными лотами.

    SubCategoryTypes.CURRENCY - подкатегория с лотами игровой валюты (их нельзя поднимать).
    """
    COMMON = 0
    """Подкатегория со стандартными лотами."""
    CURRENCY = 1
    """Подкатегория с лотами игровой валюты (их нельзя поднимать)."""


class ChatShortcut:
    """
    Класс, описывающий виджет чат (виджет чата).
    """

    def __init__(self, id_: int, name: str, last_message_text: str,
                 unread: bool, html: str, determine_msg_type: bool = True):
        """
        :param id_: ID чата.
        :param name: название чата (никнейм собеседника).
        :param last_message_text: текст последнего сообщения в чате (макс. 250 символов).
        :param unread: флаг "непрочитанности" (если True - в чате есть непрочитанные сообщения).
        :param html: HTML код виджета чата.
        :param determine_msg_type: определять ли тип последнего сообщения?
        """
        self.id: int = id_
        """ID чата."""
        self.name: str | None = name if name else None
        """Название чата (никнейм собеседника)."""
        self.last_message_text: str = last_message_text
        """Текст последнего сообщения в чате (макс. 250 символов)."""
        self.unread: bool = unread
        """Флаг \"непрочитанности\" (если True - в чате есть непрочитанные сообщения)."""
        self.last_message_type = None if not determine_msg_type else self.get_last_message_type()
        """Тип последнего сообщения."""
        self.html: str | None = html
        """HTML код виджета чата."""

    def get_last_message_type(self) -> MessageTypes:
        """
        Определяет тип последнего сообщения в чате на основе регулярных выражений из MessageTypesRes.

        !Внимание! Результат определения типа сообщения данным методом не является правильным в 100% случаев, т.к. он
        основан на сравнении с регулярными выражениями.
        Возможно "ложное срабатывание", если пользователь напишет "поддельное" сообщение, которое совпадет с одним из
        регулярных выражений.
        """
        res = RegularExpressions()
        if self.last_message_text == res.DISCORD:
            return MessageTypes.DISCORD

        if res.ORDER_PURCHASED.findall(self.last_message_text) and res.ORDER_PURCHASED2.findall(self.last_message_text):
            return MessageTypes.ORDER_PURCHASED

        if res.ORDER_ID.search(self.last_message_text) is None:
            return MessageTypes.NON_SYSTEM

        # Регулярные выражения выставлены в порядке от самых часто-используемых к самым редко-используемым
        sys_msg_types = {
            MessageTypes.ORDER_CONFIRMED: res.ORDER_CONFIRMED,
            MessageTypes.NEW_FEEDBACK: res.NEW_FEEDBACK,
            MessageTypes.NEW_FEEDBACK_ANSWER: res.NEW_FEEDBACK_ANSWER,
            MessageTypes.FEEDBACK_CHANGED: res.FEEDBACK_CHANGED,
            MessageTypes.FEEDBACK_DELETED: res.FEEDBACK_DELETED,
            MessageTypes.REFUND: res.REFUND,
            MessageTypes.FEEDBACK_ANSWER_CHANGED: res.FEEDBACK_ANSWER_CHANGED,
            MessageTypes.FEEDBACK_ANSWER_DELETED: res.FEEDBACK_ANSWER_DELETED,
            MessageTypes.ORDER_CONFIRMED_BY_ADMIN: res.ORDER_CONFIRMED_BY_ADMIN,
            MessageTypes.PARTIAL_REFUND: res.PARTIAL_REFUND,
            MessageTypes.ORDER_REOPENED: res.ORDER_REOPENED
        }

        for i in sys_msg_types:
            if sys_msg_types[i].search(self.last_message_text):
                return i
        else:
            return MessageTypes.NON_SYSTEM

    def __str__(self):
        return self.last_message_text


class Chat:
    def __init__(self, id_: int, name: str, looking_link: str | None, looking_text: str | None,
                 html: str, messages: Optional[list[Message]] = None):
        """
        Класс, описывающий чат.
        :param id_: ID чата.
        :param name: название чата.
        :param looking_link: ссылка на лот, который смотрит собеседник.
        :param looking_text: название лота, который смотрит собеседник.
        :param html: HTML код чата.
        :param messages: последние 100 сообщений чата.
        """
        self.id = id_
        self.name = name
        self.looking_link = looking_link
        self.looking_text = looking_text
        self.html = html
        self.messages = messages or []


class Message:
    """
    Класс, описывающий сообщение.
    """

    def __init__(self, id_: int, text: str | None, chat_id: int, chat_name: str | None,
                 author: str | None, author_id: int, html: str,
                 image_link: str | None = None, determine_msg_type: bool = True):
        """
        :param id_: ID сообщения.
        :param text: текст сообщения.
        :param chat_id: ID чата, в котором появилось сообщение.
        :param chat_name: название чата, в котором появилось сообщение.
        :param author: никнейм автора сообщения.
        :param author_id: ID автора сообщения.
        :param html: HTML код сообщения.
        :param determine_msg_type: определять ли тип сообщения.
        """
        self.id: int = id_
        """ID сообщения."""
        self.text: str | None = text
        """Текст сообщения."""
        self.chat_id = chat_id
        """ID чата."""
        self.chat_name = chat_name
        """Название чата."""
        self.type = None if not determine_msg_type else self.get_message_type()
        """Тип сообщения."""
        self.author: str | None = author
        """Автор сообщения."""
        self.author_id: int = author_id
        """ID автора сообщения."""
        self.html: str = html
        """HTML-код сообщения."""
        self.image_link: str | None = image_link
        """Ссылка на изображение в сообщении (если оно есть)."""
        self.by_bot = False
        """Отправлено ли сообщение с помощью пакета FunPayAPI?"""

    def get_message_type(self) -> MessageTypes:
        """
        Определяет тип последнего сообщения в чате на основе регулярных выражений из MessageTypesRes.

        Внимание! Данный способ определения типа сообщения не является 100% правильным, т.к. он основан на сравнении с
        регулярными выражениями. Возможно ложное "срабатывание", если пользователь напишет "поддельное" сообщение,
        которое совпадет с одним из регулярных выражений.
        """
        if not self.text:
            return MessageTypes.NON_SYSTEM

        res = RegularExpressions()
        if self.text == res.DISCORD:
            return MessageTypes.DISCORD

        if res.ORDER_PURCHASED.findall(self.text) and res.ORDER_PURCHASED2.findall(self.text):
            return MessageTypes.ORDER_PURCHASED

        if res.ORDER_ID.search(self.text) is None:
            return MessageTypes.NON_SYSTEM

        # Регулярные выражения выставлены в порядке от самых часто-используемых к самым редко-используемым
        sys_msg_types = {
            MessageTypes.ORDER_CONFIRMED: res.ORDER_CONFIRMED,
            MessageTypes.NEW_FEEDBACK: res.NEW_FEEDBACK,
            MessageTypes.NEW_FEEDBACK_ANSWER: res.NEW_FEEDBACK_ANSWER,
            MessageTypes.FEEDBACK_CHANGED: res.FEEDBACK_CHANGED,
            MessageTypes.FEEDBACK_DELETED: res.FEEDBACK_DELETED,
            MessageTypes.REFUND: res.REFUND,
            MessageTypes.FEEDBACK_ANSWER_CHANGED: res.FEEDBACK_ANSWER_CHANGED,
            MessageTypes.FEEDBACK_ANSWER_DELETED: res.FEEDBACK_ANSWER_DELETED,
            MessageTypes.ORDER_CONFIRMED_BY_ADMIN: res.ORDER_CONFIRMED_BY_ADMIN,
            MessageTypes.PARTIAL_REFUND: res.PARTIAL_REFUND,
            MessageTypes.ORDER_REOPENED: res.ORDER_REOPENED
        }

        for i in sys_msg_types:
            if sys_msg_types[i].search(self.text):
                return i
        else:
            return MessageTypes.NON_SYSTEM

    def __str__(self):
        return self.text if self.text is not None else self.image_link if self.image_link is not None else ""


class OrderShortcut:
    """
    Класс, описывающий виджет заказа (со страницы funpay.com/orders/trade)
    """

    def __init__(self, id_: str, description: str, price: float,
                 buyer_username: str, buyer_id: int, status: OrderStatuses,
                 html: str, dont_search_amount: bool = False):
        """
        :param id_: ID заказа.
        :param description: описание заказа.
        :param price: цена заказа.
        :param buyer_username: никнейм покупателя.
        :param buyer_id: ID покупателя.
        :param status: статус заказа.
        :param html: HTML код виджета заказа.
        :param dont_search_amount: не искать кол-во товара.
        """
        self.id = id_ if not id_.startswith("#") else id_[1:]
        """ID заказа."""
        self.description = description
        """Описание заказа."""
        self.price = price
        """Цена заказа."""
        self.amount: int | None = self.parse_amount() if not dont_search_amount else None
        """Кол-во товаров."""
        self.buyer_username = buyer_username
        """Никнейм покупателя."""
        self.buyer_id = buyer_id
        """ID покупателя."""
        self.status = status
        """Статус заказа."""
        self.html = html
        """HTML код виджета заказа."""

    def parse_amount(self):
        res = RegularExpressions()
        result = res.PRODUCTS_AMOUNT.findall(self.description)
        if result:
            return int(result[0].split(" ")[0])
        return 1

    def __str__(self):
        return self.description


class Order:
    """
    Класс, описывающий заказ (https://funpay.com/orders/ID/)
    """
    def __init__(self, id_: str, status: OrderStatuses, subcategory: SubCategory, short_description: str | None,
                 full_description: str, sum_: float,
                 buyer_id: int, buyer_username: str,
                 seller_id: int, seller_username: str,
                 html: str, review: Review | None):
        """
        :param id_: ID заказа.
        :param status: статус заказа.
        :param subcategory: подкатегория, к которой относится заказ.
        :param short_description: краткое описание (название) заказа.
        :param full_description: полное описание заказа.
        :param sum_: сумма заказа.
        :param buyer_id: ID покупателя.
        :param buyer_username: никнейм продавца.
        :param seller_id: ID продавца.
        :param seller_username: никнейм продавца.
        :param html: HTML код заказа.
        :param review: объект отзыва на заказ.
        """
        self.id = id_
        """ID заказа."""
        self.status = status
        """Статус заказа."""
        self.subcategory = subcategory
        """Подкатегория, к которой относится заказ."""
        self.short_description = short_description
        """Краткое описание заказа."""
        self.full_description = full_description
        """Полное описание заказа."""
        self.sum = sum_
        """Сумма заказа."""
        self.buyer_id = buyer_id
        """ID покупателя."""
        self.buyer_username = buyer_username
        """Никнейм покупателя."""
        self.seller_id = seller_id
        """ID продавца."""
        self.seller_username = seller_username
        """Никнейм продавца."""
        self.html = html
        """HTML код заказа."""
        self.review = review
        """Объект отзыва заказа."""


class Category:
    """
    Класс, описывающий категорию (игру).
    """

    def __init__(self, id_: int, name: str, subcategories: list[SubCategory] | None = None):
        """
        :param id_: ID категории (game_id / data-id).
        :param name: название категории (игры).
        :param subcategories: подкатегории.
        """
        self.id = id_
        """ID категории (game_id / data-id)."""
        self.name = name
        """Название категории (игры)."""
        self.__subcategories: list[SubCategory] = subcategories or []
        """Список подкатегорий."""
        self.__sorted_subcategories: dict[SubCategoryTypes, dict[int, SubCategory]] = {
            SubCategoryTypes.COMMON: {},
            SubCategoryTypes.CURRENCY: {}
        }
        for i in self.__subcategories:
            self.__sorted_subcategories[i.type][i.id] = i

    def add_subcategory(self, subcategory: SubCategory):
        """
        Добавляет подкатегорию в список подкатегорий.

        :param subcategory:
        """
        if subcategory not in self.__subcategories:
            self.__subcategories.append(subcategory)
            self.__sorted_subcategories[subcategory.type][subcategory.id] = subcategory

    def get_subcategory(self, subcategory_type: SubCategoryTypes, subcategory_id: int) -> SubCategory | None:
        """
        Возвращает объект подкатегории.

        :param subcategory_type: тип подкатегории.
        :param subcategory_id: ID подкатегории.
        """
        return self.__sorted_subcategories[subcategory_type].get(subcategory_id)

    def get_subcategories(self) -> list[SubCategory]:
        """
        Возвращает все подкатегории данной категории (игры).
        """
        return self.__subcategories

    def get_sorted_subcategories(self) -> dict[SubCategoryTypes, dict[int, SubCategory]]:
        """
        Возвращает все подкатегории данной категории (игры) в виде словаря {type: {ID: подкатегория}}.
        """
        return self.__sorted_subcategories


class SubCategory:
    """Класс, описывающий подкатегорию."""

    def __init__(self, id_: int, name: str, type_: SubCategoryTypes, category: Category):
        """
        :param id_: ID подкатегории.
        :param name: название подкатегории.
        :param type_: тип лотов подкатегории.
        :param category: родительская категория (игра).
        """
        self.id = id_
        """ID подкатегории."""
        self.name = name
        """Название подкатегории."""
        self.type = type_
        """Тип подкатегории."""
        self.category = category
        """Родительская категория (игра)."""
        self.fullname = f"{self.name} {self.category.name}"
        """Полное название подкатегории."""
        self.public_link = f"https://funpay.com/chips/{id_}/" if type_ is SubCategoryTypes.CURRENCY else \
            f"https://funpay.com/lots/{id_}/"
        """Публичная ссылка на список лотов подкатегории."""
        self.private_link = f"{self.public_link}trade"
        """Приватная ссылка на список лотов подкатегории (для редактирования лотов)."""


class LotFields:
    """
    Класс, описывающий поля лота.
    """
    def __init__(self, lot_id: int, subcategory_id: int, fields: dict):
        """
        :param lot_id: ID лота.
        :param subcategory_id: ID категории (игры), к которой относится лот.
        :param fields: словарь с полями.
        """
        self.lot_id = lot_id
        """ID лота."""
        self.subcategory_id = subcategory_id
        """ID подкатегории, к которой относится лот."""
        self.__fields = fields
        """Поля лота."""

        self.title_ru: str = self.__fields.get("fields[summary][ru]")
        """Русское название (краткое описание) лота."""
        self.title_en: str = self.__fields.get("fields[summary][en]")
        """Английское название (краткое описание) лота."""
        self.description_ru: str = self.__fields.get("fields[desc][ru]")
        """Русское полное описание лота."""
        self.description_en: str = self.__fields.get("fields[desc][en]")
        """Английское полное описание лота."""
        self.amount: int | None = int(i) if (i := self.__fields.get("amount")) else None
        """Кол-во товара."""
        self.price: float = float(i) if (i := self.__fields.get("price")) else None
        """Цена за 1шт."""
        self.active: bool = "active" in self.__fields
        """Активен ли лот."""
        self.deactivate_after_sale: bool = "deactivate_after_sale[]" in self.__fields
        """Деактивировать ли лот после продажи."""

    def get_fields(self) -> dict[str, str]:
        """
        Возвращает все поля лота в виде словаря.
        """
        return self.__fields

    def edit_fields(self, fields: dict):
        """
        Редактирует переданные поля лота.

        :param fields: поля лота, которые нужно заменить, и их значения.
        """
        for i in fields:
            self.__fields[i] = fields[i]

    def set_fields(self, fields: dict):
        """
        Сбрасывает текущие поля лота и устанавливает переданные.

        :param fields: поля лота.
        """
        self.__fields = fields

    def renew_fields(self) -> LotFields:
        """
        Обновляет поля лота, основываясь на измененных свойствах экземпляра.
        Необходимо перед сохранением лота на FunPay после изменения любого свойства экземпляра.

        :return: экземпляр класса LotFields с новыми полями лота.
        """
        self.__fields["fields[summary][ru]"] = self.title_ru
        self.__fields["fields[summary][en]"] = self.title_en
        self.__fields["fields[desc][ru]"] = self.description_ru
        self.__fields["fields[desc][en]"] = self.description_en
        self.__fields["price"] = str(self.price) if self.price is not None else ""
        if self.amount is not None:
            self.__fields["amount"] = str(self.amount)
        else:
            if "amount" in self.__fields:
                self.__fields.pop("amount")

        if self.active:
            self.__fields["active"] = "on"
        else:
            if "active" in self.__fields:
                self.__fields.pop("active")

        if self.deactivate_after_sale:
            if "deactivate_after_sale" in self.__fields:
                self.__fields.pop("deactivate_after_sale")
            self.__fields["deactivate_after_sale[]"] = "on"
        else:
            if "deactivate_after_sale[]" in self.__fields:
                self.__fields.pop("deactivate_after_sale[]")
            self.__fields["deactivate_after_sale"] = ""
        return self


class LotShortcut:
    def __init__(self, id_: int | str, server: str | None,
                 description: str | None, price: float, subcategory: SubCategory, html: str):
        self.id = id_
        if isinstance(self.id, str) and self.id.isnumeric():
            self.id = int(self.id)
        """ID лота."""
        self.server = server
        """Название сервера (если указан)."""
        self.description = description
        """Краткое описание лота."""
        self.price = price
        """Цена лота."""
        self.subcategory = subcategory
        """Подкатегория лота."""
        self.html = html
        """HTML-код виджета лота."""
        self.public_link = f"https://funpay.com/chips/offer?id={self.id}" \
            if self.subcategory.type is SubCategoryTypes.CURRENCY else f"https://funpay.com/lots/offer?id={self.id}"
        """Публичная ссылка на лот."""


class UserProfile:
    """
    Класс, описывающий страницу пользователя.
    """

    def __init__(self, id_: int, username: str, profile_photo: str, online: bool, banned: bool, html: str):
        self.id = id_
        """ID пользователя."""
        self.username = username
        """Никнейм пользователя."""
        self.profile_photo = profile_photo
        """Ссылка на фото профиля."""
        self.online = online
        """Онлайн ли пользователь."""
        self.banned = banned
        """Заблокирован ли пользователь."""
        self.html = html
        """HTML код страницы пользователя."""
        self.__lots: list[LotShortcut] = []
        """Все лоты пользователя."""
        self.__lots_ids: dict[int | str, LotShortcut] = {}
        """Все лоты пользователя в виде словаря {ID: лот}}"""
        self.__sorted_lots: dict[SubCategory, dict[int | str, LotShortcut]] = {}
        """Все лоты пользователя в виде словаря {подкатегория: {ID: лот}}"""

    def get_lot(self, lot_id: int | str) -> LotShortcut | None:
        """
        Возвращает объект лота.

        :param lot_id: ID лота.
        """
        if isinstance(lot_id, str) and lot_id.isnumeric():
            return self.__lots_ids.get(int(lot_id))
        return self.__lots_ids.get(lot_id)

    def get_lots(self) -> list[LotShortcut]:
        """
        Возвращает список всех лотов пользователя.
        """
        return self.__lots

    @overload
    def get_sorted_lots(self, mode: Literal[1]) -> dict[int | str, LotShortcut]: ...

    @overload
    def get_sorted_lots(self, mode: Literal[2]) -> dict[SubCategory, dict[int | str, LotShortcut]]: ...

    def get_sorted_lots(self, mode: Literal[1, 2]) -> dict[int | str, LotShortcut] | dict[SubCategory,
                                                                                          dict[int | str, LotShortcut]]:
        """
        Возвращает список всех лотов пользователя в виде словаря.

        :param mode: вариант словаря.
            1 - {ID: лот}
            2 - {подкатегория: {ID: лот}}
        """
        if mode == 1:
            return self.__lots_ids
        else:
            return self.__sorted_lots

    def add_lot(self, lot: LotShortcut):
        """
        Добавляет лот в список лотов.
        :param lot: объект лота.
        """
        if lot in self.__lots:
            return

        self.__lots.append(lot)
        self.__lots_ids[lot.id] = lot
        if lot.subcategory not in self.__sorted_lots:
            self.__sorted_lots[lot.subcategory] = {}
        self.__sorted_lots[lot.subcategory][lot.id] = lot

    def __str__(self):
        return self.username


class Review:
    """
    Класс, описывающий отзыв.
    """
    def __init__(self, stars: int | None, text: str | None, reply: str | None, anonymous: bool, html: str,
                 order_id: str | None = None, author: str | None = None, author_id: int | None = None):
        """
        :param stars: кол-во звезд в отзыве.
        :param text: текст отзыва.
        :param reply: текст ответа на отзыв.
        :param anonymous: анонимный ли отзыв?
        :param html: HTML код отзыва.
        :param order_id: ID заказа, к которому относится отзыв.
        :param author: автор отзыва.
        :param author_id: ID автора отзыва.
        """
        self.stars = stars
        """Кол-во звезде в отзыве."""
        self.text = text
        """Текст отзыва."""
        self.reply = reply
        """Текст ответа на отзыв."""
        self.anonymous = anonymous
        """Анонимный ли отзыв?"""
        self.html = html
        """HTML код отзыва."""
        self.order_id = order_id
        """ID заказа, к которому относится отзыв."""
        self.author = author
        """Автор отзыва."""
        self.author_id = author_id
        """ID автора отзыва."""


class RaiseResponse:
    """
    Класс, описывающий ответ FunPay на запрос о поднятии лотов.
    """
    def __init__(self, complete: bool, wait: int, raised_subcategories: list[SubCategory], funpay_response: dict):
        """
        :param complete: удалось ли поднять лоты.

        :param wait: примерное время ожидания до следующего поднятия.

        :param raised_subcategories: список объектов поднятых подкатегорий.

        :param funpay_response: полный ответ Funpay.
        """
        self.complete = complete
        """Удалось ли поднять лоты."""
        self.wait = wait
        """Примерное время ожидания до след. поднятия."""
        self.raised_subcategories = raised_subcategories
        """Список объектов поднятых подкатегорий."""
        self.funpay_response = funpay_response
        """полный ответ FunPay."""
