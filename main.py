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
# テーマの取得
if st.get_option("theme.base") == "light":
    theme = "ライトモード"
else:
    theme = "ダークモード"

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

    # 日報データの表示
    for _, report in filtered_report_data.iterrows():
        # 区切り線と背景色を追加
     # 区切り線と背景色を追加
        st.markdown("---")
        st.markdown(f"### {report['title']}")
        st.markdown(f"**日付:** {report['date'].strftime('%Y-%m-%d')}")
        st.markdown(f"**概要:** {report['summary']}")
        st.markdown(f"**コンディション:** {report['condition']}")
        st.markdown("**内容**")
        if pd.notnull(report['report']):
            st.markdown(f"{report['report']}")
        else:
            st.markdown("")
        st.markdown(f"")
        if pd.notnull(report['info']):
            st.markdown(f"**連絡事項:** {report['info']}")
        else:
            st.markdown(f"**連絡事項:** -")
        st.markdown(f"**作成日時:** {report['created_at']}")
        st.markdown(f"**更新日時:** {report['updated_at']}")

        # コメントの表示
        st.markdown("#### コメント")
        report_comments = comment_data[comment_data['report_id']
                                       == report['id']]
        for _, comment in report_comments.iterrows():
            user_name = user_master[user_master['id']
                                    == comment['user_id']]['name'].values[0]
            st.markdown(
                f"{user_name} ({comment['created_at']}): {comment['text']}")
        st.markdown("</div>", unsafe_allow_html=True)
