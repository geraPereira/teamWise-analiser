
import streamlit as st
import pandas as pd
import numpy as np
import math

st.set_page_config(page_title="Retrô – Match Insights", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data/events.csv")

def simple_xg(distance, angle, header):
    z = -3.0 + (-0.08 * distance) + (0.8 * (angle)) + (-0.6 * header)
    return 1/(1+math.exp(-z))

df = load_data()
st.title("Retrô – Match Insights (Demo)")
st.caption("Substitua os dados em data/events.csv ou use o uploader abaixo.")

ul = st.file_uploader("Carregar CSV de eventos", type=["csv"])
if ul:
    df = pd.read_csv(ul)

shots = df[df["event_type"]=="shot"].copy()
if not shots.empty:
    shots["xg"] = shots.apply(lambda r: simple_xg(r.get("distance",0), r.get("angle",0), r.get("header",0)), axis=1)
    xg = shots["xg"].sum()
else:
    xg = 0.0

passes_opp = len(df[(df["event_type"]=="pass") & (df["team"]!="Retrô")]) if "team" in df.columns else 0
def_actions = len(df[(df["event_type"].isin(["recovery","foul_won"])) & (df["team"]=="Retrô")])
ppda = (passes_opp / def_actions) if def_actions>0 else None

c1,c2,c3 = st.columns(3)
c1.metric("xG (Retrô)", f"{xg:.2f}")
c2.metric("Finalizações", f"{len(shots)}")
c3.metric("PPDA (aprox.)", f"{ppda:.2f}" if ppda is not None else "—")

import plotly.graph_objects as go
fig = go.Figure()
fig.update_xaxes(range=[0,100], showgrid=False, zeroline=False, visible=False)
fig.update_yaxes(range=[0,100], showgrid=False, zeroline=False, visible=False)
fig.add_shape(type="rect", x0=83, y0=21.1, x1=100, y1=78.9, line=dict(width=1))
fig.add_shape(type="line", x0=100, y0=44.8, x1=100, y1=55.2)
fig.add_trace(go.Scatter(
    x=shots["x"] if not shots.empty else [],
    y=shots["y"] if not shots.empty else [],
    mode="markers",
    marker=dict(size=8, opacity=0.7),
    name="Shots"
))
st.subheader("Mapa de Finalizações (Retrô → direita)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("**Notas**: App demonstrativo. Para PPDA real, inclua eventos do oponente e delimite zona/tempo.")
