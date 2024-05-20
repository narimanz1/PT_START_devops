import logging
import re
import paramiko
import os
import psycopg2
from psycopg2 import Error


from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('TOKEN')

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO, encoding="utf-8"
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')


def helpCommand(update: Update, context):
    update.message.reply_text('Доступные команды: \n1) /find_phone_number\n2) /find_email\n3)/verify_password\n4) /get_release\n5) /get_uname\n6) /get_uptime\n7) /get_df\n8) /get_free \n9) /get_mpstat \n10) /get_w\n11) /get_auths\n12) /get_critical\n13) /get_ps \n14) /get_ss\n15) /get_apt_list\n16) /get_services\n17)/get_emails\n18)/get_phone_numbers\n19)/get_repl_logs')



#==========ТЕЛЕФОННЫЕ НОМЕРА============
# Команда поиска телефонных номеров
def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'
# Поиск телефонных номеров
def findPhoneNumbers (update: Update, context):
    user_input = update.message.text 
    phoneNumRegex = re.compile(r'(?:(?:\+7|8)[ -]?)?\(?(\d{3})\)?[ -]?(\d{3})[ -]?(\d{2})[ -]?(\d{2})') 
    phoneNumberList = phoneNumRegex.findall(user_input)
    if not phoneNumberList:
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END
    phoneNumbers = ''
    phoneNumbersList = []
    for i, phoneNumber in enumerate(phoneNumberList):
        formatted_number = f'8 ({phoneNumber[0]}) {phoneNumber[1]}-{phoneNumber[2]}-{phoneNumber[3]}'
        phoneNumbers += f'{i+1}. {formatted_number}\n'
        phoneNumbersList.append(formatted_number)
    update.message.reply_text(phoneNumbers)
    context.user_data['numbers_to_save'] = phoneNumbersList
    update.message.reply_text('Хотите записать найденные номера в базу данных? (да/нет)', reply_markup=ForceReply())
    return 'confirm_save'
# Подтверждение сохранения
def confirmSaveNumbers(update: Update, context):
    reply_text = update.message.text.lower().strip()
    if reply_text == 'да':
        success = save_numbers_to_db(context.user_data['numbers_to_save'])
        if success:
            update.message.reply_text('Номера телефонов успешно записаны в базу данных.')
        else:
            update.message.reply_text('Произошла ошибка при записи номеров телефона в базу данных.')
    elif reply_text == 'нет':
        update.message.reply_text('Запись номеров телефона в базу данных отменена.')
    else:
        update.message.reply_text('Пожалуйста, ответьте "да" или "нет".')

    return ConversationHandler.END
# Сохранение номеров телефона в базу данных
def save_numbers_to_db(numbers):
    load_dotenv()
    connection = None
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                    password=os.getenv("DB_PASSWORD"),
                                    host=os.getenv("DB_HOST"),
                                    port=os.getenv("DB_PORT"), 
                                    database=os.getenv("DB_DATABASE"))
        cursor = connection.cursor()
        for number in numbers:
            cursor.execute("INSERT INTO phone_table (phone_number) VALUES (%s)", (number,))
        connection.commit()
        return True
    except (Exception, psycopg2.Error) as error:
        print("Ошибка при записи в базу данных:", error)
        return False
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
# Получение телефонных номеров из базы данных
def get_phone_numbers(update: Update, context):
    load_dotenv()
    connection = None
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                    password=os.getenv("DB_PASSWORD"),
                                    host=os.getenv("DB_HOST"),
                                    port=os.getenv("DB_PORT"), 
                                    database=os.getenv("DB_DATABASE"))
        cursor = connection.cursor()
        cursor.execute("SELECT phone_number FROM phone_table;")
        data = cursor.fetchall()
        phone_list  = "\n".join([row[0] for row in data]) 
        message = "Список номеров телефонов:\n" + phone_list 
        update.message.reply_text(message)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()


#==========ЭЛЕКТРОННАЯ ПОЧТА============
# Команда поиска адресов электронной почты
def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска адресов электронной почты: ')
    return 'find_email'
# Поиск адресов электронной почты
def findEmails (update: Update, context):
    user_input = update.message.text
    emailRegex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b') 
    emailList = emailRegex.findall(user_input) 
    if not emailList:
        update.message.reply_text('Адреса электронной почты не найдены')
        return ConversationHandler.END
    emails = ''
    for i in range(len(emailList)):
        emails += f'{i+1}. {emailList[i]}\n'
    update.message.reply_text(emails)
    context.user_data['emails_to_save'] = emailList
    update.message.reply_text('Хотите записать найденные адреса в базу данных? (да/нет)', reply_markup=ForceReply())
    return 'confirm_save'
# Подтверждение сохранения
def confirmSaveEmails(update: Update, context):
    reply_text = update.message.text.lower().strip()
    if reply_text == 'да':
        success = save_emails_to_db(context.user_data['emails_to_save'])
        if success:
            update.message.reply_text('Адреса электронной почты успешно записаны в базу данных.')
        else:
            update.message.reply_text('Произошла ошибка при записи адресов электронной почты в базу данных.')
    elif reply_text == 'нет':
        update.message.reply_text('Запись адресов электронной почты в базу данных отменена.')
    else:
        update.message.reply_text('Пожалуйста, ответьте "да" или "нет".')

    return ConversationHandler.END
# Сохранение адресов электронной почты в базу данных
def save_emails_to_db(emails):
    load_dotenv()
    connection = None
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                    password=os.getenv("DB_PASSWORD"),
                                    host=os.getenv("DB_HOST"),
                                    port=os.getenv("DB_PORT"), 
                                    database=os.getenv("DB_DATABASE"))
        cursor = connection.cursor()
        for email in emails:
            cursor.execute("INSERT INTO email_table (email) VALUES (%s)", (email,))
        connection.commit()
        return True
    except (Exception, psycopg2.Error) as error:
        print("Ошибка при записи в базу данных:", error)
        return False
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
# Получение списка адресов электронной почты из базы данных
def get_emails(update: Update, context):
    load_dotenv()
    connection = None
    try:
        connection = psycopg2.connect(user=os.getenv('DB_USER'),
                                    password=os.getenv("DB_PASSWORD"),
                                    host=os.getenv("DB_HOST"),
                                    port=os.getenv("DB_PORT"), 
                                    database=os.getenv("DB_DATABASE"))
        cursor = connection.cursor()
        cursor.execute("SELECT email FROM email_table;")
        data = cursor.fetchall()
        email_list = "\n".join([row[0] for row in data]) 
        message = "Список email-адресов:\n" + email_list
        update.message.reply_text(message)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()


#==========Проверка сложности пароля=============
def verifyPassCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки сложности: ')
    return 'verify_password'
def verifyPass (update: Update, context):
    user_input = update.message.text
    verPassRegex = re.compile(r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()]).{8,}') 
    verPassList = verPassRegex.findall(user_input) 
    
    if not verPassList:
        update.message.reply_text('Пароль простой')
        return ConversationHandler.END #В любом случае заканчивается диалог, даже если пароль простой
    
    update.message.reply_text('Пароль сложный')
    return ConversationHandler.END
#==========Мониторинг Linux системы===================
def monitorLinux (update: Update, context): 
    load_dotenv()

    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASSWORD')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    message_text = update.message.text
    commands = message_text.split()
    package = ""
    if len(commands) < 2:
        command = commands[0][1::]
    else:
        command = commands[0][1::]
        package = commands[1]
    match(command):
        case 'get_release':
            exec_command = "lsb_release -a"
        case 'get_uname':
            exec_command = "uname -a"
        case 'get_uptime':
            exec_command = "uptime"
        case 'get_df':
            exec_command = "df -h"
        case 'get_free':
            exec_command = "free -h"
        case 'get_mpstat':
            exec_command = "mpstat"
        case 'get_w':
            exec_command = "w"
        case 'get_auths':
            exec_command = "last -n 10"
        case 'get_repl_logs':
            exec_command = 'cat /var/log/postgresql/* | grep replic | tail -n 25'
        case 'get_critical':
            exec_command = 'tail -n 5 /var/log/syslog | grep "CRITICAL"'
        case 'get_ps':
            exec_command = 'ps aux | head -n 10 && echo "...First 10 ps"...'
        case 'get_ss':
            exec_command = 'ss -tuln'
        case 'get_apt_list':
            if len(package) < 2:
                exec_command = 'dpkg-query -W | head -n 50 && echo "...First 50 apt"...'
            else:
                exec_command = "dpkg-query -s " + package
        case 'get_services':
            exec_command = 'systemctl list-units --type=service | head -n 30 && echo "...First 30 services"...'    
        case _:
            update.message.reply_text("Неверная команда!")
    stdin, stdout, stderr = client.exec_command(exec_command)
    data = stdout.read() + stderr.read()
    output = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    if exec_command == f'cat /var/log/postgresql/postgresql-14-main.log | grep replic | tail -n 25' and 'repl' in output.lower():
        logs = output.split('\n')
        log_out = 'Repl logs:\n'
        for log in logs:
            if 'repl' in log:
                log_out += log + '\n'
        if len(log_out) <= 12:
            log_out = 'No logs'
        output = log_out

            	
    update.message.reply_text(output)
    client.close

# Эхо
def echo(update: Update, context):
    update.message.reply_text(update.message.text)
# Вывод логов о репликации
def get_replication_logs(update: Update, context):
    load_dotenv()

    host = os.getenv('RM_HOST')
    port = os.getenv('RM_PORT')
    username = os.getenv('RM_USER')
    password = os.getenv('RM_PASS')
    host_db = os.getenv('DB_HOST')

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, username=username, password=password, port=port)
    #command = 'grep -E \"repl_user|database\" /var/log/postgresql/postgresql-15-main.log | tail -n 25'
    command = 'cat /var/log/postgresql/postgresql-14-main.log | grep replica | tail -n 25'
    stdin, stdout, stderr = client.exec_command(command)
    data = stdout.read() + stderr.read()
    update.message.reply_text(str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1])
    update.message.reply_text(host_db)
    client.close
    

 # Получение списка номеров телефона из базы данных   

def main():
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога
    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
            'confirm_save': [MessageHandler(Filters.text & ~Filters.command, confirmSaveNumbers)],
        },
        fallbacks=[]
    )
    
    convHandlerFindEmails = ConversationHandler(
        entry_points=[CommandHandler('find_email', findEmailsCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            'confirm_save': [MessageHandler(Filters.text & ~Filters.command, confirmSaveEmails)],
        },
        fallbacks=[],
    )
    convHandlerverifyPass = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPassCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verifyPass)],
        },
        fallbacks=[]
    )
		
	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(CommandHandler(['get_release', 'get_uname', 'get_uptime','get_df',
                                   'get_free', 'get_mpstat','get_w', 'get_auths', 'get_critical', 
                                   'get_ps','get_ss','get_repl_logs', 'get_services',], monitorLinux))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(CommandHandler("get_apt_list", monitorLinux, pass_args=True))
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerverifyPass)
    #dp.add_handler(CommandHandler("get_repl_logs", get_replication_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
	# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
		
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
