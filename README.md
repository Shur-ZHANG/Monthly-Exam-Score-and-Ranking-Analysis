# Monthly-Exam-Score-and-Ranking-Analysis
学生月考成绩与位次分析-基于streamlit
# 📊 学生月考成绩与位次趋势分析

一个基于 **Streamlit** 的交互式数据可视化应用，帮助教师和家长快速分析学生多次月考中七大学科（数学、语文、英语、道法、地理、生物、历史）的成绩变化与年级总排名走势。

---

## ✨ 功能特点

- 📂 **灵活的数据导入**：支持上传 Excel / CSV 文件，或直接使用内置示例数据。
- 👤 **个体追踪**：选择任意学生，查看其历次月考的各科成绩折线图与年级排名变化。
- 🎯 **进退步自动标注**：年级排名图中自动计算并标注每次考试的进步/退步名次。
- 📈 **班级整体统计**：展示班级各科平均分趋势和每次考试的年级排名箱线图。
- 📥 **示例数据下载**：提供可下载的模拟成绩 CSV，方便快速体验。
- 🌐 **零安装使用**：可通过 Streamlit Cloud 部署为在线应用，浏览器访问即用。

---

## 🛠 本地运行

### 环境要求
- Python 3.9 ~ 3.11（推荐）
- pip 包管理工具

### 安装依赖
bash
-pip install streamlit pandas plotly openpyxl numpy

-streamlit run main.py
streamlit
pandas
plotly
openpyxl
numpy
