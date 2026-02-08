
"""
Email Validator - проверка валидности email-адресов
Проверяет: MX-записи домена + SMTP Handshake (существование пользователя)
"""

import re
import smtplib
import dns.resolver
from typing import List, Tuple
from colorama import Fore, Style, init

# Инициализация colorama для цветного вывода
init(autoreset=True)


class EmailValidator:
    """Класс для валидации email-адресов через MX и SMTP проверку"""
    
    def __init__(self, timeout: int = 10):
        """
        Args:
            timeout: Таймаут для SMTP-соединения (секунды)
        """
        self.timeout = timeout
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = 5
        self.dns_resolver.lifetime = 5
    
    def validate_email_format(self, email: str) -> bool:
        """Проверка формата email через regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def get_mx_records(self, domain: str) -> List[str]:
        """
        Получение MX-записей домена
        
        Returns:
            Список MX-серверов, отсортированных по приоритету
        """
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            # Сортируем по приоритету (preference)
            mx_hosts = sorted(
                [(r.preference, str(r.exchange).rstrip('.')) for r in mx_records],
                key=lambda x: x[0]
            )
            return [host for _, host in mx_hosts]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            return []
        except dns.resolver.NoAnswer:
            return []
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Ошибка при получении MX для {domain}: {e}")
            return []
    
    def smtp_verify(self, email: str, mx_host: str) -> Tuple[bool, str]:
        """
        SMTP Handshake - проверка существования email без отправки письма
        
        Returns:
            (exists, message): exists=True если адрес существует
        """
        try:
            # Подключаемся к SMTP серверу
            server = smtplib.SMTP(timeout=self.timeout)
            server.set_debuglevel(0)
            server.connect(mx_host)
            server.helo('polza-validator.com')  # HELO - представляемся
            server.mail('validator@polza-validator.com')  # MAIL FROM
            
            # RCPT TO - проверяем существование получателя
            code, message = server.rcpt(email)
            server.quit()
            
            # Коды 250 и 251 означают успех
            if code == 250 or code == 251:
                return True, "адрес существует"
            else:
                return False, f"адрес не найден (код {code})"
                
        except smtplib.SMTPServerDisconnected:
            return False, "сервер разорвал соединение"
        except smtplib.SMTPConnectError:
            return False, "не удалось подключиться к серверу"
        except Exception as e:
            return False, f"ошибка SMTP: {str(e)[:50]}"
    
    def validate_email(self, email: str) -> dict:
        """
        Полная проверка email-адреса
        
        Returns:
            dict с результатами проверки
        """
        result = {
            'email': email,
            'valid_format': False,
            'domain_exists': False,
            'mx_records': [],
            'smtp_check': False,
            'status': '',
            'details': ''
        }
        
        # 1. Проверка формата
        if not self.validate_email_format(email):
            result['status'] = 'некорректный формат'
            result['details'] = 'email не соответствует стандартному формату'
            return result
        
        result['valid_format'] = True
        domain = email.split('@')[1]
        
        # 2. Проверка MX-записей
        mx_records = self.get_mx_records(domain)
        
        if not mx_records:
            result['status'] = 'MX-записи отсутствуют или некорректны'
            result['details'] = f'домен {domain} не имеет MX-записей'
            return result
        
        result['domain_exists'] = True
        result['mx_records'] = mx_records
        
        # 3. SMTP Handshake - проверяем с первым MX-сервером
        primary_mx = mx_records[0]
        smtp_valid, smtp_msg = self.smtp_verify(email, primary_mx)
        result['smtp_check'] = smtp_valid
        
        if smtp_valid:
            result['status'] = 'домен валиден'
            result['details'] = f'адрес подтверждён через {primary_mx}'
        else:
            result['status'] = 'домен валиден, но адрес не найден'
            result['details'] = f'{smtp_msg} (проверено через {primary_mx})'
        
        return result


def print_result(result: dict):
    """Красивый вывод результата проверки"""
    email = result['email']
    status = result['status']
    
    # Выбираем цвет в зависимости от статуса
    if 'валиден' in status and result['smtp_check']:
        color = Fore.GREEN
        icon = '✅'
    elif 'валиден' in status:
        color = Fore.YELLOW
        icon = '⚠️ '
    else:
        color = Fore.RED
        icon = '❌'
    
    print(f"\n{color}{icon} {email}")
    print(f"{color}   Статус: {status}")
    print(f"{color}   Детали: {result['details']}")
    
    if result['mx_records']:
        print(f"{Fore.CYAN}   MX-серверы: {', '.join(result['mx_records'][:3])}")


def main():
    """Основная функция - запуск валидатора"""
    
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}📧  EMAIL VALIDATOR - Polza Outreach Engine")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    # Читаем список email из файла
    try:
        with open('test_emails.txt', 'r', encoding='utf-8') as f:
            emails = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}❌ Файл test_emails.txt не найден!")
        print(f"{Fore.YELLOW}Создайте файл test_emails.txt с email-адресами (по одному на строку)")
        return
    
    if not emails:
        print(f"{Fore.YELLOW}⚠️  Файл test_emails.txt пуст!")
        return
    
    print(f"{Fore.WHITE}Проверяю {len(emails)} адресов...\n")
    
    # Создаём валидатор
    validator = EmailValidator(timeout=10)
    
    # Проверяем каждый email
    results = []
    for email in emails:
        print(f"{Fore.WHITE}🔍 Проверяю: {email}...", end='')
        result = validator.validate_email(email)
        results.append(result)
        print(f"\r{' '*80}\r", end='')  # Очищаем строку
        print_result(result)
    
    # Итоговая статистика
    print(f"\n{Fore.CYAN}{'='*70}")
    valid_count = sum(1 for r in results if r['smtp_check'])
    mx_valid_count = sum(1 for r in results if r['domain_exists'])
    
    print(f"{Fore.GREEN}✅ Полностью валидных: {valid_count}/{len(emails)}")
    print(f"{Fore.YELLOW}⚠️  С валидным доменом: {mx_valid_count}/{len(emails)}")
    print(f"{Fore.RED}❌ Невалидных: {len(emails) - mx_valid_count}/{len(emails)}")
    print(f"{Fore.CYAN}{'='*70}\n")


if __name__ == '__main__':
    main()