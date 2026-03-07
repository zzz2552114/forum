---
trigger: always_on
---

Windows 10 环境执行与开发补充规则
核心环境声明
Host OS: Windows 10
Preferred Shell: PowerShell (默认) 
Git Environment: Git for Windows (但执行 Shell 命令时遵循 PowerShell 语法)
严禁假设当前环境为 Linux/macOS/WSL。所有命令行操作必须原生兼容 Windows 10。
命令行语法强制规则
1. 命令连接符
禁止使用 && 连接命令。
必须使用分号 ; 进行命令串联。
错误: git add . && git commit -m "update"
正确: git add . ; git commit -m "update"
2. 路径分隔符
优先使用反斜杠 \ 作为路径分隔符。
虽然部分 Windows 程序兼容正斜杠 /，但在操作文件系统、拼接路径时，除非特殊的情况，否则必须使用 \ 以确保原生兼容性。
示例: E:\forum\models.py
3. 环境变量与命令
引用环境变量时，使用 PowerShell 语法: $env:VAR_NAME。
若需临时设置环境变量并执行命令，使用 $env:VAR="value"; command 模式。
Git 与文件操作注意事项
1. Git 提交与脚本
当生成包含 Git 操作的多行脚本或序列时，严格遵守上述 ; 规则。
涉及文件通配符时，优先使用 PowerShell 的 Get-ChildItem 或明确的文件名，避免复杂的 glob 模式兼容性问题。
2. 文件编码
对于 Python 源码文件，推荐生成 UTF-8 with BOM 或 UTF-8 (无 BOM) 格式，优先与项目现有文件保持一致。
若在 Windows 上出现中文乱码问题，优先检查并设置 $env:PYTHONIOENCODING="utf-8"。
Python 开发环境规则
1. 虚拟环境 (Virtual Env)
若项目使用 venv，激活命令必须使用 Windows 路径:
正确: .\venv\Scripts\Activate.ps1 (PowerShell)
正确: .\venv\Scripts\activate.bat (CMD)
禁止生成 source venv/bin/activate 命令。
2. 路径处理代码
在编写 Python 代码处理路径时，强烈推荐使用 pathlib.Path 或 os.path.join，确保代码跨平台兼容。
但在命令行层面执行操作（如 mv, cp, rm）时，必须使用 Windows 原生命令 (Move-Item, Copy-Item, Remove-Item) 或其别名。

检查清单 (Checklist)
在生成任何需要执行的代码或命令前，请默念：
我用 ; 代替 && 了吗？
路径分隔符是 \ 吗？
如果是 Python venv，激活路径是 Scripts 而不是 bin 吗？