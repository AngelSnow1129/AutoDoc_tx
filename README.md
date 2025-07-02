# AutoDoc_tx

 
架构一个基于 Playwright 和 Python GUI 框架的、适用于腾讯文档的弹性数据提取与分析管道


第一部分：基础架构与项目设置

本报告旨在为使用 Python 和 Playwright 从腾讯文档在线表格中提取数据并进行处理提供一个全面、稳健且可扩展的技术方案。该方案不仅涵盖了数据提取的核心逻辑，还前瞻性地规划了图形用户界面（GUI）的集成，确保了项目的长期可维护性和用户友好性。

1.1 架构哲学：解耦数据平面与表示平面

成功的软件架构始于清晰的关注点分离。对于本项目而言，最核心的设计原则是将数据提取的逻辑（数据平面）与用户交互界面（表示平面）进行彻底解耦。这一决策直接响应了未来集成图形化界面的需求，是构建一个弹性系统的基石。
我们将设计两个主要且相互独立的组件：
数据提取核心：一个独立的 Python 模块，封装所有与 Playwright 相关的自动化操作。这包括浏览器启动、用户认证、网络请求拦截以及最终的数据抓取。此模块将以异步方式实现，并对外暴露一个简洁的接口，例如一个函数 fetch_sheet_data(url)，其最终返回一个 Pandas DataFrame 对象。
表示层 (GUI)：另一个独立的模块，负责处理所有的用户交互。它将导入并调用“数据提取核心”，但对其内部实现细节保持未知。换言之，GUI 层不关心底层是使用 Playwright、Selenium 还是直接的 API 调用。
这种分离至关重要。GUI 框架，如 Tkinter 或 PyQt，拥有其自身的事件循环（例如 Tkinter 的 root.mainloop() 或 PyQt 的 app.exec_()），用于响应用户的点击和键盘输入 1。而 Playwright 的异步操作则依赖于
asyncio 事件循环 3。如果将耗时的 Playwright 异步任务直接在 GUI 的主线程中运行，将会阻塞 GUI 事件循环，导致界面冻结，用户体验极差。因此，自动化逻辑必须被设计为在独立的后台线程中运行。这种架构要求两个组件之间有一个清晰、定义良好的接口，从而避免了将自动化脚本重构以适应 GUI 的巨大工作量，为项目的平滑演进奠定了坚实的基础。

1.2 项目结构与依赖管理

一个良好组织的项目结构能够显著提升代码的可读性和可维护性。推荐采用以下目录结构：



tencent_docs_scraper/
├── core/
│   ├── __init__.py
│   ├── authenticator.py  # 封装认证逻辑，包括首次QR码处理和状态复用
│   └── extractor.py      # 核心数据提取逻辑，调用Playwright并返回DataFrame
├── gui/
│   ├── __init__.py
│   ├── main_window.py    # 主应用窗口，包含UI元素和线程管理
│   └── data_model.py     # 用于在QTableView中高效显示Pandas DataFrame的Qt模型
├── main.py               # 启动GUI应用的入口点
├── auth_state.json       # 保存的认证状态文件（应被.gitignore忽略）
├── requirements.txt      # 项目依赖列表
└──.gitignore


项目的成功运行依赖于一系列高质量的 Python 库。下表详细列出了这些依赖及其在项目中的作用。
表1：项目依赖与库功能概览
库 (Library)
推荐版本
核心功能
选择理由
playwright
~1.42
浏览器自动化
用户查询明确指定。提供强大的浏览器控制和网络拦截API，是实现数据提取的核心工具 4。
pandas
~2.2
数据处理与分析
业界标准的表格数据处理库。对于将提取到的JSON数据转换为结构化、易于分析的DataFrame至关重要 6。
pyotp
~2.9
TOTP 生成
腾讯文档等现代应用普遍采用基于时间的一次性密码（TOTP）进行双因素认证（2FA），此库是自动化该流程的必需品 8。
pyzbar
~0.1.9
QR码解码
在首次认证设置中，从QR码图片中解码出TOTP密钥的关键组件 8。
Pillow
~10.0
图像处理
pyzbar 的依赖，用于在解码前加载和处理QR码图像 8。
PySide6
~6.7
GUI 框架
功能强大的Qt绑定库，对多线程（QThread）和大规模数据集展示（QTableView）提供卓越支持，是构建本项目数据密集型应用的理想选择 9。


第二部分：腾讯文档的高级认证协议

自动化访问如腾讯文档这类安全平台，首要挑战是处理其复杂的认证流程。我们提出一个健壮的两阶段认证策略，该策略结合了一次性的交互式设置和后续完全无交互的自动化操作，实现了效率与安全性的平衡。

2.1 第一阶段：首次握手 - 自动化QR码认证

此阶段专为应用的首次运行设计，目标是获取并保存长期有效的认证凭据。这被视为一个必要的初始化步骤，而非日常操作。
详细流程如下：
以“有头”模式启动 Playwright：调用 playwright.chromium.launch(headless=False) 启动一个可见的浏览器窗口，以便用户进行交互 11。
用户手动登录：脚本将导航至腾讯文档登录页面，用户需手动输入其账号和密码。
捕获 QR 码：当双因素认证（2FA）页面出现并显示 QR 码时，使用 Playwright 的定位器功能锁定 QR 码元素，并通过 locator.screenshot() 方法将其截取为图像文件（例如 qrcode.png） 8。
解码 QR 码：利用 pyzbar 和 Pillow 库，程序将打开刚才保存的图像文件并解码其内容。解码结果通常是一个 otpauth://totp/... 格式的 URL 8。
提取 TOTP 密钥：通过解析上述 URL，提取其中的 secret 参数。这个密钥是未来生成所有动态验证码的核心。
安全存储密钥：此密钥极为敏感，绝不能硬编码在代码中。必须强调应将其存储在安全的位置，例如操作系统的环境变量或专门的密钥管理服务中。
这个过程并非绕过安全机制，而是以编程方式参与了标准的 2FA 协议，将一次性的手动操作转化为可复现的自动化设置步骤 14。

2.2 第二阶段：操作标准 - 通过状态管理实现持久化会话

这是所有后续自动化任务推荐采用的标准模式。它不仅速度更快、可靠性更高，还能有效避免因频繁触发登录和 2FA 流程而可能导致的安全警报。
核心机制：利用 Playwright 提供的浏览器上下文状态管理功能 16。
实现流程如下：
保存认证状态：在第一阶段成功登录后，立即调用 context.storage_state(path="auth_state.json")。此函数会将当前会话的所有信息，包括 Cookies、Local Storage 和 IndexedDB 数据，完整地序列化并保存到一个 JSON 文件中 16。
配置版本控制忽略：将 auth_state.json 文件名添加到项目的 .gitignore 文件中。这是一个至关重要的安全措施，可以防止包含敏感会话令牌的文件被意外提交到代码仓库 16。
复用认证状态：在所有后续的脚本运行中，不再执行登录流程。取而代之，通过 browser.new_context(storage_state="auth_state.json") 来创建一个新的浏览器上下文。这个新创建的上下文会加载已保存的状态，从而直接进入一个已经认证的会话，完全跳过了登录页面和 QR 码验证环节 12。
这两个阶段构成了完整的认证生命周期：一次性的设置孕育了可持久复用的认证状态。这种策略远优于每次运行时都尝试处理 QR 码的脆弱方法，后者不仅效率低下，而且更容易被目标网站的反机器人机制标记。

第三部分：数据提取方法论 - 从脆弱的DOM解析到弹性的API拦截

本节对数据提取技术进行深入分析，旨在引导开发者避开常见陷阱，采用一种专业且长效的解决方案。

3.1 初级方法：直接DOM解析（及其固有脆弱性）

这种方法涉及使用 Playwright 的定位器（如 page.locator('table >> tr >> td')）来查找页面上的 HTML 表格元素，然后提取其文本内容 20。对于简单的静态网站，这或许可行，但对于像腾讯文档这样复杂的单页应用（SPA），此方法的可靠性极低。
其主要缺陷包括：
动态类名：现代前端框架（如 React, Vue）在构建时常会生成混淆或动态的 CSS 类名和 ID。这些标识符在每次网站更新后都可能改变，导致之前编写的定位器瞬间失效。
虚拟化渲染：为了高效处理大型电子表格，应用通常只将用户当前视口内可见的行和列渲染到 DOM 中。当用户滚动时，新的数据才被动态加载和渲染。这意味着简单的 DOM 抓取只能获取到一小部分数据，完整获取需要编写复杂的滚动和等待逻辑 22。
Canvas 渲染：更极端的情况下，核心的表格网格可能完全由 HTML <canvas> 元素绘制。在这种技术下，单个单元格在 DOM 树中并不作为独立元素存在，使得基于 DOM 的抓取工具完全无法访问其内容。谷歌表格等产品就采用了类似技术，有理由相信腾讯文档也可能如此 23。
网页上数据的视觉表现与其在 DOM 中的结构化表示常常是脱钩的。试图抓取你所看到的东西，是一个在现代 Web 应用中极易失败的前提。

3.2 专业选择：拦截XHR/Fetch API调用

这是本报告强烈推荐的核心策略。我们不再与渲染后的 HTML 交互，而是利用 Playwright 强大的网络监控能力，在数据从服务器传输到客户端的过程中，直接捕获原始的数据包。
实施步骤如下：
侦察：打开腾讯文档，并启动浏览器的开发者工具（通常按 F12），切换到“网络”（Network）标签页，并筛选出 XHR/Fetch 类型的请求。加载或操作电子表格，观察新出现的网络请求，找到那个其响应内容（Response/Preview）为结构化数据（通常是 JSON 格式）的 API 端点 24。
拦截：在 Playwright 脚本中，使用 page.on("response", handler_function) 注册一个监听器，它会在每个网络响应完成时被触发 25。
过滤：在 handler_function 内部，通过检查 response.url 属性，判断当前响应是否来自第一步中确定的目标 API 端点。
提取：如果 URL 匹配，调用 response.json() 方法。该方法会自动将响应体解析为一个 Python 字典。这个字典中就包含了纯净、结构化的表格数据，没有任何 HTML 或 CSS 的干扰 28。
这种技术从根本上将抓取范式从“UI 自动化”转变为“API 客户端模拟”。它对几乎所有的前端界面变更（如样式调整、元素重构、框架迁移）都具有免疫力。只要后端的 API 接口保持稳定，数据提取脚本就能持续工作。这正是一个稳健、低维护成本的自动化解决方案的定义。
表2：数据提取方法论对比

方法
可靠性/脆弱性
复杂度
性能
可维护性
推荐度
DOM 解析
低（UI 变更即失效）
高（需处理滚动、虚拟化）
慢（需等待页面渲染）
差
不推荐用于SPA
XHR 拦截
高（与 UI 解耦）
低（找到端点后逻辑简单）
快（直接获取原始数据）
优秀
强烈推荐


第四部分：使用Pandas进行数据转换与建模

本节将阐述如何将从 API 捕获的原始数据，高效地转换为可供分析的、规整的 Pandas DataFrame，这是连接数据提取与数据应用的桥梁。

4.1 解析捕获的JSON负载

通过前述的 XHR 拦截方法，我们得到的 response.json() 是一个 Python 字典或列表 25。首要任务是检查其数据结构，以定位真正包含表格数据的键。这通常是一个名为
data、result 或 rows 的键，其对应的值是一个包含多个对象的列表，每个对象代表表格的一行。

4.2 使用 pandas.json_normalize 驾驭嵌套数据

问题陈述：从 API 获取的 JSON 数据极有可能是嵌套的。例如，一个单元格的数据可能是一个包含 value、format、comment 等键的字典。如果直接使用 pd.DataFrame() 函数来转换这样的数据，结果将是某些列中含有复杂的字典或列表对象，这对于后续的数据分析非常不便 30。
解决方案：Pandas 库中的 pandas.json_normalize() 函数正是为解决这一痛点而设计的 6。它能够“压平”嵌套的 JSON 结构，将其转换为规整的二维表格。
详细应用指南：
json_normalize 的强大之处在于其灵活的参数配置。以下是核心参数的说明及示例：
data：输入的 JSON 数据，通常是一个字典列表。
record_path：指定需要被“展开”为多行的嵌套列表的路径。例如，如果数据结构是 {'result': {'rows': [...]}}，那么 record_path 就应设置为 ['result', 'rows']。这会将 rows 列表中的每一个元素转换成 DataFrame 的一行 31。
meta：指定需要从父级结构中提取并添加到每一行记录中的元数据字段。例如，可以将文档标题、工作表名称等顶层信息作为新列添加到所有行中，以保持数据的上下文完整性 31。
sep：定义用于连接各层级键名以形成新列名的分隔符。默认是 .，例如 cell.value。可以根据需要修改为 _ 等其他字符。
示例代码：
假设捕获的 JSON 如下：

JSON


{
  "sheetName": "Q1 Sales",
  "data": {
    "records":
  }
}


使用 json_normalize 进行转换：

Python


import pandas as pd

json_data = #... (captured json)

df = pd.json_normalize(
    json_data['data']['records'],
    meta=['sheetName'],
    meta_prefix='meta_', # 可选，为元数据列添加前缀
    record_path=None, # 此处记录是顶层列表，但agent是嵌套的
    sep='_'
)
# 如果agent本身也是一个列表，则需要更复杂的处理，但对于嵌套字典，json_normalize会自动处理
print(df)


输出将会是一个扁平化的 DataFrame，列名如 id, sales, agent_name, agent_region, meta_sheetName。
通过熟练运用 json_normalize，我们可以将复杂的、多层级的 API 响应高效地转换为可直接用于分析的、干净的二维数据表，这是数据处理流程中至关重要的一步。

第五部分：图形用户界面（GUI）的架构设计

本节将应对项目中最具挑战性的架构问题：如何将异步的 Playwright 核心与同步的 GUI 框架相结合，创造出一个响应流畅、不会卡顿的应用程序。

5.1 核心架构挑战：集成异步与同步事件循环

问题所在：无论是 PyQt/PySide 还是 Tkinter，这些 GUI 工具包都依赖于一个主事件循环来处理用户输入（如点击、按键）和界面刷新。而 Playwright 的异步 API 则运行在 asyncio 的事件循环之上。如果在 GUI 的主线程中（例如，在一个按钮的点击事件处理器中）直接调用一个耗时的 async Playwright 函数，GUI 的事件循环将被阻塞，直到该函数执行完毕。这将导致整个应用程序界面冻结，无法响应任何用户操作，这是用户体验设计的重大失败。
解决方案：必须将耗时的 Playwright 任务转移到一个独立的后台线程中执行。GUI 的主线程与这个后台工作线程之间需要建立一个安全的通信机制，用于启动任务、报告进度以及传递最终结果（即提取到的 DataFrame）。这个模式是并发 GUI 编程的基本原则，在不同框架的实践中反复出现 1。
表3：GUI 集成方案对比
框架/方案
集成模式
复杂度
特性与可扩展性
推荐度
Tkinter
threading.Thread + queue.Queue 或使用 tk_async_execute 库 34
中等
提供基础控件，对于复杂数据应用的可扩展性较差。
适用于简单工具
PyQt/PySide
QThread + 信号/槽 (signals/slots) 33
中等（但结构清晰）
拥有丰富的控件集、成熟的数据模型（QAbstractTableModel），高度可扩展。
推荐用于此数据密集型应用


5.2 推荐实现：采用 PyQt/PySide 的 QThread 与信号机制

基于其强大的功能和为数据密集型应用设计的成熟模式，我们推荐使用 PyQt/PySide。以下是推荐架构的详细蓝图。
组件分解：
Worker(QObject)：这是一个不包含任何 UI 元素的纯逻辑类，它将被移动到后台线程。它包含一个 run 方法，该方法是实际工作的执行入口，内部会调用 asyncio.run(core.extractor.fetch_sheet_data(...))。此类还将定义一系列信号，如 progress(str) 用于更新状态，finished(object) 用于在任务完成时传递结果（DataFrame），以及 error(str) 用于报告异常。
MainWindow(QMainWindow)：主 GUI 窗口类。它负责创建和管理界面元素，如按钮和表格视图。它还将创建一个 QThread 实例。
连接各组件：
在 MainWindow 中，实例化 Worker 对象和 QThread 对象。
使用 worker.moveToThread(thread) 将 Worker 对象“移动”到后台线程。这一步至关重要，它确保了 Worker 的所有方法（槽）都将在该后台线程中执行。
将线程的 started 信号连接到 Worker 的 run 槽。这样，一旦线程启动，工作便会自动开始。
将 Worker 的 finished(object) 信号连接到 MainWindow 中的一个槽函数，该函数负责接收后台传来的 DataFrame 并进行处理（例如，更新表格视图）。
当用户点击“获取数据”按钮时，其事件处理器只需调用 thread.start() 即可，后续的一切都将通过信号和槽自动协调。
Qt 的信号/槽机制是原生线程安全的，这使其成为在后台 Playwright 线程和主 GUI 线程之间进行通信的理想方式。它避免了手动管理锁和复杂的队列逻辑，使得代码更加清晰和易于维护，是比其他手动方法更优越的架构选择 33。

5.3 数据可视化：将 Pandas DataFrame 绑定到 QTableView

挑战：如何高效地在 GUI 中展示一个可能包含大量数据且动态更新的 Pandas DataFrame？逐个单元格地填充 QTableWidget 是一种非常低效的方式，当数据量大时会导致性能瓶颈。
专业解决方案：实现一个自定义的数据模型，该模型继承自 QAbstractTableModel。这个模型类充当了 Pandas DataFrame 的一个轻量级适配器或代理。然后，将这个模型设置给 QTableView 控件。QTableView 是一种模型-视图架构的实现，它非常高效，因为它只向模型请求当前需要绘制在屏幕上的那部分数据。
实现指南：我们将提供一个完整的 PandasModel(QAbstractTableModel) 类的 Python 代码。该类需要实现几个关键方法：
rowCount()：返回 DataFrame 的行数。
columnCount()：返回 DataFrame 的列数。
data(index, role)：根据给定的索引（行和列）和角色（如显示文本、对齐方式等），从 DataFrame 返回相应的数据。
headerData(section, orientation, role)：返回行和列的表头信息。
这种实现方式是 Qt 中处理表格数据的最佳实践，能够以极高的性能和极低的内存占用展示海量数据。已有现成的示例代码可以作为我们实现的模板和参考 10。这种模型-视图方法将数据处理世界（Pandas）与表示世界（Qt）以最地道、最高效的方式连接起来，是构建真实世界级数据应用的关键。

第六部分：综合实现与完整蓝图

本节将前面讨论的所有概念融合成一个连贯的、可操作的应用程序蓝图，并提供关键模块的代码结构，以展示各部分如何协同工作。

6.1 数据提取模块 (core/extractor.py)

此模块是整个数据管道的起点，负责与 Web 页面交互。

Python


# core/extractor.py
import asyncio
from playwright.async_api import async_playwright, Page, Response
import pandas as pd

# 假设目标API端点包含 'api/get_sheet_data'
TARGET_API_ENDPOINT = "api/get_sheet_data"
captured_data = None

async def handle_response(response: Response):
    """监听并捕获包含表格数据的API响应"""
    global captured_data
    if TARGET_API_ENDPOINT in response.url and response.request.method == 'POST':
        print(f"Captured data from: {response.url}")
        try:
            captured_data = await response.json()
        except Exception as e:
            print(f"Error parsing JSON from response: {e}")

async def fetch_sheet_data(url: str, auth_file: str) -> pd.DataFrame:
    """
    启动Playwright，使用认证状态访问腾讯文档，并拦截API获取数据。
    """
    global captured_data
    captured_data = None  # 重置捕获的数据

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=auth_file)
        page = await context.new_page()

        # 注册响应监听器
        page.on("response", handle_response)

        await page.goto(url, wait_until="networkidle")

        # 在这里可以添加一些操作来触发数据加载，如果需要的话
        # 例如：await page.get_by_text("Sheet2").click()
        # 等待数据被捕获，设置一个超时
        for _ in range(10): # 等待最多10秒
            if captured_data:
                break
            await asyncio.sleep(1)

        await browser.close()

        if captured_data:
            # 使用json_normalize处理可能嵌套的JSON
            # 这里的 'data.records' 是一个假设的路径，需要根据实际API响应调整
            try:
                df = pd.json_normalize(captured_data['data']['records'])
                return df
            except KeyError as e:
                print(f"JSON structure unexpected. Key not found: {e}")
                return pd.DataFrame() # 返回空DataFrame
        else:
            print("Failed to capture target API response.")
            return pd.DataFrame()



6.2 GUI 模块 (gui/main_window.py)

此模块负责用户交互和后台任务的调度。

Python


# gui/main_window.py
import sys
import asyncio
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableView, QLabel
from PySide6.QtCore import QThread, QObject, Signal

# 假设PandasModel和extractor已在其他文件中定义
from.data_model import PandasModel
from core.extractor import fetch_sheet_data

class Worker(QObject):
    finished = Signal(object)  # 信号，完成后发射DataFrame
    error = Signal(str)

    def __init__(self, url, auth_file):
        super().__init__()
        self.url = url
        self.auth_file = auth_file

    def run(self):
        try:
            # 在新线程中运行asyncio事件循环
            df = asyncio.run(fetch_sheet_data(self.url, self.auth_file))
            self.finished.emit(df)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tencent Docs Scraper")
        self.setup_ui()
        self.thread = None
        self.worker = None

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.status_label = QLabel("Ready. Enter URL and click Fetch.")
        self.fetch_button = QPushButton("Fetch Data")
        self.table_view = QTableView()

        layout.addWidget(self.status_label)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.table_view)

        self.fetch_button.clicked.connect(self.start_fetching)

    def start_fetching(self):
        # 假设URL和auth_file路径从UI控件或配置中获取
        url = "https://docs.qq.com/sheet/your_sheet_id"
        auth_file = "auth_state.json"

        self.fetch_button.setEnabled(False)
        self.status_label.setText("Fetching data... please wait.")

        self.thread = QThread()
        self.worker = Worker(url, auth_file)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.display_data)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def display_data(self, df):
        if not df.empty:
            model = PandasModel(df)
            self.table_view.setModel(model)
            self.status_label.setText(f"Success! Displaying {len(df)} rows.")
        else:
            self.status_label.setText("Failed to fetch data or data is empty.")
        self.fetch_button.setEnabled(True)

    def on_error(self, err_msg):
        self.status_label.setText(f"Error: {err_msg}")
        self.fetch_button.setEnabled(True)




6.3 应用入口点 (main.py)

这个简洁的脚本负责启动整个应用程序。

Python


# main.py
import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())



6.4 结论与最终建议

本报告提出的方案是一个全面且专业的解决方案，它通过分层和解耦，成功地将复杂的浏览器自动化、网络拦截、数据处理和并发GUI编程结合在一起。
最终建议：
错误处理：在 core 模块中应加入更详尽的错误处理逻辑，例如处理 Playwright 的 TimeoutError、网络连接中断、认证状态失效（auth_state.json 过期）等情况。当认证失效时，应能引导用户重新执行第一阶段的认证流程。
日志记录：为 core 和 gui 模块配置结构化的日志记录（例如使用 logging 库）。这对于调试后台线程中的问题至关重要，因为 print 语句可能不会按预期显示。
配置管理：将 URL、文件路径、API 端点等可变信息移至一个单独的配置文件（如 config.ini 或 config.yaml），而不是硬编码在代码中，以提高灵活性。
打包与分发：当应用开发完成后，可以使用 PyInstaller 或 cx_Freeze 等工具将其打包成一个独立的可执行文件，方便非技术用户在没有 Python 环境的情况下直接运行。
引用的著作
Using Bleak within a tkinter GUI with ASYNCIO · hbldh bleak · Discussion #481 - GitHub, 访问时间为 七月 2, 2025， https://github.com/hbldh/bleak/discussions/481
Async like pattern in pyqt? Or cleaner background call pattern? - Stack Overflow, 访问时间为 七月 2, 2025， https://stackoverflow.com/questions/24689800/async-like-pattern-in-pyqt-or-cleaner-background-call-pattern
Python Playwright: a complete guide, 访问时间为 七月 2, 2025， https://blog.apify.com/python-playwright/
Installation | Playwright Python, 访问时间为 七月 2, 2025， https://playwright.dev/python/docs/intro
Playwright Python, 访问时间为 七月 2, 2025， https://playwright.dev/python/docs/api/class-playwright
Converting JSONs to Pandas DataFrames: Parsing Them the Right Way - KDnuggets, 访问时间为 七月 2, 2025， https://www.kdnuggets.com/converting-jsons-to-pandas-dataframes-parsing-them-the-right-way
Convert JSON to Pandas DataFrame - GeeksforGeeks, 访问时间为 七月 2, 2025， https://www.geeksforgeeks.org/pandas-convert-json-to-dataframe/
Automate 2FA: TOTP Authentication with QR ... - The Green Report, 访问时间为 七月 2, 2025， https://www.thegreenreport.blog/articles/automate-2fa-totp-authentication-with-qr-code-decoding/automate-2fa-totp-authentication-with-qr-code-decoding.html
Async “Minimal” Example - Qt for Python, 访问时间为 七月 2, 2025， https://doc.qt.io/qtforpython-6/examples/example_async_minimal.html
Pandas Simple Example - Qt for Python, 访问时间为 七月 2, 2025， https://doc.qt.io/qtforpython-6/examples/example_external_pandas.html
Authentication | Playwright Python - CukeTest, 访问时间为 七月 2, 2025， https://www.cuketest.com/playwright/python/docs/auth/
Authentication - Playwright, 访问时间为 七月 2, 2025， https://playwright.bootcss.com/python/docs/auth
How to Bypass TOTP-Based 2FA Login Flows With Playwright - Checkly, 访问时间为 七月 2, 2025， https://www.checklyhq.com/blog/how-to-bypass-totp-based-2fa-login-flows-with-playwright/
Playwright Login Test With Two Factor Authentication (2FA) Enabled (TOTP), 访问时间为 七月 2, 2025， https://playwrightsolutions.com/playwright-login-test-with-2-factor-authentication-2fa-enabled/
Automate TOTP 2-Factor Authentication (2FA) with Playwright - SpurQLabs, 访问时间为 七月 2, 2025， https://spurqlabs.com/automating-2fa-authentication-for-secured-website/
Authentication | Playwright Python, 访问时间为 七月 2, 2025， https://playwright.dev/python/docs/auth
How to Manage Authentication in Playwright - Checkly, 访问时间为 七月 2, 2025， https://www.checklyhq.com/learn/playwright/authentication/
Playwright 'Re-use state' & 'Re-use Authentication' with Firebase - Stack Overflow, 访问时间为 七月 2, 2025， https://stackoverflow.com/questions/77325496/playwright-re-use-state-re-use-authentication-with-firebase
Playwright Tutorial: Re-use state & Re-use Authentication - YouTube, 访问时间为 七月 2, 2025， https://www.youtube.com/watch?v=QJL6uV7z-8I
How to Scrape HTML Table in JavaScript + Ready-To-Use Code - ScraperAPI, 访问时间为 七月 2, 2025， https://www.scraperapi.com/blog/scrape-html-table-to-csv/
Web Scraping HTML Tables with JavaScript | ScrapingAnt, 访问时间为 七月 2, 2025， https://scrapingant.com/blog/js-scrape-html-tables
Scraping page with javascript filled table - html - Stack Overflow, 访问时间为 七月 2, 2025， https://stackoverflow.com/questions/44999568/scraping-page-with-javascript-filled-table
how to inspect html of Google sheets in firefox - Stack Overflow, 访问时间为 七月 2, 2025， https://stackoverflow.com/questions/29999013/how-to-inspect-html-of-google-sheets-in-firefox
How to determine which files are used by website - Webmasters Stack Exchange, 访问时间为 七月 2, 2025， https://webmasters.stackexchange.com/questions/48231/how-to-determine-which-files-are-used-by-website
How to Intercept XHR Requests for Web Scraping - Medium, 访问时间为 七月 2, 2025， https://medium.com/@datajournal/web-scraping-intercepting-xhr-requests-38dc244c6f4e
Network | Playwright Python, 访问时间为 七月 2, 2025， https://playwright.dev/python/docs/network
How to capture background requests and responses in Playwright? - Scrapfly, 访问时间为 七月 2, 2025， https://scrapfly.io/blog/how-to-capture-xhr-requests-playwright/
How to Intercept Requests in Playwright | Checkly, 访问时间为 七月 2, 2025， https://www.checklyhq.com/learn/playwright/intercept-requests/
Playwright Guide - Capturing Background XHR Requests - ScrapeOps, 访问时间为 七月 2, 2025， https://scrapeops.io/playwright-web-scraping-playbook/nodejs-playwright-capture-xhr-requests/
pandas: Convert a list of dictionaries to DataFrame with json_normalize | note.nkmk.me, 访问时间为 七月 2, 2025， https://note.nkmk.me/en/python-pandas-json-normalize/
How to convert nested JSON into a Pandas DataFrame | by Avi Patel - Medium, 访问时间为 七月 2, 2025， https://avithekkc.medium.com/how-to-convert-nested-json-into-a-pandas-dataframe-9e8779914a24
Quick Tutorial: Flatten Nested JSON in Pandas - Kaggle, 访问时间为 七月 2, 2025， https://www.kaggle.com/code/jboysen/quick-tutorial-flatten-nested-json-in-pandas
Code to achieve multithreading with pyqt5 framework. - GitHub Gist, 访问时间为 七月 2, 2025， https://gist.github.com/sabapathygithub/160ecf262063bcb826787a7af1637f44
Tkinter-Async-Execute, 访问时间为 七月 2, 2025， https://tkinter-async-execute.readthedocs.io/
Tkinter background threading example - GitHub Gist, 访问时间为 七月 2, 2025， https://gist.github.com/nasingfaund/9ac047dd6e9fad7391b80d608fcfa7cf
Simple example of the correct way to use (Py)Qt(5) and QThread - GitHub Gist, 访问时间为 七月 2, 2025， https://gist.github.com/jazzycamel/8abd37bf2d60cce6e01d
pyqt thread example - GitHub Gist, 访问时间为 七月 2, 2025， https://gist.github.com/waspinator/b1729031e2d5c60d4d9dbe48d88c54c5
