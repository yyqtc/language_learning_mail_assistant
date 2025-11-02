from language_learning_agent_factory import create_language_learning_agent
from history_message_summarizer import summarizer_agent
from mail_server import mail_server as imap_mail_server
from langchain.tools import tool
from chroma import client

import json
import logging
from uuid import uuid4

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

config = json.load(open("./config.json", encoding="utf-8"))

english_learning_agent = create_language_learning_agent("英语")
english_word_learning_collection = client.get_or_create_collection("english_word_learning")

@tool
def english_word_learning(mail_address: str, input_message: str) -> str:
    """
    教学生学习英语单词的老师

    Args:
        mail_address: 用户的邮件地址
        input_message: 用户输入的消息

    Returns:
        老师根据学生输入的信息，返回的回答内容
    """
    prompt_message = input_message
    id = str(uuid4())
    history_message_wrapper = english_word_learning_collection.get(
        where={"mail_address": mail_address}
    )
    if len(history_message_wrapper["documents"]) > 0:
        id = history_message_wrapper["ids"][0]
        temp_message = history_message_wrapper["documents"][0] + "\n\n" + input_message
        if len(temp_message) > 2000:
            prompt_message = summarizer_agent.invoke(history_message_wrapper["documents"][0]).content + "\n\n" + input_message
        else:
            prompt_message = temp_message

    teacher_message = english_learning_agent.invoke(prompt_message).content

    english_word_learning_collection.upsert(
        documents=[prompt_message + "\n\n" + teacher_message],
        metadatas=[{"mail_address": mail_address}],
        ids=[id]
    )

    return teacher_message

@tool
def send_email(to: str, subject: str, content: str) -> int:
    """
    发送邮件到邮箱

    Args:
        to: 邮件接收者邮箱地址
        subject: 邮件主题
        content: 邮件内容

    Returns:
        发送成功，返回0
        发送失败，返回1
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    msg = MIMEMultipart()
    msg['From'] = config["EMAIL"]["SENDER_EMAIL"]
    msg['To'] = to 
    msg['Subject'] = subject

    msg.attach(MIMEText(content, 'html', 'utf-8'))  # 添加编码
    try:
        # 使用SSL连接而不是TLS
        with smtplib.SMTP_SSL(config["EMAIL"]["SMTP"]["SERVER"], config["EMAIL"]["SMTP"]["PORT"]) as server:
            server.login(config["EMAIL"]["SENDER_EMAIL"], config["EMAIL"]["SENDER_PASSWORD"])
            server.send_message(msg)
        
        logger.info(f"邮件发送成功：{to}")
        return 0
    except Exception as e:
        logger.info(f"邮件发送失败：{to}", e)
        return 1

@tool
def resume_email_status(email_id: str) -> str:
    """
    恢复邮件未读状态

    Args:
        email_id: 邮件ID

    Returns:
        恢复成功，返回"邮件未读状态恢复成功"
        恢复失败，返回"邮件未读状态恢复失败"
    """
    try:
        # 确保选择了 INBOX 邮箱
        imap_mail_server.select("INBOX")
        

        email_id = email_id.encode() if type(email_id) == str else email_id
        logger.info(f"恢复邮件未读状态：{email_id}")

        # 移除 \Seen 标志即可恢复未读状态
        status, response = imap_mail_server.store(email_id, "-FLAGS", "\\Seen")
        
        if status == "OK":
            logger.info(f"邮件未读状态恢复成功：{email_id}")
            return "邮件未读状态恢复成功"
        else:
            logger.error(f"邮件未读状态恢复失败：{response}")
            return f"邮件未读状态恢复失败：{response}"
            
    except Exception as e:
        logger.error(f"恢复邮件未读状态时发生异常：{e}")
        return f"邮件未读状态恢复失败：{e}"

tools = [
    send_email,
    english_word_learning,
    resume_email_status
]


if __name__ == "__main__":
    # english_word_learning_collection.upsert(
    #     documents=["hello world"],
    #     metadatas={"mail_address": "15108264418@163.com"},
    #     ids=[str(uuid4())]
    # )

    result = english_word_learning_collection.get(
        where={"mail_address": "15108264419@163.com"}
    )
    print(result["documents"])