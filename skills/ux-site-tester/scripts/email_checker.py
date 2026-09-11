#!/usr/bin/env python3
"""
Email Checker for UX Site Tester
Проверяет почту через IMAP для тестирования email-рассылок.
"""

import imaplib
import ssl
import email
from email.header import decode_header
from datetime import datetime
import json
import os

# Конфигурация
IMAP_SERVER = os.getenv('TESTER_IMAP_SERVER', 'imap.mail.ru')
IMAP_PORT = 993
EMAIL = os.getenv('TESTER_EMAIL', 'Art_east@internet.ru')
PASSWORD = os.getenv('TESTER_EMAIL_PASSWORD', '')


def connect_to_mailbox():
    """Подключение к почтовому ящику."""
    ctx = ssl.create_default_context()
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ctx)
    mail.login(EMAIL, PASSWORD)
    return mail


def get_folders(mail):
    """Получение списка папок."""
    status, folders = mail.list()
    folder_list = []
    for folder in folders:
        parts = folder.decode().split(' "')
        folder_name = parts[-1].strip('"')
        folder_list.append(folder_name)
    return folder_list


def check_emails_from_sender(mail, folder='INBOX', sender=None, subject_contains=None):
    """
    Проверка писем от указанного отправителя.
    
    Args:
        mail: IMAP соединение
        folder: Папка для проверки
        sender: Email отправителя (например 'hello@safemind.pro')
        subject_contains: Фильтр по теме письма
    
    Returns:
        list: Список найденных писем с метаданными
    """
    mail.select(folder)
    
    # Формируем критерии поиска
    if sender:
        status, messages = mail.search(None, 'FROM', sender)
    else:
        status, messages = mail.search(None, 'ALL')
    
    msg_ids = messages[0].split()
    emails = []
    
    for msg_id in msg_ids:
        status, data = mail.fetch(msg_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        
        # Декодируем тему
        subject = decode_header(msg['Subject'])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode('utf-8', errors='replace')
        
        # Фильтр по теме
        if subject_contains and subject_contains.lower() not in subject.lower():
            continue
        
        # Получаем отправителя
        from_addr = msg['From']
        
        # Получаем дату
        date = msg['Date']
        
        # Проверяем вложения
        attachments = []
        has_html = False
        has_links = False
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition', ''))
                
                # Проверяем HTML
                if content_type == 'text/html':
                    has_html = True
                    body = part.get_payload(decode=True)
                    if body:
                        body_text = body.decode('utf-8', errors='replace')
                        # Проверяем наличие ссылок
                        has_links = 'href=' in body_text or 'http' in body_text
                
                # Проверяем вложения
                if 'attachment' in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'size': len(part.get_payload(decode=True) or b'')
                        })
        else:
            content_type = msg.get_content_type()
            if content_type == 'text/html':
                has_html = True
        
        emails.append({
            'id': msg_id.decode(),
            'subject': subject,
            'from': from_addr,
            'date': date,
            'has_html': has_html,
            'has_links': has_links,
            'attachments': attachments,
            'attachment_count': len(attachments)
        })
    
    return emails


def check_all_folders_for_sender(mail, sender):
    """Проверка всех папок на наличие писем от отправителя."""
    results = {}
    folders = get_folders(mail)
    
    for folder in folders:
        try:
            emails = check_emails_from_sender(mail, folder, sender)
            if emails:
                results[folder] = emails
        except Exception as e:
            print(f"Ошибка проверки папки {folder}: {e}")
    
    return results


def generate_email_report(sender, results):
    """Генерация отчёта по email."""
    report = {
        'timestamp': datetime.now().isoformat(),
        'email_account': EMAIL,
        'sender_checked': sender,
        'total_emails': 0,
        'folders': {},
        'issues': []
    }
    
    for folder, emails in results.items():
        report['total_emails'] += len(emails)
        report['folders'][folder] = {
            'count': len(emails),
            'emails': emails
        }
        
        # Проверяем проблемы
        for email_data in emails:
            if not email_data['has_html']:
                report['issues'].append({
                    'email_id': email_data['id'],
                    'issue': 'Письмо без HTML-форматирования',
                    'severity': 'warning'
                })
            
            if not email_data['has_links']:
                report['issues'].append({
                    'email_id': email_data['id'],
                    'issue': 'Письмо без ссылок',
                    'severity': 'info'
                })
    
    return report


def main():
    """Основная функция для CLI использования."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Email Checker')
    parser.add_argument('--sender', default='hello@safemind.pro', help='Email отправителя')
    parser.add_argument('--check-safemind', action='store_true', help='Проверить письма SafeMind')
    parser.add_argument('--output', '-o', help='Файл для сохранения отчёта (JSON)')
    
    args = parser.parse_args()
    
    if args.check_safemind:
        sender = 'hello@safemind.pro'
    else:
        sender = args.sender
    
    print(f"🔍 Проверка писем от: {sender}")
    print(f"📧 Почтовый ящик: {EMAIL}")
    
    try:
        mail = connect_to_mailbox()
        print("✅ Подключение к почте успешно")
        
        # Получаем список папок
        folders = get_folders(mail)
        print(f"📁 Найдено папок: {len(folders)}")
        
        # Проверяем все папки
        results = check_all_folders_for_sender(mail, sender)
        
        # Генерируем отчёт
        report = generate_email_report(sender, results)
        
        # Выводим результаты
        print(f"\n📊 Результаты:")
        print(f"Всего писем: {report['total_emails']}")
        
        for folder, data in results.items():
            print(f"\n📂 {folder}: {len(data)} писем")
            for email_data in data:
                print(f"  - {email_data['subject']}")
                print(f"    HTML: {'✅' if email_data['has_html'] else '❌'}")
                print(f"    Ссылки: {'✅' if email_data['has_links'] else '❌'}")
                print(f"    Вложения: {email_data['attachment_count']}")
        
        if report['issues']:
            print(f"\n⚠️ Найдено проблем: {len(report['issues'])}")
            for issue in report['issues']:
                print(f"  - {issue['issue']} (важность: {issue['severity']})")
        
        # Сохраняем отчёт если указан файл
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n💾 Отчёт сохранён: {args.output}")
        
        mail.logout()
        print("\n✅ Проверка завершена")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
