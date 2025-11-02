import imaplib
import json

config = json.load(open("./config.json", encoding="utf-8"))

def init_imap_server():
    imaplib.Commands["ID"]=("AUTH")
    mail_server = imaplib.IMAP4_SSL(config["EMAIL"]["IMAP"]["SERVER"], config["EMAIL"]["IMAP"]["PORT"])
    mail_server.login(config["EMAIL"]["SENDER_EMAIL"], config["EMAIL"]["SENDER_PASSWORD"])

    # RFC 2971 导致必须进行二次验证
    args = ("name",config["EMAIL"]["SENDER_NAME"],"contact",config["EMAIL"]["SENDER_EMAIL"],"version","1.0.0","vendor","myclient")
    typ, dat = mail_server._simple_command('ID', '("' + '" "'.join(args) + '")')

    return mail_server

mail_server = init_imap_server()
