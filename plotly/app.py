import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu 
from IPython.core.display import display, HTML
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64
from sklearn.model_selection import train_test_split
from os import getenv
import os
import datetime
from kafka import KafkaConsumer
import seaborn as sns
import json
import matplotlib.pyplot as plt
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
selected = option_menu(
    menu_title=None,
    options=["data analysis","auto enconder model implementation", "isolation forest model implementation"],
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
    st.header("📊 Data Summary")
    df=pd.read_csv('data.csv')
    
    df['Label_Type'] = df['Label'].apply(lambda x: 'normal' if x == 'BENIGN' else 'anomaly')
   
    df = df.sample(frac=0.4, random_state=42)
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
def page2():
    df=pd.read_csv('data.csv')
def page3():
    df=pd.read_csv('data.csv')

if selected == "data analysis":
  page1()
if selected == "auto enconder model implementation":
  page2()
if selected == "isolation forest model implementation":
  page3()

