import imaplib
import json
import time
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

config = json.load(open("./config.json", encoding="utf-8"))

class IMAPServerWrapper:
    """带自动重连功能的 IMAP 服务器包装类"""
    
    def __init__(self):
        self._server = self._init_imap_server()
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._reconnect_delay = 5  # 初始重连延迟（秒）
        
    def _init_imap_server(self, mailbox='INBOX'):
        """初始化 IMAP 服务器连接"""
        try:
            imaplib.Commands["ID"] = ("AUTH")
            mail_server = imaplib.IMAP4_SSL(
                config["EMAIL"]["IMAP"]["SERVER"], 
                config["EMAIL"]["IMAP"]["PORT"]
            )
            mail_server.login(
                config["EMAIL"]["SENDER_EMAIL"], 
                config["EMAIL"]["SENDER_PASSWORD"]
            )

            # RFC 2971 导致必须进行二次验证
            args = (
                "name", config["EMAIL"]["SENDER_NAME"],
                "contact", config["EMAIL"]["SENDER_EMAIL"],
                "version", "1.0.0",
                "vendor", "myclient"
            )
            typ, dat = mail_server._simple_command('ID', '("' + '" "'.join(args) + '")')
            
            self._reconnect_attempts = 0  # 重置重连计数
            logger.info("IMAP 服务器连接成功")

            mail_server.select(mailbox)

            return mail_server
        except Exception as e:
            logger.error(f"初始化 IMAP 服务器失败: {e}")
            raise
    
    def _ensure_connected(self):
        """确保连接有效，如果断开则重连"""
        if self._server is None:
            self._server = self._init_imap_server()
            return
        
        try:
            # 尝试执行一个简单的命令来检查连接是否有效
            self._server.noop()
        except (imaplib.IMAP4.abort, imaplib.IMAP4.error, AttributeError, OSError, EOFError) as e:
            logger.warning(f"检测到连接断开: {e}，尝试重连...")
            self._reconnect()
    
    def _reconnect(self):
        """重新连接 IMAP 服务器"""
        self._reconnect_attempts += 1
        
        if self._reconnect_attempts > self._max_reconnect_attempts:
            logger.error(f"重连次数超过最大限制 ({self._max_reconnect_attempts})，等待更长时间...")
            time.sleep(60)  # 等待 1 分钟后重试
            self._reconnect_attempts = 0
        
        try:
            # 关闭旧连接（如果存在）
            if self._server is not None:
                logger.info("关闭旧连接")
                try:
                    self._server.close()
                    self._server.logout()
                except:
                    pass
            
            # 等待后重连
            wait_time = min(self._reconnect_delay * self._reconnect_attempts, 30)
            logger.info(f"等待 {wait_time} 秒后重连...")
            time.sleep(wait_time)
            
            self._server = self._init_imap_server()
            logger.info("重连成功")
        except Exception as e:
            logger.error(f"重连失败: {e}")
            raise
    
    def _handle_operation(self, operation_name, operation_func, *args, **kwargs):
        """执行操作，如果失败则重连并重试"""
        max_retries = 2
        for attempt in range(max_retries):
            try:
                self._ensure_connected()
                return operation_func(*args, **kwargs)
            except (imaplib.IMAP4.abort, imaplib.IMAP4.error, AttributeError, OSError, EOFError) as e:
                logger.warning(f"{operation_name} 操作失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    try:
                        self._server = None  # 标记连接无效
                        self._reconnect()
                    except Exception as reconnect_error:
                        logger.error(f"重连过程中出错: {reconnect_error}")
                        if attempt == max_retries - 1:
                            raise
                else:
                    raise
    
    def search(self, charset, *criteria):
        """搜索邮件"""
        def _search():
            return self._server.search(charset, *criteria)
        return self._handle_operation("search", _search)
    
    def fetch(self, message_set, message_parts):
        """获取邮件"""
        def _fetch():
            return self._server.fetch(message_set, message_parts)
        return self._handle_operation("fetch", _fetch)
    
    def store(self, message_set, command, flags):
        """存储邮件标志"""
        def _store():
            return self._server.store(message_set, command, flags)
        return self._handle_operation("store", _store)
    
    def noop(self):
        """NOOP 命令，用于保持连接"""
        def _noop():
            return self._server.noop()
        return self._handle_operation("noop", _noop)

# 创建全局邮件服务器实例
mail_server = IMAPServerWrapper()