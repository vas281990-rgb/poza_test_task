
"""
Telegram Sender - отправка текста из файла в Telegram-чат
Использует Telegram Bot API
"""

import asyncio
import os
from pathlib import Path
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Инициализация
init(autoreset=True)
load_dotenv()


class TelegramSender:
    """Класс для отправки сообщений в Telegram через бота"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Args:
            bot_token: Токен Telegram-бота (от @BotFather)
            chat_id: ID чата для отправки (можно получить от @userinfobot)
        """
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
    
    async def send_message(self, text: str) -> bool:
        """
        Отправка текстового сообщения в чат
        
        Args:
            text: Текст сообщения для отправки
            
        Returns:
            True если отправлено успешно
        """
        try:
            # Отправляем сообщение
            message = await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='Markdown'  # Поддержка Markdown форматирования
            )
            
            print(f"{Fore.GREEN}✅ Сообщение отправлено успешно!")
            print(f"{Fore.CYAN}   Message ID: {message.message_id}")
            print(f"{Fore.CYAN}   Chat ID: {self.chat_id}")
            print(f"{Fore.CYAN}   Длина текста: {len(text)} символов")
            return True
            
        except TelegramError as e:
            print(f"{Fore.RED}❌ Ошибка при отправке: {e}")
            return False
        except Exception as e:
            print(f"{Fore.RED}❌ Неожиданная ошибка: {e}")
            return False
    
    async def send_from_file(self, file_path: str) -> bool:
        """
        Чтение текста из файла и отправка в Telegram
        
        Args:
            file_path: Путь к текстовому файлу
            
        Returns:
            True если отправлено успешно
        """
        try:
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            
            if not text:
                print(f"{Fore.YELLOW}⚠️  Файл {file_path} пуст!")
                return False
            
            print(f"{Fore.WHITE}📄 Прочитан файл: {file_path}")
            print(f"{Fore.WHITE}📝 Длина текста: {len(text)} символов")
            print(f"{Fore.WHITE}🚀 Отправляю в Telegram...\n")
            
            # Отправляем
            return await self.send_message(text)
            
        except FileNotFoundError:
            print(f"{Fore.RED}❌ Файл {file_path} не найден!")
            return False
        except UnicodeDecodeError:
            print(f"{Fore.RED}❌ Ошибка чтения файла. Проверьте кодировку (должна быть UTF-8)")
            return False
        except Exception as e:
            print(f"{Fore.RED}❌ Ошибка: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Проверка подключения к боту"""
        try:
            bot_info = await self.bot.get_me()
            print(f"{Fore.GREEN}✅ Подключение к боту успешно!")
            print(f"{Fore.CYAN}   Bot username: @{bot_info.username}")
            print(f"{Fore.CYAN}   Bot name: {bot_info.first_name}")
            return True
        except TelegramError as e:
            print(f"{Fore.RED}❌ Ошибка подключения к боту: {e}")
            print(f"{Fore.YELLOW}💡 Проверьте правильность токена в .env файле")
            return False


async def main():
    """Основная функция"""
    
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}📱 TELEGRAM SENDER - Polza Outreach Engine")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    # Читаем настройки из .env
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    # Проверяем наличие настроек
    if not bot_token or not chat_id:
        print(f"{Fore.RED}❌ Ошибка: не найдены настройки в .env файле!\n")
        print(f"{Fore.YELLOW}📋 Инструкция:")
        print(f"{Fore.WHITE}   1. Скопируй .env.example в .env:")
        print(f"{Fore.CYAN}      cp .env.example .env")
        print(f"{Fore.WHITE}   2. Открой .env и заполни:")
        print(f"{Fore.CYAN}      TELEGRAM_BOT_TOKEN=твой_токен_от_BotFather")
        print(f"{Fore.CYAN}      TELEGRAM_CHAT_ID=твой_chat_id")
        print(f"{Fore.WHITE}   3. Запусти скрипт снова\n")
        return
    
    # Создаём отправителя
    sender = TelegramSender(bot_token=bot_token, chat_id=chat_id)
    
    # Тестируем подключение
    print(f"{Fore.WHITE}🔍 Проверяю подключение к боту...")
    if not await sender.test_connection():
        return
    
    print()
    
    # Отправляем сообщение из файла
    message_file = 'message.txt'
    
    if not Path(message_file).exists():
        print(f"{Fore.YELLOW}⚠️  Файл {message_file} не найден!")
        print(f"{Fore.WHITE}📝 Создаю файл с примером текста...")
        
        # Создаём файл с примером
        with open(message_file, 'w', encoding='utf-8') as f:
            f.write("🚀 Тестовое сообщение от Polza Outreach Engine\n\n")
            f.write("Этот текст был отправлен через Telegram Bot API.\n")
            f.write("Бот готов к работе! ✅")
        
        print(f"{Fore.GREEN}✅ Файл создан!\n")
    
    # Отправляем
    success = await sender.send_from_file(message_file)
    
    if success:
        print(f"\n{Fore.GREEN}{'='*70}")
        print(f"{Fore.GREEN}🎉 Всё готово! Сообщение доставлено.")
        print(f"{Fore.GREEN}{'='*70}\n")
    else:
        print(f"\n{Fore.RED}{'='*70}")
        print(f"{Fore.RED}❌ Не удалось отправить сообщение")
        print(f"{Fore.RED}{'='*70}\n")


if __name__ == '__main__':
    # Запускаем асинхронную функцию
    asyncio.run(main())