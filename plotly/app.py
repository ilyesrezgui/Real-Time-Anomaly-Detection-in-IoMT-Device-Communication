import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu 
from IPython.core.display import display, HTML
import math
from collections import deque
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from collections import Counter
import base64
from sklearn.model_selection import train_test_split
from os import getenv
import random
import os
import datetime
from kafka import KafkaConsumer
import seaborn as sns
import json
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix
import joblib 
st.set_page_config(page_title="OST data analysis", page_icon="logo.jpg", layout="wide")
def hide_anchor_link():
    st.markdown(
        body="""
        <style>
            h1 > div > a {
                display: none;
            }
            h2 > div > a {
                display: none;
            }
            h5 > div > a {
                display: none;
            }
            h4 > div > a {
                display: none;
            }
            h5 > div > a {
                display: none;
            }
            h6 > div > a {
                display: none;
            }
        </style>
        """,
         unsafe_allow_html=True,
)




def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

st.markdown("""
        <style>
        .css-15zrgzn {display: none}
        .css-eczf16 {display: none}
        .css-jn99sy {display: none}
        </style>
        """, unsafe_allow_html=True)





link="https://github.com/ilyesrezgui/Real-Time-Anomaly-Detection-in-IoMT-Device-Communication"
image_base64 = get_base64_of_bin_file('git.jpg')
a = f'<div style="background-color:#ee605f;left: 0;top: 0;width: 100%;margin-left: 0px; margin-right: 0px;"><div class="column"style="float: left;width: 15.0%;"><a href="{link}"><img src="data:image/png;base64,{image_base64}"style="width:180px; height:auto;"></a></div><div class="column"style="float: left;width: 70.0%;"><h2  style="margin: 0px 0px 0px 0px;padding: 0px 0px 50px 0px ;text-align: center;font-family:Calibri (Body);"> Open source technology <br/> Data visualization </h2></div><div class="column"style="float: left;width: 15.0%;"></div></div>' 
st.markdown(a, unsafe_allow_html=True)


try:
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        consumer_timeout_ms=100
    )
except Exception as e:
    consumer = []

df = pd.DataFrame()
stframe = st.empty()

for message in consumer:
    try:
        data = message.value
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        stframe.dataframe(df)
        if len(df) > 100:
            df = df.tail(100)
    except Exception as e:
        continue
st.markdown(f'<div class="line" style=" display: inline-block;border-top: 1px solid black;width:  100%;margin-top: 0px; margin-bottom: 20px"></div>', unsafe_allow_html=True)
def ams_f2(df, column, k=20, seed=42):
    random.seed(seed)
    estimates = []

    for _ in range(k):
        h = {}

        def sign(x):
            if x not in h:
                h[x] = random.choice([-1, 1])
            return h[x]

        Z = 0
        for x in df[column]:
            Z += sign(x)

        estimates.append(Z * Z)

    return np.mean(estimates)
class ADWIN:
    def __init__(self, delta=0.002):
        self.delta = delta
        self.window = deque()
        self.width = 0
        self.total = 0.0

    def _epsilon(self, n0, n1):
        n = n0 + n1
        return math.sqrt(
            (1 / (2 * n0)) * math.log(4 * n / self.delta)
        ) + math.sqrt(
            (1 / (2 * n1)) * math.log(4 * n / self.delta)
        )

    def update(self, value):
        self.window.append(value)
        self.width += 1
        self.total += value

        drift_detected = False

        for i in range(1, self.width):
            w0 = list(self.window)[:i]
            w1 = list(self.window)[i:]

            n0, n1 = len(w0), len(w1)
            if n0 == 0 or n1 == 0:
                continue

            mean0 = sum(w0) / n0
            mean1 = sum(w1) / n1

            if abs(mean0 - mean1) > self._epsilon(n0, n1):
                self.window = deque(w1)
                self.width = n1
                self.total = sum(w1)
                drift_detected = True
                break

        return drift_detected
selected = option_menu(
    menu_title=None,
    options=["data analysis", "isolation forest model implementation"],
    icons=["bar-chart-fill", "diagram-3", "table"], 
    orientation="horizontal",
    styles={
        "container": {"margin": "0","max-width": "100%"},
    }
)
features = [
        'Header_Length', 'Protocol Type', 'Time_To_Live', 'Rate',
        'fin_flag_number', 'syn_flag_number', 'psh_flag_number', 'ack_flag_number',
        'syn_count', 'fin_count', 'ack_count', 'rst_count', 'HTTP', 'HTTPS',
        'TCP', 'UDP', 'ICMP', 'Tot sum', 'Min', 'Max', 'IAT', 'Variance', 'Label_Type'
    ]


def page1():
    df=pd.read_csv('data.csv')
    df['Label_Type'] = df['Label'].apply(lambda x: 'normal' if x == 'BENIGN' else 'anomaly')
    df = df.sample(frac=0.4, random_state=42)
    st.header("📊 Data Summary")
    st.dataframe(df.describe())
    col1_row1, col2_row1 = st.columns(2)
    with col1_row1:
        fig = px.histogram(df, x="Label", color="Label", title="Count of Labels")
        st.header("📊 Label Distribution")
        st.plotly_chart(fig)
    with col2_row1:
        fig = px.box(df, x="Label", y='Header_Length', color="Label", title=f'Header_Length by {"Label"}')
        st.plotly_chart(fig)

    col1_row2, col2_row2 = st.columns(2)
    with col1_row2:
        fig = px.box(df, x="Label", y='Time_To_Live', color="Label", title=f'Time_To_Live by {"Label"}')
        st.plotly_chart(fig)
    with col2_row2:
        fig = px.box(df, x="Label", y='HTTP', color="Label", title=f'HTTP by {"Label"}')
        st.plotly_chart(fig)
    fig = plt.figure(figsize=(20, 15))
    sns.heatmap(df.corr(numeric_only=True), cmap="YlGnBu", annot=False)
    st.header("🔍 Correlation Heatmap")
    st.pyplot(fig)
    df["header protocole"] = list(zip(df["Header_Length"], df["Protocol Type"]))

    ams_header_page = ams_f2(df, column="header protocole")
    freq_page = Counter(df["page"])
    exact_f2_page = sum(v * v for v in freq_page.values())

    # Exact F2 for (user, page)
    freq_page = Counter(df["header protocole"])
    exact_f2 = sum(v * v for v in freq_page.values())
    st.subheader("Exact F₂ Values")

    st.write("Exact F₂ (page):", exact_f2_page)
    st.write("Exact F₂ (user, page):", exact_f2)
def page2():
    df=pd.read_csv('data.csv')
    df['Label_Type'] = df['Label'].apply(lambda x: 'normal' if x == 'BENIGN' else 'anomaly')
    df = df.sample(frac=0.4, random_state=42)
    df = df[features]
    try:
        with open("forest.pkl", "rb") as file:
            model = joblib.load(file)
    except FileNotFoundError:
        st.error("Model file not found. Ensure model.pkl is inside /app.")
    except Exception as e:
        st.error(f"Error loading model: {e}")
    X = df.drop(['Label_Type'], axis=1)
    y = df['Label_Type']
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    y_pred_raw = model.predict(X_scaled)
    y_pred_iso = ['anomaly' if x==1 else 'normal' for x in y_pred_raw]
    df_result = X.copy()
    df_result['Label_Type'] = y
    df_result['Predicted'] = y_pred_iso
    cm = confusion_matrix(y, y_pred_iso, labels=['normal', 'anomaly'])
    col1_row1, col2_row1 = st.columns(2)
    with col1_row1:
        fig = px.histogram(
    df_result,
    x="Header_Length",
    color="Label_Type",
    barmode="overlay",
    opacity=0.6,
    title="Distribution of Header_Length by Label Type"
)
        st.plotly_chart(fig)
    with col2_row1:
        fig = px.histogram(
    df_result,
    x="Time_To_Live",
    color="Label_Type",
    barmode="overlay",
    opacity=0.6,
    title="Distribution of Time_To_Live by Label Type")
        st.plotly_chart(fig)
   

    col1_row2, col2_row2 = st.columns(2)
    with col1_row2:
        fig = px.histogram(
    df_result,
    x="HTTP",
    color="Label_Type",
    barmode="overlay",
    opacity=0.6,
    title="Distribution of HTTP by Label Type")
        st.plotly_chart(fig)
   
    with col2_row2:
        fig = px.histogram(
    df_result,
    x="TCP",
    color="Label_Type",
    barmode="overlay",
    opacity=0.6,
    title="Distribution of TCP by Label Type")
        st.plotly_chart(fig)
   
    fig = plt.figure(figsize=(20, 10))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=['normal', 'anomaly'],
        yticklabels=['normal', 'anomaly'])
    

    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')

    st.pyplot(fig)
    adwin = ADWIN(delta=0.01)

    drift_points = []

    for i, x in enumerate(df["value"]):
        if adwin.update(x):
            drift_points.append(i)

    st.subheader("ADWIN Drift Detection")

    st.write("Drift detected at indices:", drift_points)

if selected == "data analysis":
  page1()
if selected == "isolation forest model implementation":
  page2()

