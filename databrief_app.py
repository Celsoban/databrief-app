import streamlit as st
import pandas as pd
import anthropic
import json
import io

# ── Página ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DataBrief",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS — fiel ao React ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stVerticalBlock"],
.stApp {
    background-color: #0A0C10 !important;
    color: #E8EAF0 !important;
    font-family: 'Inter', sans-serif !important;
}

#MainMenu, header[data-testid="stHeader"], footer { display: none !important; }

.block-container {
    padding: 28px 32px !important;
    max-width: 1100px !important;
    margin: 0 auto !important;
    background: transparent !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #111318; }
::-webkit-scrollbar-thumb { background: #1E2230; border-radius: 2px; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}

/* ── Logo ── */
.db-logo { font-family:'Syne',sans-serif; font-weight:800; font-size:24px; color:#E8EAF0; letter-spacing:-.01em; line-height:1; }
.db-logo span { color:#00E5C0; }
.db-subtitle { font-family:'IBM Plex Mono',monospace; font-size:10px; color:#6B7280; letter-spacing:.12em; text-transform:uppercase; margin-top:3px; }
.db-logo-icon {
    width:34px; height:34px;
    background: linear-gradient(135deg,#00E5C0,#0099FF);
    border-radius:9px;
    display:inline-flex; align-items:center; justify-content:center;
    font-size:16px; margin-right:10px; vertical-align:middle;
}

/* ── Tags ── */
.db-tag {
    display:inline-flex; align-items:center; gap:5px;
    background:#00E5C020; color:#00E5C0;
    border:1px solid #00E5C030; border-radius:20px;
    padding:3px 11px; font-size:11px;
    font-family:'IBM Plex Mono',monospace; letter-spacing:.06em; font-weight:500;
    margin-right:6px;
}

/* ── Section title ── */
.db-section-title {
    font-family:'Syne',sans-serif; font-weight:700; font-size:11px;
    letter-spacing:.12em; text-transform:uppercase;
    color:#6B7280; margin-bottom:14px; margin-top:0;
}

/* ── KPI Card ── */
.db-kpi {
    background:#111318; border:1px solid #1E2230; border-radius:14px;
    padding:20px 24px; animation:fadeUp .5s ease both;
    transition: border-color .2s, transform .2s;
}
.db-kpi:hover { border-color:#00E5C050; transform:translateY(-2px); }
.db-kpi-label { font-family:'IBM Plex Mono',monospace; font-size:11px; color:#6B7280; letter-spacing:.08em; text-transform:uppercase; margin-bottom:8px; }
.db-kpi-value { font-family:'Syne',sans-serif; font-weight:700; font-size:28px; color:#00E5C0; line-height:1; }
.db-kpi-sub { font-size:12px; color:#6B7280; margin-top:6px; line-height:1.4; }

/* ── Insight Card ── */
.db-insight-card {
    background:#111318; border:1px solid #1E2230; border-radius:14px;
    padding:22px 26px; animation:fadeUp .5s ease both;
}
.db-insight-line {
    border-left:2px solid #00E5C0; padding-left:14px;
    margin:10px 0; font-size:14px; color:#E8EAF0; line-height:1.65;
}

/* ── Chat bubbles ── */
[data-testid="stChatMessage"] { background:transparent !important; border:none !important; }
[data-testid="stChatMessageContent"] { font-family:'Inter',sans-serif !important; font-size:14px !important; line-height:1.7 !important; color:#E8EAF0 !important; }

/* ── Chat input ── */
[data-testid="stChatInput"] { background:#111318 !important; border:1px solid #1E2230 !important; border-radius:10px !important; }
[data-testid="stChatInput"]:focus-within { border-color:#00E5C060 !important; box-shadow:none !important; }
[data-testid="stChatInput"] textarea { background:transparent !important; color:#E8EAF0 !important; font-family:'Inter',sans-serif !important; font-size:14px !important; }
[data-testid="stChatInput"] textarea::placeholder { color:#6B7280 !important; }
[data-testid="stChatInput"] button { background:#00E5C0 !important; color:#000 !important; border-radius:8px !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background:#111318 !important; border:2px dashed #1E2230 !important;
    border-radius:14px !important; padding:24px !important;
    transition:border-color .25s, background .25s !important;
}
[data-testid="stFileUploader"]:hover { border-color:#00E5C0 !important; background:#00E5C008 !important; }
[data-testid="stFileUploader"] label { color:#E8EAF0 !important; font-family:'Syne',sans-serif !important; font-size:15px !important; font-weight:700 !important; }
[data-testid="stFileUploader"] small, [data-testid="stFileUploaderDropzoneInstructions"] { color:#6B7280 !important; font-size:13px !important; }
[data-testid="stFileUploader"] button { background:#00E5C0 !important; color:#000 !important; font-family:'Syne',sans-serif !important; font-weight:700 !important; border:none !important; border-radius:8px !important; }

/* ── Botão ghost ── */
.stButton > button {
    background:transparent !important; color:#6B7280 !important;
    border:1px solid #1E2230 !important; border-radius:8px !important;
    font-family:'Inter',sans-serif !important; font-size:13px !important;
    padding:8px 18px !important; transition:color .2s, border-color .2s !important;
}
.stButton > button:hover { color:#E8EAF0 !important; border-color:#6B7280 !important; background:transparent !important; }

/* ── Divider ── */
hr { border-color:#1E2230 !important; margin:0 0 28px 0 !important; }

/* ── Shimmer skeleton ── */
.db-shimmer {
    background: linear-gradient(90deg,#111318 25%,#1E2230 50%,#111318 75%);
    background-size:200% 100%; animation:shimmer 1.5s infinite;
    border-radius:14px; height:96px;
}

/* ── Glow fundo upload ── */
.db-glow {
    position:fixed; top:-20%; left:50%; transform:translateX(-50%);
    width:80vw; height:50vh;
    background:radial-gradient(ellipse,#00E5C012 0%,transparent 70%);
    pointer-events:none; z-index:0;
}

/* ── Upload center ── */
.db-upload-title { font-family:'Syne',sans-serif; font-weight:800; font-size:34px; color:#E8EAF0; letter-spacing:-.02em; line-height:1.2; margin-bottom:12px; }
.db-upload-title span { color:#00E5C0; }
.db-upload-sub { color:#6B7280; font-size:15px; line-height:1.7; max-width:420px; margin:0 auto 32px auto; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def read_excel_clean(file) -> pd.DataFrame:
    """Lê Excel ignorando fórmulas, usando só a primeira aba com dados."""
    import openpyxl, io
    raw = file.read() if hasattr(file, "read") else open(file, "rb").read()
    wb  = openpyxl.load_workbook(io.BytesIO(raw), data_only=True)
    # Escolhe a aba com mais dados
    best_sheet = max(wb.sheetnames, key=lambda s: wb[s].max_row * wb[s].max_column)
    ws   = wb[best_sheet]
    data = list(ws.values)
    if not data:
        raise ValueError("Planilha vazia.")
    headers = [str(h) if h is not None else f"Col{i}" for i, h in enumerate(data[0])]
    rows    = data[1:]
    df = pd.DataFrame(rows, columns=headers)
    # Remove colunas totalmente vazias ou que começam com fórmula
    df = df.loc[:, df.apply(lambda col: not col.astype(str).str.startswith("=").all())]
    df = df.dropna(how="all").reset_index(drop=True)
    return df


@st.cache_resource
def get_client():
    import os
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    print(f"[DataBrief] API key presente: {bool(key)} | primeiros chars: {key[:12] if key else 'VAZIA'}", flush=True)
    return anthropic.Anthropic(api_key=key)

def _safe_val(v):
    import math
    if v is None: return None
    if isinstance(v, float) and math.isnan(v): return None
    try:
        import pandas as _pd
        if isinstance(v, _pd.Timestamp): return v.isoformat() if not _pd.isna(v) else None
    except Exception: pass
    if hasattr(v, "item"): return v.item()
    if hasattr(v, "isoformat"): return v.isoformat()
    return v

def build_summary(df: pd.DataFrame) -> str:
    import math, pandas as _pd

    df = df.copy()

    # Converte TODAS as colunas de data/hora para string — inclui datetime64, datetimetz e object com Timestamp/NaT
    for col in df.columns:
        if _pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime("%Y-%m-%d").fillna("")
        else:
            # Converte cell a cell para pegar Timestamp/NaT escondido em object columns
            def _to_safe(v):
                if v is None: return None
                if isinstance(v, float) and math.isnan(v): return None
                if isinstance(v, _pd.Timestamp): return v.strftime("%Y-%m-%d") if not _pd.isna(v) else None
                try:
                    if _pd.isna(v): return None
                except Exception: pass
                if hasattr(v, "item"): return v.item()
                return v
            df[col] = df[col].apply(_to_safe)

    num_cols  = df.select_dtypes(include="number").columns.tolist()
    text_cols = [c for c in df.columns if c not in num_cols]

    agg = {}
    for col in num_cols:
        vals = df[col].dropna()
        if len(vals) == 0: continue
        agg[col] = {
            "soma":      round(float(vals.sum()),  2),
            "media":     round(float(vals.mean()), 2),
            "min":       round(float(vals.min()),  2),
            "max":       round(float(vals.max()),  2),
            "nao_nulos": int(vals.count()),
        }

    # Frequências: só colunas com baixa cardinalidade (categorias reais, não IDs/datas)
    freq = {}
    for col in text_cols:
        unique = df[col].nunique(dropna=True)
        if unique <= 20:  # ignora colunas com muitos valores únicos (nomes, IDs, datas)
            f = df[col].value_counts(dropna=True).head(5).to_dict()
            freq[col] = {str(k): int(v) for k, v in f.items()}

    # Amostra reduzida: só 3 linhas, só colunas numéricas + categóricas relevantes
    cols_amostra = num_cols[:8] + [c for c in text_cols if c in freq][:5]
    amostra = df[cols_amostra].head(3).where(df[cols_amostra].head(3).notna(), other=None).to_dict(orient="records")

    payload = {
        "ATENCAO": "Use APENAS os dados abaixo. Nunca invente ou estime valores.",
        "total_registros_exato": len(df),
        "colunas_numericas": num_cols,
        "colunas_categoricas": list(freq.keys()),
        "agregados_numericos": agg,
        "frequencias_categoricas": freq,
        "amostra_3_linhas": amostra,
    }
    result = json.dumps(payload, ensure_ascii=False, separators=(',',':'), default=str)
    print(f"[DataBrief] summary otimizado — {len(result)} chars", flush=True)
    return result

def call_claude(system: str, message: str, max_tok: int = 800) -> str:
    import time, httpx, os
    t0 = time.time()
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    print(f"[DataBrief] Chamando API Claude... max_tokens={max_tok} | key={key[:12] if key else 'VAZIA'}", flush=True)
    try:
        client = anthropic.Anthropic(
            api_key=key,
            timeout=httpx.Timeout(45.0, connect=10.0)
        )
        r = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tok,
            system=system,
            messages=[{"role": "user", "content": message}],
        )
        print(f"[DataBrief] API respondeu em {time.time()-t0:.1f}s", flush=True)
        return r.content[0].text
    except Exception as e:
        print(f"[DataBrief] ERRO na API: {type(e).__name__}: {e}", flush=True)
        raise

def analyze_data(df: pd.DataFrame, tipo_negocio: str = "") -> dict:
    print(f"[DataBrief] analyze_data iniciado — {len(df)} linhas", flush=True)
    summary  = build_summary(df)
    print(f"[DataBrief] summary gerado — {len(summary)} chars", flush=True)
    contexto = f"Tipo de negócio: {tipo_negocio}." if tipo_negocio else "Tipo de negócio: não informado — identifique pelo contexto dos dados."
    system   = (
        "Você é o DataBrief, analista de dados especialista em pequenos negócios.\n"
        + contexto + "\n"
        + "Planilha recebida:\n" + summary + "\n"
        + "Responda em português, de forma clara e direta para um dono de negócio sem conhecimento técnico."
    )
    raw     = call_claude(system, """Analise os dados e retorne SOMENTE JSON válido (sem markdown, sem texto extra):
{
  "kpis": [
    {"label":"...","value":"...","sub":"..."}
  ],
  "melhorou": ["ponto positivo 1", "ponto positivo 2"],
  "piorou":   ["ponto negativo 1", "ponto negativo 2"],
  "alertas":  ["anomalia ou atenção 1", "anomalia ou atenção 2"],
  "recomendacao": "Uma ação concreta e imediata que o dono deve tomar agora."
}
REGRAS CRÍTICAS:
- Use EXCLUSIVAMENTE os números dos campos "agregados_numericos" e "frequencias_categoricas"
- O total de registros é EXATAMENTE o campo "total_registros_exato" — nunca use outro número
- NUNCA invente ou estime valores que não estejam explicitamente nos dados
- Valores dos KPIs devem vir diretamente dos dados, com unidade (ex: "R$ 2.344.793", "71 registros")
- "melhorou" e "piorou": comparações reais dentro dos dados (top vs bottom de frequências)
- "alertas": concentrações, valores extremos, campos com muitos nulos
- "recomendacao": 1 única ação prática baseada nos dados reais
- Se não houver dados suficientes para alguma seção, retorne lista vazia []""")
    return json.loads(raw.replace("```json","").replace("```","").strip())

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("df",None),("file_name",""),("analysis",None),("messages",[]),("tipo_negocio","")]:
    if k not in st.session_state:
        st.session_state[k] = v

TIPOS_NEGOCIO = [
    {"emoji": "🍽️", "label": "Restaurante"},
    {"emoji": "🏪", "label": "Loja / Varejo"},
    {"emoji": "🏥", "label": "Clínica / Saúde"},
    {"emoji": "🏋️", "label": "Academia / Fitness"},
    {"emoji": "💼", "label": "Agência / Serviços"},
    {"emoji": "📦", "label": "Outro"},
]

# ═══════════════════════════════════════════════════════
# TELA DE UPLOAD
# ═══════════════════════════════════════════════════════
if st.session_state.df is None:

    st.markdown('<div class="db-glow"></div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        # Logo
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:36px;">
            <div class="db-logo-icon">✦</div>
            <div>
                <div class="db-logo">Data<span>Brief</span></div>
                <div class="db-subtitle">AI Data Analyst</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Headline
        st.markdown("""
        <div style="text-align:center;">
            <div class="db-upload-title">Seus dados.<br><span>Inteligência instantânea.</span></div>
            <div class="db-upload-sub">
                Faça upload da sua planilha e receba análise,
                KPIs e insights em segundos — com IA.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Seleção de tipo de negócio ──
        st.markdown("""
        <div style="margin:24px 0 10px 0;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#6B7280;
                        letter-spacing:.12em;text-transform:uppercase;text-align:center;margin-bottom:12px;">
                Qual é o seu negócio?
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Botões de tipo — 3 colunas x 2 linhas
        row1 = TIPOS_NEGOCIO[:3]
        row2 = TIPOS_NEGOCIO[3:]
        for row in [row1, row2]:
            cols = st.columns(3)
            for col, tipo in zip(cols, row):
                with col:
                    selecionado = st.session_state.tipo_negocio == tipo["label"]
                    border = "#00E5C0" if selecionado else "#1E2230"
                    bg     = "#00E5C015" if selecionado else "#111318"
                    color  = "#00E5C0"  if selecionado else "#6B7280"
                    st.markdown(f"""
                    <div style="background:{bg};border:1px solid {border};border-radius:12px;
                                padding:12px 8px;text-align:center;cursor:pointer;
                                transition:all .2s;margin-bottom:8px;">
                        <div style="font-size:22px;margin-bottom:4px;">{tipo['emoji']}</div>
                        <div style="font-size:12px;font-family:'Syne',sans-serif;font-weight:700;color:{color};">
                            {tipo['label']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(tipo["label"], key=f"tipo_{tipo['label']}", use_container_width=True):
                        st.session_state.tipo_negocio = tipo["label"]
                        st.rerun()

        # Mostrar selecionado
        if st.session_state.tipo_negocio:
            tipo_sel = next(t for t in TIPOS_NEGOCIO if t["label"] == st.session_state.tipo_negocio)
            st.markdown(f"""
            <div style="text-align:center;margin:8px 0 20px 0;">
                <span class="db-tag">{tipo_sel['emoji']} {tipo_sel['label']} selecionado</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Uploader ──
        uploaded = st.file_uploader(
            "⬆  Arraste seu CSV ou Excel aqui, ou clique para selecionar",
            type=["csv", "xlsx", "xls"],
            label_visibility="visible",
        )

    if uploaded:
        try:
            ext = uploaded.name.split(".")[-1].lower()
            if ext in ("xlsx", "xls"):
                df = read_excel_clean(uploaded)
            else:
                df = pd.read_csv(uploaded, sep=None, engine="python")
            st.session_state.df        = df
            st.session_state.file_name = uploaded.name
            st.session_state.analysis  = None
            st.session_state.messages  = []
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

# ═══════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════
else:
    df = st.session_state.df

    # ── Header ────────────────────────────────────────────────────────────────
    c_logo, c_tags, c_btn = st.columns([2, 4, 1])
    with c_logo:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding-top:4px;">
            <div class="db-logo-icon">✦</div>
            <div>
                <div class="db-logo">Data<span>Brief</span></div>
                <div class="db-subtitle">AI Data Analyst</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c_tags:
        st.markdown(f"""
        <div style="padding-top:10px;">
            <span class="db-tag">📄 {st.session_state.file_name}</span>
            <span class="db-tag">✦ {len(df)} linhas</span>
            <span class="db-tag">{len(df.columns)} colunas</span>
        </div>
        """, unsafe_allow_html=True)
    with c_btn:
        if st.button("Novo arquivo"):
            for k in ("df","file_name","analysis","messages"):
                st.session_state[k] = None if k in ("df","analysis") else ([] if k=="messages" else "")
            st.session_state.tipo_negocio = ""
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Análise ────────────────────────────────────────────────────────────────
    if st.session_state.analysis is None:
        with st.spinner("✦  Analisando seus dados com IA…"):
            try:
                st.session_state.analysis = analyze_data(df, st.session_state.tipo_negocio)
            except Exception as e:
                st.session_state.analysis = {"kpis":[],"insights":[f"Erro: {e}"]}

    analysis = st.session_state.analysis

    # ── KPIs ──────────────────────────────────────────────────────────────────
    st.markdown('<p class="db-section-title">Visão Geral</p>', unsafe_allow_html=True)
    kpis = analysis.get("kpis", [])
    if kpis:
        cols = st.columns(len(kpis))
        for i, kpi in enumerate(kpis):
            with cols[i]:
                st.markdown(f"""
                <div class="db-kpi" style="animation-delay:{i*80}ms">
                    <div class="db-kpi-label">{kpi.get('label','')}</div>
                    <div class="db-kpi-value">{kpi.get('value','')}</div>
                    <div class="db-kpi-sub">{kpi.get('sub','')}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        for col in st.columns(3):
            with col:
                st.markdown('<div class="db-shimmer"></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Análise Estruturada ───────────────────────────────────────────────────
    st.markdown('<p class="db-section-title">Análise</p>', unsafe_allow_html=True)

    melhorou   = analysis.get("melhorou", [])
    piorou     = analysis.get("piorou", [])
    alertas    = analysis.get("alertas", [])
    recomendacao = analysis.get("recomendacao", "")

    col_a, col_b = st.columns(2)

    with col_a:
        if melhorou:
            items = "".join(f'<div class="db-insight-line" style="border-color:#00E5C0">✅ {i}</div>' for i in melhorou)
            st.markdown(f"""
            <div class="db-insight-card" style="margin-bottom:14px;">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#00E5C0;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px;">O que melhorou</div>
                {items}
            </div>""", unsafe_allow_html=True)

        if alertas:
            items = "".join(f'<div class="db-insight-line" style="border-color:#FFB547">⚠️ {i}</div>' for i in alertas)
            st.markdown(f"""
            <div class="db-insight-card">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#FFB547;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px;">Alertas</div>
                {items}
            </div>""", unsafe_allow_html=True)

    with col_b:
        if piorou:
            items = "".join(f'<div class="db-insight-line" style="border-color:#FF4D6D">📉 {i}</div>' for i in piorou)
            st.markdown(f"""
            <div class="db-insight-card" style="margin-bottom:14px;">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#FF4D6D;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px;">O que piorou</div>
                {items}
            </div>""", unsafe_allow_html=True)

        if recomendacao:
            st.markdown(f"""
            <div class="db-insight-card" style="border-color:#00E5C040;background:linear-gradient(135deg,#00E5C008,#111318);">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#00E5C0;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px;">★ Ação imediata</div>
                <div style="font-size:14px;color:#E8EAF0;line-height:1.65;font-weight:500;">{recomendacao}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chat ──────────────────────────────────────────────────────────────────
    st.markdown('<p class="db-section-title">Converse com seus dados</p>', unsafe_allow_html=True)

    summary     = build_summary(df)
    tipo_ctx = f"Tipo de negócio: {st.session_state.tipo_negocio}. " if st.session_state.tipo_negocio else ""
    # Versão compacta do sumário para o chat — evita payload gigante a cada mensagem
    import json as _json
    _s = _json.loads(summary)
    summary_chat = _json.dumps({
        "total_registros": _s.get("total_registros_exato"),
        "agregados":       _s.get("agregados_numericos", {}),
        "frequencias":     {k: dict(list(v.items())[:5]) for k, v in _s.get("frequencias_categoricas", {}).items()},
    }, ensure_ascii=False)

    system_chat = f"""Você é o DataBrief, analista de dados especialista em pequenos negócios.
{tipo_ctx}Resumo dos dados da planilha:
{summary_chat}
Responda em português, de forma clara, objetiva e útil para tomada de decisão. Seja direto e conciso."""

    # Histórico do chat
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center;color:#6B7280;font-size:13px;padding:28px 0 8px 0;">
            💬  Faça qualquer pergunta sobre seus dados em linguagem natural.
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"]=="user" else "✦"):
            st.markdown(msg["content"])

    # Input
    user_input = st.chat_input(
        "Ex: Qual produto vendeu mais? Quem performa melhor? Qual mês teve mais receita?"
    )

    if user_input:
        st.session_state.messages.append({"role":"user","content":user_input})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("DataBrief está analisando…"):
                history = "\n".join(
                    f"{'Usuário' if m['role']=='user' else 'DataBrief'}: {m['content']}"
                    for m in st.session_state.messages
                )
                try:
                    answer = call_claude(
                        system_chat,
                        f"Histórico:\n{history}\n\nResponda à última pergunta de forma clara e objetiva."
                    )
                except Exception as e:
                    answer = f"Erro ao conectar com a IA: {e}"
            st.markdown(answer)
        st.session_state.messages.append({"role":"assistant","content":answer})
