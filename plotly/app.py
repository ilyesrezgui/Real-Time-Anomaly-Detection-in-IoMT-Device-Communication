import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from IPython.core.display import display, HTML
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import base64
from os import getenv
import os
import datetime

st.set_page_config(page_title="My Streamlit App", layout="centered")

st.title("🚀 Welcome to My Streamlit App")
st.write("This is a simple example Streamlit page.")
