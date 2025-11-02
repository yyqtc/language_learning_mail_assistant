from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from tool import tools
from middleware import middlewares
from custom_type import ContextSchema
from mail_server import mail_server

from email import message_from_bytes
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime

import imaplib
import time
import json
from datetime import datetime

config = json.load(open("./config.json", encoding="utf-8"))

def _initiate_agent():
    _model = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=config["DEEPSEEK_API_KEY"],
        openai_api_base=config["DEEPSEEK_API_BASE"],
        temperature=0.7
    )

    _prompt = """
        你是一位专业的、审美在线的、熟练使用html的、给各个老师转发学生疑问的助手，总是可以准确的根据邮件的主题和内容判断应该调用什么能力。
        你可以选择调用能力或是得到最终答案。
        当你认为需要调用能力时，必须按照以下JSON格式进行响应：
        {{
            "action": "能力的名称（必须是上述能力之一）",
            "action_input": {{
                "参数名": "参数值"
            }}
        }}

        如果你认为可以得出最终答案了，并按照以下JSON格式进行响应：
        {{
            "action": "Final Answer",
            "action_input": {{
                "output": "你的最终答案"
            }}
        }}

        注意！
        你只能选择调用能力或是得出最终答案。
        如果你发现没有符合你目的的能力，请尝试使用你的现有知识进行回答。
        你的响应必须符合JSON格式规范，不要添加任何多余的字符串。
    """

    # 创建 agent，使用 LangChain 1.0 的新 API
    agent = create_agent(
        model=_model,
        tools=tools,
        middleware=middlewares,
        system_prompt=_prompt,
        context_schema=ContextSchema
    )
    
    return agent

def _get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in content_disposition:
                continue
            elif content_type == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                body += part.get_payload(decode=True).decode(charset, errors="ignore")
            elif content_type == "text/html":
                continue
    else:
        charset = msg.get_content_charset() or "utf-8"
        body += msg.get_payload(decode=True).decode(charset, errors="ignore")

    return body

def main():
    agent = _initiate_agent()
    
    while True:
        mail_server.select("INBOX")

        print("开始监听邮箱...")
        try:
            status, email_ids = mail_server.search("UTF-8", "UNSEEN")
            if email_ids or len(email_ids) > 0:
                checked_email_ids = []
                for email_id in email_ids:
                    if len(email_id) == 0:
                        continue

                    decoded_email_id = email_id
                    if type(email_id) == bytes:
                        decoded_email_id = email_id.decode()

                    if " " in decoded_email_id:
                        splitted_email_ids = decoded_email_id.split(" ")
                        for id in splitted_email_ids:
                            checked_email_ids.append(id.encode())

                    else:
                        checked_email_ids.append(decoded_email_id.encode())

                for email_id in checked_email_ids:
                        
                    print(f"开始处理邮件：{email_id}")

                    status, email_data = mail_server.fetch(email_id, "(RFC822)")
                    raw_email = email_data[0][1]
                    msg = message_from_bytes(raw_email)

                    subject = decode_header(msg.get("Subject", ""))[0][0].decode("utf-8")
                    from_addr = parseaddr(msg.get("From", ""))[1]
                    email_body = _get_email_body(msg)

                    if "---原始邮件---" in email_body:
                        email_body = email_body.split("---原始邮件---")[0].strip()
                        
                    prompt = f"""
                        这封邮件的主题是：{subject}
                        这封邮件的正文是：{email_body}
                        这封邮件的邮件ID是：{email_id.decode()}
                        发送这封邮件的学生的邮箱地址是：{from_addr}

                        注意！
                        如果你认为这封邮件和各个老师没有关系，请调用能力恢复邮件未读状态，并返回“邮件未读状态恢复成功”
                        如果你认为这封邮件和某个老师有关，请一定要把老师的回复以邮件的形式发送给学生，并返回“邮件发送成功”
                        邮件必须是html格式，风格清爽，使用卡片式布局（如果有标题请务必隐藏，因为实在太丑了），一定要照顾移动端用户的体验，注意内容中不要包含任何多余的字符串!
                        注意卡片之间不要嵌套！不要嵌套！不要嵌套！不要嵌套！
                    """
                    mail_server.store(email_id, "+FLAGS", "\\Seen")
                    agent.invoke(
                        {"messages": [{"role": "user", "content": prompt}]},
                        context= {
                            "cur_email_id": email_id.decode(),
                            "sent_email_id": ""
                        }
                    )
                    time.sleep(10)
        
        except Exception as e:
            print(f"处理邮件时发生异常：{e}")

        time.sleep(300) # 每5分钟检查一次邮箱
        

if __name__ == "__main__":
    main()
