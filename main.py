"""
=============================================================================
学生月考成绩与位次趋势分析 - Streamlit 数据可视化应用
=============================================================================
编程思想：
1. 模块化设计：将数据加载、图表绘制、页面布局等功能拆分成独立函数。
2. 面向数据处理：使用 pandas 进行数据清洗、转换和聚合，便于可视化。
3. 交互式探索：通过 Streamlit 组件实现用户选择学生、科目，动态更新图表。
4. 数据驱动视图：所有图表均基于用户筛选后的数据生成，保证一致性。
5. 防御性编程：检查数据完整性，提供示例数据兜底，捕获异常避免崩溃。

主要功能：
- 上传 Excel/CSV 或使用内置示例数据
- 查看单个学生的各科成绩趋势图
- 查看年级排名变化并自动标注进退步
- 展示班级各科平均分趋势和排名分布箱线图
- 支持导出示例 CSV
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import random
import numpy as np

# -------------------------------------------------------------------------
# 页面基本配置
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="学生月考成绩与位次趋势分析",
    layout="wide"  # 使用宽屏布局，让图表有更多空间
)
st.title("📊 学生月考成绩与年级位次趋势分析")
st.markdown("### 支持数学、语文、英语、道法、地理、生物、历史七大学科的成绩及年级总排名变化趋势可视化")

# -------------------------------------------------------------------------
# 侧边栏：数据导入说明
# -------------------------------------------------------------------------
st.sidebar.header("📁 数据导入")
st.sidebar.markdown("请上传符合格式的 Excel 或 CSV 文件，列名需包含：")
required_cols = [
    "学生姓名", "考试日期", "数学", "语文", "英语",
    "道法", "地理", "生物", "历史", "年级排名"
]
st.sidebar.markdown("\n".join([f"- {col}" for col in required_cols]))
st.sidebar.markdown(
    "> 注：考试日期建议格式 YYYY-MM-DD 或 YYYY-MM，程序会自动排序。"
    "年级排名数值越小表示排名越靠前。"
)

# =========================================================================
# 函数定义区
# =========================================================================

def generate_sample_data():
    """
    生成示例数据：6 名学生，4 次月考，成绩有合理波动，年级排名基于总分计算。
    
    编程思想：
        - 为每个学生设定基础能力（各科均值）和进步因子，模拟真实成绩变化。
        - 每次考试总分排名：总分高者排名数字小（第1名最好）。
        - 加入随机噪声但限制分数范围（45-100），使数据既真实又可控。
        - 返回排序好的 DataFrame，方便直接使用。
    
    Returns:
        pd.DataFrame: 包含所有学生历次考试成绩和排名的数据框。
    """
    # 固定的随机种子，保证每次生成的数据一致（可复现）
    random.seed(42)
    np.random.seed(42)
    
    students = ["张三", "李四", "王芳", "赵磊", "陈雨桐", "周明"]
    exam_dates = ["2025-03-01", "2025-04-01", "2025-05-01", "2025-06-01"]
    subjects = ["数学", "语文", "英语", "道法", "地理", "生物", "历史"]
    
    # 为每个学生随机生成各科基础能力分（65~92分之间）
    ability = {
        student: {subj: random.randint(65, 92) for subj in subjects}
        for student in students
    }
    # 进步因子：数值为正表示成绩逐步提升，为负表示下降
    trend_factor = {student: random.uniform(-1.5, 3.0) for student in students}
    
    records = []  # 用于存储所有成绩记录
    
    for exam_date in exam_dates:
        exam_idx = exam_dates.index(exam_date)  # 考试次序（0,1,2,3）
        student_scores = {}  # 暂存本次考试每位学生的各科成绩
        
        for student in students:
            scores = {}
            for subj in subjects:
                base = ability[student][subj]
                # 成绩 = 基础分 + 趋势因子 × 考试次数 × 0.6 + 随机波动
                variation = trend_factor[student] * (exam_idx + 1) * 0.6 + random.uniform(-5, 6)
                score = base + variation
                # 限制分数在 45~100 之间（真实场景下限和上限）
                score = max(45, min(100, score))
                scores[subj] = round(score, 1)
            student_scores[student] = scores
        
        # 计算总分并排名（总分越高，排名数字越小）
        total_scores = []
        for student in students:
            total = sum(student_scores[student][subj] for subj in subjects)
            total_scores.append((student, total))
        # 按总分降序排序
        total_scores.sort(key=lambda x: x[1], reverse=True)
        # 生成排名字典：学生 -> 名次（1-based）
        ranking = {student: idx + 1 for idx, (student, _) in enumerate(total_scores)}
        
        # 组装记录
        for student in students:
            record = {
                "学生姓名": student,
                "考试日期": exam_date,
                **student_scores[student],  # 把各科成绩展开
                "年级排名": ranking[student]
            }
            records.append(record)
    
    df = pd.DataFrame(records)
    df["考试日期"] = pd.to_datetime(df["考试日期"])  # 转换为日期类型
    df.sort_values(["学生姓名", "考试日期"], inplace=True)  # 按姓名和日期排序
    return df


# 使用 Streamlit 的缓存装饰器，避免每次交互都重新加载/计算数据
@st.cache_data
def load_data(uploaded_file):
    """
    加载用户上传的文件，或返回示例数据（如果未上传文件）。
    
    参数:
        uploaded_file: Streamlit 文件上传对象（可能为 None）
    
    返回:
        pd.DataFrame 或 None: 处理好的数据框，如果文件有问题返回 None。
    
    编程思想：
        - 根据文件扩展名自动选择读取方式（CSV/Excel）。
        - 校验必要列是否存在，防止后续代码出错。
        - 统一转换日期列并排序，确保时间序列正确。
    """
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        try:
            if file_extension == "csv":
                df = pd.read_csv(uploaded_file)
            elif file_extension in ["xlsx", "xls"]:
                df = pd.read_excel(uploaded_file)
            else:
                st.error("不支持的文件格式，请上传 CSV 或 Excel 文件")
                return None
        except Exception as e:
            st.error(f"读取文件失败：{e}")
            return None
        
        # 检查必要列是否齐全
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"上传文件缺少必要列：{missing_cols}")
            return None
        
        # 确保考试日期是日期类型，并按学生、日期排序
        df["考试日期"] = pd.to_datetime(df["考试日期"])
        df.sort_values(["学生姓名", "考试日期"], inplace=True)
        return df
    else:
        # 没有上传文件时使用内置示例数据
        return generate_sample_data()


def download_sample_csv():
    """
    在侧边栏生成一个可下载的示例 CSV 文件链接。
    
    编程思想：
        - 将示例数据转换为 CSV 格式并 Base64 编码，生成 HTML 下载链接。
        - 使用 st.sidebar.markdown 渲染该链接，允许用户点击下载。
    """
    sample_df = generate_sample_data()
    csv_buffer = BytesIO()
    # 使用 utf-8-sig 编码，让 Excel 能正确打开中文
    sample_df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    csv_buffer.seek(0)
    b64 = base64.b64encode(csv_buffer.read()).decode()
    href = f'<a href="data:text/csv;base64,{b64}" download="学生成绩示例数据.csv">📥 点击下载示例CSV文件</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)


def plot_score_trends(student_data, selected_subjects, exam_dates_sorted):
    """
    绘制所选学生各科成绩的趋势折线图。
    
    参数:
        student_data (pd.DataFrame): 仅包含该学生的历次考试数据。
        selected_subjects (list): 用户选择要显示的科目列表。
        exam_dates_sorted (pd.Series): 排序后的考试日期（用于 x 轴）。
    
    返回:
        plotly.graph_objects.Figure 或 None: 绘制好的图表对象。
    
    编程思想：
        - 使用 melt 将宽表（每科一列）转为长表（科目作为类别），符合 plotly 输入要求。
        - 设置合理的 y 轴范围（45-105），让分数变化一目了然。
        - 添加交互提示（hovermode='closest'）和图例。
    """
    if student_data.empty or not selected_subjects:
        return None
    
    # 提取日期和选定科目的成绩，然后转换为长格式
    plot_df = student_data[["考试日期"] + selected_subjects].copy()
    plot_df = plot_df.melt(id_vars=["考试日期"], var_name="科目", value_name="成绩")
    
    fig = px.line(
        plot_df,
        x="考试日期",
        y="成绩",
        color="科目",          # 不同科目用不同颜色
        markers=True,          # 显示数据点
        line_shape="linear",   # 线性连接
        title="各科成绩变化趋势",
        labels={"成绩": "分数", "考试日期": "考试时间"}
    )
    # 调整 y 轴范围，确保所有分数清晰可见
    fig.update_layout(
        yaxis=dict(range=[45, 105], title="成绩 (分)"),
        xaxis_title="考试日期",
        hovermode="closest",   # 鼠标靠近时显示最近点的数据
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def plot_rank_trend(student_data):
    """
    绘制年级排名变化趋势图，y 轴反转（排名1在顶部），并自动标注进退步。
    
    参数:
        student_data (pd.DataFrame): 学生历次考试数据（已按日期排序）
    
    返回:
        plotly.graph_objects.Figure 或 None
    
    编程思想：
        - 使用 plotly.express 画线，然后通过 update_layout 反转 y 轴。
        - 遍历相邻两次考试，计算排名差（正数=进步，负数=退步），添加箭头注释。
        - 箭头颜色：绿色进步，红色退步，让用户一眼看出变化。
    """
    if student_data.empty:
        return None
    
    fig = px.line(
        student_data,
        x="考试日期",
        y="年级排名",
        markers=True,
        line_shape="linear",
        title="年级总排名变化趋势",
        labels={"年级排名": "年级排名 (数值越小越靠前)", "考试日期": "考试时间"}
    )
    # 反转 y 轴，使排名1出现在顶部（视觉上“向上”=进步）
    fig.update_layout(yaxis=dict(autorange="reversed"))
    
    # 添加进步/退步标注
    ranks = student_data["年级排名"].values
    dates = student_data["考试日期"].dt.strftime("%Y-%m-%d").values
    
    for i in range(1, len(ranks)):
        diff = ranks[i-1] - ranks[i]  # 正数表示进步（排名数字变小）
        if diff > 0:
            color = "green"
            arrow = "↑"
            text = f"进步{diff}名"
        elif diff < 0:
            color = "red"
            arrow = "↓"
            text = f"退步{-diff}名"
        else:
            continue
        
        # 在图上添加指向该数据点的箭头注释
        fig.add_annotation(
            x=dates[i],
            y=ranks[i],
            text=f"{arrow} {text}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor=color,
            font=dict(color=color, size=10),
            ax=0,
            ay=-20 if diff > 0 else 20  # 箭头偏移方向
        )
    return fig


# =========================================================================
# 主程序逻辑
# =========================================================================
def main():
    """
    主函数：编排整个 Streamlit 应用的界面和逻辑流程。
    
    步骤：
    1. 侧边栏文件上传和示例下载
    2. 加载数据（用户上传或示例）
    3. 展示数据预览
    4. 用户选择学生和科目
    5. 显示该学生的关键指标卡片
    6. 绘制成绩趋势图和排名趋势图
    7. 展示详细成绩表格
    8. 展示班级整体统计（平均分趋势和排名分布）
    """
    
    # ---- 侧边栏：文件上传和示例下载 ----
    uploaded_file = st.sidebar.file_uploader(
        "上传成绩数据 (.csv / .xlsx)", type=["csv", "xlsx"]
    )
    download_sample_csv()  # 提供示例数据下载
    
    # ---- 加载数据 ----
    df = load_data(uploaded_file)
    if df is None:
        st.warning("请上传有效数据或等待示例数据加载...")
        return  # 数据无效则停止后续渲染
    
    st.success(
        f"✅ 数据加载成功！共 {df['学生姓名'].nunique()} 名学生，"
        f"{df['考试日期'].nunique()} 次月考记录"
    )
    
    # ---- 数据预览（折叠区） ----
    with st.expander("📋 数据预览（最近20行）"):
        st.dataframe(df.head(20), use_container_width=True)
    
    # ---- 获取学生列表 ----
    student_list = sorted(df["学生姓名"].unique())
    if not student_list:
        st.error("未找到任何学生数据")
        return
    
    # ---- 科目选择（默认全部选中） ----
    all_subjects = ["数学", "语文", "英语", "道法", "地理", "生物", "历史"]
    available_subjects = [sub for sub in all_subjects if sub in df.columns]
    
    # 布局分为两列：左侧选学生，右侧选科目
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_student = st.selectbox("👩‍🎓 选择学生", student_list)
    with col2:
        selected_subjects = st.multiselect(
            "📚 选择要展示的科目（成绩趋势图）",
            available_subjects,
            default=available_subjects  # 默认全选
        )
    
    # ---- 过滤出所选学生的数据 ----
    student_df = df[df["学生姓名"] == selected_student].copy()
    student_df = student_df.sort_values("考试日期")
    
    if student_df.empty:
        st.warning("该学生无成绩记录")
        return
    
    # ---- 关键指标卡片 ----
    exam_count = len(student_df)
    latest_rank = student_df.iloc[-1]["年级排名"]
    latest_date = student_df.iloc[-1]["考试日期"].strftime("%Y-%m-%d")
    first_rank = student_df.iloc[0]["年级排名"]
    rank_change = first_rank - latest_rank  # 正数进步，负数退步
    rank_status = (
        f"进步了{rank_change}名" if rank_change > 0
        else f"退步了{-rank_change}名" if rank_change < 0
        else "持平"
    )
    
    st.subheader(f"📈 {selected_student} 的趋势分析")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("参加月考次数", exam_count)
    col_b.metric("最新排名 (日期)", f"{latest_rank} 名 ({latest_date})")
    col_c.metric(
        "排名变化 (首→末)",
        f"{first_rank} → {latest_rank}",
        delta=rank_change,
        delta_color="normal"  # 正数为绿色，负数为红色
    )
    
    # ---- 成绩趋势图 ----
    if selected_subjects:
        score_fig = plot_score_trends(student_df, selected_subjects, student_df["考试日期"])
        if score_fig:
            st.plotly_chart(score_fig, use_container_width=True)
        else:
            st.info("没有选择科目或数据不足")
    else:
        st.info("请至少选择一个科目来查看成绩趋势")
    
    # ---- 年级排名趋势图 ----
    if "年级排名" in student_df.columns:
        rank_fig = plot_rank_trend(student_df)
        st.plotly_chart(rank_fig, use_container_width=True)
    else:
        st.warning("数据中缺少'年级排名'列，无法展示位次趋势")
    
    # ---- 详细月考记录表格 ----
    with st.expander("📋 详细月考记录（含各科成绩及年级排名）"):
        display_cols = ["考试日期"] + available_subjects + ["年级排名"]
        display_df = student_df[display_cols].copy()
        display_df["考试日期"] = display_df["考试日期"].dt.strftime("%Y-%m-%d")
        st.dataframe(display_df, use_container_width=True, height=300)
    
    # ---- 班级整体统计 ----
    with st.expander("📊 班级整体趋势（年级平均分及各科平均分）"):
        # 按考试日期计算各科平均分
        avg_by_exam = df.groupby("考试日期")[available_subjects].mean().reset_index()
        avg_by_exam["考试日期"] = avg_by_exam["考试日期"].dt.strftime("%Y-%m-%d")
        
        if not avg_by_exam.empty:
            # 绘制班级各科平均分趋势
            avg_melt = avg_by_exam.melt(
                id_vars=["考试日期"],
                var_name="科目",
                value_name="班级平均分"
            )
            fig_avg = px.line(
                avg_melt,
                x="考试日期",
                y="班级平均分",
                color="科目",
                markers=True,
                title="班级各科平均分趋势",
                labels={"班级平均分": "平均分", "考试日期": "考试时间"}
            )
            fig_avg.update_layout(yaxis=dict(range=[50, 100]), hovermode="closest")
            st.plotly_chart(fig_avg, use_container_width=True)
            
            # 绘制年级排名箱线图（展示每次考试的排名分布）
            fig_box = go.Figure()
            for exam_date in sorted(df["考试日期"].unique()):
                ranks = df[df["考试日期"] == exam_date]["年级排名"]
                fig_box.add_trace(
                    go.Box(
                        y=ranks,
                        name=exam_date.strftime("%Y-%m-%d"),
                        boxmean='sd'  # 显示标准差
                    )
                )
            fig_box.update_layout(
                title="各次月考年级排名分布（箱线图）",
                yaxis=dict(title="年级排名", autorange="reversed"),
                xaxis_title="考试日期"
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("暂无平均分数据")
    
    # 底部提示
    st.markdown("---")
    st.caption("💡 提示：点击图例可隐藏/显示科目曲线；年级排名图 Y 轴已反转（排名1位于顶部）。")


# =========================================================================
# 程序入口：当脚本直接运行时执行 main()
# =========================================================================
if __name__ == "__main__":
    main()
