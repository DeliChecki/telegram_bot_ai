import datetime
import os
import random
from typing import Union

from telebot import TeleBot
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import User as TelegramUser
from sqlmodel import Session, select, create_engine, SQLModel
from telegram.dataobjects import User
import yaml

from requests import Session as RequestsSession
import logging


class DatabaseUtils:
    def __init__(self, engine):
        self.engine = engine

    @staticmethod
    def generate_random_login(user: TelegramUser) -> str:
        # if user has own domain, return it
        if user.username:
            return user.username

        # generate login
        login = ""
        for i in range(10):
            login += chr(random.randint(97, 122))

        return login

    @staticmethod
    def generate_password():
        password = ""
        for i in range(7):
            password += chr(random.randint(97, 122))

        return password

    def get_user_or_create_new(self, user: TelegramUser) -> Union[User, None]:
        if user.id is None:
            return None

        session = Session(self.engine)
        find_user = select(User).where(User.telegram_id == user.id)
        find_user = session.exec(find_user).one_or_none()

        if not find_user:
            login = self.generate_random_login(user)
            password = self.generate_password()

            new_user = User(
                telegram_id=user.id,
                login=login,
                password=password,
                created_at=datetime.datetime.now().timestamp()
            )

            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            find_user = new_user

        session.close()

        return find_user

    def confirm_registered(self, user: TelegramUser) -> bool:
        session = Session(self.engine)
        find_user = select(User).where(User.telegram_id == user.id)
        find_user = session.exec(find_user).one_or_none()

        if not find_user:
            return False

        find_user.registered = True
        session.add(find_user)
        session.commit()
        session.close()

        return True


class CocoServerUtils:
    def __init__(self, config):
        self.config = config
        self.session = RequestsSession()

        if status_code := self.authorize() != 200:
            raise Exception(f"Cannot authorize to coco server: {status_code}")

    def authorize(self):
        data = {
            "username": self.config["host_username"],
            "password": self.config["host_password"]
        }

        response = self.session.post(self.config["host_url"] + self.config["api_map"]["authorize"], json=data)

        return response.status_code

    def create_user(self, user: User):
        data = {
            "username": user.login,
            "password": user.password,
            "email": "",
            "name": "Telegram User " + str(user.telegram_id),
            "isAdmin": False,
        }

        response = self.session.post(self.config["host_url"] + self.config["api_map"]["create_user"], json=data)

        return response.status_code, response.text

    def share_dataset(self, user: User):
        data = {
            "users": [user.login]
        }

        response = self.session.post(self.config["host_url"] + self.config["api_map"]["share_dataset"], json=data)

        return response.status_code, response.text


class CocoTelegram:
    def __init__(self):
        # abs_path to current file
        self.config_abs_path = os.path.join(os.path.dirname(__file__), "config.yml")

        # read config
        with open(self.config_abs_path, 'r') as config_file:
            self.config = yaml.safe_load(config_file)

        # connect args
        self.connect_args = {"check_same_thread": False}

        self.engine = create_engine(
            'sqlite:///{0}'.format(self.config["local_database_name"]),
            connect_args=self.connect_args
        )

        SQLModel.metadata.create_all(self.engine)

        # database utils
        self.database_utils = DatabaseUtils(self.engine)

        # initialize Telebot
        self.bot = TeleBot(self.config["telegram_access_token"], parse_mode="Markdown")

        # coco server utils
        self.coco_server_utils = CocoServerUtils(self.config)

        # create logger
        self.logger = telebot.logger
        self.logger.setLevel(telebot.logging.INFO)

        self.handlers()

    def handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message: Message):
            telegram_user: TelegramUser = message.from_user
            user = self.database_utils.get_user_or_create_new(message.from_user)

            response_text = "Привет, @{0}!\n".format(telegram_user.username)
            response_text += "Вот твои данные для входа в редактирование датасета:\n\n"
            response_text += "Логин: `{0}`\n".format(user.login)
            response_text += "Пароль: `{0}`\n\n".format(user.password)
            response_text += "Теперь ты можешь перейти на сайт для просмотра датасета и его редактирования 🤗"

            if user.registered is False:
                status_code, response = self.coco_server_utils.create_user(user)
                self.logger.info(f"{status_code} {response}")

                n_status_code, n_response = self.coco_server_utils.share_dataset(user)
                self.logger.info(f"{n_status_code} {n_response}")

                self.database_utils.confirm_registered(telegram_user)

            # set link to inline keyboard
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Перейти на сайт", url=self.config["host_url"])]
            ])

            return self.bot.send_message(message.chat.id, response_text, reply_markup=keyboard)

    def run(self):
        self.bot.infinity_polling(timeout=9999)
