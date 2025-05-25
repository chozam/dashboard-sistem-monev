import pandas as pd
import streamlit as st
import plotly.express as px
import nltk
from wordcloud import WordCloud, STOPWORDS
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from collections import Counter

nltk.download("stopwords")
stopwords_id = set(stopwords.words("indonesian"))
nltk.download("punkt_tab")

st.sidebar.title("Menu Tampilan")

# Data desaa mengembalikan df instagram, tiktok, gmaps
nama_desa = st.sidebar.radio(
    "Pilih Desa Wisata:", ["Nganggring", "Nglanggeran", "Dewi Sinta", "Goa Cemara"]
)
media_sosial = st.sidebar.selectbox(
    "Pilih Media Sosial yang akan Dianalisis:", ["Instagram", "Google Maps", "Tiktok"]
)

dict_desa = {
    "Nganggring": {
        "Instagram": "data instagram/desawisatanganggring_instagram.csv",
        "Google Maps": "gmap-dataset/Desa-Wisata-Nganggring.csv",
        "Tiktok": "data tiktok/desawisata.nganggring_tiktok.csv",
    },
    "Nglanggeran": {
        "Instagram": "data instagram/desawisatanglanggeran_instagram.csv",
        "Google Maps": "gmap-dataset/Desa-Wisata-Nglanggeran.csv",
        "Tiktok": "data tiktok/gunungapipurba_tiktok.csv",
    },
    "Dewi Sinta": {
        "Instagram": "data instagram/desawisata_sitimulyo_instagram.csv",
        "Google Maps": "gmap-dataset/Desa-Wisata-Sitimulyo-Dewi-Sinta.csv",
    },
    "Goa Cemara": {
        "Instagram": "data instagram/goacemarabeach_instagram.csv",
        "Google Maps": "gmap-dataset/Desa-Wisata-Patihan-Goa-Cemara.csv",
        "Tiktok": "data tiktok/safaritrip_goacemara_tiktok.csv",
    },
}

insta_top = {
    "Nganggring": {
        "like": "top_instagram_post/top_like_nganggring.csv",
        "comment": "top_instagram_post/top_like_nganggring.csv",
    },
    "Nglanggeran": {
        "like": "top_instagram_post/top_like_nglanggeran.csv",
        "comment": "top_instagram_post/top_komen_nglanggeran.csv",
    },
    "Dewi Sinta": {
        "like": "top_instagram_post/top_like_sitimulyo.csv",
        "comment": "top_instagram_post/top_like_sitimulyo.csv",
    },
    "Goa Cemara": {
        "like": "top_instagram_post/top_like_goacemara.csv",
        "comment": "top_instagram_post/top_komen_goacemara.csv",
    },
}


# --- Load data sesuai pilihan ---
@st.cache_data
def load_data(name, media_sosial):
    try:
        return pd.read_csv(dict_desa[name][media_sosial])
    except Exception as e:
        raise e


def all_word_cloud(kolom, max_word=12, max_font_size=128):
    corpus = []
    for list_words in kolom.str.split():
        for word in list_words:
            corpus.append(word.lower())
    corpus_text = " ".join(corpus)
    wc = WordCloud(
        background_color="white",
        max_words=max_word,
        stopwords=stopwords_id,
        max_font_size=max_font_size,
        random_state=42,
    )
    wc.generate(corpus_text)
    fig, ax = plt.subplots()
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)


def show_statistik(df):
    st.write("##### **Statistik Deskriptif Likes dan Comments**")
    st.write(df[["total_likes", "total_comments"]].describe().transpose())

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.histogram(
            df,
            x="total_likes",
            nbins=20,
            title="Distribusi Jumlah Likes",
            color_discrete_sequence=px.colors.qualitative.Set2,  # ganti warna palet
        )
        fig1.update_traces(
            marker_line_width=0.5, marker_line_color="black"
        )  # beri outline
        fig1.update_layout(bargap=0.2)  # tambahkan jarak antar bar
        st.plotly_chart(fig1, use_container_width=True)

    # Histogram Jumlah Komentar
    with col2:
        fig2 = px.histogram(
            df,
            x="total_comments",
            nbins=20,
            title="Distribusi Jumlah Komentar",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig2.update_traces(marker_line_width=0.5, marker_line_color="black")
        fig2.update_layout(bargap=0.2)
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.scatter(
        df,
        x="total_likes",
        y="total_comments",
        title="Scatter Plot Interaktif Likes vs Comments",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hover_data=["link_post"],
    )
    st.plotly_chart(fig3, use_container_width=True)


def show_top_posts(df):
    show_chart_likes = st.toggle("Tampilkan chart visual", value=True, key="likes")

    top_likes = df.sort_values(by="total_likes", ascending=False).head(10)
    top_likes["link_post"] = top_likes["link_post"].apply(
        lambda x: x.replace("https://www.instagram.com/", "")
    )
    if show_chart_likes:
        fig1 = px.bar(
            data_frame=top_likes,
            x="total_likes",
            y="link_post",
            title="Top 10 Postingan dengan Likes Terbanyak",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig1.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig1, use_container_width=True)
    else:
        # TAMPILKAN TEKS YANG BISA DISALIN
        st.markdown("### 📝 Salin Label Postingan (Top 10)")
        label_text = "\n".join(
            [
                f"{i+1}. {row['link_post']} — {row['total_likes']} likes"
                for i, row in top_likes.reset_index(drop=True).iterrows()
            ]
        )
        st.text_area("Klik lalu salin:", label_text, height=240)

    show_chart_comment = st.toggle("Tampilkan chart visual", value=True, key="comment")

    top_comments = df.sort_values(by="total_comments", ascending=False).head(10)
    top_comments["link_post"] = top_comments["link_post"].apply(
        lambda x: x.replace("https://www.instagram.com/", "")
    )
    if show_chart_comment:
        fig2 = px.bar(
            data_frame=top_comments,
            x="total_comments",
            y="link_post",
            title="Top 10 Postingan dengan Komentar Terbanyak",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig2.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        # TAMPILKAN TEKS YANG BISA DISALIN
        st.markdown("### 📝 Salin Label Postingan (Top 10)")
        label_text = "\n".join(
            [
                f"{i+1}. {row['link_post']} — {row['total_comments']} comments"
                for i, row in top_comments.reset_index(drop=True).iterrows()
            ]
        )
        st.text_area("Klik lalu salin:", label_text, height=240)


def show_correlation(df):
    corr_matrix = df[["total_likes", "total_comments"]].corr()

    # Buat heatmap interaktif dengan Plotly
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="RdBu_r",  # Sama seperti 'coolwarm'
        aspect="auto",
        title="Korelasi Likes dan Comments",
    )

    st.plotly_chart(fig)


def show_sentiment_distribution(df, judul, key1, key2):
    st.subheader(f"**{judul}**")
    col1, col2, col3 = st.columns([4, 5, 1])  
    with col3:
        chart_type = st.select_slider(label='', options=["Bar", "Pie"], value="Bar", key=key1
        )
    sentiment_counts = (
        df["sentiment"]
        .value_counts()
        .reindex(["positive", "neutral", "negative"], fill_value=0)
    )
    if chart_type == "Bar":
        fig_bar = px.bar(
            x=sentiment_counts.index,
            y=sentiment_counts.values,
            labels={"x": "Sentimen", "y": "Jumlah"},
            color=sentiment_counts.index,
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Distribusi Sentimen",
        )
        st.plotly_chart(fig_bar, use_container_width=True, key=key2)
    else:
        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=sentiment_counts.index,
                    values=sentiment_counts.values,
                    hole=0.3,
                    marker=dict(colors=px.colors.qualitative.Set2),
                    textinfo="label+percent",
                )
            ]
        )
        fig_pie.update_layout(title_text="Distribusi Sentimen (Pie)")
        st.plotly_chart(fig_pie, use_container_width=True, key=key2)


def show_common_words(df, key, judul):
    if len(df) <= 0:
        st.write(f"###### **{judul}**")
        st.write("##### *Tidak ada data valid yang bisa diproses*")
        return
    corpus = []
    df = df.dropna(subset=["clean_comment"])
    for list_words in df["clean_comment"].str.split():
        for word in list_words:
            corpus.append(word.lower())

    word_freq = Counter([word for word in corpus])
    top_words = word_freq.most_common(10)

    words, freqs = zip(*top_words)

    fig = px.bar(
        x=freqs,
        y=words,
        orientation="h",
        labels={"x": "Frekuensi", "y": "Kata"},
        title=judul,
        color=words,
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})

    st.plotly_chart(fig, use_container_width=True, key=key)


# --- Main Content ---
st.title("🏠 Dashboard Analisis Desa Wisata")
st.subheader(f"Menampilkan data Desa: **{nama_desa}**")
st.write(f"Menampilkan Analisis **{media_sosial}**")

try:
    data = load_data(nama_desa, media_sosial)
except Exception as e:
    st.header(f"Data untuk media sosial {media_sosial} tidak ditemukan")
else:
    if media_sosial == "Instagram":
        data["total_likes"] = pd.to_numeric(data["total_likes"], errors="coerce")
        data["total_comments"] = pd.to_numeric(data["total_comments"], errors="coerce")
        data.dropna(subset=["total_likes", "total_comments"], inplace=True)

        tab1, tab2, tab3, tab4 = st.tabs(
            ["Statistik", "Top Postingan", "Analisis Komentar", "Tabel Data"]
        )

        with tab1:
            show_statistik(data)
            show_correlation(data)
        with tab2:
            show_top_posts(data)
        with tab3:
            likes = insta_top[nama_desa]["like"]
            comments = insta_top[nama_desa]["comment"]

            if likes == comments:
                judul = "Like dan Comment Terbanyak"
            else:
                judul = "Like Terbanyak"
            like_df = pd.read_csv(likes)
            like_df = like_df.dropna(subset=['clean_comment'])
            show_sentiment_distribution(
                like_df, judul=f"Analisis Postingan dengan {judul}", key1='likes_slider', key2='likes_dist'
            )
            st.write(f"##### **Common Word pada Postingan dengan {judul}**")
            show_common_words(like_df, key="likes_word", judul=f"Kata yang sering Muncul pada Komentar Postingan dengan {judul}")
            show_common_words(like_df.loc[like_df['sentiment'] == 'positive'], key="pos_word_l", judul=f"Kata Positif yang sering Muncul pada Postingan dengan {judul}")
            show_common_words(like_df.loc[like_df['sentiment'] == 'negative'], key="neg_word_l", judul=f"Kata Negatif yang sering Muncul pada Postingan dengan {judul}")
            show_common_words(like_df.loc[like_df['sentiment'] == 'neutral'], key="net_word_l", judul=f"Kata Netral yang sering Muncul pada Postingan dengan {judul}")
            st.write(f"##### **WordCloud Postingan dengan {judul}**")
            all_word_cloud(like_df['clean_comment'])


            if likes != comments:
                comments_df = pd.read_csv(comments)
                comments_df = comments_df.dropna(subset=['clean_comment'])
                show_sentiment_distribution(
                    comments_df, judul=f"Analisis Postingan dengan Komentar Terbanyak", key1='comment_slider', key2='comment_dist'
                )
                show_common_words(comments_df, key="comment_word", judul='Kata yang sering Muncul pada Komentar Postingan dengan Komentar Terbanyak')
                show_common_words(comments_df.loc[comments_df['sentiment'] == 'positive'], key="pos_word_c", judul=f"Kata Positif yang sering Muncul pada Postingan dengan {judul}")
                show_common_words(comments_df.loc[comments_df['sentiment'] == 'negative'], key="neg_word_c", judul=f"Kata Negatif yang sering Muncul pada Postingan dengan {judul}")
                show_common_words(comments_df.loc[comments_df['sentiment'] == 'neutral'], key="net_word_c", judul=f"Kata Netral yang sering Muncul pada Postingan dengan {judul}")
                
                st.write(f"##### **WordCloud Postingan dengan Komentar Terbanyak**")
                all_word_cloud(comments_df['clean_comment'])
                st.write(f"###### **WordCloud untuk Sentimen Positif**")

        with tab4:
            st.dataframe(data)
    elif media_sosial == "Google Maps":
        tab1, tab2 = st.tabs(
            ["Analisis Ulasan", "Tabel Data"]
        )
        data = data.dropna(subset=['clean_comment'])
        with tab1:
            show_sentiment_distribution(
                data, judul=f"Analisis Ulasan Google Maps", key1='likes_slider', key2='likes_dist'
            )
            show_common_words(data, key="likes_word", judul="Kata yang sering Muncul pada Ulasan Google Maps")
            show_common_words(data.loc[data['sentiment'] == 'positive'], key="pos_word", judul=f"Kata Positif yang sering Muncul pada Ulasan Google Maps")
            show_common_words(data.loc[data['sentiment'] == 'negative'], key="neg_word", judul=f"Kata Negatif yang sering Muncul pada Ulasan Google Maps")
            show_common_words(data.loc[data['sentiment'] == 'neutral'], key="net_word", judul=f"Kata Netral yang sering Muncul pada Ulasan Google Maps")
            st.write(f"##### **WordCloud Ulasan Google Maps**")
            all_word_cloud(data['clean_comment'], max_word=20)
            st.write(f"###### **WordCloud untuk Sentimen Positif**")
            all_word_cloud(data.loc[data['sentiment'] == 'positive'].clean_comment, max_word=20)
            st.write(f"###### **WordCloud untuk Sentimen Negatif**")
            all_word_cloud(data.loc[data['sentiment'] == 'negative'].clean_comment, max_word=20)
            st.write(f"###### **WordCloud untuk Sentimen Netral**")
            all_word_cloud(data.loc[data['sentiment'] == 'neutral'].clean_comment, max_word=20)
        with tab2:
            st.dataframe(data)
    elif media_sosial == "Tiktok":
        tab1, tab2 = st.tabs(
            ["Statistik dan Top Post", "Tabel Data"]
        )
        with tab1:
            st.write("##### **Statistik Deskriptif Total Views Tiktok**")
            st.write(data[['views']].describe().transpose())

            fig1 = px.histogram(
                data,
                x="views",
                nbins=20,
                title="Distribusi Jumlah Likes",
                color_discrete_sequence=px.colors.qualitative.Set2,  # ganti warna palet
            )
            fig1.update_traces(
                marker_line_width=0.5, marker_line_color="black"
            )  # beri outline
            fig1.update_layout(bargap=0.2)  # tambahkan jarak antar bar
            st.plotly_chart(fig1, use_container_width=True)

            show_chart_views = st.toggle("Tampilkan chart visual", value=True, key="views")

            top_views = data.sort_values(by="views", ascending=False).head(10)
            top_views["link"] = top_views["link"].apply(
                lambda x: x.replace("https://www.tiktok.com/", "")
            )
            if show_chart_views:
                # st.subheader("Top 10 Postingan dengan Likes Terbanyak")
                fig2 = px.bar(
                    data_frame=top_views,
                    x="views",
                    y="link",
                    title="Top 10 Postingan dengan Views Terbanyak",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
                fig2.update_layout(yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig2, use_container_width=True)
            else:
                # TAMPILKAN TEKS YANG BISA DISALIN
                st.markdown("### 📝 Salin Label Postingan (Top 10)")
                label_text = "\n".join(
                    [
                        f"{i+1}. {row['link']} — {row['views']} views"
                        for i, row in top_views.reset_index(drop=True).iterrows()
                    ]
                )
                st.text_area("Klik lalu salin:", label_text, height=240)

        with tab2:
            st.dataframe(data)