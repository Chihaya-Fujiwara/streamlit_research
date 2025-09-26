# 必要なライブラリをインポート
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------
# ページ設定 (サイドバーやページの基本設定)
# st.set_page_config() は一度しか呼び出せないので、最初に記述するのが一般的です。
# -----------------------------------------------------------------
st.set_page_config(
    page_title="研究業績ダッシュボード",   # "アプリ"より"ダッシュボード"の方がデータ可視化のニュアンスに合います
    page_icon="📊",                     # アイコンをデータ分析らしいものに変更
    layout="wide",                     # レイアウトを"wide"にして表示領域を最大化
    initial_sidebar_state="expanded",  # サイドバーを最初から開いた状態に
    
    menu_items={
        'Get Help': 'https://www.streamlit.io',
        'About': "# 研究業績分析アプリ\nこのアプリは研究者の論文リストを可視化し、業績リストをcsvファイルにまとめます。"
    }
)

@st.cache_data()
def summury(name):
    dat_paper = []
    author_total = []
    try:
        for j in range(1,1040,20):

            url = "https://api.researchmap.jp/"+str(name)+"/published_papers?limit=20&start=" + str(j)
            response = requests.get(url)
            jsonData = response.json()

            
            for i in range(len(jsonData['items'])):    
                author_list = []
                try:
                    authors = jsonData['items'][i]['authors']['en']
                except KeyError:
                    authors = jsonData['items'][i]['authors']['ja']

                try:
                    title = jsonData['items'][i]['paper_title']['en']
                except KeyError:
                    title = jsonData['items'][i]['paper_title']['ja']

                try:
                    journal = jsonData['items'][i]['publication_name']['en']
                except KeyError:
                    try:
                        journal = jsonData['items'][i]['publication_name']['ja']
                    except KeyError:
                        journal = ''
                
                date =  jsonData['items'][i]['publication_date']
                
                try:
                    doi = jsonData['items'][i]['identifiers']['doi'][0]
                except KeyError:
                    doi = ''
                
                try:
                    number = jsonData['items'][i]['number']
                
                except KeyError:
                    number = ''
                    
                try:
                    starting_page = jsonData['items'][i]['starting_page']
                    ending_page = jsonData['items'][i]['ending_page']
                    page = starting_page + '-' + ending_page
                    
                except KeyError:
                    starting_page = ''
                    ending_page = ''
                    page = ''

                try:
                    referee = jsonData['items'][i]['referee']
                    check = 'peer reviewed'
                            
                except KeyError:
                    check = ''
                
                try:
                    vol = jsonData['items'][i]['volume']
                except KeyError:
                    vol = ''
                
                for j in range(len(authors)):
                    author = ''.join(authors[j].values())
                    author_list.append(author)
                    author_total.append(author)
                
                
                paper_detail = title+', '+journal
                paper_detail = paper_detail.replace('&lt;sub&gt;', '')
                paper_detail = paper_detail.replace('&lt;/sub&gt;','')
                paper_detail = paper_detail.replace('<inf>','')
                paper_detail = paper_detail.replace('</inf>','')
                paper_detail = paper_detail.replace('<sub>','')
                paper_detail = paper_detail.replace('<sup>','')
                paper_detail = paper_detail.replace('</sup>','')
                paper_detail = paper_detail.replace('</sub>','')
                
                if vol != '':
                    paper_detail = paper_detail + ', ' + vol
                
                if number != '':
                    paper_detail = paper_detail + ' ' + number
                
                if page != '':
                    paper_detail = paper_detail + ' ' + page
                
                if date != '':
                    paper_detail = paper_detail + ' ' + date
                
                author_list = ', '.join(author_list)
                
                #st.write(i)
                #st.write(author_list)
                #st.write(paper_detail+ ' ')
                #st.write('doi: '+doi)
                #st.write(check)
                
                dat_paper.append([author_list,date,paper_detail,'doi: '+doi, check,journal])    

    except ZeroDivisionError as e:
        print('error')
        

    dat_paper = pd.DataFrame(dat_paper)
    dat_paper.columns = 'authors','date','paper','doi','reviewed','journal name'
    
    author_total = pd.DataFrame(author_total)

    return dat_paper, author_total

# -----------------------------------------------------------------
# タイトルとヘッダー
# -----------------------------------------------------------------
st.title("")
st.header("# 研究業績分析アプリ\nこのアプリは研究者のリサーチマップ上の論文リストを可視化し、業績リストをcsvファイルにまとめます。")
st.write("リサーチマップ: https://researchmap.jp/")

st.write("Research mapを基に、https://researchmap.jp/hogehogehoge hogehogehoge部分を確認し、下記にコピーあんどぺーすと")
st.write("Clickをpush後1分程度待機")
st.write("表の右上のダウンロードボタンを押し、csvファイルを保存")

name = st.text_input('hogehogehoge 部分を入力')

# ボタン
if st.button("Click"):
    data = summury(name)
    st.write(data[0])
    journal_counter = data[0]['journal name'].value_counts()
    

    # --- ▼▼▼ ここが修正点 ▼▼▼ ---
    # 1. value_counts()の結果(Series)をDataFrameに変換します
    df_agg = journal_counter.reset_index()

    # 2. DataFrameの列名をPlotlyのコードが期待するものに設定します
    df_agg.columns = ['journal name', 'count']
    # --- ▲▲▲ ここまで ▲▲▲ ---


    # バブルの位置（x, y座標）をランダムに生成
    np.random.seed(0) # 毎回同じ位置にプロットするための乱数固定
    df_agg['x'] = np.random.rand(len(df_agg))
    df_agg['y'] = np.random.rand(len(df_agg))

    # Plotly Expressでバブルチャートを作成
    fig = px.scatter(
        df_agg,
        x='x',
        y='y',
        size='count',          # バブルのサイズ
        color='count',         # バブルの色
        color_continuous_scale='viridis',
        hover_name='journal name', # マウスオーバーで表示する名前
        size_max=100,           # 最大バブルサイズの調整
        title='Journal Publication Counts'
    )

    # レイアウトの調整
    fig.update_traces(textposition='top center') # テキストの位置
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, visible=False), # X軸を非表示
        yaxis=dict(showgrid=False, zeroline=False, visible=False), # Y軸を非表示
        plot_bgcolor='white', # 背景色を白に
        font=dict(size=10),
        width=800,
        height=800,
        title="Kinds of Journal, Total = " + str(len(data[0])) 
    )

    
    
    data[0]['date'] = pd.to_datetime(data[0]['date'], errors='coerce')
    df = data[0]['date'].dt.year


    # 3. グラフ描画: Plotly Expressでヒストグラムを作成
    fig1 = px.histogram(
        df,
        x='date',  # 横軸に'year'列を指定
        title='年別の論文発表数 (Histogram of Publications per Year)',
        labels={'year': '年 (Year)', 'count': '論文数 (Count)'} # 軸ラベルを設定
    )

    # グラフの見た目を調整（棒グラフ同士の間隔を空ける）
    fig1.update_layout(bargap=0.1)

    # グラフを表示
    #fig.show()

    author_counter = data[1].value_counts()

        # --- ▼▼▼ ここが修正点 ▼▼▼ ---
    # 1. value_counts()の結果(Series)をDataFrameに変換します
    df_agg_ = author_counter.reset_index()

    # 2. DataFrameの列名をPlotlyのコードが期待するものに設定します
    df_agg_.columns = ['author', 'count']
    # --- ▲▲▲ ここまで ▲▲▲ ---

    # バブルの位置（x, y座標）をランダムに生成
    np.random.seed(0) # 毎回同じ位置にプロットするための乱数固定
    df_agg_['x'] = np.random.rand(len(df_agg_))
    df_agg_['y'] = np.random.rand(len(df_agg_))

    # Plotly Expressでバブルチャートを作成
    fig2 = px.scatter(
        df_agg_,
        x='x',
        y='y',
        size='count',          # バブルのサイズ
        color='count',         # バブルの色
        color_continuous_scale='viridis',
        hover_name='author', # マウスオーバーで表示する名前
        size_max=100,           # 最大バブルサイズの調整
        title='Journal Publication Counts'
    )

    # レイアウトの調整
    fig2.update_traces(textposition='top center') # テキストの位置

    fig2.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, visible=False), # X軸を非表示
        yaxis=dict(showgrid=False, zeroline=False, visible=False), # Y軸を非表示
        plot_bgcolor='white', # 背景色を白に
        font=dict(size=10),
        width=800,
        height=800,
        title="Co-author"
    )

    col1,col2 = st.columns(2)
    col1.plotly_chart(fig, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig1, use_container_width=True)

