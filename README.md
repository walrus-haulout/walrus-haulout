# DeepSurge Intelligence Dashboard

**Project Walrus-Eye** - A data mining and analysis platform for the Walrus Haulout Hackathon 2025.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)

[中文文档](README.zh.md)

## 🎯 Overview

DeepSurge Intelligence Dashboard is an automated data mining and visualization system designed for the **Walrus Haulout Hackathon 2025**. It overcomes pagination limitations to fetch 100% of project data, providing multi-dimensional statistics and quality filtering capabilities.

### Key Features

- ✅ **Full Data Extraction** - Automatic pagination to fetch all projects
- 📊 **Interactive Dashboard** - Built with Streamlit for real-time data exploration
- 🔍 **Advanced Filtering** - Filter by track, status, and search keywords
- 📈 **Macro Statistics** - Track distribution, deployment status, and trends
- 📥 **Data Export** - Download complete dataset as CSV
- 🤖 **Auto Fork** - GitHub Action to fork all hackathon projects

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip or pipenv

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/walrus-haulout/walrus-haulout.git
   cd walrus-haulout
   ```

2. **Create virtual environment and install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your DeepSurge cookie if needed
   ```

4. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   ```
   http://localhost:8501
   ```

## 📖 Usage

### Mining Data

1. Open the dashboard in your browser
2. In the sidebar, check **"Auto Mine All (Until End)"** for complete data extraction
3. Click **🚀 Start Mining**
4. Wait for the process to complete
5. Explore data in the **Macro Overview** and **Detail Grid** tabs

### Filtering and Search

- **Filter by Track**: Select specific competition tracks
- **Filter by Status**: Filter by submission status
- **Search**: Enter keywords to find projects

### Export Data

Click **📥 Download CSV** in the sidebar to export the complete dataset.

## 🔧 GitHub Action Setup

The repository includes a GitHub Action to automatically fork all hackathon projects to the `walrus-haulout` organization.

See [FORK_ACTION.md](docs/FORK_ACTION.md) for detailed setup instructions.

## 📊 Data Dictionary

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Unique project identifier |
| `projectName` | String | Project name |
| `description` | String | Project description (HTML) |
| `track` | String | Competition track |
| `status` | String | Submission status |
| `deployNetwork` | String | Deployment network (Testnet/Mainnet) |
| `packageId` | String | Sui blockchain package ID |
| `github_url` | String | GitHub repository URL |
| `website_url` | String | Project website URL |
| `youtube_url` | String | Demo video URL |
| `likeCount` | Integer | Number of likes |
| `createdAt` | DateTime | Creation timestamp |

## 🏗️ Architecture

```
walrus-haulout/
├── app.py                  # Main Streamlit application
├── scraper.py              # Data fetching and processing
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration (not in git)
├── .github/
│   └── workflows/
│       └── fork-projects.yml  # Auto-fork GitHub Action
├── scripts/
│   └── fork_projects.py    # Fork automation script
└── docs/
    └── FORK_ACTION.md      # GitHub Action documentation
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas
- **HTTP Requests**: Requests
- **HTML Parsing**: BeautifulSoup4
- **Visualization**: Plotly Express

## 📝 License

MIT License

## 🤝 Contributors

Built for the Walrus Haulout Hackathon 2025 by the community.

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Note**: This tool uses public APIs and does not require authentication. Make sure to comply with DeepSurge's terms of service.