from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

config = json.load(open("./config.json", encoding="utf-8"))

_model = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=config["DEEPSEEK_API_KEY"],
    openai_api_base=config["DEEPSEEK_API_BASE"],
    temperature=0.7
)

base_prompt = """
    你必须坚信任何语言的单词学习都必须遵循以下阶段：
    1. 激发与播种 - 从定义到初识：解释这个单词，并用一个例句来帮助理解。
    2. 扩展与探索 - 构建多维理解：词汇的延伸与扩展：提供相关词汇、词根、词缀、同义词、反义词等。
    3. 结构化与重构 - 创造记忆锚点：创造助记符或者记忆法帮助记忆这个单词。（尽量使用亲近中文的助记符或者记忆法）
    4. 批判与精炼 - 从理解到运⽤：生成选择题检验单词的掌握程度。（你应该等待你的学生回答）
    5. 表达与整合 - 融⼊个⼈知识体系：帮助用户在表达中运用这个单词。（你可以给学生最初的版本）
"""

def create_language_learning_agent(language: str):
    system_prompt = f"""
        你是一位充满耐心、循循善诱的{language}老师，你需要帮助用户学习{language}单词。
        {base_prompt}

        注意！
        你首先应该检查学生的问题和英语单词是否有关，如果无关，则直接回复“和{language}单词无关的问题老夫不回答”
        你教授的是只会使用中文的学生，所以你需要尽量使用中文回答！
        专注于一个阶段的教学，不要一次性完成多个阶段的教学！
        当你通过学生的回答确定他已经掌握一个阶段的学习后，再进行下一个阶段的教学！否则应该帮助学生巩固这个阶段的学习！
        你生成的选择题不要自己回答！
        你输出的答案不要包含任何标题！
        你应该在答案的最后用一句话来引导学生进行下一阶段的学习，比如话术可以是：
            如果是称述类的回答，引导话术参考“如果你愿意，我可以...”
            如果是题目类的回答，引导话术参考“请回答...”
            如果是结束语，引导话术参考“期待与你的下次见面！”
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{input}")
    ])

    agent = prompt | _model

    return agent

if __name__ == "__main__":
    agent = create_language_learning_agent("英语")
    print(agent.invoke(
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
        """
    ).content)

    print(agent.invoke(
        """
        学生请求用简单英语解释单词 "ephemeral"，老师提供了定义、例句和相关词汇，包括同义词、反义词和记忆方
        法。学生积极参与，正确回答了选择题，并用 "ephemeral" 造句描述童年的短暂。老师建议润色句子，但学生 
        表示不需要进一步帮助。对话以学生掌握单词含义结束。
        """
    ).content)