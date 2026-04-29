# docassemble 项目核心功能总结

## 功能概述

这是一个非常实用的"智能文档生成系统"，你可以把它想象成一个**会问问题的文档生成器**。

简单来说，它的工作流程是这样的：
1. 开发者用 YAML 写好一个"访谈脚本"，定义好要问哪些问题、问题之间的逻辑关系（比如如果用户回答"是"就问A问题，回答"否"就问B问题）
2. 系统把这个脚本变成一个网页版的问卷，用户一步步回答问题
3. 回答完所有问题后，系统自动把收集到的信息填入预设的文档模板（支持 Word、PDF 等格式）
4. 最后生成一份完整的、个性化的文档

它特别适合用来生成法律文书、合同、申请表这类需要收集很多信息且格式固定的文档。比如你想写一份遗嘱，不需要自己去查法律条款，只需要回答系统问你的问题（比如"你叫什么名字？"、"你有哪些财产？"、"你想把财产留给谁？"），系统就会自动帮你生成一份符合法律规范的遗嘱文档。

这个项目的名字叫 **docassemble**，是一个开源的文档组装（document assembly）系统，广泛应用于法律科技领域。

---

## 技术实现深度解析

### 一次完整的 Interview 执行流程

#### 1. 用户打开 Interview（请求入口）

**核心入口文件**：`docassemble_webapp/docassemble/webapp/server.py` 中的 `index()` 函数（约第 6990 行）

**处理流程**：
1. **路由解析**：用户访问 `/interview?i=xxx` 或 `/i?i=xxx` 路由
2. **参数提取**：从 URL 参数中获取 `i`（YAML 文件名，如 `docassemble.demo:data/questions/hello.yml`）
3. **会话管理**：
   - 未登录用户创建临时用户（`TempUser` 表）
   - 从 cookie 或请求参数中获取 `secret`（会话密钥）
   - 管理 `session`、`uid` 等状态
4. **状态恢复**：调用 `fetch_user_dict()` 从数据库或 Redis 恢复用户之前的回答状态
5. **加载 Interview**：通过 `interview_cache.get_interview(yaml_filename)` 加载并解析 YAML 脚本
6. **执行逻辑**：调用 `interview.assemble(user_dict, interview_status)` 开始核心执行循环

#### 2. YAML 脚本加载与解析

**核心类**：`docassemble_base/docassemble/base/parse.py` 中的 `Interview` 类（第 8099 行）

**解析流程**：
1. **读取源文件**：
   - `InterviewSourceFile`：从文件系统读取 YAML（支持 `package:path` 格式）
   - `InterviewSourceString`：从字符串读取（用于动态生成）

2. **分块解析**：
   - YAML 用 `---` 分隔成多个"块"（block）
   - 每个块被解析为一个 `Question` 对象（第 2071 行）
   - 根据块中的关键字判断块类型：
     - `modules` / `imports`：导入 Python 模块
     - `objects`：初始化对象（如 `user: Individual`）
     - `code`：执行 Python 代码
     - `question`：向用户展示问题
     - `attachment`：定义生成的文档

3. **建立索引**：
   - `self.questions`：按变量名索引问题（如 `user.name.first` → 对应的问题）
   - `self.questions_by_name`：按 `id` 或 `name` 属性索引
   - `self.generic_questions`：泛型问题（适用于某类对象的所有实例）
   - `self.invalidation` / `self.onchange`：依赖关系和变化回调

#### 3. 核心执行循环（assemble 方法）

**核心方法**：`Interview.assemble()`（`parse.py` 第 8739 行）

这是整个系统的"心脏"，采用**需求驱动**的执行模式：

```
┌─────────────────────────────────────────────────────────────┐
│                    assemble() 主循环                          │
├─────────────────────────────────────────────────────────────┤
│  1. 初始化 user_dict（包含 _internal 存储元数据）              │
│  2. 执行 initial/code/modules 块（一次性初始化）               │
│  3. 遍历所有 mandatory（必填）块：                              │
│     ├─ 执行 code 块                                           │
│     ├─ 处理 data/objects_from_file 等数据加载块               │
│     └─ 尝试访问 question/attachment 块中的变量                │
│  4. 如果变量未定义 → 抛出 NameError/UndefinedError            │
│  5. 捕获异常 → 调用 askfor() 寻找能提供该变量的问题            │
│  6. 找到问题 → 填充 interview_status 并跳出循环                │
│  7. 没找到问题 → 报错（DAErrorNoEndpoint）                     │
└─────────────────────────────────────────────────────────────┘
```

**关键设计思想**：
- **惰性求值**：只在需要时才收集信息
- **异常驱动流程**：通过捕获 `NameError` 来"发现"需要问的问题
- **循环重试**：每次用户回答后，重新从开头执行，直到所有必填变量都有值

#### 4. 如何判断下一个问题（askfor 方法）

**核心方法**：`Interview.askfor()`（`parse.py` 第 9259 行）

当 `assemble()` 中访问一个未定义的变量时，系统需要找到"谁能提供这个变量"：

**查找逻辑**：
1. **变量名解析**：将复杂变量名（如 `user.name.first`）分解为多种变体
2. **精确匹配**：在 `self.questions[variable_name]` 中查找
3. **泛型匹配**：如果是对象属性，查找 `self.generic_questions` 中的泛型问题
4. **排序选择**：
   - 优先选择更具体的（点号更多、迭代器更少）
   - 优先选择非泛型的
5. **返回问题**：返回找到的 `Question` 对象，供前端展示

**示例**：
```yaml
# 这个问题负责提供 user.name.first 变量
question: What is your first name?
fields:
  - First Name: user.name.first
```

当代码中访问 `user.name.first` 时，`askfor()` 会找到这个问题并返回。

#### 5. 用户答案提交与状态保存

**提交处理**：在 `server.py` 的 `index()` 函数中处理 POST 请求

**状态保存**：`save_user_dict()`（`server.py` 第 2925 行）

**保存流程**：
1. **清理临时变量**：删除 `session_local`、`device_local`、`user_local` 等运行时变量
2. **更新元数据**：
   - `modtime`：修改时间
   - `accesstime`：访问时间
   - `steps`：步骤计数
3. **序列化**：
   - 加密模式：`encrypt_dictionary(user_dict, secret)` → AES 加密
   - 普通模式：`pack_dictionary(user_dict)` → pickle 序列化
4. **存储**：
   - 保存到 `UserDict` 数据库表
   - 或缓存到 Redis（`r_user`、`r_store`）

**状态恢复**：`fetch_user_dict()`（`backend.py`）
- 从数据库 `UserDict` 表查询
- 或从 Redis 读取缓存
- 解密/反序列化恢复 `user_dict`

#### 6. 文档生成机制

**核心处理**：`Question.processed_attachments()`（`parse.py` 第 6865 行）

**支持的文档格式**：

| 格式 | 生成方式 | 依赖工具 |
|------|---------|---------|
| PDF | Markdown → Pandoc → PDF | pandoc, LaTeX |
| DOCX | 模板渲染 / Markdown 转换 | docxtpl, pandoc |
| RTF | Markdown → Pandoc → RTF | pandoc |
| HTML | Markdown → HTML | 内置 |
| PDF 表单 | 填充现有 PDF 表单 | pdftk |

**生成流程**：
1. **解析 attachment 块**：
```yaml
attachment:
  name: My Document
  filename: my_doc
  content: |
    # ${ user.name }
    
    Your date of birth is ${ user.birthdate }.
```

2. **模板渲染**：
   - 使用 Jinja2 或 Mako 模板引擎
   - 将 `${ variable }` 替换为实际值
   - 支持条件判断、循环等逻辑

3. **格式转换**：
   - Markdown → PDF：调用 `pandoc` + LaTeX
   - DOCX 模板：使用 `docxtpl` 的 `template.render()`
   - PDF 表单：使用 `pdftk fill_form` 填充字段

4. **保存结果**：
   - 调用 `save_numbered_file()` 保存到服务器
   - 返回文件路径和元数据供用户下载

---

## 核心数据结构

### user_dict（用户状态字典）

这是存储所有用户数据的核心结构：

```python
user_dict = {
    # 用户回答的变量
    'user': <Individual object>,
    'quest': 'to find the Holy Grail',
    'benefits': 'Medicaid',
    
    # 内部元数据
    '_internal': {
        'tracker': 42,           # 执行追踪计数
        'progress': 75,          # 进度百分比
        'steps': 15,             # 步骤数
        'answered': {'q1', 'q2'}, # 已回答的问题名
        'answers': {...},        # 原始答案
        'objselections': {...},  # 对象选择记录
        'dirty': {...},          # 需要重新计算的变量
        'session_local': {...},  # 会话级本地存储
        'device_local': {...},   # 设备级本地存储
        'user_local': {...},     # 用户级本地存储
        'doc_cache': {...},      # 文档缓存
        'starttime': ...,        # 开始时间
        'modtime': ...,          # 修改时间
        'accesstime': {...},     # 各用户访问时间
        'secret': 'abc123',      # 加密密钥
    },
    
    'url_args': {...},           # URL 参数
    'nav': <DANav object>,       # 导航状态
}
```

### Interview 类关键属性

```python
class Interview:
    self.questions = {}           # 变量名 → 问题列表
    self.generic_questions = {}   # 泛型问题
    self.questions_by_id = {}     # ID → 问题
    self.questions_by_name = {}   # 名称 → 问题
    self.questions_list = []      # 所有问题的有序列表
    
    self.invalidation = {}        # 变量失效依赖
    self.onchange = {}            # 变量变化回调
    
    self.metadata = []            # 元数据块
    self.defs = {}                # 定义块
    self.terms = {}               # 术语表
    
    self.options = {}             # 全局选项
    self.default_language = 'en'  # 默认语言
```

---

## 关键设计模式

### 1. 解释器模式
- YAML 脚本被解释执行
- 每个 `Question` 块是一个"语句"
- `assemble()` 是"解释器"的主循环

### 2. 惰性求值
- 只在需要时才收集信息
- 通过异常（`NameError`）驱动流程
- 避免问不必要的问题

### 3. 状态机
- `user_dict` 存储完整状态
- 每次请求都是状态转换
- 支持暂停、恢复、回退

### 4. 依赖注入
- 问题之间通过变量隐式依赖
- `invalidation` 机制处理依赖失效
- 当变量变化时，相关变量被标记为"dirty"

---

## 目录结构与职责对应

| 目录 | 职责 | 关键文件/类 |
|------|------|------------|
| `docassemble_base/` | 核心引擎 | `parse.py` (Interview, Question), `util.py` (数据模型) |
| `docassemble_webapp/` | Web 层 | `server.py` (请求处理), `backend.py` (数据存储) |
| `docassemble_demo/` | 示例 | `data/questions/*.yml` (示例访谈脚本) |
| `Docker/` | 部署 | 配置文件、启动脚本 |
| `tests/` | 测试 | BDD 功能测试 |

---

## 技术栈总结

| 层级 | 技术 |
|------|------|
| Web 框架 | Flask, Flask-Login, Flask-WTF |
| 数据库 | SQLAlchemy (PostgreSQL/MySQL/SQLite) |
| 缓存 | Redis |
| 任务队列 | Celery + RabbitMQ |
| 模板引擎 | Jinja2, Mako |
| 文档处理 | Pandoc, pdftk, docxtpl, pikepdf |
| YAML 解析 | ruamel.yaml |
| 序列化 | pickle, JSON |
| 加密 | PyCryptodome (AES) |
| Web 服务器 | Nginx, Apache, uWSGI |
