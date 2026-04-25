import streamlit as st
import sqlite3
import os
import random
import pandas as pd
from datetime import datetime, timedelta
from openai import OpenAI
from database import get_conn, get_or_create_subject, get_difficulty_id, log_audit, create_database
import re

st.set_page_config(
    page_title="AI Math Tutor Pro",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,400;0,600;0,700;0,800;1,400&family=Lora:ital,wght@0,600;0,700;1,500&display=swap');

/* ══════════════════════════════════════════════════
   MATH NOTEBOOK — warm honey & terracotta palette
   ══════════════════════════════════════════════════ */
:root {
    --navy:        #3b2f2f;
    --navy-mid:    #4e3b30;
    --ink:         #2c1f14;
    --ink-mid:     #5c3d2e;
    --ink-light:   #9a7b65;
    --gold:        #d4852a;
    --gold-light:  #e8a84a;
    --gold-pale:   #fdecc8;
    --terracotta:  #c0613a;
    --terra-light: #e0856a;
    --terra-pale:  #fce8e0;
    --sage:        #6b8f6b;
    --sage-pale:   #e8f0e8;
    --cream:       #fdf6ec;
    --cream-dark:  #f5e8d4;
    --cream-line:  #e8d8c0;
    --paper:       #fffdf7;
    --paper-dark:  #f8f0e3;
    --error:       #b83a2a;
    --error-bg:    #fdf0ee;
    --success:     #3a7a4a;
    --success-bg:  #eef7f2;
    --radius-sm:   5px;
    --radius-md:   10px;
    --radius-lg:   16px;
    --radius-xl:   24px;
    --shadow-sketch: 3px 4px 0px rgba(60,30,10,.09), 5px 7px 16px rgba(60,30,10,.07);
    --shadow-lift:   4px 5px 0px rgba(60,30,10,.12), 6px 9px 22px rgba(60,30,10,.09);
    --font-body:   'Nunito', 'Segoe UI', system-ui, sans-serif;
    --font-serif:  'Lora', Georgia, serif;
}

/* App background — warm honey paper + scattered math doodles */
.stApp {
    background-color: var(--cream) !important;
    background-image:
        radial-gradient(ellipse at 15% 20%, rgba(212,133,42,.07) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 70%, rgba(192,97,58,.06) 0%, transparent 50%),
        repeating-linear-gradient(180deg, transparent 0px, transparent 37px, rgba(212,133,42,.08) 37px, rgba(212,133,42,.08) 38px),
        url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='700' height='700'%3E%3Cg opacity='0.06' font-family='Georgia%2Cserif' fill='%234e3b30'%3E%3Ctext x='15' y='55' font-size='32' transform='rotate(-9 15 55)'%3E%CF%80%3C/text%3E%3Ctext x='100' y='88' font-size='15' transform='rotate(6 100 88)'%3E%E2%88%91n%E1%B5%A2%3C/text%3E%3Ctext x='185' y='38' font-size='13' transform='rotate(-4 185 38)'%3Ef(x)%3Dx%C2%B2%3C/text%3E%3Ctext x='295' y='72' font-size='22' transform='rotate(8 295 72)'%3E%E2%88%9A2%3C/text%3E%3Ctext x='385' y='42' font-size='13' transform='rotate(-6 385 42)'%3Eax%C2%B2%2Bbx%2Bc%3C/text%3E%3Ctext x='530' y='82' font-size='28' transform='rotate(5 530 82)'%3E%E2%88%9E%3C/text%3E%3Ctext x='610' y='44' font-size='15' transform='rotate(-7 610 44)'%3E%CF%86%3C/text%3E%3Ctext x='660' y='70' font-size='18' transform='rotate(4 660 70)'%3E%CE%B8%3C/text%3E%3Ctext x='25' y='175' font-size='14' transform='rotate(7 25 175)'%3Edy%2Fdx%3C/text%3E%3Ctext x='120' y='155' font-size='24' transform='rotate(-5 120 155)'%3E%CE%B1%3C/text%3E%3Ctext x='205' y='182' font-size='14' transform='rotate(4 205 182)'%3E%E2%88%ABf(x)dx%3C/text%3E%3Ctext x='355' y='162' font-size='13' transform='rotate(-8 355 162)'%3Esin%C2%B2%2Bcos%C2%B2%3D1%3C/text%3E%3Ctext x='520' y='175' font-size='21' transform='rotate(6 520 175)'%3E%CE%B2%3C/text%3E%3Ctext x='605' y='158' font-size='14' transform='rotate(-4 605 158)'%3En!%3C/text%3E%3Ctext x='660' y='178' font-size='11' transform='rotate(5 660 178)'%3Elim%E2%86%920%3C/text%3E%3Ctext x='15' y='268' font-size='16' transform='rotate(-6 15 268)'%3Ey%3Dmx%2Bb%3C/text%3E%3Ctext x='130' y='252' font-size='14' transform='rotate(5 130 252)'%3Elim(x%E2%86%920)%3C/text%3E%3Ctext x='265' y='278' font-size='20' transform='rotate(-7 265 278)'%3E%CE%BC%3C/text%3E%3Ctext x='340' y='255' font-size='14' transform='rotate(4 340 255)'%3E2%C2%B3%3D8%3C/text%3E%3Ctext x='445' y='272' font-size='26' transform='rotate(-5 445 272)'%3E%CE%B4%3C/text%3E%3Ctext x='530' y='258' font-size='14' transform='rotate(7 530 258)'%3Elog%E2%82%90b%3C/text%3E%3Ctext x='620' y='275' font-size='22' transform='rotate(-6 620 275)'%3E%CE%BB%3C/text%3E%3Ctext x='30' y='358' font-size='24' transform='rotate(6 30 358)'%3E%CE%B3%3C/text%3E%3Ctext x='118' y='375' font-size='14' transform='rotate(-5 118 375)'%3Ea%C2%B2%2Bb%C2%B2%3Dc%C2%B2%3C/text%3E%3Ctext x='270' y='352' font-size='14' transform='rotate(8 270 352)'%3Ex%E2%88%88%E2%84%9D%3C/text%3E%3Ctext x='388' y='372' font-size='14' transform='rotate(-4 388 372)'%3E%CE%94x%E2%86%920%3C/text%3E%3Ctext x='500' y='355' font-size='26' transform='rotate(5 500 355)'%3E%CF%83%3C/text%3E%3Ctext x='600' y='370' font-size='14' transform='rotate(-7 600 370)'%3E%E2%8A%82%E2%88%AA%E2%88%A9%3C/text%3E%3Ctext x='14' y='455' font-size='15' transform='rotate(-4 14 455)'%3E%E2%88%82y%2F%E2%88%82x%3C/text%3E%3Ctext x='118' y='470' font-size='24' transform='rotate(7 118 470)'%3E%CF%89%3C/text%3E%3Ctext x='220' y='452' font-size='14' transform='rotate(-6 220 452)'%3EP(A%E2%88%A9B)%3C/text%3E%3Ctext x='342' y='468' font-size='26' transform='rotate(4 342 468)'%3E%E2%84%95%3C/text%3E%3Ctext x='438' y='450' font-size='14' transform='rotate(-8 438 450)'%3E%CE%B5-%CE%B4%3C/text%3E%3Ctext x='540' y='466' font-size='21' transform='rotate(6 540 466)'%3E%CE%B7%3C/text%3E%3Ctext x='635' y='450' font-size='14' transform='rotate(-5 635 450)'%3E%7Cx%7C%E2%89%A41%3C/text%3E%3Ctext x='35' y='548' font-size='14' transform='rotate(5 35 548)'%3Etan%CE%B8%3C/text%3E%3Ctext x='158' y='565' font-size='24' transform='rotate(-7 158 565)'%3E%CF%88%3C/text%3E%3Ctext x='268' y='545' font-size='14' transform='rotate(4 268 545)'%3Ef\'(x)%3D2x%3C/text%3E%3Ctext x='390' y='562' font-size='30' transform='rotate(-5 390 562)'%3E%CF%80%3C/text%3E%3Ctext x='508' y='545' font-size='14' transform='rotate(6 508 545)'%3Ex%C2%B2%2By%C2%B2%3Dr%C2%B2%3C/text%3E%3Ctext x='625' y='560' font-size='20' transform='rotate(-4 625 560)'%3E%CF%87%3C/text%3E%3Ctext x='18' y='635' font-size='14' transform='rotate(-6 18 635)'%3E%E2%84%A4%E2%8A%82%E2%84%9A%3C/text%3E%3Ctext x='148' y='648' font-size='14' transform='rotate(5 148 648)'%3En%E2%82%96%E2%86%92%E2%88%9E%3C/text%3E%3Ctext x='295' y='632' font-size='14' transform='rotate(-4 295 632)'%3E%E2%88%82%C2%B2f%2F%E2%88%82x%C2%B2%3C/text%3E%3Ctext x='428' y='650' font-size='22' transform='rotate(7 428 650)'%3E%CE%A9%3C/text%3E%3Ctext x='545' y='635' font-size='14' transform='rotate(-6 545 635)'%3Ee%5Ei%CF%80%2B1%3D0%3C/text%3E%3Ctext x='655' y='648' font-size='18' transform='rotate(4 655 648)'%3E%CE%BE%3C/text%3E%3C/g%3E%3C/svg%3E") !important;
    background-size: auto, auto, auto, 700px 700px !important;
}

/* Only target content areas for font, never Streamlit chrome */
.stApp [class*="stMarkdown"],
.stApp [class*="stText"],
.stApp .stButton > button,
.stApp .stTextInput input,
.stApp .stTextArea textarea,
.stApp [data-testid="stWidgetLabel"] p {
    font-family: var(--font-body) !important;
    color: var(--ink) !important;
}

/* ── SIDEBAR ─────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(175deg, var(--navy) 0%, #2c1f14 100%) !important;
    border-right: 3px solid var(--gold) !important;
    box-shadow: 4px 0 20px rgba(60,30,10,.18) !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span:not([data-testid]),
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div[class*="stRadio"] label {
    color: #f0e4d0 !important;
    font-family: var(--font-body) !important;
}
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stSelectbox label {
    color: #d4b896 !important;
    font-size: 0.76rem;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    font-weight: 700;
}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: rgba(255,255,255,.06);
    border: 1.5px solid rgba(212,133,42,.3);
    border-radius: var(--radius-md);
    padding: .5rem .85rem;
    margin: .25rem 0;
    font-size: .92rem !important;
    text-transform: none !important;
    letter-spacing: normal !important;
    font-weight: 600 !important;
    color: #f0e4d0 !important;
    transition: all .2s;
}
section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
    background: rgba(212,133,42,.2);
    border-color: var(--gold);
    transform: translateX(3px);
}
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--gold-light) !important;
    font-family: var(--font-serif) !important;
    font-size: 1.15rem !important;
    border-bottom: 1.5px solid rgba(212,133,42,.35);
    padding-bottom: .55rem;
    margin-bottom: 1.1rem;
}
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] .stCaption p {
    color: rgba(240,228,208,.38) !important;
    font-size: .74rem !important;
}

/* ── HEADINGS ────────────────────────────────── */
h1, h2, h3 { font-family: var(--font-serif) !important; color: var(--ink) !important; }
h1 { font-size: 1.9rem !important; }
h2 { font-size: 1.45rem !important; }
h3 { font-size: 1.12rem !important; }

/* ── BUTTONS — warm sketch/offset shadow ─────── */
.stButton > button {
    font-family: var(--font-body) !important;
    font-weight: 700 !important;
    font-size: .9rem !important;
    border-radius: var(--radius-md) !important;
    padding: .52rem 1.2rem !important;
    background: var(--paper) !important;
    color: var(--ink) !important;
    border: 2px solid var(--ink-mid) !important;
    box-shadow: 3px 4px 0px var(--ink-mid) !important;
    transition: all .15s ease !important;
    letter-spacing: .01em !important;
}
.stButton > button:hover {
    background: var(--gold-pale) !important;
    border-color: var(--gold) !important;
    box-shadow: 4px 5px 0px var(--gold) !important;
    transform: translateY(-2px) translateX(-1px);
    color: var(--ink) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--navy-mid) 0%, var(--navy) 100%) !important;
    color: var(--gold-light) !important;
    border: 2px solid var(--navy) !important;
    box-shadow: 3px 4px 0px var(--gold) !important;
    font-size: .95rem !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--ink-mid) 0%, var(--navy) 100%) !important;
    box-shadow: 5px 6px 0px var(--gold) !important;
    transform: translateY(-2px) translateX(-1px);
}

/* ── FORM INPUTS — warm notebook underline ─── */
.stTextInput input, .stTextArea textarea {
    background: var(--paper) !important;
    border: 1.5px solid var(--cream-line) !important;
    border-radius: var(--radius-md) !important;
    color: var(--ink) !important;
    font-family: var(--font-body) !important;
    font-size: .95rem !important;
    box-shadow: inset 0 1px 3px rgba(60,30,10,.05) !important;
    transition: border-color .18s, box-shadow .18s;
    padding: .55rem .8rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(212,133,42,.15) !important;
    outline: none !important;
    background: #fffdf5 !important;
}
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background: var(--paper) !important;
    border: 1.5px solid var(--cream-line) !important;
    border-radius: var(--radius-md) !important;
    color: var(--ink) !important;
    font-family: var(--font-body) !important;
    box-shadow: 2px 2px 0px rgba(212,133,42,.12) !important;
}
label[data-testid="stWidgetLabel"] p,
.stTextInput label, .stTextArea label,
.stSelectbox label, .stFileUploader label {
    font-family: var(--font-body) !important;
    font-weight: 800 !important;
    font-size: .76rem !important;
    color: var(--ink-light) !important;
    letter-spacing: .09em;
    text-transform: uppercase;
}

/* ── TABS — warm underline with terracotta active ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid var(--cream-line) !important;
    gap: .2rem !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: .91rem !important;
    color: var(--ink-light) !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    padding: .65rem 1.2rem !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    transition: all .15s;
}
.stTabs [aria-selected="true"] {
    color: var(--navy) !important;
    border-bottom-color: var(--terracotta) !important;
    font-weight: 800 !important;
    background: rgba(192,97,58,.06) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--ink) !important;
    background: rgba(212,133,42,.08) !important;
}

/* ── METRICS — warm index cards ─────────────── */
[data-testid="stMetric"] {
    background: var(--paper) !important;
    border: 2px solid var(--cream-line) !important;
    border-top: 4px solid var(--gold) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem 1.2rem !important;
    box-shadow: var(--shadow-sketch) !important;
    transition: transform .15s, box-shadow .15s;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lift) !important;
}
[data-testid="stMetricLabel"] {
    font-family: var(--font-body) !important;
    font-size: .74rem !important;
    letter-spacing: .09em;
    text-transform: uppercase;
    color: var(--ink-light) !important;
    font-weight: 800 !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-serif) !important;
    font-size: 2rem !important;
    color: var(--navy) !important;
    font-weight: 700 !important;
}

/* ── DATAFRAMES ─────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1.5px solid var(--cream-line) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden;
    box-shadow: 2px 3px 0px var(--cream-line);
}

/* ── EXPANDER — sticky note with warm left accent ── */
[data-testid="stExpander"] {
    border: 2px solid var(--cream-line) !important;
    border-left: 5px solid var(--gold-pale) !important;
    border-radius: var(--radius-md) !important;
    background: var(--paper) !important;
    box-shadow: var(--shadow-sketch) !important;
    margin-bottom: .7rem;
    transition: border-left-color .2s;
}
[data-testid="stExpander"]:hover {
    border-left-color: var(--gold) !important;
}
[data-testid="stExpander"] summary {
    font-family: var(--font-body) !important;
    font-weight: 700 !important;
    color: var(--ink) !important;
    padding: .75rem 1.1rem !important;
}

/* ── DOWNLOAD BUTTON ────────────────────────── */
.stDownloadButton > button {
    background: var(--paper) !important;
    color: var(--ink) !important;
    border: 2px solid var(--ink-mid) !important;
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    box-shadow: 2px 2px 0px var(--cream-line) !important;
    transition: all .15s !important;
}
.stDownloadButton > button:hover {
    background: var(--gold-pale) !important;
    box-shadow: 3px 3px 0px var(--gold) !important;
}

/* ── FILE UPLOADER ──────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--paper) !important;
    border: 2px dashed var(--cream-line) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1rem !important;
    transition: border-color .2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--gold) !important;
    background: #fffdf5 !important;
}

/* ── ALERTS ─────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    font-family: var(--font-body) !important;
    font-size: .91rem !important;
    border-left-width: 4px !important;
}

/* ── HR — dashed like notebook ──────────────── */
hr { border: none; border-top: 1.5px dashed var(--cream-line); margin: 1.1rem 0; }

/* ── CAPTION ────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] p {
    font-size: .8rem !important;
    color: var(--ink-light) !important;
    font-style: italic;
}

/* ══════════════════════════════════════════════
   COMPONENT CLASSES
   ══════════════════════════════════════════════ */

/* PAGE HEADER — warm honey strip */
.page-header {
    background: linear-gradient(135deg, var(--paper-dark) 0%, #fef3e2 100%);
    border: 2px solid var(--cream-line);
    border-left: 6px solid var(--gold);
    border-radius: var(--radius-md);
    padding: 1.1rem 1.6rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow-sketch);
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute;
    right: 1.5rem; top: 50%; transform: translateY(-50%);
    font-family: Georgia, serif;
    font-size: 4rem;
    color: rgba(212,133,42,.08);
    pointer-events: none;
    line-height: 1;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0; height: 3px;
    background: repeating-linear-gradient(90deg, var(--gold-pale) 0px, var(--gold-pale) 14px, transparent 14px, transparent 20px);
}
.page-header h2 {
    font-family: var(--font-serif) !important;
    color: var(--navy) !important;
    margin: 0 !important;
    font-size: 1.3rem !important;
    border: none !important;
    padding: 0 !important;
}
.page-header .sub {
    font-size: .79rem;
    color: var(--ink-light);
    margin-top: .25rem;
    font-family: var(--font-body);
    letter-spacing: .07em;
    text-transform: uppercase;
    font-weight: 600;
}

/* LOGIN CARD — warm notebook page with ruled lines */
.login-card {
    background: var(--paper);
    border: 2px solid var(--cream-line);
    border-top: 5px solid var(--gold);
    border-radius: var(--radius-lg);
    padding: 2.2rem 2rem 1.8rem;
    box-shadow: var(--shadow-lift);
    position: relative;
    overflow: hidden;
}
.login-card::before {
    content: '';
    position: absolute;
    left: 0; right: 0; top: 0; bottom: 0;
    background: repeating-linear-gradient(180deg, transparent 0px, transparent 29px, rgba(212,133,42,.12) 29px, rgba(212,133,42,.12) 30px);
    pointer-events: none;
}
.login-card::after {
    content: '';
    position: absolute;
    left: 42px; top: 0; bottom: 0; width: 2px;
    background: rgba(192,97,58,.14);
    pointer-events: none;
}
.login-card h2 {
    font-family: var(--font-serif) !important;
    color: var(--navy) !important;
    font-size: 1.45rem !important;
    margin-bottom: .2rem !important;
    border: none !important;
    padding: 0 !important;
    position: relative; z-index: 1;
}
.login-card .login-subtitle {
    color: var(--ink-light);
    font-size: .84rem;
    margin-bottom: 1.3rem;
    font-style: italic;
    position: relative; z-index: 1;
    font-family: var(--font-body);
}

/* MATH SYMBOLS STRIP */
.math-strip {
    display: flex;
    justify-content: center;
    gap: 1.2rem;
    margin: .5rem 0 1.2rem;
    font-family: Georgia, serif;
    font-size: 1.25rem;
    color: var(--gold);
    opacity: .7;
    letter-spacing: .04em;
    user-select: none;
    text-shadow: 1px 1px 2px rgba(212,133,42,.2);
}

/* SECTION LABEL */
.section-label {
    font-family: var(--font-body);
    font-size: .72rem;
    font-weight: 800;
    color: var(--ink-light);
    letter-spacing: .12em;
    text-transform: uppercase;
    margin: 1.3rem 0 .5rem;
    padding-bottom: .35rem;
    border-bottom: 2px dashed var(--cream-line);
}

/* WORKSHEET CARD — warm ruled paper */
.worksheet-card {
    background: var(--paper);
    border: 2px solid var(--cream-line);
    border-radius: var(--radius-lg);
    padding: 1.8rem 2rem;
    margin: .8rem 0;
    box-shadow: var(--shadow-sketch);
    position: relative;
    background-image: repeating-linear-gradient(180deg, transparent 0px, transparent 33px, rgba(212,133,42,.09) 33px, rgba(212,133,42,.09) 34px);
}
.worksheet-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0; width: 6px;
    background: linear-gradient(180deg, var(--gold) 0%, var(--terracotta) 100%);
    border-radius: var(--radius-lg) 0 0 var(--radius-lg);
}

/* OPTION BOX */
.option-box {
    padding: .25rem 0;
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

/* INLINE ALERTS */
.alert-red {
    color: var(--error) !important;
    font-weight: 700;
    background: var(--error-bg);
    padding: .6rem .9rem;
    border-radius: var(--radius-md);
    border-left: 5px solid var(--error);
    font-family: var(--font-body);
    font-size: .9rem;
}

/* BADGES */
.badge {
    display: inline-block;
    background: var(--navy);
    color: var(--gold-light);
    font-size: .71rem;
    font-weight: 800;
    letter-spacing: .07em;
    padding: .2rem .6rem;
    border-radius: 20px;
    text-transform: uppercase;
    margin-right: .35rem;
}
.badge-gold { background: var(--gold); color: var(--ink); }
.badge-terra { background: var(--terracotta); color: #fff; }

/* MATH DOODLE BG on cards */
.math-doodle-bg { position: relative; overflow: hidden; }
.math-doodle-bg::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='420' height='320'%3E%3Cg opacity='0.065' font-family='Georgia%2Cserif' fill='%234e3b30'%3E%3Ctext x='10' y='42' font-size='26' transform='rotate(-8 10 42)'%3E%CF%80%3C/text%3E%3Ctext x='75' y='28' font-size='13' transform='rotate(6 75 28)'%3Ef(x)%3Dx%C2%B2%3C/text%3E%3Ctext x='165' y='50' font-size='20' transform='rotate(-5 165 50)'%3E%E2%88%9A2%3C/text%3E%3Ctext x='240' y='32' font-size='13' transform='rotate(7 240 32)'%3Eax%C2%B2%2Bbx%3C/text%3E%3Ctext x='330' y='52' font-size='26' transform='rotate(-6 330 52)'%3E%E2%88%9E%3C/text%3E%3Ctext x='390' y='30' font-size='18' transform='rotate(4 390 30)'%3E%CE%B8%3C/text%3E%3Ctext x='10' y='118' font-size='14' transform='rotate(5 10 118)'%3Edy%2Fdx%3C/text%3E%3Ctext x='90' y='100' font-size='22' transform='rotate(-6 90 100)'%3E%CE%B1%3C/text%3E%3Ctext x='155' y='122' font-size='13' transform='rotate(4 155 122)'%3E%E2%88%ABf(x)dx%3C/text%3E%3Ctext x='280' y='105' font-size='13' transform='rotate(-7 280 105)'%3Esin%C2%B2%2Bcos%C2%B2%3D1%3C/text%3E%3Ctext x='385' y='118' font-size='19' transform='rotate(5 385 118)'%3E%CE%BC%3C/text%3E%3Ctext x='15' y='198' font-size='13' transform='rotate(-4 15 198)'%3Ey%3Dmx%2Bb%3C/text%3E%3Ctext x='108' y='180' font-size='24' transform='rotate(6 108 180)'%3E%CE%B4%3C/text%3E%3Ctext x='188' y='205' font-size='13' transform='rotate(-5 188 205)'%3Ea%C2%B2%2Bb%C2%B2%3Dc%C2%B2%3C/text%3E%3Ctext x='305' y='188' font-size='22' transform='rotate(4 305 188)'%3E%CE%BB%3C/text%3E%3Ctext x='360' y='205' font-size='13' transform='rotate(-6 360 205)'%3Elog%E2%82%90b%3C/text%3E%3Ctext x='22' y='275' font-size='22' transform='rotate(5 22 275)'%3E%CF%83%3C/text%3E%3Ctext x='98' y='290' font-size='13' transform='rotate(-4 98 290)'%3Ex%E2%88%88%E2%84%9D%3C/text%3E%3Ctext x='205' y='272' font-size='13' transform='rotate(7 205 272)'%3E%CE%94x%E2%86%920%3C/text%3E%3Ctext x='318' y='288' font-size='24' transform='rotate(-5 318 288)'%3E%CF%89%3C/text%3E%3Ctext x='380' y='272' font-size='19' transform='rotate(4 380 272)'%3E%CE%B3%3C/text%3E%3C/g%3E%3C/svg%3E");
    background-size: 420px 320px;
    pointer-events: none;
    z-index: 0;
}
.math-doodle-bg > * { position: relative; z-index: 1; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: var(--paper) !important;
    border: 2.5px dashed var(--cream-line) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.2rem !important;
    transition: all .2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--gold) !important;
    background: #fffdf5 !important;
    box-shadow: 0 0 0 3px rgba(212,133,42,.1) !important;
}

/* ── DOWNLOAD BUTTON ── */
.stDownloadButton > button {
    background: var(--paper) !important;
    color: var(--ink) !important;
    border: 2px solid var(--ink-mid) !important;
    border-radius: var(--radius-md) !important;
    font-weight: 700 !important;
    font-family: var(--font-body) !important;
    box-shadow: 2px 3px 0px var(--cream-line) !important;
    transition: all .15s !important;
}
.stDownloadButton > button:hover {
    background: var(--gold-pale) !important;
    box-shadow: 3px 4px 0px var(--gold) !important;
    transform: translateY(-1px) !important;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    font-family: var(--font-body) !important;
    font-size: .92rem !important;
    border-left-width: 5px !important;
}

/* ── HR ── */
hr { border: none; border-top: 2px dashed var(--cream-line); margin: 1.2rem 0; }

/* ── CAPTION ── */
.stCaption, [data-testid="stCaptionContainer"] p {
    font-size: .8rem !important;
    color: var(--ink-light) !important;
    font-style: italic;
    font-family: var(--font-body) !important;
}

/* ── DATAFRAMES ── */
[data-testid="stDataFrame"] {
    border: 2px solid var(--cream-line) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden;
    box-shadow: var(--shadow-sketch);
}

/* ── PROGRESS ── */
.stProgress > div > div { background: linear-gradient(90deg, var(--gold) 0%, var(--terracotta) 100%) !important; border-radius: 99px !important; }
</style>
""", unsafe_allow_html=True)



pplx_key = st.secrets.get("PERPLEXITY_API_KEY", "")
USE_PPLX = bool(pplx_key)

TEACHERS = {
    "Algebra": {
        "username": st.secrets.get("TEACHER_ALGEBRA_USER", ""),
        "password": st.secrets.get("TEACHER_ALGEBRA_PASS", ""),
    },
    "Fractions": {
        "username": st.secrets.get("TEACHER_FRACTIONS_USER", ""),
        "password": st.secrets.get("TEACHER_FRACTIONS_PASS", ""),
    },
    "Calculus": {
        "username": st.secrets.get("TEACHER_CALCULUS_USER", ""),
        "password": st.secrets.get("TEACHER_CALCULUS_PASS", ""),
    },
}

client = None
if USE_PPLX:
    try:
        client = OpenAI(api_key=pplx_key, base_url="https://api.perplexity.ai")
    except Exception as e:
        st.sidebar.warning(f"Perplexity init failed: {e}")
        USE_PPLX = False

st.sidebar.markdown("## ✏️ AI Math Tutor Pro")
st.sidebar.markdown('<p style="color:rgba(240,228,208,0.52);font-size:0.78rem;margin-top:-0.5rem;margin-bottom:1rem;font-style:italic;">Adaptive Learning Platform</p>', unsafe_allow_html=True)
view_mode = st.sidebar.radio("Select Mode", ["Student Access", "Teacher Dashboard"])

previous_mode = st.session_state.get("active_mode")
if previous_mode and previous_mode != view_mode:
    if view_mode == "Student Access":
        st.session_state.pop("teacher_user", None)
    else:
        st.session_state.pop("student_user", None)
        for k in ["worksheet", "submitted", "show_answers", "answers"]:
            st.session_state.pop(k, None)
st.session_state["active_mode"] = view_mode

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

create_database()


# ── CACHED QUERIES (all use new schema with JOINs) ────────────────────────────
@st.cache_data(ttl=30)
def get_allowed_students_for_subject(subject):
    with get_conn() as conn:
        df = pd.read_sql("""
            SELECT DISTINCT a.student_name
            FROM allowed_students a
            JOIN student_subjects ss ON a.student_name = ss.student_name
            JOIN subjects s ON ss.subject_id = s.id
            WHERE s.name = ?
            ORDER BY a.student_name
        """, conn, params=(subject,))
    return df["student_name"].tolist()


@st.cache_data(ttl=30)
def get_subjects_for_student(student_name):
    with get_conn() as conn:
        df = pd.read_sql("""
            SELECT DISTINCT s.name AS subject
            FROM student_subjects ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE ss.student_name = ?
            ORDER BY s.name
        """, conn, params=(student_name,))
    return df["subject"].tolist()


@st.cache_data(ttl=30)
def get_student_summary(name):
    with get_conn() as conn:
        return pd.read_sql("""
            SELECT s.name AS topic,
                   d.label AS difficulty,
                   COUNT(*) as attempts,
                   ROUND(AVG(p.score)*20,1) as avg_percent,
                   MAX(p.score) as best_out_of_5
            FROM performance p
            JOIN subjects s ON p.subject_id = s.id
            JOIN difficulty_levels d ON p.difficulty_id = d.id
            WHERE p.student_name = ?
            GROUP BY s.name, d.label
            ORDER BY s.name, d.rank
        """, conn, params=(name,))


@st.cache_data(ttl=30)
def get_student_history(name):
    with get_conn() as conn:
        return pd.read_sql("""
            SELECT s.name AS topic,
                   d.label AS difficulty,
                   p.score,
                   ROUND(p.score*20,0) as percent,
                   p.submitted_at
            FROM performance p
            JOIN subjects s ON p.subject_id = s.id
            JOIN difficulty_levels d ON p.difficulty_id = d.id
            WHERE p.student_name = ?
            ORDER BY p.submitted_at DESC
        """, conn, params=(name,))


@st.cache_data(ttl=45)
def get_class_scoreboard_for_subject(subject):
    with get_conn() as conn:
        df = pd.read_sql("""
            SELECT p.student_name,
                   d.label AS difficulty,
                   COUNT(*) as attempts,
                   ROUND(AVG(p.score)*20,1) as avg_percent,
                   MAX(p.score) as best_out_of_5
            FROM performance p
            JOIN subjects s ON p.subject_id = s.id
            JOIN difficulty_levels d ON p.difficulty_id = d.id
            WHERE s.name = ?
            GROUP BY p.student_name, d.label
            ORDER BY p.student_name
        """, conn, params=(subject,))
    if df.empty:
        return df
    wide = df.pivot_table(
        index="student_name",
        columns="difficulty",
        values=["best_out_of_5", "avg_percent"],
        aggfunc="max"
    )
    wide.columns = [f"{c[1]} ({'Best/5' if c[0]=='best_out_of_5' else 'Avg%'})" for c in wide.columns]
    return wide.reset_index()


@st.cache_data(ttl=30)
def get_question_counts_for_subject(subject):
    with get_conn() as conn:
        return pd.read_sql("""
            SELECT d.label AS difficulty, COUNT(*) AS questions
            FROM question_bank q
            JOIN subjects s ON q.subject_id = s.id
            JOIN difficulty_levels d ON q.difficulty_id = d.id
            WHERE s.name = ?
            GROUP BY d.label
            ORDER BY d.rank
        """, conn, params=(subject,))


@st.cache_data(ttl=30)
def get_study_material(subject):
    with get_conn() as conn:
        return pd.read_sql("""
            SELECT m.id, m.title, m.content, m.file_name, m.file_data, m.uploaded_at
            FROM study_material m
            JOIN subjects s ON m.subject_id = s.id
            WHERE s.name = ?
            ORDER BY m.uploaded_at DESC
        """, conn, params=(subject,))


@st.cache_data(ttl=30)
def get_weak_students(subject):
    with get_conn() as conn:
        return pd.read_sql("""
            SELECT p.student_name,
                   ROUND(AVG(p.score)*20,1) AS avg_percent,
                   COUNT(*) AS attempts
            FROM performance p
            JOIN subjects s ON p.subject_id = s.id
            WHERE s.name = ?
            GROUP BY p.student_name
            HAVING avg_percent < 50
            ORDER BY avg_percent ASC
        """, conn, params=(subject,))


def get_student_streak(student_name):
    """Return number of consecutive days the student has submitted at least one worksheet."""
    with get_conn() as conn:
        df = pd.read_sql("""
            SELECT DATE(submitted_at) as day
            FROM performance
            WHERE student_name = ?
            ORDER BY day DESC
        """, conn, params=(student_name,))
    if df.empty:
        return 0
    days = sorted(df["day"].unique(), reverse=True)
    streak = 0
    today = datetime.now().date()
    for i, d in enumerate(days):
        expected = str(today - timedelta(days=i))
        if d == expected:
            streak += 1
        else:
            break
    return streak


def load_chat_history_from_db(student_name, topic):
    with get_conn() as conn:
        df = pd.read_sql("""
            SELECT c.role, c.content
            FROM chat_history c
            JOIN subjects s ON c.subject_id = s.id
            WHERE c.student_name = ? AND s.name = ?
            ORDER BY c.id ASC LIMIT 40
        """, conn, params=(student_name, topic))
    return df.to_dict(orient="records") if not df.empty else []


def save_chat_message(student_name, topic, role, content):
    with get_conn() as conn:
        subject_id = get_or_create_subject(conn, topic)
        conn.execute("""
            INSERT INTO chat_history (student_name, subject_id, role, content, sent_at)
            VALUES (?, ?, ?, ?, ?)
        """, (student_name, subject_id, role, content, datetime.now().isoformat()))
        conn.commit()


# ── HELPERS ───────────────────────────────────────────────────────────────────
def randomize_choices(q_dict):
    correct_text = q_dict["choices"][q_dict["correct"]]
    shuffled = q_dict["choices"][:]
    random.shuffle(shuffled)
    return {"q": q_dict["q"], "choices": shuffled, "correct": shuffled.index(correct_text)}


def clean_question_prefix(q):
    q = re.sub(r'^\s*\d+[.)]\s*', '', str(q).strip())
    q = re.sub(r'^(?:Question|Q)\s*\d+[:.)]?\s*', '', q, flags=re.I)
    return q.strip()


def normalize_math_text(text):
    text = str(text).strip()
    for old, new in {"÷": r"\div", "×": r"\times", "−": "-", "∞": r"\infty",
                     "→": r"\to", "√": r"\sqrt", "²": "^2", "³": "^3", "⁴": "^4"}.items():
        text = text.replace(old, new)
    text = re.sub(r'\\\((.*?)\\\)', r'\1', text)
    text = re.sub(r'\\\[(.*?)\\\]', r'\1', text)
    return text.strip()


def looks_like_math(text):
    return any(m in str(text) for m in [r"\frac", r"\sqrt", r"\int", r"\lim",
                                         r"\sin", r"\cos", r"\tan", "^", "_", "="])


def render_math_or_text(text, label=None):
    cleaned = normalize_math_text(clean_question_prefix(text))
    if label:
        st.markdown(f"**{label}**")
    if looks_like_math(cleaned):
        try:
            st.latex(cleaned)
            return
        except Exception:
            pass
    st.markdown(cleaned)


def score_feedback(score):
    if score == 5:
        st.success("🏆 Perfect score! Outstanding work!")
    elif score == 4:
        st.success("🌟 Great job! Just one slip — review it and you've got this.")
    elif score == 3:
        st.info("👍 Solid effort! Check the ones you missed in the Study Material tab.")
    elif score == 2:
        st.warning("📖 Keep going! Try reviewing the Study Material and attempt again.")
    else:
        st.error("💪 Don't give up! Visit the 🤖 AI Tutor tab for step-by-step help.")


# ── QUESTION GENERATION ───────────────────────────────────────────────────────
def generate_db_questions(topic, difficulty):
    with get_conn() as conn:
        df = pd.read_sql("""
            SELECT q.question, q.choice_a, q.choice_b, q.choice_c, q.choice_d, q.correct_letter
            FROM question_bank q
            JOIN subjects s ON q.subject_id = s.id
            JOIN difficulty_levels d ON q.difficulty_id = d.id
            WHERE s.name = ? AND d.label = ?
        """, conn, params=(topic, difficulty))
    if df.empty:
        return []
    rows = df.to_dict(orient="records")
    selected = random.sample(rows, min(5, len(rows)))
    questions = []
    for row in selected:
        idx = "ABCD".find(str(row["correct_letter"]).strip().upper())
        if idx == -1:
            continue
        questions.append(randomize_choices({
            "q": row["question"],
            "choices": [row["choice_a"], row["choice_b"], row["choice_c"], row["choice_d"]],
            "correct": idx
        }))
    return questions


def generate_perplexity_questions(topic, difficulty):
    if not USE_PPLX or not client:
        return []
    prompt = f"""Generate exactly 5 {difficulty.lower()} {topic} multiple-choice questions.
Each must have 4 choices (A-D), one correct answer. Use LaTeX for math. No commentary.

Format:
Q: <question>
A: <option>
B: <option>
C: <option>
D: <option>
Correct: <letter>"""
    try:
        response = client.chat.completions.create(
            model="sonar",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600
        )
        text = response.choices[0].message.content.strip()
        questions, current = [], {}
        for line in text.splitlines():
            line = re.sub(r'^[*-]\s*', '', line.strip())
            if not line:
                continue
            if line.startswith("Q:"):
                if current:
                    questions.append(current)
                current = {"q": line[2:].strip()}
            elif line.startswith(("A:", "B:", "C:", "D:")):
                current[line[0]] = line[2:].strip()
            elif line.startswith("Correct:"):
                letter = line.split(":", 1)[1].strip().upper()
                current["correct"] = "ABCD".index(letter) if letter in "ABCD" else 0
        if current and "q" in current:
            questions.append(current)
        norm = []
        for q in questions[:5]:
            if all(k in q for k in ["A", "B", "C", "D", "correct"]):
                norm.append(randomize_choices({
                    "q": q["q"],
                    "choices": [q["A"], q["B"], q["C"], q["D"]],
                    "correct": q["correct"]
                }))
        return norm
    except Exception as e:
        st.error(f"Perplexity error: {str(e)[:120]}")
        return []


def ask_ai_tutor(question, topic, chat_history):
    if not USE_PPLX or not client:
        return "AI Tutor unavailable. Add PERPLEXITY_API_KEY to Streamlit Secrets."
    last_call = st.session_state.get("last_ai_call")
    if last_call and (datetime.now() - last_call).total_seconds() < 4:
        return "⏳ Please wait a moment before sending another message."
    system_prompt = f"""You are a concise math tutor for {topic} students.
- Only answer math questions, especially about {topic}
- Give brief step-by-step guidance, do NOT solve worksheet questions directly
- Use plain text or LaTeX-style math notation
- Keep responses under 150 words"""
    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})
    try:
        response = client.chat.completions.create(
            model="sonar",
            messages=messages,
            temperature=0.3,
            max_tokens=300
        )
        st.session_state["last_ai_call"] = datetime.now()
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I couldn't process that. Error: {str(e)[:100]}"


# ── AUTH ──────────────────────────────────────────────────────────────────────
def teacher_login():
    if "teacher_user" in st.session_state:
        return st.session_state["teacher_user"]
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div class="login-card math-doodle-bg">
            <h2>🏫 Teacher Login</h2>
            <p class="login-subtitle">Access your class dashboard and manage worksheets</p>
        </div>
        <div class="math-strip">π &nbsp; ∑ &nbsp; √ &nbsp; ∫ &nbsp; ∞ &nbsp; θ &nbsp; α &nbsp; Δ &nbsp; ≈ &nbsp; ℝ</div>
        """, unsafe_allow_html=True)
        subject = st.selectbox("Subject", list(TEACHERS.keys()))
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        if st.button("Sign In →", type="primary", use_container_width=True):
            conf = TEACHERS.get(subject, {})
            if username == conf.get("username") and password == conf.get("password"):
                st.session_state["teacher_user"] = {"username": username, "subject": subject}
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")
    st.stop()


def student_login():
    if "student_user" in st.session_state:
        return st.session_state["student_user"]
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div class="login-card math-doodle-bg">
            <h2>🎓 Student Login</h2>
            <p class="login-subtitle">Sign in to access your personalised worksheets</p>
        </div>
        <div class="math-strip">π &nbsp; ∑ &nbsp; √ &nbsp; ∫ &nbsp; ∞ &nbsp; θ &nbsp; α &nbsp; Δ &nbsp; ≈ &nbsp; ℝ</div>
        """, unsafe_allow_html=True)
        username = st.text_input("Student Name", placeholder="Enter your full name")
        password = st.text_input("Password", type="password", key="student_pw", placeholder="Enter your password")
        if st.button("Sign In →", key="student_login_btn", type="primary", use_container_width=True):
            with get_conn() as conn:
                row = conn.execute(
                    "SELECT password FROM student_logins WHERE student_name = ?",
                    (username.strip(),)
                ).fetchone()
            if row and password == row[0]:
                st.session_state["student_user"] = username.strip()
                st.rerun()
            else:
                st.error("❌ Invalid name or password. Please try again.")
    st.stop()


# ── STUDENT VIEW ──────────────────────────────────────────────────────────────
if view_mode == "Student Access":
    student_name = student_login()

    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f"""
        <div class="page-header math-doodle-bg">
            <div>
                <h2>🎓 Student Access</h2>
                <div class="sub">Welcome back, {student_name}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)
        if st.button("⬡ Sign Out", key="student_logout"):
            for k in ["student_user", "worksheet", "submitted", "show_answers", "answers"]:
                st.session_state.pop(k, None)
            st.rerun()

    allowed_subjects = get_subjects_for_student(student_name)
    if not allowed_subjects:
        st.warning("Your teachers have not added you to any subject yet.")
        st.stop()

    # ── Sidebar: question source + streak ─────────────────────────────────
    if USE_PPLX:
        question_source = st.sidebar.radio("Question Source", ["Teacher Uploads", "Perplexity AI"])
    else:
        question_source = "Teacher Uploads"
        st.sidebar.info("Add PERPLEXITY_API_KEY to Streamlit Secrets for AI questions")

    streak = get_student_streak(student_name)
    if streak > 0:
        fire = "🔥" * min(streak, 5)
        st.sidebar.markdown(
            f'<p style="color:#d4af48;font-size:0.88rem;font-weight:700;margin-top:0.5rem;">'
            f'{fire} {streak}-day streak!</p>',
            unsafe_allow_html=True
        )

    # topic/difficulty stored via selectboxes above (hidden difficulty); worksheet tab shows them prominently
    if "ws_topic" not in st.session_state:
        st.session_state["ws_topic"] = allowed_subjects[0]
    if "ws_difficulty" not in st.session_state:
        st.session_state["ws_difficulty"] = "Easy"
    topic = st.session_state["ws_topic"]
    difficulty = st.session_state["ws_difficulty"]

    stab1, stab2, stab3, stab4 = st.tabs(["📚 Study Material", "📝 Worksheet", "🤖 AI Tutor", "📊 My Progress"])

    # ── TAB 1: STUDY MATERIAL ────────────────────────────────────────────────
    with stab1:
        st.markdown(f'<div class="page-header" style="padding:1rem 1.5rem;margin-bottom:1rem;"><div><h2 style="font-size:1.1rem!important;">📚 Study Material</h2><div class="sub">Reference notes and resources uploaded by your teachers</div></div></div>', unsafe_allow_html=True)
        any_material_found = False
        for subj in allowed_subjects:
            materials = get_study_material(subj)
            if materials.empty:
                continue
            any_material_found = True
            st.markdown(f'<div class="section-label">📘 {subj}</div>', unsafe_allow_html=True)
            for _, row in materials.iterrows():
                with st.expander(f"📄 {row['title']}"):
                    st.caption(f"Uploaded: {row['uploaded_at']}")
                    if row["content"]:
                        st.markdown(row["content"])
                    elif row["file_data"] is not None:
                        if str(row["file_name"]).endswith(".pdf"):
                            st.download_button(
                                f"⬇️ Download {row['file_name']}",
                                data=bytes(row["file_data"]),
                                file_name=row["file_name"],
                                mime="application/pdf",
                                key=f"s_dl_{row['id']}"
                            )
                        else:
                            st.image(bytes(row["file_data"]), caption=row["file_name"])
        if not any_material_found:
            st.info("No study material available for your subjects yet.")

    # ── TAB 2: WORKSHEET ──────────────────────────────────────────────────────
    with stab2:
        # ── Settings card ─────────────────────────────────────────────────
        st.markdown('<div class="section-label">⚙️ Worksheet Settings</div>', unsafe_allow_html=True)
        ws_col1, ws_col2 = st.columns([2, 1])
        with ws_col1:
            new_topic = st.selectbox("Topic", allowed_subjects, index=allowed_subjects.index(topic) if topic in allowed_subjects else 0, key="ws_topic_sel")
        with ws_col2:
            new_diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=["Easy","Medium","Hard"].index(difficulty), key="ws_diff_sel")
        if new_topic != topic or new_diff != difficulty:
            st.session_state["ws_topic"] = new_topic
            st.session_state["ws_difficulty"] = new_diff
            for k in ["worksheet", "submitted", "show_answers", "answers", "last_score", "elapsed_sec"]:
                st.session_state.pop(k, None)
            topic = new_topic
            difficulty = new_diff
            st.rerun()

        if st.button("✨ Generate New Worksheet", type="primary", use_container_width=True):
            worksheet = (
                generate_perplexity_questions(topic, difficulty)
                if question_source == "Perplexity AI"
                else generate_db_questions(topic, difficulty)
            )
            if not worksheet:
                if question_source == "Perplexity AI":
                    st.error("Could not generate AI questions right now. Try again.")
                else:
                    st.error(f"No uploaded {difficulty} questions found for {topic}.")
            else:
                st.session_state["worksheet"] = worksheet
                st.session_state["submitted"] = False
                st.session_state["show_answers"] = False
                st.session_state["answers"] = {}
                st.session_state["worksheet_start"] = datetime.now()   # ← timer start
                # clear any previous hints
                for k in list(st.session_state.keys()):
                    if k.startswith("hint_shown_"):
                        del st.session_state[k]
                st.rerun()

        if "worksheet" in st.session_state:
            submitted = st.session_state.get("submitted", False)
            show_answers = st.session_state.get("show_answers", False)

            # ── Timer display ──────────────────────────────────────────────
            start_time = st.session_state.get("worksheet_start")
            if start_time and not submitted:
                elapsed = int((datetime.now() - start_time).total_seconds())
                mins, secs = divmod(elapsed, 60)
                st.markdown(
                    f'<p style="text-align:right;color:var(--ink-light);font-size:0.82rem;'
                    f'margin-bottom:0.25rem;">⏱️ Time elapsed: <b>{mins:02d}:{secs:02d}</b></p>',
                    unsafe_allow_html=True
                )

            st.markdown('<div class="worksheet-card math-doodle-bg">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-label">📝 Worksheet — Multiple Choice{"&nbsp;&nbsp;<span class=\'badge badge-gold\'>Review Mode</span>" if show_answers else ""}</div>', unsafe_allow_html=True)

            for i, q_data in enumerate(st.session_state["worksheet"]):
                st.markdown(f"### Q{i+1}")
                render_math_or_text(q_data["q"])
                choices = q_data["choices"]
                correct_idx = q_data["correct"]
                selected_idx = st.session_state["answers"].get(i)

                for j, ch in enumerate(choices):
                    st.markdown('<div class="option-box">', unsafe_allow_html=True)
                    cols = st.columns([1, 12])
                    with cols[0]:
                        if st.button(
                            "●" if selected_idx == j else "○",
                            key=f"pick_{i}_{j}",
                            disabled=submitted
                        ):
                            st.session_state["answers"][i] = j
                            st.rerun()
                    with cols[1]:
                        render_math_or_text(ch, label=f"{chr(65+j)}.")
                    st.markdown('</div>', unsafe_allow_html=True)

                if show_answers:
                    if selected_idx is not None:
                        if selected_idx == correct_idx:
                            st.success(f"✅ Correct: {chr(65+selected_idx)}")
                        else:
                            st.error(f"Your answer: {chr(65+selected_idx)}")
                            st.info(f"Correct answer: {chr(65+correct_idx)}")
                    else:
                        st.warning("You didn't answer this question")
                        st.info(f"Correct answer: {chr(65+correct_idx)}")
                elif not submitted:
                    # ── Hint button (only before submitting) ──────────────
                    hint_key = f"hint_{i}"
                    hint_shown_key = f"hint_shown_{i}"
                    if USE_PPLX:
                        if st.button(f"💡 Hint for Q{i+1}", key=hint_key):
                            with st.spinner("Getting hint..."):
                                hint_prompt = (
                                    f"Give a single short hint (max 2 sentences, no answer) "
                                    f"for this {topic} question: {q_data['q']}"
                                )
                                hint = ask_ai_tutor(hint_prompt, topic, [])
                            st.session_state[hint_shown_key] = hint
                        if hint_shown_key in st.session_state:
                            st.info(f"💡 {st.session_state[hint_shown_key]}")

            colA, colB = st.columns([3, 1])
            with colA:
                if not submitted:
                    if st.button("📤 Submit Answers", type="primary",
                                 disabled=len(st.session_state["answers"]) == 0):
                        final_score = sum(
                            1 for i, q_data in enumerate(st.session_state["worksheet"])
                            if st.session_state["answers"].get(i) == q_data["correct"]
                        )
                        # capture elapsed time
                        start_t = st.session_state.get("worksheet_start")
                        elapsed_sec = int((datetime.now() - start_t).total_seconds()) if start_t else 0
                        st.session_state["elapsed_sec"] = elapsed_sec

                        with get_conn() as conn:
                            subject_id    = get_or_create_subject(conn, topic)
                            difficulty_id = get_difficulty_id(conn, difficulty)
                            conn.execute("""
                                INSERT INTO performance
                                    (student_name, subject_id, difficulty_id, score, submitted_at)
                                VALUES (?, ?, ?, ?, ?)
                            """, (student_name, subject_id, difficulty_id,
                                  final_score, datetime.now().isoformat()))
                            log_audit(conn, student_name, "student", "submit_worksheet",
                                      f"Score {final_score}/5 on {topic} {difficulty} in {elapsed_sec}s")
                            conn.commit()
                        st.session_state["submitted"] = True
                        st.session_state["show_answers"] = True
                        st.session_state["last_score"] = final_score
                        st.cache_data.clear()
                        st.rerun()   # balloons removed here — shown after rerun below
                else:
                        last_score = st.session_state.get("last_score", 0)
                        elapsed_sec = st.session_state.get("elapsed_sec")
                        if elapsed_sec is not None:
                            mins, secs = divmod(elapsed_sec, 60)
                            st.markdown(
                                f'<p style="color:var(--ink-light);font-size:0.82rem;">'
                                f'⏱️ Completed in <b>{mins:02d}:{secs:02d}</b></p>',
                                unsafe_allow_html=True
                            )
                        score_feedback(last_score)
                        if last_score == 5:
                            st.balloons()

            with colB:
                if st.button("➜ New Worksheet"):
                    for k in ["worksheet", "submitted", "show_answers", "answers", "last_score"]:
                        st.session_state.pop(k, None)
                    st.rerun()

            if submitted:
                missed = [
                    st.session_state["worksheet"][i]
                    for i in range(len(st.session_state["worksheet"]))
                    if st.session_state["answers"].get(i) != st.session_state["worksheet"][i]["correct"]
                ]
                if missed:
                    st.markdown("---")
                    if st.button(f"🔁 Practice {len(missed)} Missed Question(s)", use_container_width=True):
                        st.session_state["worksheet"] = missed
                        st.session_state["submitted"] = False
                        st.session_state["show_answers"] = False
                        st.session_state["answers"] = {}
                        st.session_state.pop("last_score", None)
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 4: MY PROGRESS ───────────────────────────────────────────────────
    with stab4:
        st.markdown(f'<div class="page-header" style="padding:1rem 1.5rem;margin-bottom:1rem;"><div><h2 style="font-size:1.1rem!important;">📊 My Progress — {student_name}</h2><div class="sub">Track your performance over time</div></div></div>', unsafe_allow_html=True)

        # streak badge
        streak = get_student_streak(student_name)
        if streak > 0:
            fire = "🔥" * min(streak, 5)
            st.markdown(
                f'<p style="font-size:1rem;font-weight:700;color:var(--gold);">'
                f'{fire} {streak}-day streak! Keep it up!</p>',
                unsafe_allow_html=True
            )

        history = get_student_history(student_name)

        if history.empty:
            st.info("Complete a worksheet to start tracking your progress.")
        else:
            # ── Score trend chart ─────────────────────────────────────────
            st.markdown('<div class="section-label">📈 Score Trend Over Time</div>', unsafe_allow_html=True)
            chart_df = history[["submitted_at", "percent", "topic"]].copy()
            chart_df["submitted_at"] = pd.to_datetime(chart_df["submitted_at"])
            chart_df = chart_df.sort_values("submitted_at")
            pivot = chart_df.pivot_table(
                index="submitted_at", columns="topic", values="percent", aggfunc="mean"
            )
            st.line_chart(pivot, use_container_width=True)

            # ── Full history ──────────────────────────────────────────────
            st.markdown('<div class="section-label">🗂️ Full Attempt History</div>', unsafe_allow_html=True)
            hist_display = history[["topic", "difficulty", "score", "percent", "submitted_at"]].copy()
            hist_display["Score"] = hist_display["score"].apply(lambda s: f"{int(s)}/5")
            hist_display["Percentage (%)"] = hist_display["percent"].apply(lambda p: f"{int(round(p))}%")
            hist_display["Submitted"] = pd.to_datetime(hist_display["submitted_at"], errors="coerce").dt.strftime("%d/%m/%y, %H:%M")
            hist_display = hist_display.rename(columns={"topic": "Topic", "difficulty": "Difficulty"})
            hist_display = hist_display[["Topic", "Difficulty", "Score", "Percentage (%)", "Submitted"]]
            st.dataframe(hist_display, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Download My History",
                data=hist_display.to_csv(index=False),
                file_name=f"{student_name}_history.csv",
                mime="text/csv"
            )

    # ── TAB 3: AI TUTOR ───────────────────────────────────────────────────────
    with stab3:
        st.markdown(f'<div class="page-header" style="padding:1rem 1.5rem;margin-bottom:1rem;"><div><h2 style="font-size:1.1rem!important;">🤖 AI Tutor — {topic}</h2><div class="sub">Ask me anything · I guide you, I don\'t give away answers!</div></div></div>', unsafe_allow_html=True)
        if not USE_PPLX:
            st.warning("AI Tutor requires a PERPLEXITY_API_KEY in Streamlit Secrets.")
        else:
            chat_key = f"chat_history_{student_name}_{topic}"
            if chat_key not in st.session_state:
                st.session_state[chat_key] = load_chat_history_from_db(student_name, topic)

            col_a, col_b = st.columns([3, 1])
            with col_b:
                if st.button("🗑️ Clear Chat", key="clear_chat"):
                    st.session_state[chat_key] = []
                    with get_conn() as conn:
                        subject_id = get_or_create_subject(conn, topic)
                        conn.execute(
                            "DELETE FROM chat_history WHERE student_name = ? AND subject_id = ?",
                            (student_name, subject_id)
                        )
                        conn.commit()
                    st.rerun()

            chat_history = st.session_state[chat_key]
            for msg in chat_history:
                if msg["role"] == "user":
                    st.markdown(
                        f'<div class="chat-bubble-user">🧑‍🎓 <b>{student_name}:</b> {msg["content"]}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="chat-bubble-ai">🤖 <b>AI Tutor:</b> {msg["content"]}</div>',
                        unsafe_allow_html=True
                    )

            suggestions = {
                "Algebra":   ["How do I solve for x?", "Explain slope-intercept form", "What is the quadratic formula?"],
                "Fractions": ["How do I add fractions?", "What is a mixed number?", "How do I divide fractions?"],
                "Calculus":  ["What is a derivative?", "How do I find an integral?", "Explain the chain rule"],
            }
            quick_prompts = suggestions.get(topic, ["Explain this topic", "Give me a study tip", "What should I focus on?"])
            st.markdown('<div class="section-label">💬 Quick Questions</div>', unsafe_allow_html=True)
            cols = st.columns(len(quick_prompts))
            for i, prompt in enumerate(quick_prompts):
                with cols[i]:
                    if st.button(prompt, key=f"quick_{i}"):
                        with st.spinner("🤖 AI Tutor is thinking..."):
                            reply = ask_ai_tutor(prompt, topic, chat_history)
                        st.session_state[chat_key].append({"role": "user", "content": prompt})
                        st.session_state[chat_key].append({"role": "assistant", "content": reply})
                        save_chat_message(student_name, topic, "user", prompt)
                        save_chat_message(student_name, topic, "assistant", reply)
                        st.rerun()

            with st.form(key="chat_form", clear_on_submit=True):
                user_input = st.text_input(
                    "Ask a question...",
                    placeholder=f"e.g. Can you explain how to simplify {topic} problems?"
                )
                send = st.form_submit_button("Send ➤")

            if send and user_input.strip():
                with st.spinner("🤖 AI Tutor is thinking..."):
                    reply = ask_ai_tutor(user_input.strip(), topic, chat_history)
                st.session_state[chat_key].append({"role": "user", "content": user_input.strip()})
                st.session_state[chat_key].append({"role": "assistant", "content": reply})
                save_chat_message(student_name, topic, "user", user_input.strip())
                save_chat_message(student_name, topic, "assistant", reply)
                st.rerun()


# ── TEACHER VIEW ──────────────────────────────────────────────────────────────
else:
    teacher = teacher_login()
    subject = teacher["subject"]

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"""
        <div class="page-header math-doodle-bg">
            <div>
                <h2>🏫 Teacher Dashboard</h2>
                <div class="sub">{subject} &nbsp;·&nbsp; {teacher["username"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)
        if st.button("⬡ Sign Out", key="teacher_logout"):
            st.session_state.pop("teacher_user", None)
            st.rerun()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📊 Overview", "👥 Manage Students", "⚠️ Reset Data", "⬆️ Upload Questions", "📖 Study Material", "📋 Student Reports"]
    )

    # ── TAB 1: OVERVIEW ───────────────────────────────────────────────────────
    with tab1:
        all_students = get_allowed_students_for_subject(subject)
        qcounts = get_question_counts_for_subject(subject)
        weak = get_weak_students(subject)
        scoreboard = get_class_scoreboard_for_subject(subject)

        # Count total worksheets generated (= total performance rows for this subject)
        with get_conn() as _conn:
            _ws_row = _conn.execute(
                """SELECT COUNT(*) FROM performance p
                   JOIN subjects s ON p.subject_id = s.id
                   WHERE s.name = ?""", (subject,)
            ).fetchone()
        total_worksheets = _ws_row[0] if _ws_row else 0

        # ── Top metrics row ───────────────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("👥 Enrolled", len(all_students))
        m2.metric("📄 Worksheets Generated", total_worksheets)
        m3.metric("⚠️ At-Risk", len(weak))
        avg_class = scoreboard["avg_percent"].mean() if not scoreboard.empty and "avg_percent" in scoreboard.columns else None
        m4.metric("📈 Class Avg", f"{avg_class:.1f}%" if avg_class is not None else "—")

        st.markdown('<div class="section-label">🏆 Class Scoreboard</div>', unsafe_allow_html=True)
        if all_students:
            # Build per-student worksheet attempt counts
            with get_conn() as _conn:
                _att_df = pd.read_sql(
                    """SELECT p.student_name, COUNT(*) AS attempted
                       FROM performance p
                       JOIN subjects s ON p.subject_id = s.id
                       WHERE s.name = ?
                       GROUP BY p.student_name""",
                    _conn, params=(subject,)
                )
            att_map = dict(zip(_att_df["student_name"], _att_df["attempted"])) if not _att_df.empty else {}
            # Total worksheets available = total performance rows across all students (use as denominator)
            # For "Not Yet Attempted": students in the class who have 0 attempts
            sb_rows = []
            for i, sname in enumerate(sorted(all_students), start=1):
                attempted = att_map.get(sname, 0)
                sb_rows.append({
                    "S.No": i,
                    "Student Name": sname,
                    "Worksheets Attempted": attempted,
                    "Yet to Attempt": "✅ Started" if attempted > 0 else "⏳ Not Started Yet",
                })
            sb_display = pd.DataFrame(sb_rows)
            st.dataframe(sb_display, use_container_width=True, hide_index=True)
            st.download_button(
                "⬇️ Export Scoreboard CSV",
                data=sb_display.to_csv(index=False),
                file_name=f"{subject}_scoreboard.csv",
                mime="text/csv"
            )
        else:
            st.info("No students enrolled for this subject yet.")

        st.markdown('<div class="section-label">📋 Uploaded Question Counts</div>', unsafe_allow_html=True)
        if not qcounts.empty:
            st.dataframe(qcounts, hide_index=True, use_container_width=True)
        else:
            st.info("No questions uploaded yet.")

    # ── TAB 2: MANAGE STUDENTS ────────────────────────────────────────────────
    with tab2:
        current = get_allowed_students_for_subject(subject)
        st.markdown(f'<div class="page-header" style="padding:1rem 1.5rem;margin-bottom:1rem;"><div><h2 style="font-size:1.1rem!important;">👥 {subject} Students ({len(current)})</h2><div class="sub">Manage enrolment, passwords and access</div></div></div>', unsafe_allow_html=True)
        if current:
            st.dataframe(pd.DataFrame({"Student": sorted(current)}), hide_index=True)
        else:
            st.info(f"No students registered for {subject} yet.")

        st.markdown('<div class="section-label">➕ Add Student to This Subject</div>', unsafe_allow_html=True)

        add_mode = st.radio("Add method", ["Single student", "Bulk upload (CSV)"], horizontal=True)

        if add_mode == "Single student":
            new_student_name = st.text_input("Student name")
            new_student_password = st.text_input("Student password", type="password")
            if st.button("Add Student"):
                if not new_student_name.strip():
                    st.error("Enter a student name.")
                elif not new_student_password.strip():
                    st.error("Enter a password.")
                else:
                    clean_name = new_student_name.strip()
                    clean_pwd  = new_student_password.strip()
                    with get_conn() as conn:
                        try:
                            conn.execute("BEGIN")
                            conn.execute("INSERT OR IGNORE INTO student_logins (student_name, password) VALUES (?,?)",
                                         (clean_name, clean_pwd))
                            conn.execute("INSERT OR IGNORE INTO allowed_students (student_name) VALUES (?)", (clean_name,))
                            subject_id = get_or_create_subject(conn, subject)
                            conn.execute("INSERT OR IGNORE INTO student_subjects (student_name, subject_id) VALUES (?,?)",
                                         (clean_name, subject_id))
                            log_audit(conn, teacher["username"], "teacher", "add_student",
                                      f"Added {clean_name} to {subject}")
                            conn.execute("COMMIT")
                        except Exception as e:
                            conn.execute("ROLLBACK")
                            st.error(f"Failed to add student: {e}")
                    st.cache_data.clear()
                    st.success(f"Added {clean_name} to {subject}.")
                    st.rerun()
        else:
            st.caption("CSV must have two columns: `student_name` and `password`")
            bulk_file = st.file_uploader("Upload student roster CSV", type=["csv"], key="bulk_students")
            if bulk_file:
                try:
                    bulk_df = pd.read_csv(bulk_file)
                    bulk_df.columns = [c.strip().lower() for c in bulk_df.columns]
                    if {"student_name", "password"} - set(bulk_df.columns):
                        st.error("CSV must contain columns: student_name, password")
                    else:
                        st.markdown('<div class="section-label">👁️ Preview</div>', unsafe_allow_html=True)
                        st.dataframe(bulk_df[["student_name", "password"]].head(10), hide_index=True)
                        if st.button(f"Add {len(bulk_df)} Students to {subject}"):
                            added, skipped = 0, 0
                            with get_conn() as conn:
                                try:
                                    conn.execute("BEGIN")
                                    sid = get_or_create_subject(conn, subject)
                                    for _, row in bulk_df.iterrows():
                                        nm = str(row["student_name"]).strip()
                                        pw = str(row["password"]).strip()
                                        if not nm or not pw:
                                            skipped += 1
                                            continue
                                        conn.execute("INSERT OR IGNORE INTO student_logins (student_name, password) VALUES (?,?)", (nm, pw))
                                        conn.execute("INSERT OR IGNORE INTO allowed_students (student_name) VALUES (?)", (nm,))
                                        conn.execute("INSERT OR IGNORE INTO student_subjects (student_name, subject_id) VALUES (?,?)", (nm, sid))
                                        added += 1
                                    log_audit(conn, teacher["username"], "teacher", "bulk_add_students",
                                              f"Bulk added {added} students to {subject}")
                                    conn.execute("COMMIT")
                                except Exception as e:
                                    conn.execute("ROLLBACK")
                                    st.error(f"Bulk add failed: {e}")
                            st.cache_data.clear()
                            st.success(f"✅ Added {added} students to {subject}." + (f" Skipped {skipped} rows." if skipped else ""))
                            st.rerun()
                except Exception as e:
                    st.error(f"Could not read CSV: {e}")

        st.markdown("---")
        st.markdown('<div class="section-label">➖ Remove Student from Subject</div>', unsafe_allow_html=True)
        to_remove = st.selectbox(f"Remove student from {subject}", ["— select —"] + sorted(current))
        if st.button("Remove From This Subject"):
            if to_remove != "— select —":
                with get_conn() as conn:
                    subject_id = get_or_create_subject(conn, subject)
                    conn.execute("DELETE FROM student_subjects WHERE student_name = ? AND subject_id = ?",
                                 (to_remove, subject_id))
                    log_audit(conn, teacher["username"], "teacher", "remove_student",
                              f"Removed {to_remove} from {subject}")
                    conn.commit()
                st.cache_data.clear()
                st.warning(f"Removed {to_remove} from {subject}")
                st.rerun()

        st.markdown("---")
        st.markdown('<div class="section-label">🔑 Reset Student Password</div>', unsafe_allow_html=True)
        pwd_student = st.selectbox(
            f"Choose student in {subject} to set password",
            ["— select —"] + sorted(current),
            key="pwd_student_select"
        )
        new_pwd = st.text_input("New password", type="password", key="reset_student_pwd")
        if st.button("Save Password"):
            if pwd_student == "— select —":
                st.error("Choose a student first.")
            elif not new_pwd.strip():
                st.error("Enter a password.")
            else:
                with get_conn() as conn:
                    conn.execute("""
                        INSERT INTO student_logins (student_name, password)
                        VALUES (?, ?)
                        ON CONFLICT(student_name) DO UPDATE SET password = excluded.password
                    """, (pwd_student, new_pwd.strip()))
                    log_audit(conn, teacher["username"], "teacher", "reset_password",
                              f"Password reset for {pwd_student}")
                    conn.commit()
                st.cache_data.clear()
                st.success(f"Password set for {pwd_student}")
                st.rerun()

    # ── TAB 3: RESET DATA ─────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="page-header" style="padding:1rem 1.5rem;margin-bottom:1rem;background:linear-gradient(135deg,#7f1d1d,#991b1b);"><div><h2 style="font-size:1.1rem!important;color:#fca5a5!important;">⚠️ Reset Data</h2><div class="sub" style="color:rgba(252,165,165,0.7);">These actions are permanent and cannot be undone</div></div></div>', unsafe_allow_html=True)
        with get_conn() as conn:
            subject_id = get_or_create_subject(conn, subject)
            perf_df = pd.read_sql(
                "SELECT DISTINCT student_name FROM performance WHERE subject_id = ?",
                conn, params=(subject_id,)
            )
        perf_students = perf_df["student_name"].tolist()

        st.markdown('<div class="section-label">👤 Reset Individual Student</div>', unsafe_allow_html=True)
        student_reset = st.selectbox("Reset student data (this subject only)", ["— select —"] + perf_students)
        if st.button("Clear This Student"):
            if student_reset != "— select —":
                with get_conn() as conn:
                    subject_id = get_or_create_subject(conn, subject)
                    conn.execute("DELETE FROM performance WHERE student_name = ? AND subject_id = ?",
                                 (student_reset, subject_id))
                    log_audit(conn, teacher["username"], "teacher", "clear_student_data",
                              f"Cleared {subject} records for {student_reset}")
                    conn.commit()
                st.cache_data.clear()
                st.success(f"Cleared {subject} records for {student_reset}")
                st.rerun()

        st.markdown("---")
        st.markdown('<div class="section-label" style="color:#b91c1c;border-color:#fca5a5;">🗑️ Danger Zone — Clear All Scores</div>', unsafe_allow_html=True)
        confirm_clear_all = st.checkbox(f"Yes, delete ALL performance data for {subject}")
        if st.button("🗑️ Clear ALL Scores for this Subject"):
            if confirm_clear_all:
                with get_conn() as conn:
                    subject_id = get_or_create_subject(conn, subject)
                    conn.execute("DELETE FROM performance WHERE subject_id = ?", (subject_id,))
                    log_audit(conn, teacher["username"], "teacher", "clear_all_scores",
                              f"Cleared all {subject} scores")
                    conn.commit()
                st.cache_data.clear()
                st.error(f"All {subject} scores have been cleared.")
                st.rerun()
            else:
                st.warning("Please confirm before deleting all scores.")

    # ── TAB 4: UPLOAD QUESTIONS ───────────────────────────────────────────────
    with tab4:
        st.markdown(f'<div class="page-header" style="padding:1rem 1.5rem;margin-bottom:1rem;"><div><h2 style="font-size:1.1rem!important;">⬆️ Upload Questions — {subject}</h2><div class="sub">CSV columns required: difficulty · question · choice_a/b/c/d · correct_letter</div></div></div>', unsafe_allow_html=True)

        template_df = pd.DataFrame({
            "difficulty": ["Easy", "Medium", "Hard"],
            "question": ["enter your question here"] * 3,
            "choice_a": ["enter option A"] * 3,
            "choice_b": ["enter option B"] * 3,
            "choice_c": ["enter option C"] * 3,
            "choice_d": ["enter option D"] * 3,
            "correct_letter": ["enter correct option(A,B,C,D)"] * 3
        })
        st.download_button(
            "Download CSV Template",
            data=template_df.to_csv(index=False),
            file_name=f"{subject.lower()}_questions_template.csv",
            mime="text/csv"
        )

        upload_mode = st.radio("Upload mode", ["Append", "Replace all for this subject"])
        uploaded_file = st.file_uploader("Upload worksheet CSV", type=["csv"])

        if uploaded_file is not None:
            try:
                uploaded_file.seek(0)
                preview_df = pd.read_csv(uploaded_file)
                st.markdown('<div class="section-label">📋 Preview</div>', unsafe_allow_html=True)
                st.dataframe(preview_df, use_container_width=True)

                required_cols = {"difficulty", "question", "choice_a", "choice_b",
                                  "choice_c", "choice_d", "correct_letter"}
                missing = required_cols - {c.strip() for c in preview_df.columns}
                if missing:
                    st.error(f"Missing required columns: {', '.join(sorted(missing))}")
                else:
                    df = preview_df.copy()
                    df.columns = [c.strip() for c in df.columns]
                    df["difficulty"] = df["difficulty"].astype(str).str.strip().str.capitalize()
                    # Auto-convert numeric correct_letter (1→A, 2→B, 3→C, 4→D)
                    num_to_letter = {"1": "A", "2": "B", "3": "C", "4": "D"}
                    df["correct_letter"] = (
                        df["correct_letter"]
                        .astype(str).str.strip().str.upper()
                        .replace(num_to_letter)
                    )

                    if st.button("Save Uploaded Questions"):
                        with get_conn() as conn:
                            try:
                                conn.execute("BEGIN")
                                subject_id = get_or_create_subject(conn, subject)
                                if upload_mode == "Replace all for this subject":
                                    conn.execute("DELETE FROM question_bank WHERE subject_id = ?", (subject_id,))
                                rows = []
                                skipped_rows = []
                                for idx, row in df.iterrows():
                                    diff_val = str(row["difficulty"]).strip().capitalize()
                                    # Normalize common variations
                                    diff_map = {"Easy": "Easy", "Medium": "Medium", "Hard": "Hard",
                                                "Easy ": "Easy", "Med": "Medium", "Difficult": "Hard"}
                                    diff_val = diff_map.get(diff_val, diff_val)
                                    difficulty_id = get_difficulty_id(conn, diff_val)
                                    if difficulty_id is None:
                                        skipped_rows.append(idx + 2)  # +2: header + 0-index
                                        continue
                                    rows.append((
                                        subject_id, difficulty_id,
                                        str(row["question"]).strip(),
                                        str(row["choice_a"]).strip(),
                                        str(row["choice_b"]).strip(),
                                        str(row["choice_c"]).strip(),
                                        str(row["choice_d"]).strip(),
                                        str(row["correct_letter"]).strip().upper(),
                                        datetime.now().isoformat()
                                    ))
                                if rows:
                                    conn.executemany("""
                                        INSERT OR REPLACE INTO question_bank
                                            (subject_id, difficulty_id, question,
                                             choice_a, choice_b, choice_c, choice_d,
                                             correct_letter, uploaded_at)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, rows)
                                log_audit(conn, teacher["username"], "teacher", "upload_questions",
                                          f"Uploaded {len(rows)} questions for {subject}")
                                conn.execute("COMMIT")
                                st.cache_data.clear()
                                if rows:
                                    st.success(f"✅ Saved {len(rows)} question(s) for {subject}.")
                                else:
                                    st.error("❌ No questions were saved. Check that the 'difficulty' column uses: Easy, Medium, or Hard.")
                                if skipped_rows:
                                    st.warning(f"⚠️ Skipped {len(skipped_rows)} row(s) with unrecognised difficulty (rows: {skipped_rows}). Allowed values: Easy, Medium, Hard.")
                                if rows:
                                    st.rerun()
                            except Exception as e:
                                conn.execute("ROLLBACK")
                                st.error(f"Upload failed: {e}")
            except Exception as e:
                st.error(f"Could not read CSV file: {str(e)[:150]}")

    # ── TAB 5: STUDY MATERIAL ─────────────────────────────────────────────────
    with tab5:
        st.markdown(f'<div class="page-header" style="padding:1rem 1.5rem;margin-bottom:1rem;"><div><h2 style="font-size:1.1rem!important;">📖 Study Material — {subject}</h2><div class="sub">Upload notes, PDFs or images for students</div></div></div>', unsafe_allow_html=True)

        material_type = st.radio("Material Type", ["Text / Notes", "File Upload (PDF or Image)"])

        if material_type == "Text / Notes":
            material_title = st.text_input("Title", placeholder="e.g. Introduction to Algebra")
            material_body  = st.text_area("Content", height=250, placeholder="Paste notes, formulas, explanations...")
            if st.button("Save Study Material"):
                if not material_title.strip() or not material_body.strip():
                    st.error("Please enter both a title and content.")
                else:
                    with get_conn() as conn:
                        subject_id = get_or_create_subject(conn, subject)
                        conn.execute("""
                            INSERT INTO study_material (subject_id, title, content, uploaded_at)
                            VALUES (?, ?, ?, ?)
                        """, (subject_id, material_title.strip(), material_body.strip(), datetime.now().isoformat()))
                        log_audit(conn, teacher["username"], "teacher", "upload_material",
                                  f"Added text material: {material_title.strip()}")
                        conn.commit()
                    st.cache_data.clear()
                    st.success(f"Saved: {material_title.strip()}")
                    st.rerun()
        else:
            material_title    = st.text_input("Title", placeholder="e.g. Algebra Cheat Sheet", key="file_title")
            uploaded_material = st.file_uploader("Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
            if st.button("Save File"):
                if not material_title.strip() or uploaded_material is None:
                    st.error("Please enter a title and upload a file.")
                else:
                    file_bytes = uploaded_material.read()
                    with get_conn() as conn:
                        subject_id = get_or_create_subject(conn, subject)
                        conn.execute("""
                            INSERT INTO study_material
                                (subject_id, title, file_name, file_data, uploaded_at)
                            VALUES (?, ?, ?, ?, ?)
                        """, (subject_id, material_title.strip(),
                              uploaded_material.name, file_bytes, datetime.now().isoformat()))
                        log_audit(conn, teacher["username"], "teacher", "upload_material",
                                  f"Added file: {uploaded_material.name}")
                        conn.commit()
                    st.cache_data.clear()
                    st.success(f"Saved: {uploaded_material.name}")
                    st.rerun()

        st.markdown("---")
        st.markdown('<div class="section-label">📂 Existing Materials</div>', unsafe_allow_html=True)
        existing = get_study_material(subject)
        if existing.empty:
            st.info("No study material uploaded yet.")
        else:
            for _, row in existing.iterrows():
                with st.expander(f"📄 {row['title']}"):
                    st.caption(f"Uploaded: {row['uploaded_at']}")
                    if row["content"]:
                        st.markdown(row["content"])
                    elif row["file_data"] is not None:
                        if str(row["file_name"]).endswith(".pdf"):
                            st.download_button(
                                f"⬇️ Download {row['file_name']}",
                                data=bytes(row["file_data"]),
                                file_name=row["file_name"],
                                mime="application/pdf",
                                key=f"dl_{row['id']}"
                            )
                        else:
                            st.image(bytes(row["file_data"]), caption=row["file_name"])
                    if st.button("🗑️ Delete", key=f"del_mat_{row['id']}"):
                        with get_conn() as conn:
                            conn.execute("DELETE FROM study_material WHERE id = ?", (row["id"],))
                            log_audit(conn, teacher["username"], "teacher", "delete_material",
                                      f"Deleted material: {row['title']}")
                            conn.commit()
                        st.cache_data.clear()
                        st.rerun()

    # ── TAB 6: STUDENT REPORTS ────────────────────────────────────────────────
    with tab6:
        st.markdown(f'<div class="page-header" style="padding:1rem 1.5rem;margin-bottom:1rem;"><div><h2 style="font-size:1.1rem!important;">📋 Student Reports — {subject}</h2><div class="sub">Individual performance history and at-risk flags</div></div></div>', unsafe_allow_html=True)

        all_students_r = get_allowed_students_for_subject(subject)

        # ── At-risk students with flag action (#10) ───────────────────────
        weak_r = get_weak_students(subject)
        if not weak_r.empty:
            st.markdown('<div class="section-label" style="color:#b91c1c;border-color:#fca5a5;">⚠️ At-Risk Students (avg below 50%)</div>', unsafe_allow_html=True)
            for _, wrow in weak_r.iterrows():
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.markdown(
                        f'<p style="margin:0.3rem 0;"><b>{wrow["student_name"]}</b> — '
                        f'avg <b style="color:#b91c1c;">{wrow["avg_percent"]}%</b> '
                        f'over {wrow["attempts"]} attempt(s)</p>',
                        unsafe_allow_html=True
                    )
                with c2:
                    flag_key = f"flagged_{wrow['student_name']}"
                    already_flagged = st.session_state.get(flag_key, False)
                    if already_flagged:
                        st.markdown('<span style="color:#b8972a;font-size:0.82rem;font-weight:700;">🚩 Flagged</span>', unsafe_allow_html=True)
                    else:
                        if st.button("🚩 Flag", key=f"flag_btn_{wrow['student_name']}"):
                            st.session_state[flag_key] = True
                            log_audit(
                                None, teacher["username"], "teacher", "flag_student",
                                f"Flagged {wrow['student_name']} for review in {subject}"
                            ) if False else None  # audit without DB open here
                            with get_conn() as conn:
                                log_audit(conn, teacher["username"], "teacher", "flag_student",
                                          f"Flagged {wrow['student_name']} for review in {subject}")
                                conn.commit()
                            st.rerun()
                with c3:
                    # quick unflag
                    if st.session_state.get(flag_key):
                        if st.button("✕ Unflag", key=f"unflag_{wrow['student_name']}"):
                            st.session_state[flag_key] = False
                            st.rerun()
            st.markdown("---")

        # ── Drill-down ────────────────────────────────────────────────────
        st.markdown('<div class="section-label">🔍 Individual Student Drill-Down</div>', unsafe_allow_html=True)
        drill_student = st.selectbox(
            "Select a student to view full history",
            ["— select —"] + sorted(all_students_r),
            key="drill_select"
        )
        if drill_student != "— select —":
            drill_history = get_student_history(drill_student)
            if drill_history.empty:
                st.info(f"No attempts recorded for {drill_student} yet.")
            else:
                # mini metrics
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Attempts", len(drill_history))
                m2.metric("Average Score", f"{drill_history['percent'].mean():.1f}%")
                m3.metric("Best Score", f"{drill_history['percent'].max():.0f}%")

                # trend chart
                st.markdown('<div class="section-label">📈 Score Trend</div>', unsafe_allow_html=True)
                chart_h = drill_history[["submitted_at", "percent"]].copy()
                chart_h["submitted_at"] = pd.to_datetime(chart_h["submitted_at"])
                chart_h = chart_h.sort_values("submitted_at").set_index("submitted_at")
                st.line_chart(chart_h["percent"], use_container_width=True)

                # full table
                st.markdown('<div class="section-label">🗂️ Full History</div>', unsafe_allow_html=True)
                display_h = drill_history[["topic", "difficulty", "score", "submitted_at"]].copy()
                # Format score as "obtained / 5"
                display_h["Score"] = display_h["score"].apply(lambda s: f"{int(s)}/5")
                # Format date as dd/mm/yy HH:MM
                display_h["Submitted At"] = pd.to_datetime(display_h["submitted_at"], errors="coerce").dt.strftime("%d/%m/%y %H:%M")
                display_h = display_h.rename(columns={"topic": "Topic", "difficulty": "Difficulty"})
                display_h = display_h[["Topic", "Difficulty", "Score", "Submitted At"]]
                st.dataframe(display_h, use_container_width=True, hide_index=True)
                st.download_button(
                    f"⬇️ Export {drill_student}'s History",
                    data=display_h.to_csv(index=False),
                    file_name=f"{drill_student}_{subject}_history.csv",
                    mime="text/csv",
                    key="export_drill_history"
                )

st.sidebar.markdown("---")
st.sidebar.markdown('<p style="color:rgba(240,228,208,0.32);font-size:0.74rem;text-align:center;font-style:italic;">AI Math Tutor Pro &nbsp;•&nbsp; 2025–2026<br>Adaptive · Intelligent · Effective</p>', unsafe_allow_html=True)