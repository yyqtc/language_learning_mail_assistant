from langchain.agents.middleware import before_model, after_model
from langchain.agents import AgentState
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime

from custom_type import ContextSchema
from typing import Any, Dict

import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@after_model(can_jump_to=["end"])
def avoid_sending_duplicate_email(state: AgentState, runtime: Runtime[ContextSchema]) -> Dict[str, Any] | None:
    """防止重复发送邮件的中间件"""
    cur_email_id = runtime.context.get("cur_email_id", "")
    sent_email_id = runtime.context.get("sent_email_id", "")

    print(f"cur_email_id: {cur_email_id}")
    print(f"sent_email_id: {sent_email_id}")

    if len(cur_email_id) == 0:
        return {
            "jump_to": "end"
        }

    if len(sent_email_id) and sent_email_id == cur_email_id:
        return {
            "jump_to": "end"
        }

    return None

@before_model
def set_sent_email_id(state: AgentState, runtime: Runtime[ContextSchema]) -> Dict[str, Any] | None:
    
    if isinstance(state["messages"][-1], ToolMessage):
        if state["messages"][-1].name == "send_email" and state["messages"][-1].content == "0":
            runtime.context["sent_email_id"] = runtime.context["cur_email_id"]

    return None

middlewares = [
    avoid_sending_duplicate_email, 
    set_sent_email_id
]
