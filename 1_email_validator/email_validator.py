
"""
Email Validator - проверка валидности email-адресов
TODO: добавить SMTP Handshake
"""

import re
import dns.resolver
from typing import List


class EmailValidator:
    """Класс для валидации email-адресов через DNS MX"""
    
    def __init__(self):
        self.dns_resolver = dns.resolver.Resolver()
        self.dns_resolver.timeout = 5
        self.dns_resolver.lifetime = 5
    
    def validate_email_format(self, email: str) -> bool:
        """Проверка формата email через regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def get_mx_records(self, domain: str) -> List[str]:
        """Получение MX-записей домена"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
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
            print(f"Ошибка при получении MX для {domain}: {e}")
            return []
    
    def validate_email(self, email: str) -> dict:
        """Базовая проверка email (без SMTP)"""
        result = {
            'email': email,
            'valid_format': False,
            'domain_exists': False,
            'mx_records': [],
            'status': ''
        }
        
        # 1. Проверка формата
        if not self.validate_email_format(email):
            result['status'] = 'некорректный формат'
            return result
        
        result['valid_format'] = True
        domain = email.split('@')[1]
        
        # 2. Проверка MX-записей
        mx_records = self.get_mx_records(domain)
        
        if not mx_records:
            result['status'] = 'MX-записи отсутствуют'
            return result
        
        result['domain_exists'] = True
        result['mx_records'] = mx_records
        result['status'] = 'домен валиден (SMTP проверка не выполнена)'
        
        return result


def main():
    """Основная функция"""
    print("="*60)
    print("📧  EMAIL VALIDATOR - v0.1 (без SMTP)")
    print("="*60)
    print()
    
    validator = EmailValidator()
    
    # Тестовые адреса
    test_emails = [
        'test@gmail.com',
        'info@google.com',
        'invalid@fake-domain.com'
    ]
    
    for email in test_emails:
        print(f"Проверяю: {email}")
        result = validator.validate_email(email)
        print(f"  Статус: {result['status']}")
        if result['mx_records']:
            print(f"  MX: {result['mx_records'][0]}")
        print()


if __name__ == '__main__':
    main()