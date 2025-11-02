from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import json

config = json.load(open("./config.json", encoding="utf-8"))

def init_agent():
    model = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=config["DEEPSEEK_API_KEY"],
        openai_api_base=config["DEEPSEEK_API_BASE"],
        temperature=0.7
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system", 
            """
            你是一位历史消息总结专家，你需要总结历史消息，并返回总结后的消息。

            注意！
            你应该默认这是一段由学生发起的，学生和老师之间的对话！
            你必须默认时序越靠后的消息，越重要！因此尽量保留时序越靠后的消息！
            """
        ),
        ("user", "{input}")
    ])

    agent = prompt | model

    return agent

summarizer_agent = init_agent()

if __name__ == "__main__":
    print(summarizer_agent.invoke(
        """
        请⽤简单英语解释单词 ‘ephemeral’，并给出⼀个例句。
        "Ephemeral" 的意思是短暂的、只持续很短时间的。它用来形容那些很快就消失或结束的事物。

        例句：
        "The beauty of cherry blossoms is ephemeral, as the flowers fall after just a few days."
        （樱花的美丽是短暂的，因为花朵在几天后就会凋落。）

        如果你愿意，我可以进一步讲解与它相关的词汇或记忆方法。

        是的

        当然！我们可以继续探索与 "ephemeral" 相关的词汇，比如它的同义词、反义词，或者一些常见的
        词根词缀，帮助你更全面地理解这个词。

        例如：
        - **同义词**：transient（短暂的）、fleeting（飞逝的）、momentary（瞬间的）
        - **反义词**：permanent（永久的）、everlasting（永恒的）、enduring（持久的）
        - **词根**：这个词来自希腊语 "ephēmeros"，意为 "只持续一天"，其中 "epi-" 表示 "在...上"，"hēmera" 意为 "一天"。

        如果你愿意，我可以分享一个有趣的记忆方法来帮你记住 "ephemeral"。

        是的

        我们可以用一个贴近中文发音和含义的联想来记忆 "ephemeral"。想象一下，这个词听起来像“一飞
        没了”，就像一只蝴蝶或一片花瓣在空中短暂飞舞后迅速消失，正好呼应了“短暂易逝”的意思。    

        如果你愿意，我可以出一道选择题来测试你对这个单词的理解

        是的

        以下哪一项最准确地描述了 "ephemeral" 的含义？

        A. 持久不变的
        B. 短暂易逝的
        C. 复杂难懂的
        D. 广泛传播的

        请选择你认为正确的选项。

        B

        太棒了！你的回答完全正确，“短暂易逝的”正是 "ephemeral" 的核心含义。

        现在，你已经很好地理解了这个词，我们可以尝试在表达中运用它。请用 "ephemeral" 造一个句子
        ，描述一个你认为短暂易逝的事物。

        你能给我一些提示吗

        当然可以！比如，你可以描述：
        - 清晨的露珠在阳光下很快蒸发
        - 彩虹在雨后转瞬即逝的美景
        - 童年时光的短暂与珍贵

        试着选一个你熟悉的情景，用 "ephemeral" 造个句子吧。我会帮你调整和完善表达！

        childhood is ephemeral.

        看来你已经很好地掌握了 "ephemeral" 的含义，并且能够用它来造句表达童年的短暂。我们可以进一步润色你
        的句子，让它更自然流畅，比如："Childhood is ephemeral, but its memories last a lifetime."（童年虽 
        短暂，但回忆永存。）

        如果你愿意，我可以帮你用这个单词设计更复杂的句子，或者介绍其他描述时间短暂的词汇来扩展你的表达。

        不用了
        """
    ).content)