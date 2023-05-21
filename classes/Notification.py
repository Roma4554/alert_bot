from re import search
from typing import Optional, Union
from datetime import datetime, date
from collections.abc import Iterable, Iterator

from configobj import ConfigObj


config = ConfigObj('settings.ini')


class Notification:

    def __init__(self,
                 employee_id: Optional[int] = None,
                 date: Optional[str] = None,
                 notification: Optional[str] = None
                 ) -> None:
        self.employee_id = employee_id
        self.date = date
        self.notification = notification

    def __iter__(self) -> Iterator:
        self.list_attr = [self.notification, self.date, self.employee_id]
        return self

    def __next__(self) -> Iterable[Union[int, str]]:
        if self.list_attr:
            return self.list_attr.pop()
        else:
            raise StopIteration

    def __str__(self):
        return f'{self.convert_date()}: [{self.employee_id}] {self.notification}'

    def date_to_datetime(self) -> datetime.date:
        """
        Метод возвращающий дату в формате datetime.date
        """
        self.__verify_date_if_not_none(self.date)
        return date.fromisoformat(self.date.replace('.', '-'))

    def convert_date(self, date_format: str = '%d.%m.%Y') -> str:
        """
        Метод возвращающий дату в указанном формате
        """
        return self.date_to_datetime().strftime(date_format)

    @classmethod
    def __verify_date_if_not_none(cls, date: str) -> None:
        if date is None:
            raise TypeError('Дата отсутствует (None)')

    @classmethod
    def __verify_employee_id(cls, employee_id: int) -> None:
        if not isinstance(employee_id, int) and employee_id is not None:
            raise TypeError("Табельный номер пользователя должно быть целочисленным значением.")
        if employee_id is not None:
            if len(str(employee_id)) != int(config['DEFAULT']['len_employee_id']):
                raise ValueError(f"Некорректный формат табельного номера")

    @classmethod
    def __verify_date(cls, date: str) -> None:
        pattern = r'\b(?:[12]\d{3})\.(?:0[1-9]|1[012])\.(?:0[1-9]|[12]\d|3[01])\b'
        if not isinstance(date, str) and date is not None:
            raise TypeError("Дата должна быть строкой или None.")
        elif date is not None and not search(pattern, date):
            raise ValueError('Дата должна быть в формате ГГГГ.ММ.ДД')

    @classmethod
    def __verify_notification(cls, notification: str) -> None:
        if not isinstance(notification, str) and notification is not None:
            raise TypeError("Оповещение должно быть строкой.")

    @property
    def employee_id(self) -> int:
        return self.__employee_id

    @employee_id.setter
    def employee_id(self, value: int) -> None:
        self.__verify_employee_id(value)
        self.__employee_id = value

    @property
    def date(self) -> str:
        return self.__date

    @date.setter
    def date(self, value: str) -> None:
        self.__verify_date(value)
        self.__date = value

    @property
    def notification(self) -> str:
        return self.__notification

    @notification.setter
    def notification(self, value: str) -> None:
        self.__verify_notification(value)
        self.__notification = value
