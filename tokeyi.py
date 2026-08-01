# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import random

# Page configuration
st.set_page_config(
    page_title="東洋養生ナビ - 黄帝内経 x 傷寒論",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Dark Oriental Medical Theme)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0c0a09;
        color: #f5f5f4;
    }
    .main-header {
        background: linear-gradient(135deg, #1c1917 0%, #292524 100%);
        border: 1px solid #78350f;
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .header-title {
        color: #fbbf24;
        font-size: 2.2rem;
        font-weight: 900;
        margin: 0;
    }
    .header-subtitle {
        color: #a8a29e;
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }
    .oriental-card {
        background-color: #1c1917;
        border: 1px solid #44403c;
        border-radius: 1rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .badge-amber {
        background-color: #451a03;
        color: #fbbf24;
        border: 1px solid #92400e;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .badge-emerald {
        background-color: #064e3b;
        color: #34d399;
        border: 1px solid #047857;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .stButton>button {
        background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%);
        color: #0c0a09;
        font-weight: 800;
        border: 1px solid #fef3c7;
        border-radius: 0.75rem;
        padding: 0.5rem 1.25rem;
    }
    .stButton>button:hover {
        filter: brightness(1.1);
        color: #0c0a09;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Session State Initializations
if "wood" not in st.session_state:
    st.session_state.wood = 65
if "fire" not in st.session_state:
    st.session_state.fire = 70
if "earth" not in st.session_state:
    st.session_state.earth = 50
if "metal" not in st.session_state:
    st.session_state.metal = 60
if "water" not in st.session_state:
    st.session_state.water = 55

if "shanghan_type" not in st.session_state:
    st.session_state.shanghan_type = "太陽病 (たいようびょう)"

if "fortune" not in st.session_state:
    st.session_state.fortune = None

if "xp" not in st.session_state:
    st.session_state.xp = 120

# Header Banner
st.markdown(
    """
    <div class="main-header">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div>
                <span class="badge-amber">東洋医学 x 現代食養生</span>
                <h1 class="header-title">🌿 東洋養生ナビ (Streamlit版)</h1>
                <p class="header-subtitle">黄帝内経 (子午流注) & 傷寒論 六病体質診断 --- 無薬・食養生・生活習慣アドバイザー</p>
            </div>
            <div>
                <span class="badge-emerald">Level 2 養生実践者 (XP: {} / 300)</span>
            </div>
        </div>
    </div>
    """.format(st.session_state.xp),
    unsafe_allow_html=True,
)

# Sidebar Navigation
st.sidebar.title("🧭 養生ナビゲーション")
page = st.sidebar.radio(
    "メニューを選択",
    [
        "📊 総合ダッシュボード & 五行診断",
        "🩺 傷寒論 体質診断アンケート",
        "⏰ 黄帝内経 子午流注 (24時間時計)",
        "🥠 デイリーおみくじ & 養生クエスト",
        "📋 GitHub用 Python (Streamlit) 全コード",
    ],
)

# ------------------------------------------------------------------
# Page 1: 総合ダッシュボード & 五行診断
# ------------------------------------------------------------------
if page == "📊 総合ダッシュボード & 五行診断":
    st.subheader("📊 あなたの五行バランス (5 Elements Balance)")
    st.write("生年月日または現在の体調から、木・火・土・金・水バランスを調整・確認できます。")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### ⚙️ 五行スコア調整")
        st.session_state.wood = st.slider("🌲 木 (Wood / 肝・胆)", 0, 100, st.session_state.wood)
        st.session_state.fire = st.slider("🔥 火 (Fire / 心・小腸)", 0, 100, st.session_state.fire)
        st.session_state.earth = st.slider("⛰️ 土 (Earth / 脾・胃)", 0, 100, st.session_state.earth)
        st.session_state.metal = st.slider("⚔️ 金 (Metal / 肺・大腸)", 0, 100, st.session_state.metal)
        st.session_state.water = st.slider("💧 水 (Water / 腎・膀胱)", 0, 100, st.session_state.water)

        # Birthdate Calculation Form
        st.markdown("---")
        st.markdown("#### 🎂 生年月日による自動判定")
        birth_date = st.date_input("生年月日を選択", datetime.date(1995, 5, 15))
        if st.button("生年月日から五行を算出"):
            # Simple algorithmic element mapping
            year = birth_date.year
            month = birth_date.month
            day = birth_date.day
            st.session_state.wood = (year * 3 + day) % 60 + 40
            st.session_state.fire = (month * 7 + year) % 55 + 45
            st.session_state.earth = (day * 5 + month) % 50 + 50
            st.session_state.metal = (year + month + day) % 65 + 35
            st.session_state.water = (day * 11) % 60 + 40
            st.success("生年月日からの五行バランスを更新しました！")
            if hasattr(st, "rerun"):
                st.rerun()
            elif hasattr(st, "experimental_rerun"):
                st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Plotly Radar Chart
        categories = ["木 (肝)", "火 (心)", "土 (脾)", "金 (肺)", "水 (腎)"]
        values = [
            st.session_state.wood,
            st.session_state.fire,
            st.session_state.earth,
            st.session_state.metal,
            st.session_state.water,
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                fillcolor="rgba(251, 191, 36, 0.25)",
                line=dict(color="#fbbf24", width=3),
                name="現在の五行バランス",
            )
        )
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#a8a29e"),
                angularaxis=dict(color="#fbbf24", font=dict(size=14, color="#fbbf24")),
                bgcolor="#1c1917",
            ),
            paper_bgcolor="#0c0a09",
            plot_bgcolor="#0c0a09",
            margin=dict(l=40, r=40, t=20, b=20),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    # 5 Elements Lucky Prescriptions
    st.markdown("---")
    st.subheader("💎 あなたの五行 ラッキー属性 & 養生処方")
    
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    
    with col_a:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 🌲 木 (Wood)")
        st.write(f"**スコア**: {st.session_state.wood}")
        st.write("**ラッキー天然石**: アベンチュリン, エメラルド")
        st.write("**養生色**: 青・緑")
        st.write("**おすすめ食材**: 酢・シソ・緑黄色野菜")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 🔥 火 (Fire)")
        st.write(f"**スコア**: {st.session_state.fire}")
        st.write("**ラッキー天然石**: カーネリアン, ルビー")
        st.write("**養生色**: 赤・朱色")
        st.write("**おすすめ食材**: トマト・ゴーヤ・小豆")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_c:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### ⛰️ 土 (Earth)")
        st.write(f"**スコア**: {st.session_state.earth}")
        st.write("**ラッキー天然石**: タイガーアイ, トパーズ")
        st.write("**養生色**: 黄・ベージュ")
        st.write("**おすすめ食材**: かぼちゃ・サツマイモ・蜂蜜")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_d:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### ⚔️ 金 (Metal)")
        st.write(f"**スコア**: {st.session_state.metal}")
        st.write("**ラッキー天然石**: 水晶, パール")
        st.write("**養生色**: 白・シルバー")
        st.write("**おすすめ食材**: 大根・豆腐・白ごま")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_e:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 💧 水 (Water)")
        st.write(f"**スコア**: {st.session_state.water}")
        st.write("**ラッキー天然石**: ラピスラズリ, オニキス")
        st.write("**養生色**: 黒・紺色")
        st.write("**おすすめ食材**: 黒ごま・黒豆・昆布")
        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Page 2: 傷寒論 体質診断アンケート
# ------------------------------------------------------------------
elif page == "🩺 傷寒論 体質診断アンケート":
    st.subheader("🩺 傷寒論 (しょうかんろん) 六病 体質診断")
    st.write("以下の質問に回答すると、あなたに最適な傷寒論タイプと無薬食養生アドバイスを出力します。")

    with st.form("shanghan_form"):
        st.markdown("#### 1. 風邪の初期症状や現在の体調で一番近いものは？")
        q1 = st.radio(
            "選択してください",
            [
                "ゾクゾクする寒気、首や肩のこり、頭痛がある (太陽病)",
                "高熱、顔の火照り、強い喉の渇き、大汗をかく (陽明病)",
                "寒気と熱っぽさが交互に来る、口が苦い、脇腹が張る (少陽病)",
                "お腹が冷えて張る、軟便や下痢をしやすい (太陰病)",
                "手足が氷のように冷える、体がだるく横になりたい (少陰病)",
                "上熱下寒 (のぼせと足冷え)、激しい頭痛や嘔気 (厥陰病)",
            ],
        )

        st.markdown("#### 2. 日常の胃腸や冷えの状態は？")
        q2 = st.multiselect(
            "当てはまるものを全て選択",
            [
                "首や背中が冷えやすい",
                "冷たい水や炭酸飲料をよく飲みたくなる",
                "ストレスで胃がキリキリ痛みやすい",
                "温かいスープやお粥を食べると落ち着く",
                "朝起きるのが辛く体力がない",
                "手足の末端が一年中冷えている",
            ],
        )

        submitted = st.form_submit_button("診断結果を出す")

    if submitted:
        if "太陽病" in q1:
            st.session_state.shanghan_type = "太陽病 (たいようびょう)"
        elif "陽明病" in q1:
            st.session_state.shanghan_type = "陽明病 (ようめいびょう)"
        elif "少陽病" in q1:
            st.session_state.shanghan_type = "少陽病 (しょうようびょう)"
        elif "太陰病" in q1:
            st.session_state.shanghan_type = "太陰病 (たいいんびょう)"
        elif "少陰病" in q1:
            st.session_state.shanghan_type = "少陰病 (しょういんびょう)"
        else:
            st.session_state.shanghan_type = "厥陰病 (けついんびょう)"

    # Display Current Shanghan Prescription
    st.markdown("---")
    st.markdown(f"### 📜 診断結果: <span style='color:#fbbf24;'>{st.session_state.shanghan_type}</span>", unsafe_allow_html=True)

    shanghan_data = {
        "太陽病 (たいようびょう)": {
            "desc": "体表に寒邪が侵入している状態。発汗・発散により表邪を取り除くことが養生の鍵です。",
            "prescription": "生姜湯・ねぎ湯・葛湯",
            "acupoint": "風池 (ふうち)・大椎 (だいつい)",
            "foods": "生姜、ネギ、葛粉、シナモン、紫蘇",
            "habit": "首の後ろと肩を蒸しタオルで温め、じんわり汗をかいて早めに就寝する。",
        },
        "陽明病 (ようめいびょう)": {
            "desc": "体内 (胃腸) に強い熱がこもっている状態。清熱と生津 (水分補給) が必要です。",
            "prescription": "夏みかん・緑茶・豆腐養生",
            "acupoint": "曲池 (きょくち)・内庭 (ないてい)",
            "foods": "大根、豆腐、トマト、きゅうり、緑茶、梨",
            "habit": "油っこい食事を控え、水分補給をこまめに行い胃腸の熱を冷ます。",
        },
        "少陽病 (しょうようびょう)": {
            "desc": "半表半裏 (自律神経・気機) の滞り。和解・理気による気のスムーズな巡りが重要です。",
            "prescription": "紫蘇レモン・陳皮ハーブ茶",
            "acupoint": "陽陵泉 (ようりょうせん)・太衝 (たいしょう)",
            "foods": "陳皮、紫蘇、柑橘類、セロリ、ジャスミン茶",
            "habit": "深呼吸を意識し、香りの良いハーブティーでストレスを緩和する。",
        },
        "太陰病 (たいいんびょう)": {
            "desc": "脾胃 (消化器) が冷えて水分代謝が低下している状態。温中健脾 (腹部を温める) が必須。",
            "prescription": "人参かぼちゃ粥・乾姜スープ",
            "acupoint": "足三里 (あしさんり)・中脘 (ちゅうかん)",
            "foods": "かぼちゃ、サツマイモ、長芋、生姜、ヒノヒカリ粥",
            "habit": "冷たい飲食を徹底的に避け、腹巻きや湯たんぽでお腹を保温する。",
        },
        "少陰病 (しょういんびょう)": {
            "desc": "心腎の陽気が著しく低下した寒証。温陽補気 (根本的な熱の補給) が必要です。",
            "prescription": "黒ごま足湯・シナモン紅茶",
            "acupoint": "湧泉 (ゆうせん)・関元 (かんげん)",
            "foods": "黒ごま、ニラ、羊肉、シナモン、核桃 (クルミ)",
            "habit": "就寝前に熱めの足湯を行い、22時までに布団に入り体力を回復する。",
        },
        "厥陰病 (けついんびょう)": {
            "desc": "寒熱が錯雑し、手足の末端が極度に冷える状態。暖肝温経 (血行促進と寒気の解消) が重要。",
            "prescription": "当帰なつめ茶・和漢スパイス湯",
            "acupoint": "太衝 (たいしょう)・三陰交 (さんいんこう)",
            "foods": "なつめ、当帰茶、山椒、生姜、黒糖",
            "habit": "手首・足首・首の「三つの首」を温め、軽いストレッチで血流を促す。",
        },
    }

    info = shanghan_data.get(st.session_state.shanghan_type, shanghan_data["太陽病 (たいようびょう)"])

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 📖 体質の特徴")
        st.write(info["desc"])
        st.markdown("#### 🍵 無薬 食養生処方")
        st.write(f"**おすすめ養生食**: {info['prescription']}")
        st.write(f"**適した食材**: {info['foods']}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_res2:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 📍 おすすめ特効穴 (ツボ)")
        st.write(f"**ツボ名**: {info['acupoint']}")
        st.markdown("#### 🧘 生活習慣アドバイス")
        st.write(info["habit"])
        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Page 3: 黄帝内経 子午流注 (24時間時計)
# ------------------------------------------------------------------
elif page == "⏰ 黄帝内経 子午流注 (24時間時計)":
    st.subheader("⏰ 黄帝内経 子午流注 (しごるちゅう) 24時間 臓腑時間")
    st.write("古代中国医学の知恵「子午流注」に基づき、2時間ごとの経絡・臓腑の活発化時間帯に合わせた生活リズムを提案します。")

    now = datetime.datetime.now()
    current_hour = now.hour

    clock_data = [
        {"time": "23:00-01:00", "organ": "子時 (胆経)", "desc": "細胞の修復と骨髄の造血。熟睡が必要不可欠。"},
        {"time": "01:00-03:00", "organ": "丑時 (肝経)", "desc": "血液の浄化と解毒。起きてはいけない時間。"},
        {"time": "03:00-05:00", "organ": "寅時 (肺経)", "desc": "気血を全身へ巡らせる。深い呼吸が効果的。"},
        {"time": "05:00-07:00", "organ": "卯時 (大腸経)", "desc": "排泄の最高時間。コップ1杯のぬるま湯を飲む。"},
        {"time": "07:00-09:00", "organ": "辰時 (胃経)", "desc": "消化吸収が高まる。温かく栄養豊富な朝食をとる。"},
        {"time": "09:00-11:00", "organ": "巳時 (脾経)", "desc": "食べたものを気血に変える。頭脳労働に最適。"},
        {"time": "11:00-13:00", "organ": "午時 (心経)", "desc": "気血の循環と精神の安定。15-30分の昼寝を推し進める。"},
        {"time": "13:00-15:00", "organ": "未時 (小腸経)", "desc": "清濁の分別 (水分補給)。白湯を多めに飲む。"},
        {"time": "15:00-17:00", "organ": "申時 (膀胱経)", "desc": "代謝活動のピーク。運動や仕事・勉強の効率最大。"},
        {"time": "17:00-19:00", "organ": "酉時 (腎経)", "desc": "生命力 (精) の蓄積。軽い散歩や足湯で腎を補う。"},
        {"time": "19:00-21:00", "organ": "戌時 (心包経)", "desc": "心をリラックス。家族や親しい人と穏やかに過ごす。"},
        {"time": "21:00-23:00", "organ": "亥時 (三焦経)", "desc": "全身の気を整え睡眠へ。電子機器を避け就寝準備。"},
    ]

    st.markdown(f"**現在時刻**: {now.strftime('%H:%M')} (日本標準時)")

    for c in clock_data:
        # Check active hour range
        start_h = int(c["time"].split(":")[0])
        end_h = int(c["time"].split("-")[1].split(":")[0])
        
        is_current = False
        if start_h == 23:
            is_current = (current_hour >= 23 or current_hour < 1)
        elif start_h <= current_hour < end_h:
            is_current = True

        border_color = "#fbbf24" if is_current else "#44403c"
        bg_color = "#451a03" if is_current else "#1c1917"

        st.markdown(
            f"""
            <div style="background-color: {bg_color}; border: 2px solid {border_color}; border-radius: 0.75rem; padding: 1rem; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.1rem; font-weight: 800; color: #fbbf24;">{c['time']} 【{c['organ']}】</span>
                    {'<span class="badge-amber">🔥 NOW アクティブ</span>' if is_current else ''}
                </div>
                <p style="margin-top: 0.5rem; font-size: 0.9rem; color: #d6d3d1;">{c['desc']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ------------------------------------------------------------------
# Page 4: デイリーおみくじ & 養生クエスト
# ------------------------------------------------------------------
elif page == "🥠 デイリーおみくじ & 養生クエスト":
    st.subheader("🥠 東洋養生 おみくじ & 今日のクエスト")

    col_f1, col_f2 = st.columns([1, 1])

    with col_f1:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### 🥠 本日の養生おみくじ")

        if st.button("おみくじを引く"):
            fortunes = [
                {"result": "大吉 (大平穏)", "text": "気血が満ち溢れる最高の一日。白湯を飲んで心身を整えましょう。"},
                {"result": "中吉 (中和養生)", "text": "脾胃をいたわる日。消化の良い温かい食べ物が吉を呼びます。"},
                {"result": "小吉 (静心養気)", "text": "少し肩の力を抜いて、深呼吸と足湯でリフレッシュしましょう。"},
                {"result": "吉 (順天応時)", "text": "自然のリズムに合わせて早寝早起きを。散歩がおすすめ。"},
            ]
            st.session_state.fortune = random.choice(fortunes)

        if st.session_state.fortune:
            f = st.session_state.fortune
            st.markdown(f"### <span style='color:#fbbf24;'>{f['result']}</span>", unsafe_allow_html=True)
            st.write(f["text"])
        else:
            st.write("「おみくじを引く」ボタンを押して、今日の養生メッセージを受け取ってください。")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_f2:
        st.markdown("<div class='oriental-card'>", unsafe_allow_html=True)
        st.markdown("#### ✅ 本日の養生クエスト (+20 XP)")

        q_c1 = st.checkbox("朝起きたらコップ1杯の白湯 (ぬるま湯) を飲む")
        q_c2 = st.checkbox("昼休みや休憩時に3分間の深呼吸 (腹式呼吸)")
        q_c3 = st.checkbox("就寝前にぬるめのお湯で足湯を行う")

        if st.button("クエスト完了を記録 (+XP)"):
            count = sum([q_c1, q_c2, q_c3])
            st.session_state.xp += count * 20
            st.success(f"{count} 個のクエスト完了！ XPを +{count * 20} 獲得しました。")
        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------------
# Page 5: GitHub用 Python (Streamlit) 全コード
# ------------------------------------------------------------------
elif page == "📋 GitHub用 Python (Streamlit) 全コード":
    st.subheader("📋 Streamlit (Python) ソースコード全取得")
    st.write("GitHubやStreamlit Cloudにそのままデプロイできる `app.py` および `requirements.txt` のコードです。")

    st.markdown("#### 1. `requirements.txt` の内容")
    st.code(
        """streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0""",
        language="text",
    )

    st.markdown("#### 2. `app.py` の全ソースコード")
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            full_code = f.read()
        st.code(full_code, language="python")
    except Exception:
        st.info("💡 アプリ画面上の「コード閲覧＆GitHub用コピー」ボタンより `app.py` の全ソースコードをワンクリックでコピー可能です。")
