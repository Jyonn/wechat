import datetime
import email
import imaplib
from nntplib import decode_header

from SmartDjango import E

from Base.lines import Lines
from Service.models import ServiceData, Service, ParamDict


@E.register(id_processor=E.idp_cls_prefix())
class MailGetError:
    NOT_FOUND = E("找不到邮箱")


@Service.register
class MailGetService(Service):
    name = 'mailget'
    desc = '近期邮件收取'
    long_desc = Lines(
        '手动收取特定公用邮箱的邮件信息',
        '只支持收取五分钟内的邮件',
        '👉mailget mail-nickname')

    @staticmethod
    def fetch_emails(imap_server, username, password):
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username, password)
        mail.select("inbox")
        five_minutes_ago = (datetime.datetime.now() - datetime.timedelta(minutes=5)).strftime("%d-%b-%Y %H:%M:%S")

        status, messages = mail.search(None, f'(SINCE "{five_minutes_ago}")')

        email_ids = messages[0].split()
        emails = []

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parse the email content
                    msg = email.message_from_bytes(response_part[1])

                    # Decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    from_ = msg.get("From")
                    sender_name, sender_email = email.utils.parseaddr(from_)

                    emails.append(dict(
                        name=sender_name,
                        addr=sender_email,
                        subject=subject,
                    ))

        mail.logout()

        return emails

    @classmethod
    def run(cls, directory: 'Service', storage: ServiceData, pd: ParamDict, *args):
        if not args:
            return cls.need_help()

        nickname = args[0]
        global_storage = cls.get_global_storage()
        global_data = global_storage.jsonify()
        if nickname not in global_data:
            raise MailGetError.NOT_FOUND

        mail_data = global_data[nickname]

        emails = cls.fetch_emails(
            imap_server=mail_data['server'],
            username=mail_data['username'],
            password=mail_data['password'],
        )

        lines = []
        for index, email in enumerate(emails):
            lines.append(f'第 {index + 1} 封邮件：')
            name, addr, subject = email['name'], email['addr'], email['subject']
            lines.append(f'\t 发信人：{name} ({addr})')
            lines.append(f'\t 主题：{subject}')
            lines.append('')
        return Lines(*lines)
