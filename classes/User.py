from typing import Union
from collections.abc import Iterable, Iterator


class User:

    def __init__(self, user_id: int, name: str, employee_id: int, is_admin: bool = False) -> None:
        self.__verify_id(user_id)

        self.__id = user_id
        self.name = name
        self.employee_id = employee_id
        self.is_admin = bool(is_admin)

    def __str__(self):
        return f"[{self.employee_id}] {self.name}"

    def __iter__(self) -> Iterator:
        self.list_attr = [self.__id, self.name, self.employee_id]
        return self

    def __next__(self) -> Iterable[Union[int, str]]:
        if self.list_attr:
            return self.list_attr.pop()
        else:
            raise StopIteration

    @classmethod
    def __verify_id(cls, id: int) -> None:
        if not isinstance(id, int):
            raise TypeError("id пользователя должно быть целочисленным значением.")

    @classmethod
    def __verify_name(cls, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError("Имя пользователя должно быть строкой")
        if not name.replace(' ', '').isalpha():
            raise ValueError('Имя должно содержать только буквы')

    @classmethod
    def __verify_employee_id(cls, employee_id: int) -> None:
        if not isinstance(employee_id, int):
            raise TypeError("Табельный номер пользователя должно быть целочисленным значением.")

    @classmethod
    def __verify_is_admin(cls, is_admin: bool) -> None:
        if not isinstance(is_admin, bool) or is_admin not in (0, 1):
            raise TypeError("Статус администратора пользователя должен быть булевым значением.")

    @property
    def user_id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__verify_name(value)
        self.__name = value

    @property
    def employee_id(self) -> int:
        return self.__employee_id

    @employee_id.setter
    def employee_id(self, value: int) -> None:
        self.__verify_employee_id(value)
        self.__employee_id = value

    @property
    def is_admin(self) -> bool:
        return self.__is_admin

    @is_admin.setter
    def is_admin(self, value: bool) -> None:
        self.__verify_is_admin(value)
        self.__is_admin = value
