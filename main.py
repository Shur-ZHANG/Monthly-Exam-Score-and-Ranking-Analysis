import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import base64
import random
import numpy as np

# 页面配置
st.set_page_config(page_title="学生月考成绩与位次趋势分析", layout="wide")
st.title("📊 学生月考成绩与年级位次趋势分析")
st.markdown("### 支持数学、语文、英语、道法、地理、生物、历史七大学科的成绩及年级总排名变化趋势可视化")

# 侧边栏说明
st.sidebar.header("📁 数据导入")
st.sidebar.markdown("请上传符合格式的 Excel 或 CSV 文件，列名需包含：")
required_cols = ["学生姓名", "考试日期", "数学", "语文", "英语", "道法", "地理", "生物", "历史", "年级排名"]
st.sidebar.markdown("\n".join([f"- {col}" for col in required_cols]))
st.sidebar.markdown("> 注：考试日期建议格式 YYYY-MM-DD 或 YYYY-MM，程序会自动排序。年级排名数值越小表示排名越靠前。")

# 示例数据生成器（真实总分排名逻辑）
def generate_sample_data():
    """生成示例数据：6名学生，4次月考，成绩合理波动，年级排名基于总分实际计算"""
    students = ["张三", "李四", "王芳", "赵磊", "陈雨桐", "周明"]
    exam_dates = ["2025-03-01", "2025-04-01", "2025-05-01", "2025-06-01"]
    subjects = ["数学", "语文", "英语", "道法", "地理", "生物", "历史"]
    
    # 为每个学生设定基础能力（均值），后续成绩围绕均值波动
    ability = {student: {subj: random.randint(65, 92) for subj in subjects} for student in students}
    # 再给每个学生一个进步因子（随时间略微提升或下降）
    trend_factor = {student: random.uniform(-1.5, 3.0) for student in students}
    
    records = []
    for exam_date in exam_dates:
        exam_idx = exam_dates.index(exam_date)
        student_scores = {}
        for student in students:
            scores = {}
            for subj in subjects:
                base = ability[student][subj]
                # 随考试次数波动，加入进步/退步趋势和随机噪声
                variation = trend_factor[student] * (exam_idx + 1) * 0.6 + random.uniform(-5, 6)
                score = base + variation
                score = max(45, min(100, score))  # 限制在45-100之间
                scores[subj] = round(score, 1)
            student_scores[student] = scores
        # 计算总分并排名
        total_scores = []
        for student in students:
            total = sum(student_scores[student][subj] for subj in subjects)
            total_scores.append((student, total))
        # 按总分降序排序，排名数值小为优
        total_scores.sort(key=lambda x: x[1], reverse=True)
        ranking = {student: idx+1 for idx, (student, _) in enumerate(total_scores)}
        # 生成记录
        for student in students:
            record = {
                "学生姓名": student,
                "考试日期": exam_date,
                **student_scores[student],
                "年级排名": ranking[student]
            }
            records.append(record)
    df = pd.DataFrame(records)
    # 转换为日期类型
    df["考试日期"] = pd.to_datetime(df["考试日期"])
    df.sort_values(["学生姓名", "考试日期"], inplace=True)
    return df

# 数据加载和缓存
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        if file_extension == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_extension in ["xlsx", "xls"]:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("不支持的文件格式，请上传 CSV 或 Excel 文件")
            return None
        # 检查必要列
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"上传文件缺少必要列：{missing_cols}")
            return None
        # 确保考试日期是日期类型，并排序
        df["考试日期"] = pd.to_datetime(df["考试日期"])
        df.sort_values(["学生姓名", "考试日期"], inplace=True)
        return df
    else:
        # 默认使用示例数据
        return generate_sample_data()

# 下载示例CSV
def download_sample_csv():
    sample_df = generate_sample_data()
    csv_buffer = BytesIO()
    sample_df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    csv_buffer.seek(0)
    b64 = base64.b64encode(csv_buffer.read()).decode()
    href = f'<a href=" " download="学生成绩示例数据.csv">📥 点击下载示例CSV文件</a >'
    st.sidebar.markdown(href, unsafe_allow_html=True)

# 成绩趋势图（各科目折线图，支持多选科目）
def plot_score_trends(student_data, selected_subjects, exam_dates_sorted):
    # 提取成绩数据并转为长格式
    if student_data.empty or not selected_subjects:
        return None
    plot_df = student_data[["考试日期"] + selected_subjects].copy()
    plot_df = plot_df.melt(id_vars=["考试日期"], var_name="科目", value_name="成绩")
    fig = px.line(
        plot_df, x="考试日期", y="成绩", color="科目",
        markers=True, line_shape="linear",
        title="各科成绩变化趋势",
        labels={"成绩": "分数", "考试日期": "考试时间"}
    )
    fig.update_layout(
        yaxis=dict(range=[45, 105], title="成绩 (分)"),
        xaxis_title="考试日期",
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

# 年级排名趋势图（y轴反转，排名1在最上方）
def plot_rank_trend(student_data):
    if student_data.empty:
        return None
    fig = px.line(
        student_data, x="考试日期", y="年级排名",
        markers=True, line_shape="linear",
        title="年级总排名变化趋势",
        labels={"年级排名": "年级排名 (数值越小越靠前)", "考试日期": "考试时间"}
    )
    # 反转y轴
    fig.update_yaxes(autorange="reversed")
    # 标注进步/退步
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
        fig.add_annotation(
            x=dates[i], y=ranks[i],
            text=f"{arrow} {text}",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor=color,
            font=dict(color=color, size=10),
            ax=0, ay=-20 if diff > 0 else 20
        )
    return fig

# 主程序
def main():
    # 侧边栏：文件上传和下载示例
    uploaded_file = st.sidebar.file_uploader("上传成绩数据 (.csv / .xlsx)", type=["csv", "xlsx"])
    download_sample_csv()
    
    # 加载数据
    df = load_data(uploaded_file)
    if df is None:
        st.warning("请上传有效数据或等待示例数据加载...")
        return
    
    st.success(f"✅ 数据加载成功！共 {df['学生姓名'].nunique()} 名学生，{df['考试日期'].nunique()} 次月考记录")
    
    # 数据概览
    with st.expander("📋 数据预览（最近20行）"):
        st.dataframe(df.head(20), use_container_width=True)
    
    # 获取学生列表
    student_list = sorted(df["学生姓名"].unique())
    if not student_list:
        st.error("未找到任何学生数据")
        return
    
    # 多科目选择（默认选择全部7科）
    all_subjects = ["数学", "语文", "英语", "道法", "地理", "生物", "历史"]
    available_subjects = [sub for sub in all_subjects if sub in df.columns]
    
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_student = st.selectbox("👩‍🎓 选择学生", student_list)
    with col2:
        selected_subjects = st.multiselect(
            "📚 选择要展示的科目（成绩趋势图）",
            available_subjects,
            default=available_subjects  # 默认全选
        )
    
    # 过滤该学生的数据
    student_df = df[df["学生姓名"] == selected_student].copy()
    student_df = student_df.sort_values("考试日期")
    
    if student_df.empty:
        st.warning("该学生无成绩记录")
        return
    
    # 显示学生基本信息：考试次数、最新排名
    exam_count = len(student_df)
    latest_rank = student_df.iloc[-1]["年级排名"]
    latest_date = student_df.iloc[-1]["考试日期"].strftime("%Y-%m-%d")
    first_rank = student_df.iloc[0]["年级排名"]
    rank_change = first_rank - latest_rank  # 正数进步
    rank_status = f"进步了{rank_change}名" if rank_change > 0 else f"退步了{-rank_change}名" if rank_change < 0 else "持平"
    
    st.subheader(f"📈 {selected_student} 的趋势分析")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("参加月考次数", exam_count)
    col_b.metric("最新排名 (日期)", f"{latest_rank} 名 ({latest_date})")
    col_c.metric("排名变化 (首→末)", f"{first_rank} → {latest_rank}", delta=rank_change, delta_color="normal")
    
    # 成绩趋势图
    if selected_subjects:
        score_fig = plot_score_trends(student_df, selected_subjects, student_df["考试日期"])
        if score_fig:
            st.plotly_chart(score_fig, use_container_width=True)
        else:
            st.info("没有选择科目或数据不足")
    else:
        st.info("请至少选择一个科目来查看成绩趋势")
    
    # 年级排名趋势图
    if "年级排名" in student_df.columns:
        rank_fig = plot_rank_trend(student_df)
        st.plotly_chart(rank_fig, use_container_width=True)
    else:
        st.warning("数据中缺少'年级排名'列，无法展示位次趋势")
    
    # 显示详细成绩表格（每次月考的所有科目及排名）
    with st.expander("📋 详细月考记录（含各科成绩及年级排名）"):
        display_cols = ["考试日期"] + available_subjects + ["年级排名"]
        display_df = student_df[display_cols].copy()
        display_df["考试日期"] = display_df["考试日期"].dt.strftime("%Y-%m-%d")
        st.dataframe(display_df, use_container_width=True, height=300)
    
    # 额外统计：与年级平均对比（基于全部数据的每次考试平均分，仅做参考）
    with st.expander("📊 班级整体趋势（年级平均分及各科平均分）"):
        avg_by_exam = df.groupby("考试日期")[available_subjects].mean().reset_index()
        avg_by_exam["考试日期"] = avg_by_exam["考试日期"].dt.strftime("%Y-%m-%d")
        # 绘制班级平均分趋势
        if not avg_by_exam.empty:
            avg_melt = avg_by_exam.melt(id_vars=["考试日期"], var_name="科目", value_name="班级平均分")
            fig_avg = px.line(
                avg_melt, x="考试日期", y="班级平均分", color="科目",
                markers=True, title="班级各科平均分趋势",
                labels={"班级平均分": "平均分", "考试日期": "考试时间"}
            )
            fig_avg.update_layout(yaxis=dict(range=[50, 100]), hovermode="closest")
            st.plotly_chart(fig_avg, use_container_width=True)
            
            # 年级排名分布（箱线图）
            rank_box_data = df.groupby("考试日期")["年级排名"].apply(list).reset_index()
            # 准备箱线图数据
            fig_box = go.Figure()
            for _, row in rank_box_data.iterrows():
                exam_date = row["考试日期"].strftime("%Y-%m-%d")
                ranks = row["年级排名"]
                fig_box.add_trace(go.Box(y=ranks, name=exam_date, boxmean='sd'))
            fig_box.update_layout(
                title="各次月考年级排名分布（箱线图）",
                yaxis=dict(title="年级排名", autorange="reversed"),
                xaxis_title="考试日期"
            )
            st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.info("暂无平均分数据")
    
    st.markdown("---")
    st.caption("💡 提示：点击图例可隐藏/显示科目曲线；年级排名图Y轴已反转（排名1位于顶部）。")

if __name__ == "__main__":
    main()