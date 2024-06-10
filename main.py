import re
from io import StringIO

import pandas as pd
import streamlit as st

# タイトル
st.set_page_config(layout="wide")
st.title('Daily Report App')

# サイドバーにファイルアップロード部品を移動
st.sidebar.title('ファイルアップロード')
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# テーマの設定を取得
background_color = "#121212"
text_color = "#FFFFFF"
secondary_background_color = "#262730"


if uploaded_file is not None:
    try:
        # CSVファイルの読み込み
        file_content = uploaded_file.read().decode("utf-8")
        # セクションごとに分割
        sections = re.split(r'^##\s+', file_content, flags=re.MULTILINE)
        # 各セクションを処理
        data = {}
        for section in sections:
            if section.strip():
                # セクション名を取得
                section_name = section.splitlines()[0].strip()
                # データ部分を抽出
                section_data = section.splitlines()[1:]
                # CSV形式に変換
                csv_data = "\n".join(section_data)
                # Pandas DataFrameに変換
                df = pd.read_csv(StringIO(csv_data), header=0)
                # データを辞書に追加
                data[section_name] = df
    except pd.errors.ParserError as e:
        st.error(f"CSVファイルの読み込み中にエラーが発生しました: {e}")
        st.stop()

    if len(data) != 4:
        st.error("CSVファイルのフォーマットが正しくありません。4つのセクションが必要です。")
        st.stop()

    # ユーザー情報
    user_info = data['ユーザー情報']

    # 日報データ
    report_data = data['日報データ']
    report_data['date'] = pd.to_datetime(report_data['date'])

    # コメントデータ
    comment_data = data['コメントデータ']

    # ユーザーマスタ
    user_master = data['ユーザーマスタ']

    # 日報データの表示
    st.subheader('日報データ')

    # 年月ごとのリンクを表示
    report_data['year_month'] = report_data['date'].dt.strftime('%Y-%m')
    unique_year_months = report_data['year_month'].unique()
    selected_year_month = st.sidebar.selectbox('年月を選択', unique_year_months)

    # 選択された年月の日報データを取得
    filtered_report_data = report_data[report_data['year_month']
                                       == selected_year_month]
    # スタイルの調整を追加
    st.markdown(f"""
        <style>
        .report-title {{
            color: {text_color};
            font-size: 24px;
            font-weight: bold;
        }}
        .report-content {{
            color: {text_color};
            font-size: 16px;
        }}
        .report-label {{
            font-weight: bold;
            color: {text_color};
        }}
        .report-value {{
            background-color: {secondary_background_color};
            color: {text_color};
            padding: 5px;
            border-radius: 5px;
            margin-bottom: 5px;
        }}
        .inline {{
            display: inline-block;
            margin-right: 20px;
        }}
        .comment-section {{
            background-color: {secondary_background_color};
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            border: 1px solid {text_color};
        }}
        .comment {{
            background-color: {secondary_background_color};
            color: {text_color};
            padding: 5px;
            border-radius: 5px;
            margin-bottom: 5px;
        }}
        </style>
        """, unsafe_allow_html=True)

    # 日報データの表示
    for _, report in filtered_report_data.iterrows():
        st.markdown(
            f"<div class='report-title'>{report['title']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='inline'><span class='report-label'>日付:</span> <span class='report-value'>{report['date'].strftime('%Y-%m-%d')}</span></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='inline'><span class='report-label'>作成日時:</span> <span class='report-value'>{report['created_at']}</span></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='inline'><span class='report-label'>更新日時:</span> <span class='report-value'>{report['updated_at']}</span></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='report-label'>概要:</div> <div class='report-value'>{report['summary']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='report-label'>コンディション:</div> <div class='report-value'>{report['condition']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='report-label'>内容:</div>",
                    unsafe_allow_html=True)
        if pd.notnull(report['report']):
            st.markdown(
                f"<div class='report-value'>{report['report']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='report-value'></div>",
                        unsafe_allow_html=True)
        if pd.notnull(report['info']):
            st.markdown(
                f"<div class='report-label'>連絡事項:</div> <div class='report-value'>{report['info']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div class='report-label'>連絡事項:</div> <div class='report-value'>-</div>", unsafe_allow_html=True)

        st.markdown("#### コメント", unsafe_allow_html=True)
        report_comments = comment_data[comment_data['report_id']
                                       == report['id']]
        for _, comment in report_comments.iterrows():
            user_name = user_master[user_master['id']
                                    == comment['user_id']]['name'].values[0]
            st.markdown(
                f"<div class='comment'>{user_name} ({comment['created_at']}): {comment['text']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('---')
