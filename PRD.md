这是一个基于前文技术探索与原型验证生成的标准产品需求文档（PRD）。

---

# 产品需求文档 (PRD) - DeepSurge Intelligence Dashboard

| 文档版本 | V1.0 |
| :--- | :--- |
| **项目名称** | DeepSurge 赛事情报挖掘与分析平台 |
| **项目代号** | **Project Walrus-Eye** |
| **产品负责人** | Data Mining Expert |
| **创建日期** | 2025-11-24 |
| **状态** | 开发中 (Development) |

---

## 1. 项目背景与目标 (Background & Objectives)

### 1.1 背景
DeepSurge 承办的 "Walrus Haulout Hackathon 2025" 汇聚了大量基于 Walrus 和 Sui 生态的去中心化应用。目前，官网仅提供基于 Cursor 的分页列表浏览，无法进行全量检索、多维统计或项目质量的快速筛选。投资者、研究员和开发者难以快速获取宏观赛事数据。

### 1.2 核心目标
构建一套**自动化数据挖掘与可视化分析系统**，实现：
1.  **全量获取**：突破分页限制，获取 100% 参赛项目数据。
2.  **质量分级**：通过多维指标识别优质项目（"Alpha"）与空壳项目。
3.  **趋势洞察**：可视化展示热门赛道、技术栈分布及部署情况。

---

## 2. 用户角色 (User Personas)

| 角色 | 核心诉求 | 使用场景 |
| :--- | :--- | :--- |
| **VC / 投资研究员** | 寻找高完成度、有代码、有 Demo 的早期项目。 | 过滤掉无代码项目，按赛道查看 Top 10 高分项目。 |
| **开发者 / 参赛者** | 分析竞争对手，了解主流技术栈。 | 查看某一赛道下的项目列表，分析其使用的技术关键词。 |
| **生态运营人员** | 监控赛事热度，统计部署数据。 | 查看 Testnet vs Mainnet 部署比例，导出 CSV 汇报。 |

---

## 3. 功能需求说明 (Functional Requirements)

### 3.1 模块一：数据采集引擎 (Data Acquisition Engine)
**优先级：P0 (最高)**

* **功能描述**：针对 DeepSurge API 进行全量自动化抓取。
* **输入参数**：
    * API Endpoint: `https://www.deepsurge.xyz/api/projects`
    * Hackathon ID: 固定为 `26f4d734-b30f-4009-9b41-edac04308c01`
    * Page Limit: 用户可配置 (默认 50)
* **逻辑要求**：
    * **自动翻页**：必须能够识别 API 返回的 `nextCursor`，自动构造下一页请求，直至 `hasNext: false`。
    * **容错处理**：遇到网络波动需重试 (Retry)，遇到反爬限制需增加延时 (Sleep)。
    * **状态反馈**：实时向前端输出当前抓取页数、累计条数及 HTTP 状态。

### 3.2 模块二：ETL 数据清洗与处理 (Data Processing)
**优先级：P0**

* **HTML 清洗**：
    * 输入：`description` 字段（含 `<p>`, `HTML tags`）。
    * 输出：`description_text`（纯文本），用于 NLP 分析和前端展示。
* **链接展平**：
    * 输入：`links` 数组（结构嵌套）。
    * 输出：独立字段 `github_url`, `demo_url`, `video_url`。
* **PQI 质量评分模型 (Project Quality Index)**：
    * 系统需为每个项目计算 `Score` (0-10分)：
        * +3分：有 GitHub 链接
        * +3分：有 Package ID (链上合约已部署)
        * +2分：有 Website/Demo 链接
        * +2分：描述文本长度 > 100 字符

### 3.3 模块三：可视化仪表盘 (Visualization Dashboard)
**优先级：P1**

前端框架采用 **Streamlit**，包含以下视图：

#### 3.3.1 控制台视图 (Sidebar)
* 配置单页抓取数量。
* “开始挖掘” 触发按钮。
* 数据下载按钮 (CSV 格式)。

#### 3.3.2 宏观统计视图 (Overview Tab)
* **核心指标卡 (KPI Cards)**：项目总数、开源率、部署率、平均质量分。
* **赛道分布 (Pie Chart)**：各 Track 的项目占比。
* **网络状态 (Bar Chart)**：Testnet / Mainnet / Undeployed 分布。

#### 3.3.3 详细列表视图 (Detail Grid Tab)
* **表格展示**：包含项目名、赛道、评分、一句话简介、相关链接图标 (GitHub/Demo)。
* **交互筛选**：支持按 `Track` (赛道) 和 `Status` (状态) 进行多选过滤。
* **搜索功能**：支持按项目名或描述关键词搜索。

---

## 4. 数据字典 (Data Dictionary)

| 字段名 | 类型 | 来源 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | String | API | 项目唯一标识 |
| `projectName` | String | API | 项目名称 |
| `track` | String | API | 参赛赛道 (e.g., "AI x Data") |
| `description_clean`| String | ETL | 清洗后的纯文本描述 |
| `status` | String | API | 提交状态 (submitted) |
| `deployNetwork` | String | API | 部署网络 (Testnet/Mainnet) |
| `packageId` | String | API | Sui 链上合约包 ID |
| `github_url` | String | ETL | 代码仓库链接 |
| `has_demo` | Boolean| ETL | 是否有演示链接 |
| `quality_score` | Integer| ETL | 0-10 质量评分 |

---

## 5. 非功能性需求 (Non-Functional Requirements)

* **性能**：全量抓取（假设 500+ 项目）应在 60 秒内完成。
* **可用性**：界面需直观，操作路径不超过 2 步（配置 -> 点击开始）。
* **兼容性**：生成的 CSV 文件需兼容 Excel/Google Sheets 打开（UTF-8-SIG 编码）。
* **无需鉴权**：工具无需用户登录 DeepSurge 账号，利用公开接口访问。

---

## 6. 技术架构 (Technical Stack)

* **开发语言**：Python 3.8+
* **前端框架**：Streamlit (快速构建 Web App)
* **网络请求**：Requests (处理 HTTP/HTTPS)
* **数据处理**：Pandas (DataFrame 操作)
* **HTML 解析**：BeautifulSoup4
* **图表库**：Plotly Express (交互式图表)

---

## 7. 风险评估 (Risk Assessment)

| 风险项 | 可能性 | 影响程度 | 应对策略 |
| :--- | :--- | :--- | :--- |
| **API 限流 (Rate Limiting)** | 中 | 无法获取完整数据 | 脚本中增加 `time.sleep(0.5)` 延时；增加失败重试机制。 |
| **字段结构变更** | 低 | 解析报错 | 使用 `.get()` 方法安全获取字典值，避免 Key Error。 |
| **网络超时** | 中 | 任务中断 | 设置 Request Timeout，并在 UI 提示用户检查网络。 |

---

## 8. 验收标准 (Acceptance Criteria)

1.  **数据完整性**：点击“开始挖掘”后，最终显示的项目总数应与 API `pagination.total` (如果有) 或网页端显示总数一致。
2.  **评分准确性**：随机抽取 5 个项目，检查其是否有 Github 链接，且评分逻辑是否符合规则。
3.  **导出可用性**：下载的 CSV 文件无乱码，且包含关键分析字段。
4.  **图表交互**：饼图和柱状图可 hover 显示具体数值，筛选器能正确过滤表格数据。

---
