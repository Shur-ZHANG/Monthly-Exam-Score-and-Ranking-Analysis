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

### 启动应用
bash
streamlit run main.py

## 部署到 Streamlit Cloud
https://monthly-exam-score-and-ranking-analysis-8w39bpbwbnmriw36ycztgy.streamlit.app/

### 📁 数据格式要求
-上传的 Excel / CSV 文件必须包含以下列（顺序可调，但列名需完全一致）：
-学生姓名, 考试日期, 数学, 语文, 英语, 道法, 地理, 生物, 历史, 年级排名

## 🧪 调试记录与经验
-本应用在开发与部署过程中遇到以下典型问题，已逐一修复，供同类项目参考：

### 页面空白问题

-现象：本地启动后浏览器显示空白，控制台无输出。

-根因：Chrome 的 Adobe Acrobat 扩展干扰了 Streamlit 前端；同时部分环境 JavaScript 设置被意外关闭。

-解决：使用无痕窗口或禁用冲突扩展，并确认 chrome://settings/content/javascript 处于允许状态。

### 图表的 Y 轴反转报错

-代码中误用了 fig.update_yaxis()（单数），Plotly 中正确的方法为 fig.update_yaxes()（复数）或 fig.update_layout(yaxis=...)。

-修复后兼容所有 Plotly 版本。

### Streamlit Cloud 部署缺少依赖

-初次部署时 requirements.txt 未生效，导致 ModuleNotFoundError。

-检查确认文件名正确、内容无格式错误，并删除旧应用重新部署后成功。

### Python 3.14 兼容性

-Streamlit Cloud 默认分配最新 Python 版本，部分包可能尚未适配。

-通过 runtime.txt 指定 python-3.11 解决。

## 🙏 致谢
-感谢 Streamlit 社区提供如此便捷的数据应用框架，以及 Plotly 强大的可视化支持。
