---
trigger: always_on
---

Python 后端依赖与版本规则

##核心原则
在处理此仓库时，禁止凭记忆猜测 package APIs、dependency names、connection URL schemes 或 version compatibility。
对于任何框架或库集成，需先验证当前安装的版本，再编写与该版本匹配的代码。
必须将 version-sensitive code 视为高风险代码。

##强制版本检查工作流
在更改与 framework setup、ORM config、test setup、startup lifecycle、database connection 或 model definitions 相关的代码前，需按以下顺序执行：
1.检查项目环境中实际安装的 package versions。
2.检查项目的依赖事实来源：
  --pyproject.toml
  --requirements.txt
  --requirements-dev.txt
  --uv.lock
  --poetry.lock
  --pdm.lock
3.若环境与 lock/config 不一致，即时调试时以实际安装的环境为准，但需明确记录不匹配之处。
4.仅在确认版本后，方可提出代码更改建议。
5.切勿假设旧教程中的示例仍然适用。

##版本敏感库
需将以下库视为 version-sensitive，编码前进行验证：
FastAPI
Starlette
Pydantic
Tortoise ORM
asyncmy
aiomysql
pytest
pytest-asyncio
anyio
httpx

##Tortoise ORM 0.25.4 规则
1. 切勿猜测 DB URL schemes
对于 Tortoise ORM 0.25.4，切勿根据 driver name 假设 database URL scheme。
！具体而言：
禁止假设 asyncmy:// 是 Tortoise 0.25.4 有效的 DB URL scheme。
编辑配置前，需验证已安装的 Tortoise 0.25.4 版本支持的 scheme。
！区分以下两者：
ORM 接受的 URL scheme
底层 driver package
若调试启动失败并出现 Unknown DB scheme，需检查：
--Tortoise 0.25.4 版本
--当前 DB URL string
--该 scheme 属于 Tortoise 还是仅属于 driver

2. 始终检查 DB credentials 中的特殊字符
当密码包含 @、:、/、?、# 或 % 等特殊字符时，切勿直接粘贴到 DB URL 中。需检查是否需要 URL encoding。
3. 优先使用项目本地模式而非通用示例
若仓库中已有可运行的 Tortoise 0.25.4 init code、test fixtures 或 connection config，除非有确认的版本特定原因，否则需复用该 exact pattern。
4. 注意已弃用的 field arguments
编辑 Tortoise 0.25.4 models 时，需验证已安装版本是否期望：
切勿在新代码中引入已弃用的 arguments。
5. 切勿盲目重写 model APIs
在更改 fields、ForeignKeyField、ManyToManyField、pydantic_model_creator 或 FastAPI 集成 helpers 前，需先检查仓库中现有的可运行用法。

##FastAPI / Starlette 规则
1. 始终明确验证 imports
切勿假设 symbols 是全局可用的。若使用 APIRouter、Depends、HTTPException、status 或 Body，需验证它们已在文件中导入。
2. 将 startup/lifespan code 视为 version-sensitive
修改 app startup、shutdown、lifespan 或 ORM registration 时：
--检查已安装的 FastAPI 和 Starlette 版本
--匹配仓库中已使用的风格
--除非已验证，否则避免混合使用较旧的 startup-event patterns 和较新的 lifespan patterns
3. Test collection errors 首先是 import/config 问题
若 pytest 在 collection 期间失败：
--首先检查 import errors
--然后检查 router/module structure
--再检查 startup side effects
--禁止直接跳到 business logic fixes

##测试调试规则
当测试失败时，在提出修复建议前先对失败进行分类：
1.Collection/import error
缺少 import
循环 import
模块路径问题
语法错误

2.Startup/config error
错误的 DB URL
ORM init failure
缺少 env var
lifespan failure

3.Runtime logic error
endpoint logic
validation
auth
query behavior

4.Assertion mismatch
response shape changed
expected status changed
fixture data mismatch
禁止将所有失败都视为 business logic problems。


##所需调试输出格式
对于 dependency 或 framework-related failures，需按以下格式回复：

###Root cause
说明确切的 failing layer：
--import
--startup
--config
--ORM init
--runtime
--assertion

###Evidence
引用证明诊断的确切 traceback line。

###Version check
列出涉及的相关 installed package versions。

###Fix
给出所需的 minimal code or config change。

###Confidence
说明这是：
--confirmed from traceback
--highly likely
--possible but needs environment confirmation

##反幻觉规则
你必须不做以下的事情：
发明 package APIs
发明支持的 DB URL schemes
仅从 package names 推断 compatibility
除非确认 version compatibility，否则不建议迁移到新 syntax
未经警告混合不同 major versions 的示例
若不确定，请准确说明必须检查的内容。

##仓库优先规则
当仓库中已有一个 passing test 或一个使用相同 stack 的可运行 module 时，优先使用该 implementation pattern 而非互联网记忆。
优先级顺序：
1.此仓库中已有的 passing code
2.此环境中已安装的 package behavior
3.项目 dependency files
4.外部 examples

##更改最小化规则
对于 version-related issues，优先采用最小 viable fix：
--修复 import
--修复 config string
--修复 deprecated arg name
--使一个 function call 与 installed version 对齐
--调试 version mismatch 时，切勿重构 unrelated modules。

##若不确定
若对 versions 有任何疑问，请首先检查：
--installed packages
--dependency files
--仓库中的可运行 examples
--exact traceback
然后再提出更改建议。