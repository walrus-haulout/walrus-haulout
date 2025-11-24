# DeepSurge 情报分析仪表盘

**项目代号 Walrus-Eye** - Walrus Haulout Hackathon 2025 数据挖掘与分析平台

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)

[English Documentation](README.md)

## 🎯 项目概述

DeepSurge 情报分析仪表盘是为 **Walrus Haulout Hackathon 2025** 设计的自动化数据挖掘与可视化系统。它突破分页限制，获取 100% 的参赛项目数据，提供多维度统计和质量筛选能力。

### 核心功能

- ✅ **全量数据获取** - 自动翻页获取所有项目数据
- 📊 **交互式仪表盘** - 基于 Streamlit 构建，实时数据探索
- 🔍 **高级筛选** - 按赛道、状态、关键词搜索
- 📈 **宏观统计** - 赛道分布、部署状态、趋势分析
- 📥 **数据导出** - 下载完整数据集（CSV 格式）
- 🤖 **自动 Fork** - GitHub Action 批量 fork 参赛项目

## 🚀 快速开始

### 环境要求

- Python 3.9+
- pip 或 pipenv

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/walrus-haulout/walrus-haulout.git
   cd walrus-haulout
   ```

2. **创建虚拟环境并安装依赖**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，如需要可添加 DeepSurge cookie
   ```

4. **启动仪表盘**
   ```bash
   streamlit run app.py
   ```

5. **打开浏览器**
   ```
   http://localhost:8501
   ```

## 📖 使用指南

### 数据挖掘

1. 在浏览器中打开仪表盘
2. 在侧边栏勾选 **"Auto Mine All (Until End)"** 进行全量数据抓取
3. 点击 **🚀 Start Mining**
4. 等待抓取完成
5. 在 **Macro Overview** 和 **Detail Grid** 标签页中浏览数据

### 筛选与搜索

- **按赛道筛选**：选择特定竞赛赛道
- **按状态筛选**：按提交状态过滤
- **关键词搜索**：输入关键词查找项目

### 导出数据

点击侧边栏的 **📥 Download CSV** 按钮导出完整数据集。

## 🔧 GitHub Action 设置

仓库包含 GitHub Action，可自动将所有参赛项目 fork 到 `walrus-haulout` 组织。

详细设置说明请参考 [FORK_ACTION.md](docs/FORK_ACTION.md)。

## 📊 数据字典

| 字段名 | 类型 | 说明 |
|-------|------|------|
| `id` | String | 项目唯一标识符 |
| `projectName` | String | 项目名称 |
| `description` | String | 项目描述（HTML 格式）|
| `track` | String | 参赛赛道 |
| `status` | String | 提交状态 |
| `deployNetwork` | String | 部署网络（Testnet/Mainnet）|
| `packageId` | String | Sui 链上合约包 ID |
| `github_url` | String | GitHub 仓库地址 |
| `website_url` | String | 项目网站地址 |
| `youtube_url` | String | 演示视频地址 |
| `likeCount` | Integer | 点赞数 |
| `createdAt` | DateTime | 创建时间 |

## 🏗️ 项目架构

```
walrus-haulout/
├── app.py                  # Streamlit 主应用
├── scraper.py              # 数据抓取与处理
├── requirements.txt        # Python 依赖
├── .env                    # 环境配置（不在 git 中）
├── .github/
│   └── workflows/
│       └── fork-projects.yml  # 自动 Fork GitHub Action
├── scripts/
│   └── fork_projects.py    # Fork 自动化脚本
└── docs/
    └── FORK_ACTION.md      # GitHub Action 文档
```

## 🛠️ 技术栈

- **前端框架**: Streamlit
- **数据处理**: Pandas
- **HTTP 请求**: Requests
- **HTML 解析**: BeautifulSoup4
- **数据可视化**: Plotly Express

## 📝 开源协议

MIT License

## 🤝 贡献者

为 Walrus Haulout Hackathon 2025 社区构建。

## 📧 联系方式

如有问题或建议，请在 GitHub 上提 Issue。

---

**注意**：本工具使用公开 API，无需鉴权。请遵守 DeepSurge 平台的服务条款。
