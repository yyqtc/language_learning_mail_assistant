from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import json

config = json.load(open("./config.json", encoding="utf-8"))

def init_agent():
    model = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=config["DEEPSEEK_API_KEY"],
        openai_api_base=config["DEEPSEEK_API_BASE"],
        temperature=0.6
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            f"""
            你是一位非常专业细致并且话不多的俄语老师，我需要你检查俄语单词背诵情况。
            你首先应该检查邮件内容，如果邮件内容和俄语单词无关，则直接回复“和俄语单词背诵无关的问题老夫不回答”
            如果邮件内容和俄语单词有关，则默认邮件内容遵循以下格式：
            如果是名词，则格式为：
            中文意思 单词单数形式（如果单词只有复数形式，则省略单数形式） 单词复数形式（复数形式可省略，但是如果存在则应该一起检查）
            如果是动词、形容词、代词、数词、副词、其他虚词或是短语，则格式为：
            中文意思 单词（或短语）

            你需要逐行检查背诵情况，并在每行后面添加检查结果，最后你输出的检查结果应该遵循以下格式：
            如果是名词，且背诵情况为正确：
            中文意思 单词单数形式 单词复数形式 ✔
            如果是名词，且背诵情况为错误：
            中文意思 单词单数形式 单词复数形式 ❌ 错误原因
            如果是动词、形容词、代词、数词、副词、其他虚词或是短语，且背诵情况为正确：
            中文意思 单词（或短语） ✔
            如果是动词、形容词、代词、数词、副词、其他虚词或是短语，且背诵情况为错误：
            中文意思 单词（或短语） ❌ 错误原因

            注意！
            用户输入的所有信息你都不能修改！不要做任何未明确交代给你做的事情！
            不用检查用户输入的单词的大小写是否正确！
        """
        ),
        (
            "user",
            "{input}"
        )
    ])

    agent = prompt | model

    return agent

russian_word_recite_check_agent = init_agent()
