# Language Learning Mail Assistant

一个基于 LangChain 和 LangGraph 的智能语言学习邮件助手系统，通过邮件与学生进行多语言学习交互，支持英语单词学习和俄语单词背诵检查。

## 功能特性

### 🎓 智能英语单词教学
- **分阶段教学体系**：采用5阶段渐进式教学方法
  1. 激发与播种 - 解释单词并提供例句
  2. 扩展与探索 - 提供相关词汇、词根、词缀、同义词、反义词
  3. 结构化与重构 - 创造助记符或记忆法（贴近中文）
  4. 批判与精炼 - 生成选择题检验掌握程度
  5. 表达与整合 - 帮助学生在表达中运用单词

- **对话历史管理**：使用 ChromaDB 持久化存储每个学生的学习历史，按邮箱地址区分不同学生
- **智能摘要**：当对话历史（包含新输入消息）超过 2000 字符时自动进行摘要，保留时序靠后的重要信息，避免上下文超限

### 📖 俄语单词背诵检查
- **智能检查系统**：专业细致的俄语老师，逐行检查学生单词背诵情况
- **多词性支持**：
  - 名词：支持单数形式和复数形式检查
  - 动词、形容词、代词、数词、副词、其他虚词或短语
- **格式识别**：自动识别学生输入的单词格式，提供准确的检查反馈
- **错误提示**：对于错误背诵，提供详细的错误原因说明

### 📧 邮件自动处理
- **自动监听**：定时检查邮箱中的未读邮件（每5分钟检查一次）
- **智能路由**：根据邮件内容自动判断是否需要处理，如果不需要处理，会将邮件恢复成未读状态
- **防重复发送**：通过中间件机制防止对同一封邮件重复发送回复
- **自动重连**：IMAP 连接断开时自动重连，确保服务稳定性
- **HTML 邮件**：生成美观的 HTML 格式回复，采用卡片式布局，支持移动端优化
- **错误处理**：完善的异常处理机制，自动处理连接异常和邮件处理错误

## 技术栈

- **LangChain 1.0** - 智能体框架
- **LangGraph** - 工作流编排
- **ChromaDB** - 向量数据库，用于存储对话历史
- **DeepSeek Chat** - 大语言模型
- **IMAP/SMTP** - 邮件协议支持

## 项目结构

```
language_learning_mail_assistant/
├── main.py                          # 主程序入口，邮件监听和处理
├── tool.py                          # 工具定义（邮件发送、单词学习、状态恢复）
├── middleware.py                    # 中间件（防重复发送邮件）
├── language_learning_agent_factory.py  # 英语单词学习智能体工厂
├── russian_word_recite_check_agent.py  # 俄语单词背诵检查智能体
├── history_message_summarizer.py    # 历史消息摘要器
├── mail_server.py                   # IMAP 邮件服务器初始化
├── chroma.py                        # ChromaDB 客户端初始化
├── custom_type.py                   # 自定义类型定义
├── config.json                      # 配置文件（需自行创建，不提交到版本库）
├── config.default.json              # 配置文件模板
├── requirements.txt                 # Python 依赖
└── db/                              # ChromaDB 数据存储目录
```

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/yyqtc/language_learning_mail_assistant.git
cd language_learning_mail_assistant
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置信息

复制配置文件模板并填写相关信息：

```bash
cp config.default.json config.json
```

编辑 `config.json`，填写以下配置：

```json
{
    "EMAIL": {
        "SENDER_NAME": "your-sender-name",
        "SENDER_EMAIL": "your-sender-email",
        "SENDER_PASSWORD": "your-sender-password",
        "SMTP": {
            "SERVER": "smtp.163.com",
            "PORT": 465
        },
        "IMAP": {
            "SERVER": "imap.163.com",
            "PORT": 993
        }
    },
    "DEEPSEEK_API_KEY": "your-deepseek-api-key",
    "DEEPSEEK_API_BASE": "https://api.deepseek.com",
    "CHROMA_DB_PATH": "./db"
}
```

**配置说明：**
- `EMAIL`: 邮件服务器配置（需使用 163 邮箱）
  - `SENDER_NAME`: 发送者名称（用于 RFC 2971 IMAP ID 命令，必需）
  - `SENDER_EMAIL`: 发送者邮箱地址
  - `SENDER_PASSWORD`: 邮箱密码或授权码
  - `SMTP`: SMTP 服务器配置（用于发送邮件）
  - `IMAP`: IMAP 服务器配置（用于接收邮件）
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥
- `DEEPSEEK_API_BASE`: DeepSeek API 基础地址
- `CHROMA_DB_PATH`: ChromaDB 数据存储路径

## 使用方法

### 启动程序

```bash
python main.py
```

程序启动后会：
1. 初始化并连接到 IMAP 邮件服务器（使用 RFC 2971 ID 命令进行二次验证）
2. 持续监听未读邮件，每 5 分钟检查一次（防止对 IMAP 服务器造成过重负担）
3. 自动处理学生发送的邮件
4. 调用相应的学习智能体进行回复
5. 处理完每封邮件后等待 10 秒，避免处理过快
6. 自动处理连接异常，支持断开重连机制

### 工作流程

1. **邮件接收**：程序监听邮箱，发现未读邮件
2. **内容解析**：提取邮件主题、正文、发件人信息
3. **智能路由**：主智能体判断邮件类型
   - 如果与所有老师无关：恢复邮件未读状态
   - 如果与学习相关：根据内容自动选择相应工具处理
     - 英语单词学习请求 → `english_word_learning`
     - 俄语单词背诵检查 → `russian_word_recite_check`
4. **学习交互**：调用相应的学习工具，加载历史对话（如适用），生成回复
   - 英语学习：从 ChromaDB 加载该学生的历史对话，判断是否需要摘要
   - 俄语检查：独立检查，不存储历史
5. **邮件发送**：将回复以 HTML 格式发送给学生
   - 使用卡片式布局，优化移动端体验
6. **状态管理**：通过中间件记录已发送邮件，防止重复处理

### 使用示例

#### 示例 1：英语单词学习

学生发送邮件：
```
主题：学习英语单词
正文：请帮我解释单词 "ephemeral"
```

系统会自动：
- 识别这是英语学习请求
- 调用 `english_word_learning` 工具
- 加载该学生的历史对话
- 生成第一阶段的解释和例句
- 以 HTML 格式发送回复邮件
- 后续互动直接通过回复邮件进行

#### 示例 2：俄语单词背诵检查

学生发送邮件：
```
主题：俄语单词背诵检查
正文：
苹果 яблоко яблоки
书 книга книги
学习 учиться
```

系统会自动：
- 识别这是俄语背诵检查请求
- 调用 `russian_word_recite_check` 工具
- 逐行检查单词背诵情况
- 返回检查结果，格式如：
  ```
  苹果 яблоко яблоки ✔
  书 книга книги ✔
  学习 учиться ✔
  ```
- 以 HTML 格式发送回复邮件

**俄语单词输入格式说明：**
- **名词**：`中文意思 单词单数形式 单词复数形式`（如果单词只有复数形式，可省略单数形式）
- **其他词性**（动词、形容词、代词、数词、副词、其他虚词或短语）：`中文意思 单词（或短语）`

## 核心模块说明

### main.py
主程序入口，负责：
- 初始化主智能体（使用 LangChain `create_agent` API）
- 配置系统提示词，指导智能体进行邮件路由和工具调用
- 邮件监听循环（每 5 分钟检查一次未读邮件）
- 邮件解析：提取主题、正文、发件人信息，处理编码问题
- 调用智能体进行决策和工具调用
- 异常处理：捕获 IMAP 连接错误，标记连接无效以便重连
- 邮件处理间隔控制，避免处理过快

### tool.py
定义了四个核心工具（使用 LangChain `@tool` 装饰器）：
- `english_word_learning`: 英语单词学习工具
  - 参数：`mail_address`（学生邮箱）、`input_message`（输入消息）
  - 功能：维护每个学生的学习历史，加载历史对话，判断是否需要摘要
  - 存储：使用 ChromaDB 按邮箱地址存储和检索对话历史
- `russian_word_recite_check`: 俄语单词背诵检查工具
  - 参数：`input_message`（输入消息）
  - 功能：逐行检查学生单词背诵情况，不存储历史
- `send_email`: 发送邮件工具
  - 参数：`to`（收件人）、`subject`（主题）、`content`（HTML 内容）
  - 功能：使用 SMTP_SSL 发送 HTML 格式邮件，返回发送状态（0 成功，1 失败）
- `resume_email_status`: 恢复邮件未读状态工具
  - 参数：`email_id`（邮件 ID）
  - 功能：移除邮件的 `\Seen` 标志，恢复为未读状态

### middleware.py
中间件机制，基于 LangChain 和 LangGraph：
- `avoid_sending_duplicate_email`: 在模型调用后检查，防止对同一封邮件重复发送回复（通过比较当前邮件 ID 和已发送邮件 ID）
- `set_sent_email_id`: 在模型调用前检查，当邮件发送成功时（返回码为 0）记录已发送的邮件 ID 到上下文
- 使用 `ContextSchema` 定义上下文结构，包含 `cur_email_id` 和 `sent_email_id`

### language_learning_agent_factory.py
创建单词学习智能体（代码中以英语为例子，实际上只要deepseek支持可以配置任何语言），配置了详细的系统提示词，定义了 5 阶段教学流程。

### russian_word_recite_check_agent.py
创建俄语单词背诵检查智能体，配置了专业的检查规则，支持多种词性的单词检查。

### history_message_summarizer.py
历史消息摘要器，用于压缩对话历史：
- 当对话历史（包含新输入消息）超过 2000 字符时自动触发摘要
- 保留时序靠后的重要消息（默认越靠后的消息越重要）
- 主要用于英语单词学习的对话历史管理
- 使用独立的 LLM 智能体进行摘要生成

### mail_server.py
IMAP 邮件服务器包装类，提供：
- **自动重连机制**：检测连接断开时自动重连，支持最大重连次数限制（默认 5 次）
- **连接健康检查**：使用 NOOP 命令定期检查连接状态
- **操作重试机制**：操作失败时自动重连并重试（最多 2 次）
- **RFC 2971 支持**：使用 IMAP ID 命令进行客户端身份验证
- **异常处理**：捕获各种连接异常（IMAP4.abort, IMAP4.error, AttributeError, OSError, EOFError）
- 包装类设计，透明地处理底层连接问题

### chroma.py
ChromaDB 客户端初始化：
- 使用持久化客户端（PersistentClient）存储对话历史
- 数据存储在配置指定的路径（默认 `./db`）
- 支持按邮箱地址查询和更新每个学生的学习历史
- 使用 `english_word_learning` collection 存储英语学习对话历史

### custom_type.py
自定义类型定义：
- `ContextSchema`: 定义智能体上下文结构（TypedDict）
  - `cur_email_id`: 当前正在处理的邮件 ID
  - `sent_email_id`: 已成功发送回复的邮件 ID
  - 用于中间件防重复发送机制，通过 LangGraph Runtime 上下文传递

## 注意事项

⚠️ **安全提醒**
- `config.json` 包含敏感信息，已加入 `.gitignore`，不会提交到版本库
- 生产环境建议使用环境变量或密钥管理服务

⚠️ **使用限制**
- 邮件轮询间隔为 5 分钟（可在 `main.py` 中修改 `time.sleep(300)`）
- 对话历史（包含新输入消息）超过 2000 字符会自动摘要（仅适用于英语单词学习）
- 处理完每封邮件后等待 10 秒（可在 `main.py` 中修改 `time.sleep(10)`）
- 目前支持英语单词学习和俄语单词背诵检查，可扩展其他语言功能
- 俄语单词背诵检查不存储历史对话，每次检查独立进行
- 英语单词学习历史按邮箱地址区分，不同邮箱的学习记录相互独立

⚠️ **邮件格式**
- 系统会自动忽略邮件附件
- 仅提取纯文本内容（忽略 HTML 部分）
- 回复邮件采用 HTML 格式，使用卡片式布局，确保移动端良好体验

⚠️ **连接稳定性**
- IMAP 连接支持自动重连机制，最大重连次数为 5 次
- 连接断开时会自动检测并尝试重连
- 重连失败后会等待更长时间后继续尝试

## 开发说明

### 扩展新的学习功能

1. 创建新的智能体文件（如 `russian_word_recite_check_agent.py`）或使用现有的智能体工厂
2. 在 `tool.py` 中添加新的工具函数，可参考english_word_learning工具
3. 在 `tool.py` 的 `tools` 列表中注册新工具
4. 确保主智能体的提示词能够正确识别和路由到新工具

### 修改教学流程

编辑 `language_learning_agent_factory.py` 中的 `base_prompt` 变量，调整教学阶段和策略。

## License

本项目采用 MIT License，详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issue 和 Pull Request！

