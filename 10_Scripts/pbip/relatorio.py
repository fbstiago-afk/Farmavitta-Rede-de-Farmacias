# -*- coding: utf-8 -*-
"""Gera o relatório PBIR da FarmaVitta (FarmaVitta.Report): tema, fundos, páginas e visuais."""
import os, json, uuid
from PIL import Image, ImageDraw, ImageFilter, ImageFont

NS = uuid.UUID("0c2d7a10-58b4-4f7e-8f2e-6a1b9c3d2e4f")
def hid(*k): return uuid.uuid5(NS, "|".join(k)).hex[:20]

SCH = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
V_REP, V_PAGE, V_VIS, V_PAGES, V_VER = "3.0.0", "2.0.0", "2.2.0", "1.0.0", "1.0.0"
W, H = 1920, 1080
C = dict(petroleo="#103D45", petroleo2="#125F61", turquesa="#18B89F", menta="#DDF5EB", gelo="#F7FAF9", coral="#EF9277",
         grafite="#26383B", cinza="#71858A", branco="#FFFFFF", borda="#E2ECE9", pos="#0E8F7B", neg="#A34F39", alerta_bg="#FFF2EC")
FONT = "Segoe UI"; FONTB = "Segoe UI Semibold"

# ------------------------------------------------------------------ helpers de expressão
def L(v):
    if isinstance(v, bool): s = "true" if v else "false"
    elif isinstance(v, int): s = f"{v}L"
    elif isinstance(v, float): s = f"{v}D"
    else: s = "'" + str(v).replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": s}}}
def N(v): return {"expr": {"Literal": {"Value": f"{v}D"}}}
def COL(hexc): return {"solid": {"color": L(hexc)}}
def MEAS(name, ent="_Medidas"): return {"Measure": {"Expression": {"SourceRef": {"Entity": ent}}, "Property": name}}
def CLM(ent, prop): return {"Column": {"Expression": {"SourceRef": {"Entity": ent}}, "Property": prop}}
def MCOL(name): return {"solid": {"color": {"expr": MEAS(name)}}}
def P(**kw): return {"properties": kw}
def PS(sel, **kw): return {"properties": kw, "selector": sel}

def proj(f, display=None):
    if "Measure" in f:
        e, p = f["Measure"]["Expression"]["SourceRef"]["Entity"], f["Measure"]["Property"]
    else:
        e, p = f["Column"]["Expression"]["SourceRef"]["Entity"], f["Column"]["Property"]
    d = {"field": f, "queryRef": f"{e}.{p}", "nativeQueryRef": p}
    if display: d["displayName"] = display
    return d
def qref(f): return proj(f)["queryRef"]
def M(n): return MEAS(n)

# ------------------------------------------------------------------ estrutura
class Page:
    def __init__(self, key, display, bg=None, w=W, h=H, tooltip=False, hidden=False):
        self.key, self.name, self.display, self.bg, self.w, self.h = key, hid("page", key), display, bg, w, h
        self.tooltip, self.hidden, self.visuals, self.z = tooltip, hidden, [], 1000
    def add(self, key, vtype, x, y, w, h, query=None, objects=None, vco=None, sort=None, filters=None, sync=None, z=None, tooltip_page=None, title=None, subtitle=None):
        self.z += 10
        vco = dict(vco or {})
        if title is not None:
            vco["title"] = [P(show=L(True), text=L(title))]
        elif vtype not in ("textbox", "actionButton", "slicer"):
            vco.setdefault("title", [P(show=L(False))])
        if subtitle:
            vco["subTitle"] = [P(show=L(True), text=L(subtitle), fontColor=COL(C["cinza"]), fontSize=N(10))]
        if tooltip_page:
            vco["visualTooltip"] = [P(show=L(True), type=L("ReportPage"), section=L(tooltip_page.name))]
        v = {"visualType": vtype}
        if query:
            qs = {}
            for role, fields in query.items():
                qs[role] = {"projections": [f if (isinstance(f, dict) and "queryRef" in f) else (proj(*f) if isinstance(f, tuple) else proj(f)) for f in fields]}
            v["query"] = {"queryState": qs}
            if sort:
                v["query"]["sortDefinition"] = {"sort": [{"field": f, "direction": d} for f, d in sort], "isDefaultSort": False}
        if objects: v["objects"] = objects
        if vco: v["visualContainerObjects"] = vco
        if sync: v["syncGroup"] = {"groupName": sync, "fieldChanges": True, "filterChanges": True}
        vc = {"$schema": f"{SCH}/visualContainer/{V_VIS}/schema.json", "name": hid("vis", self.key, key),
              "position": {"x": x, "y": y, "z": z if z is not None else self.z, "height": h, "width": w, "tabOrder": self.z}, "visual": v}
        if filters: vc["filterConfig"] = {"filters": filters}
        self.visuals.append(vc)
        return vc

# ------------------------------------------------------------------ componentes
TRANSP = {"background": [P(show=L(False))], "border": [P(show=L(False))], "dropShadow": [P(show=L(False))]}

def textbox(pg, key, x, y, w, h, runs, align="left", z=None):
    """runs: lista de parágrafos; cada parágrafo = lista de (texto, tamanho_pt, cor, negrito)."""
    paras = []
    for para in runs:
        tr = [{"value": t, "textStyle": {"fontFamily": FONTB if b else FONT, "fontSize": f"{s}pt", "color": c}} for t, s, c, b in para]
        paras.append({"textRuns": tr, "horizontalTextAlignment": align})
    pg.add(key, "textbox", x, y, w, h, objects={"general": [P(paragraphs=paras)]}, vco=dict(TRANSP), z=z)

def nav_button(pg, key, x, y, w, h, label, target, active=False, z=None, show_text=True, align="center", size=11):
    D_ = {"id": "default"}; HV = {"id": "hover"}
    obj = {"icon": [P(show=L(False))],
           "outline": [P(show=L(False))],
           "fill": [P(show=L(True)), PS(D_, fillColor=COL(C["petroleo2"]), transparency=N(100)),
                    PS(HV, fillColor=COL(C["petroleo2"]), transparency=N(0 if show_text else 70))],
           "text": [P(show=L(show_text))]}
    if show_text:
        for sel in (D_, HV):
            obj["text"].append(PS(sel, text=L(label), fontColor=COL(C["turquesa"] if active else C["branco"]),
                                  fontSize=N(size), fontFamily=L(FONTB), horizontalAlignment=L(align), verticalAlignment=L("middle")))
    obj["shape"] = [P(roundEdge=N(10))]
    vco = dict(TRANSP)
    vco["visualLink"] = [P(show=L(True), type=L("PageNavigation"), navigationSection=L(target.name), tooltip=L(f"Ir para {target.display}"))]
    pg.add(key, "actionButton", x, y, w, h, objects=obj, vco=vco, z=z)

def reset_button(pg, x, y, w, h):
    D_ = {"id": "default"}; HV = {"id": "hover"}
    obj = {"icon": [PS(D_, shapeType=L("clearAllSlicers")), P(show=L(False))],
           "outline": [P(show=L(True)), PS(D_, lineColor=COL(C["borda"]), weight=N(1))],
           "fill": [P(show=L(True)), PS(D_, fillColor=COL(C["branco"]), transparency=N(0)), PS(HV, fillColor=COL(C["menta"]), transparency=N(0))],
           "shape": [P(roundEdge=N(8))],
           "text": [P(show=L(True)), PS(D_, text=L("↺  Limpar filtros"), fontColor=COL(C["petroleo"]), fontSize=N(10), fontFamily=L(FONTB),
                                        horizontalAlignment=L("center"), verticalAlignment=L("middle"))]}
    vco = dict(TRANSP)
    vco["visualLink"] = [P(show=L(True), type=L("ClearAllSlicers"), tooltip=L("Limpar todas as segmentações desta página"))]
    pg.add("reset", "actionButton", x, y, w, h, objects=obj, vco=vco, z=48000)

def kpi(pg, key, x, y, w, h, title, measure, var_measure=None, color_measure=None, var_color=None, tooltip_page=None, precision=None):
    lab = dict(color=COL(C["petroleo"]), fontSize=N(24), fontFamily=L(FONTB), labelDisplayUnits=N(0))
    if precision is not None: lab["labelPrecision"] = L(precision)
    pg.add(key, "card", x, y, w, h, query={"Values": [M(measure)]},
           objects={"labels": [P(**lab)], "categoryLabels": [P(show=L(False))]},
           title=title, tooltip_page=tooltip_page)
    if var_measure:
        fc = MCOL(color_measure) if color_measure else COL(var_color or C["cinza"])
        pg.add(key + "_var", "card", x + 8, y + h - 34, w - 16, 28, query={"Values": [M(var_measure)]},
               objects={"labels": [P(color=fc, fontSize=N(10), fontFamily=L(FONT))], "categoryLabels": [P(show=L(False))]},
               vco=dict(TRANSP, title=[P(show=L(False))], padding=[P(top=N(0), bottom=N(0), left=N(0), right=N(0))]))

def narrative(pg, key, x, y, w, h, measure, title="Leitura automática"):
    pg.add(key, "card", x, y, w, h, query={"Values": [M(measure)]},
           objects={"labels": [P(color=COL(C["grafite"]), fontSize=N(13), fontFamily=L(FONT))],
                    "categoryLabels": [P(show=L(False))], "wordWrap": [P(show=L(True))]},
           title=title, subtitle="Fato derivado dos filtros atuais · não indica causa")

def slicer(pg, key, x, y, w, h, ent, prop, label, single=False):
    sel = [P(selectAllCheckboxEnabled=L(True))] if not single else [P(singleSelect=L(True))]
    pg.add(key, "slicer", x, y, w, h, query={"Values": [(CLM(ent, prop), label)]},
           objects={"data": [P(mode=L("Dropdown"))], "selection": sel,
                    "header": [P(show=L(True), fontColor=COL(C["cinza"]), textSize=N(9), fontFamily=L(FONT))],
                    "items": [P(fontColor=COL(C["petroleo"]), textSize=N(10), fontFamily=L(FONT))]},
           sync=f"{ent}.{prop}")

def bar(pg, key, x, y, w, h, cat, measures, title, sort_measure=None, colors=None, tooltip_page=None, horizontal=True, labels_fmt=None, subtitle=None, legend=False, asc=False):
    vt = "clusteredBarChart" if horizontal else "clusteredColumnChart"
    obj = {"labels": [P(show=L(True), color=COL(C["grafite"]), fontSize=N(10))],
           "valueAxis": [P(show=L(False), gridlineShow=L(False))],
           "categoryAxis": [P(show=L(True), fontSize=N(10), labelColor=COL(C["grafite"]))],
           "legend": [P(show=L(legend), position=L("Top"))]}
    dp = []
    for i, ms in enumerate(measures):
        col_ = (colors or [C["turquesa"], C["cinza"], C["petroleo"]])[i % 3]
        dp.append(PS({"metadata": qref(M(ms))}, fill=COL(col_)))
    obj["dataPoint"] = dp
    srt = [(M(sort_measure or measures[0]), "Ascending" if asc else "Descending")] if sort_measure != "cat" else [(cat, "Ascending")]
    pg.add(key, vt, x, y, w, h, query={"Category": [cat], "Y": [M(ms) for ms in measures]}, objects=obj,
           sort=srt, title=title, subtitle=subtitle, tooltip_page=tooltip_page)

def line(pg, key, x, y, w, h, cat, measures, title, styles=None, colors=None, series=None, subtitle=None, tooltip_page=None):
    obj = {"lineStyles": [P(strokeWidth=N(3), showMarker=L(True), markerSize=N(4))],
           "legend": [P(show=L(True), position=L("Top"), fontSize=N(10))],
           "valueAxis": [P(show=L(True), fontSize=N(9), labelColor=COL(C["cinza"]), gridlineColor=COL(C["borda"]), gridlineStyle=L("dotted"))],
           "categoryAxis": [P(show=L(True), fontSize=N(9), labelColor=COL(C["cinza"]))],
           "labels": [P(show=L(False))]}
    if colors:
        obj["dataPoint"] = [PS({"metadata": qref(M(ms))}, fill=COL(cl)) for ms, cl in zip(measures, colors) if cl]
    if styles:
        obj["lineStyles"] += [PS({"metadata": qref(M(ms))}, lineStyle=L(st), strokeWidth=N(2), showMarker=L(False)) for ms, st in styles.items()]
    q = {"Category": [cat], "Y": [M(ms) for ms in measures]}
    if series: q["Series"] = [series]
    pg.add(key, "lineChart", x, y, w, h, query=q, objects=obj, sort=[(cat, "Ascending")], title=title, subtitle=subtitle, tooltip_page=tooltip_page)

def combo(pg, key, x, y, w, h, cat, cols, lines, title, colors=None, line_styles=None, subtitle=None, labels=False, sec=False):
    obj = {"legend": [P(show=L(True), position=L("Top"), fontSize=N(10))],
           "valueAxis": [P(show=L(True), fontSize=N(9), labelColor=COL(C["cinza"]), gridlineColor=COL(C["borda"]), gridlineStyle=L("dotted"), secShow=L(sec))],
           "categoryAxis": [P(show=L(True), fontSize=N(9), labelColor=COL(C["cinza"]))],
           "labels": [P(show=L(labels), fontSize=N(9), color=COL(C["grafite"]))],
           "lineStyles": [P(strokeWidth=N(3), showMarker=L(True), markerSize=N(4))]}
    allm = cols + lines
    cl = colors or [C["turquesa"], C["cinza"], C["coral"], C["petroleo"]]
    obj["dataPoint"] = [PS({"metadata": qref(M(ms))}, fill=COL(cl[i % len(cl)])) for i, ms in enumerate(allm)]
    if line_styles:
        obj["lineStyles"] += [PS({"metadata": qref(M(ms))}, lineStyle=L(st)) for ms, st in line_styles.items()]
    pg.add(key, "lineClusteredColumnComboChart", x, y, w, h, query={"Category": [cat], "Y": [M(c) for c in cols], "Y2": [M(c) for c in lines]},
           objects=obj, sort=[(cat, "Ascending")], title=title, subtitle=subtitle)

def table(pg, key, x, y, w, h, fields, title, sort=None, subtitle=None, gradient=None):
    obj = {"columnHeaders": [P(fontColor=COL(C["branco"]), backColor=COL(C["petroleo"]), fontFamily=L(FONTB), fontSize=N(10), wordWrap=L(True))],
           "values": [P(fontColor=COL(C["grafite"]), backColorSecondary=COL("#F4FAF8"), fontSize=N(10), fontFamily=L(FONT))],
           "total": [P(fontColor=COL(C["petroleo"]), backColor=COL(C["menta"]), fontFamily=L(FONTB))],
           "grid": [P(gridHorizontal=L(True), gridHorizontalColor=COL(C["borda"]), gridVertical=L(False), rowPadding=N(4))]}
    if gradient:
        obj["values"].append(gradient_rule(gradient))
    pg.add(key, "tableEx", x, y, w, h, query={"Values": fields}, objects=obj, sort=sort, title=title, subtitle=subtitle)

def gradient_rule(measure, lo="#FFFFFF", hi=C["turquesa"]):
    return PS({"data": [{"dataViewWildcard": {"matchingOption": 1}}], "metadata": qref(M(measure))},
              backColor={"solid": {"color": {"expr": {"FillRule": {"Input": M(measure), "FillRule": {"linearGradient2": {
                  "min": {"color": {"Literal": {"Value": f"'{lo}'"}}}, "max": {"color": {"Literal": {"Value": f"'{hi}'"}}},
                  "nullColoringStrategy": {"strategy": {"Literal": {"Value": "'asZero'"}}}}}}}}}})

def matrix(pg, key, x, y, w, h, rows, cols, values, title, subtitle=None, gradient=None, no_row_total=False):
    obj = {"columnHeaders": [P(fontColor=COL(C["branco"]), backColor=COL(C["petroleo"]), fontFamily=L(FONTB), fontSize=N(10))],
           "rowHeaders": [P(fontColor=COL(C["petroleo"]), fontFamily=L(FONTB), fontSize=N(10))],
           "values": [P(fontColor=COL(C["grafite"]), fontSize=N(10), fontFamily=L(FONT))],
           "subTotals": [P(fontColor=COL(C["petroleo"]), backColor=COL(C["menta"]), fontFamily=L(FONTB))],
           "grid": [P(gridHorizontal=L(True), gridHorizontalColor=COL(C["borda"]), gridVertical=L(False), rowPadding=N(4))]}
    if gradient: obj["values"].append(gradient_rule(gradient))
    if no_row_total: obj["subTotals"].append(P(rowSubtotals=L(False)))
    q = {"Rows": rows, "Values": [M(v) if isinstance(v, str) else v for v in values]}
    if cols: q["Columns"] = cols
    pg.add(key, "pivotTable", x, y, w, h, query=q, objects=obj, title=title, subtitle=subtitle)

def cat_filter(name, ent, prop, values):
    return {"name": name, "field": CLM(ent, prop), "type": "Categorical",
            "filter": {"Version": 2, "From": [{"Name": "d", "Entity": ent, "Type": 0}],
                       "Where": [{"Condition": {"In": {"Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": prop}}],
                                                       "Values": [[{"Literal": {"Value": f"{v}L"}}] for v in values]}}}]}}

# ------------------------------------------------------------------ páginas
PAGES_DEF = [("home", "Home"), ("exec", "Visão Executiva"), ("com", "Comercial & Clientes"), ("prod", "Produtos & Rentabilidade"),
             ("compras", "Compras & Fornecedores"), ("estoque", "Estoque & Validade"), ("fin", "Financeiro & Resultado"), ("fc", "Forecast & Planejamento")]
NAV_LABEL = {"home": "Home", "exec": "Executiva", "com": "Comercial & Clientes", "prod": "Produtos", "compras": "Compras",
             "estoque": "Estoque & Validade", "fin": "Financeiro", "fc": "Forecast"}
NAV_X0, NAV_W, NAV_GAP = 240, 166, 4
def nav_x(i): return NAV_X0 + i * (NAV_W + NAV_GAP)

def build_pages():
    pages = {k: Page(k, d, bg=f"bg_{k}.png") for k, d in PAGES_DEF}
    tt = Page("tt_loja", "TT Loja", w=380, h=250, tooltip=True, hidden=True)
    D, Lj, Pr, Fo, Cl, Ca = "dCalendario", "dLoja", "dProduto", "dFornecedor", "dCliente", "dCanal"
    mes = CLM(D, "Mes Ano")

    def header(pg):
        for i, (k, _) in enumerate(PAGES_DEF):
            nav_button(pg, f"nav_{k}", nav_x(i), 16, NAV_W, 56, NAV_LABEL[k], pages[k], active=(k == pg.key), z=50000 + i)
        textbox(pg, "hdr_base", 1612, 18, 290, 56, [[("Base sintética · dados fictícios", 9, C["menta"], False)],
                                                    [("01/10/2024 a 30/09/2026", 11, C["branco"], True)]], align="right", z=49000)

    def filtros(pg, extra):
        x = 32
        for i, (ent, prop, lab) in enumerate([(D, "Ano", "Ano"), (D, "Mes Nome", "Mês"), (Lj, "Loja", "Loja")] + extra):
            slicer(pg, f"sl_{i}", x, 102, 228, 60, ent, prop, lab); x += 244
        reset_button(pg, 1724, 110, 164, 44)
        pg.add("periodo", "card", 1360, 104, 352, 56, query={"Values": [M("Txt Período")]},
               objects={"labels": [P(color=COL(C["cinza"]), fontSize=N(10), fontFamily=L(FONT))], "categoryLabels": [P(show=L(False))]},
               vco=dict(TRANSP, title=[P(show=L(False))]))

    def kpis(pg, spec):
        wk = (1856 - 5 * 16) / 6
        for i, s in enumerate(spec):
            kpi(pg, f"kpi{i}", 32 + i * (wk + 16), 176, wk, 116, *s)

    # ---------------- Tooltip loja/categoria
    tt.add("tt_rec", "card", 8, 8, 176, 80, query={"Values": [M("Receita Líquida")]}, title="Receita líquida",
           objects={"labels": [P(fontSize=N(18), labelDisplayUnits=N(0))], "categoryLabels": [P(show=L(False))]})
    tt.add("tt_mg", "card", 196, 8, 176, 80, query={"Values": [M("Margem Bruta %")]}, title="Margem bruta",
           objects={"labels": [P(fontSize=N(18))], "categoryLabels": [P(show=L(False))]})
    tt.add("tt_yoy", "card", 8, 96, 176, 70, query={"Values": [M("Txt Receita")]}, title="Variação",
           objects={"labels": [P(fontSize=N(10), color=MCOL("Cor Receita"))], "categoryLabels": [P(show=L(False))]})
    tt.add("tt_sh", "card", 196, 96, 176, 70, query={"Values": [M("Share Receita %")]}, title="Participação na seleção",
           objects={"labels": [P(fontSize=N(16))], "categoryLabels": [P(show=L(False))]})
    textbox(tt, "tt_def", 8, 176, 364, 66, [[("Receita líquida = bruto − descontos (f_vendas). Margem = (receita − CMV) / receita. Variação só aparece quando o mesmo período do ano anterior está coberto pela base.", 8, C["cinza"], False)]])

    # ---------------- 00 HOME
    pg = pages["home"]; header(pg)
    textbox(pg, "h_t1", 88, 168, 900, 40, [[("Bem-vindo à", 20, C["menta"], False)]])
    textbox(pg, "h_t2", 88, 206, 1000, 80, [[("FarmaVitta ", 44, C["branco"], True), ("Intelligence", 44, C["turquesa"], True)]])
    textbox(pg, "h_t3", 88, 300, 760, 120, [[("Cuidar bem é viver melhor.", 18, C["branco"], True)],
                                            [("Receita, clientes, mix, compras, estoque, resultado e previsão das 4 farmácias da rede em um só lugar.", 13, C["menta"], False)]])
    textbox(pg, "h_t4", 88, 588, 1000, 40, [[("Dados 100% sintéticos para portfólio. Resultado operacional simplificado não é EBITDA. Previsões são faixas, não metas.", 10, C["menta"], False)]])
    wk = (1180 - 4 * 16) / 5
    for i, (t, ms) in enumerate([("Farmácias", "Qtd Lojas"), ("SKUs no catálogo", "SKUs no Catálogo"), ("Clientes cadastrados", "Clientes Cadastrados"),
                                 ("Vendas (cupons)", "Cupons"), ("Receita líquida", "Receita Líquida")]):
        kpi(pg, f"hk{i}", 32 + i * (wk + 16), 684, wk, 140, t, ms)
    table(pg, "h_lojas", 32, 840, 1180, 208,
          [proj(CLM(Lj, "Loja")), proj(CLM(Lj, "Cidade")), proj(M("Receita Líquida")), proj(M("Margem Bruta %")), proj(M("Atingimento Meta %")),
           proj(M("Resultado Operacional Simplificado")), proj(M("Ticket Médio"))],
          "Resumo da rede · período completo", sort=[(M("Receita Líquida"), "Descending")])
    textbox(pg, "h_nav_t", 1268, 132, 600, 40, [[("Navegue pelas análises", 18, C["branco"], True)]])
    textbox(pg, "h_nav_s", 1268, 170, 600, 24, [[("Cada página responde a uma pergunta de negócio.", 10, C["menta"], False)]])
    tiles = [("exec", "Visão Executiva", "Quem cresce com margem e onde está o gap de meta"),
             ("com", "Comercial & Clientes", "Canais, ticket, identificação, recompra e RFV"),
             ("prod", "Produtos & Rentabilidade", "Mix, margem, descontos e curva ABC"),
             ("compras", "Compras & Fornecedores", "Recebimentos, lead time, pontualidade, orçamento"),
             ("estoque", "Estoque & Validade", "Saldo, cobertura, giro, excesso e lotes"),
             ("fin", "Financeiro & Resultado", "DRE gerencial e resultado operacional simplificado"),
             ("fc", "Forecast & Planejamento", "Previsão 6 meses com backtest e cenários")]
    for i, (k, t, d) in enumerate(tiles):
        y = 208 + i * 118
        textbox(pg, f"tile_t{i}", 1360, y + 18, 500, 70, [[(t, 15, C["branco"], True)], [(d, 10, C["menta"], False)]], z=60000 + i)
        nav_button(pg, f"tile_b{i}", 1268, y, 600, 104, t, pages[k], show_text=False, z=61000 + i)

    # ---------------- 01 EXECUTIVA
    pg = pages["exec"]; header(pg); filtros(pg, [(Ca, "Canal", "Canal")])
    kpis(pg, [("Receita líquida", "Receita Líquida", "Txt Receita", "Cor Receita"),
              ("Lucro bruto", "Lucro Bruto", "Txt Lucro", "Cor Lucro"),
              ("Margem bruta", "Margem Bruta %", "Txt Margem", "Cor Margem"),
              ("Resultado operacional simplificado", "Resultado Operacional Simplificado", "Txt Margem Op", None, C["cinza"]),
              ("Atingimento da meta", "Atingimento Meta %", "Txt Meta", "Cor Meta"),
              ("Ticket médio", "Ticket Médio", "Txt Ticket", "Cor Ticket")])
    combo(pg, "evol", 32, 308, 1140, 440, mes, ["Receita Líquida"], ["Receita Líquida LY", "Meta Receita"],
          "Receita líquida mensal vs ano anterior e meta", colors=[C["turquesa"], C["cinza"], C["coral"]],
          line_styles={"Meta Receita": "dashed"}, subtitle="Ano anterior só aparece onde o mesmo mês está coberto pela base (a partir de out/25)")
    bar(pg, "lojas", 1188, 308, 700, 212, CLM(Lj, "Loja Curta"), ["Receita Líquida"], "Receita líquida por loja", tooltip_page=tt)
    bar(pg, "ating", 1188, 536, 700, 212, CLM(Lj, "Loja Curta"), ["Atingimento Meta %"], "Atingimento da meta de receita por loja",
        colors=[C["petroleo"]], subtitle="Receita líquida / meta do período")
    narrative(pg, "narr", 32, 764, 560, 284, "Narrativa Executiva")
    table(pg, "oport", 608, 764, 1280, 284,
          [proj(CLM(Pr, "Categoria")), proj(M("Receita Líquida Itens")), proj(M("Share Receita Itens %")), proj(M("Margem Bruta Itens %")),
           proj(M("Margem Itens Var pp")), proj(M("Desconto Itens %")), proj(M("Receita Itens YoY %"))],
          "Onde agir: categorias por receita, margem e desconto", sort=[(M("Receita Líquida Itens"), "Descending")])

    # ---------------- 02 COMERCIAL & CLIENTES
    pg = pages["com"]; header(pg); filtros(pg, [(Ca, "Canal", "Canal"), (Cl, "Segmento RFV", "Segmento RFV")])
    kpis(pg, [("Cupons", "Cupons", "Txt Cupons", "Cor Cupons"),
              ("Clientes ativos (identificados)", "Clientes Ativos", "Txt Clientes", "Cor Clientes"),
              ("Clientes novos", "Clientes Novos", "Txt Novos", None, C["cinza"]),
              ("Frequência média (cupons/cliente)", "Frequência Média"),
              ("Ticket médio", "Ticket Médio", "Txt Ticket", "Cor Ticket"),
              ("Cupons identificados", "% Cupons Identificados")])
    line(pg, "evol", 32, 308, 1140, 440, mes, ["Cupons", "Clientes Ativos"], "Cupons e clientes ativos por mês",
         colors=[C["turquesa"], C["petroleo"]], subtitle="Cliente ativo = identificado com 1+ cupom no mês; cupom anônimo não é cliente")
    bar(pg, "canal", 1188, 308, 700, 212, CLM(Ca, "Canal"), ["Receita Líquida"], "Receita líquida por canal", tooltip_page=tt)
    bar(pg, "pag", 1188, 536, 700, 212, CLM("fVendas", "Forma Pagamento"), ["Cupons"], "Cupons por forma de pagamento", colors=[C["petroleo"]])
    narrative(pg, "narr", 32, 764, 560, 284, "Narrativa Clientes")
    bar(pg, "rfv", 608, 764, 620, 284, CLM(Cl, "Segmento RFV"), ["Clientes Ativos"], "Clientes ativos por segmento RFV",
        sort_measure="cat", subtitle="RFV = fotografia em 30/09/2026 (quintis de recência, frequência e valor)", horizontal=True)
    matrix(pg, "ticket", 1244, 764, 644, 284, [proj(CLM(Ca, "Canal"))], None,
           ["Ticket Médio Identificado", "Ticket Médio Anônimo", "% Cupons Identificados", "Itens por Cupom", "Taxa de Recompra %"],
           "Identificado vs anônimo por canal")

    # ---------------- 03 PRODUTOS
    pg = pages["prod"]; header(pg); filtros(pg, [(Pr, "Categoria", "Categoria"), (Pr, "Subcategoria", "Subcategoria")])
    kpis(pg, [("Receita líquida (itens)", "Receita Líquida Itens", "Txt Receita Itens", "Cor Receita Itens"),
              ("Lucro bruto (itens)", "Lucro Bruto Itens"),
              ("Margem bruta (itens)", "Margem Bruta Itens %", "Txt Margem Itens", "Cor Margem Itens"),
              ("Desconto sobre bruto", "Desconto Itens %"),
              ("SKUs com venda", "SKUs Vendidos", "Txt SKUs", None, C["cinza"]),
              ("Preço médio por unidade", "Preço Médio Unitário")])
    bar(pg, "mix", 32, 308, 560, 440, CLM(Pr, "Categoria"), ["Receita Líquida Itens"], "Mix de receita por categoria", tooltip_page=tt)
    pg.add("disp", "scatterChart", 608, 308, 564, 440,
           query={"Category": [CLM(Pr, "Subcategoria")], "Series": [CLM(Pr, "Categoria")], "X": [M("Unidades Vendidas")],
                  "Y": [M("Margem Bruta Itens %")], "Size": [M("Receita Líquida Itens")]},
           objects={"legend": [P(show=L(True), position=L("Top"), fontSize=N(9))],
                    "categoryAxis": [P(show=L(True), fontSize=N(9), labelColor=COL(C["cinza"]))],
                    "valueAxis": [P(show=L(True), fontSize=N(9), labelColor=COL(C["cinza"]), gridlineColor=COL(C["borda"]))],
                    "categoryLabels": [P(show=L(False))]},
           title="Volume × margem por subcategoria", subtitle="Tamanho = receita líquida")
    bar(pg, "abc", 1188, 308, 700, 440, CLM(Pr, "Classe ABC"), ["Share Receita Itens %", "% SKUs Vendidos"],
        "Curva ABC: % da receita vs % dos SKUs", sort_measure="cat", colors=[C["turquesa"], C["cinza"]], horizontal=False, legend=True,
          subtitle="Classe estática do período completo: A até 80% da receita, B até 95%, C restante")
    narrative(pg, "narr", 32, 764, 560, 284, "Narrativa Produtos")
    table(pg, "skus", 608, 764, 1280, 284,
          [proj(M("Ranking SKU"), "#"), proj(CLM(Pr, "Produto")), proj(CLM(Pr, "Categoria")), proj(CLM(Pr, "Classe ABC")), proj(M("Receita Líquida Itens")),
           proj(M("Margem Bruta Itens %")), proj(M("Desconto Itens %")), proj(M("Unidades Vendidas")), proj(M("Receita Itens YoY %"))],
          "Ranking de SKUs (líderes no topo · ordene por margem para ver detratores)", sort=[(M("Receita Líquida Itens"), "Descending")])

    # ---------------- 04 COMPRAS
    pg = pages["compras"]; header(pg); filtros(pg, [(Pr, "Categoria", "Categoria"), (Fo, "Fornecedor", "Fornecedor")])
    kpis(pg, [("Compras recebidas", "Valor Recebido", "Txt Orçamento", None, C["cinza"]),
              ("Recebimentos", "Recebimentos"),
              ("Lead time médio", "Lead Time Médio", "Txt Pontualidade", None, C["cinza"]),
              ("Pontualidade (OTD)", "Pontualidade %"),
              ("Atraso médio quando atrasa", "Atraso Médio"),
              ("Concentração top 5 fornecedores", "Concentração Top 5 %")])
    combo(pg, "evol", 32, 308, 1140, 440, mes, ["Valor Recebido"], ["Orçamento Compras", "CMV Itens"],
          "Compras recebidas vs orçamento e CMV", colors=[C["turquesa"], C["coral"], C["cinza"]], line_styles={"Orçamento Compras": "dashed"},
          subtitle="Recebimentos derivados das entradas de estoque · não representam pedidos emitidos")
    bar(pg, "cat", 1188, 308, 700, 212, CLM(Pr, "Categoria"), ["Valor Recebido"], "Compras recebidas por categoria")
    bar(pg, "pont", 1188, 536, 700, 212, CLM(Lj, "Loja Curta"), ["Pontualidade %"], "Pontualidade por loja", colors=[C["petroleo"]])
    narrative(pg, "narr", 32, 764, 560, 284, "Narrativa Compras")
    table(pg, "forn", 608, 764, 820, 284,
          [proj(CLM(Fo, "Fornecedor")), proj(CLM(Fo, "UF Fornecedor"), "UF"), proj(M("Valor Recebido")), proj(M("Share Compras %")),
           proj(M("Lead Time Médio")), proj(M("Prazo Previsto Médio")), proj(M("Pontualidade %")), proj(M("Atraso Médio"))],
          "Fornecedores", sort=[(M("Valor Recebido"), "Descending")])
    matrix(pg, "heat", 1444, 764, 444, 284, [proj(CLM(Lj, "Loja Curta"))], [proj(CLM(Pr, "Categoria"))], ["Pontualidade %"],
           "Pontualidade: loja × categoria", gradient="Pontualidade %")

    # ---------------- 05 ESTOQUE
    pg = pages["estoque"]; header(pg); filtros(pg, [(Pr, "Categoria", "Categoria"), ("fEstoque", "Status Estoque", "Status do estoque")])
    kpis(pg, [("Estoque final (custo)", "Estoque Final (R$)", "Txt Cobertura", None, C["neg"]),
              ("Estoque final (unidades)", "Estoque Final (un)"),
              ("Cobertura estimada", "Cobertura (dias)"),
              ("Giro anualizado", "Giro Anualizado"),
              ("Perdas (custo)", "Perdas (R$)", "Txt Perdas", None, C["cinza"]),
              ("Valor em risco de validade", "Valor em Risco Validade (R$)", "Txt Validade", None, C["cinza"])])
    combo(pg, "evol", 32, 308, 1140, 440, mes, ["Perdas (R$)"], ["Estoque Final (R$)"], "Estoque final (saldo do mês, eixo direito) e perdas (colunas)",
          colors=[C["coral"], C["petroleo"]], sec=True, subtitle="Saldo é semiaditivo: cada ponto é o fim do mês; meses sem movimento carregam o saldo anterior")
    bar(pg, "status", 1188, 308, 700, 212, CLM("fEstoque", "Status Estoque"), ["Estoque Final (R$)"], "Valor por status de estoque",
        colors=[C["coral"]], subtitle="Excesso > 120 dias · Baixo < 15 dias · Sem giro = 3+ meses sem venda")
    bar(pg, "cob", 1188, 536, 700, 212, CLM(Pr, "Categoria"), ["Cobertura (dias)"], "Cobertura estimada por categoria (dias)", colors=[C["petroleo"]])
    narrative(pg, "narr", 32, 764, 560, 284, "Narrativa Estoque")
    bar(pg, "val", 608, 764, 440, 284, CLM("fLotes", "Faixa Validade"), ["Valor em Lotes (R$)"], "Validade · foto 30/09/2026",
        sort_measure="cat", colors=[C["coral"]], subtitle="Lotes simulados; não responde a filtro de data")
    table(pg, "acao", 1064, 764, 824, 284,
          [proj(CLM(Pr, "Produto")), proj(CLM(Lj, "Loja Curta"), "Loja"), proj(CLM("fEstoque", "Status Estoque"), "Status"),
           proj(M("Estoque Final (un)")), proj(M("Estoque Final (R$)")), proj(M("Cobertura (dias)"))],
          "Tabela de ação: maiores saldos valorizados", sort=[(M("Estoque Final (R$)"), "Descending")])

    # ---------------- 06 FINANCEIRO
    pg = pages["fin"]; header(pg); filtros(pg, [])
    kpis(pg, [("Receita líquida", "Receita Líquida", "Txt Receita", "Cor Receita"),
              ("Lucro bruto", "Lucro Bruto", "Txt Lucro", "Cor Lucro"),
              ("Despesas modeladas", "Despesas"),
              ("Resultado operacional simplificado", "Resultado Operacional Simplificado", "Txt ROS", "Cor ROS"),
              ("Margem operacional simplificada", "Margem Operacional Simplificada %"),
              ("Atingimento meta de lucro bruto", "Atingimento Lucro Bruto %")])
    pg.add("ponte", "waterfallChart", 32, 308, 1140, 440, query={"Category": [CLM("dDRE", "Linha DRE")], "Y": [M("Valor Ponte Resultado")]},
           objects={"labels": [P(show=L(True), fontSize=N(10), color=COL(C["grafite"]))],
                    "sentimentColors": [P(increaseFill=COL(C["turquesa"]), decreaseFill=COL(C["coral"]), totalFill=COL(C["petroleo"]))],
                    "valueAxis": [P(show=L(False), gridlineShow=L(False))], "categoryAxis": [P(show=L(True), fontSize=N(10))],
                    "legend": [P(show=L(False))]},
           sort=[(CLM("dDRE", "Linha DRE"), "Ascending")],
           filters=[cat_filter(hid("flt", "ponte"), "dDRE", "Ordem DRE", [3, 4, 6, 7, 8, 9])],
           title="Da receita líquida ao resultado operacional simplificado", subtitle="Total = resultado operacional simplificado (não é EBITDA)")
    matrix(pg, "dre", 1188, 308, 700, 440, [proj(CLM("dDRE", "Linha DRE"))], [proj(CLM(Lj, "Loja Curta"))], ["Valor DRE"],
           "DRE gerencial simplificada por loja", no_row_total=True)
    narrative(pg, "narr", 32, 764, 560, 284, "Narrativa Financeiro")
    line(pg, "mgop", 608, 764, 760, 284, mes, ["Margem Operacional Simplificada %"], "Margem operacional simplificada por loja",
         series=CLM(Lj, "Loja Curta"))
    bar(pg, "desp", 1384, 764, 504, 284, CLM(Lj, "Loja Curta"), ["Despesas % Receita"], "Despesas sobre receita por loja", colors=[C["coral"]])

    # ---------------- 07 FORECAST
    pg = pages["fc"]; header(pg)
    slicer(pg, "sl_loja", 32, 102, 228, 60, Lj, "Loja", "Loja")
    slicer(pg, "sl_cen", 276, 102, 228, 60, "dCenario", "Cenario", "Cenário", single=True)
    textbox(pg, "fc_aviso", 520, 104, 1368, 56, [[("Projeção ≠ meta ≠ fato. ", 11, C["neg"], True),
        ("Métodos simples comparados por backtesting rolling-origin com 24 meses de histórico; intervalo empírico ~80%. Cenários aplicam fatores sobre a previsão base (premissas explícitas em dCenario).", 10, C["cinza"], False)]])
    kpis(pg, [("Receita prevista · 6 meses", "Receita Prevista Cenário", "Txt Forecast Intervalo", None, C["cinza"]),
              ("Lucro bruto previsto (premissa)", "Lucro Bruto Previsto Cenário"),
              ("Crescimento vs mesmos meses LY", "Crescimento Previsto vs LY %"),
              ("WAPE do backtest", "WAPE Backtest %"),
              ("Viés do backtest", "Viés Backtest %"),
              ("Cenário ativo", "Cenário Ativo")])
    line(pg, "fc", 32, 308, 1140, 440, mes, ["Receita Real (Série)", "Receita Prevista Cenário", "Limite Inferior Cenário", "Limite Superior Cenário"],
         "Receita real e prevista com intervalo", colors=[C["petroleo"], C["turquesa"], "#9FB3B7", "#9FB3B7"],
         styles={"Limite Inferior Cenário": "dotted", "Limite Superior Cenário": "dotted"})
    bar(pg, "wape", 1188, 308, 700, 440, CLM("fBacktest", "Metodo"), ["WAPE por Método %"], "Erro por método no backtest (WAPE)",
        asc=True, colors=[C["petroleo"]], subtitle="Menor é melhor · método escolhido por loja com menor WAPE")
    narrative(pg, "narr", 32, 764, 560, 284, "Narrativa Forecast")
    matrix(pg, "tab", 608, 764, 880, 284, [proj(mes)], [proj(CLM(Lj, "Loja Curta"))], ["Receita Prevista Cenário"], "Previsão mensal por loja")
    pg.add("met", "card", 1504, 764, 384, 284, query={"Values": [M("Métodos Selecionados")]}, title="Método selecionado por loja",
           objects={"labels": [P(fontSize=N(11), color=COL(C["grafite"]), fontFamily=L(FONT))], "categoryLabels": [P(show=L(False))],
                    "wordWrap": [P(show=L(True))]})

    return [pages[k] for k, _ in PAGES_DEF] + [tt]

# ------------------------------------------------------------------ fundos
def rounded(d, box, r, fill, outline=None):
    d.rounded_rectangle(box, r, fill=fill, outline=outline)

def draw_backgrounds(out_dir, logo_path):
    os.makedirs(out_dir, exist_ok=True)
    logo = Image.open(logo_path).convert("RGBA"); logo = logo.crop(logo.getbbox())
    lh = 44; logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
    fnt = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 22)
    files = []
    for i, (k, _) in enumerate(PAGES_DEF):
        im = Image.new("RGB", (W, H), C["gelo"]); d = ImageDraw.Draw(im, "RGBA")
        d.rectangle((0, 0, W, 88), fill=C["petroleo"])
        d.rectangle((0, 88, W, 91), fill=C["turquesa"])
        rounded(d, (20, 14, 20 + logo.width + 28, 74), 14, C["branco"])
        im.paste(logo, (34, 44 - lh // 2), logo)
        ax = nav_x(i)
        rounded(d, (ax, 16, ax + NAV_W, 72), 10, C["petroleo2"])
        d.rectangle((ax + 24, 76, ax + NAV_W - 24, 80), fill=C["turquesa"])
        if k == "home":
            # hero
            hero = Image.new("RGBA", (1180, 552)); hd = ImageDraw.Draw(hero)
            for yy in range(552):
                t = yy / 551
                c1, c2 = (16, 61, 69), (18, 95, 97)
                hd.line((0, yy, 1180, yy), fill=tuple(int(a + (b - a) * t) for a, b in zip(c1, c2)) + (255,))
            deco = Image.new("RGBA", (1180, 552), (0, 0, 0, 0)); dd = ImageDraw.Draw(deco)
            cx, cy, s = 960, 250, 120
            dd.rounded_rectangle((cx - s // 2, cy - int(s * 1.5), cx + s // 2, cy + int(s * 1.5)), 40, fill=(24, 184, 159, 60))
            dd.rounded_rectangle((cx - int(s * 1.5), cy - s // 2, cx + int(s * 1.5), cy + s // 2), 40, fill=(24, 184, 159, 60))
            dd.ellipse((cx + 40, cy - 260, cx + 300, cy - 40), fill=(221, 245, 235, 40))
            hero = Image.alpha_composite(hero, deco)
            mask = Image.new("L", hero.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, 1180, 552), 24, fill=255)
            im.paste(hero, (32, 112), mask)
            # painel de navegação
            rounded(d, (1236, 112, 1888, 1048), 24, C["petroleo"])
            for j in range(7):
                y = 208 + j * 118
                rounded(d, (1268, y, 1868, y + 104), 16, C["petroleo2"])
                d.ellipse((1288, y + 28, 1336, y + 76), fill=C["turquesa"])
                n = f"{j + 1:02d}"; tw = d.textlength(n, font=fnt)
                d.text((1312 - tw / 2, y + 38), n, fill=C["petroleo"], font=fnt)
                d.polygon([(1838, y + 44), (1850, y + 52), (1838, y + 60)], fill=C["menta"])
        f = f"bg_{k}.png"; im.save(os.path.join(out_dir, f), optimize=True); files.append(f)
    return files

# ------------------------------------------------------------------ tema
def theme():
    S = lambda c: {"solid": {"color": c}}
    return {
        "name": "FarmaVitta",
        "dataColors": [C["turquesa"], C["petroleo"], C["cinza"], C["coral"], C["petroleo2"], "#8FD9C8", "#B7C4C7", "#F4C2B3", "#5C7C82", "#2E8C7E"],
        "foreground": C["grafite"], "foregroundNeutralSecondary": C["cinza"], "background": C["branco"], "backgroundLight": C["gelo"],
        "backgroundNeutral": C["borda"], "tableAccent": C["turquesa"], "good": C["pos"], "neutral": C["coral"], "bad": C["neg"],
        "maximum": C["turquesa"], "center": C["menta"], "minimum": C["branco"], "hyperlink": C["petroleo2"],
        "textClasses": {"callout": {"fontSize": 24, "fontFace": FONTB, "color": C["petroleo"]},
                        "title": {"fontSize": 13, "fontFace": FONTB, "color": C["petroleo"]},
                        "header": {"fontSize": 12, "fontFace": FONTB, "color": C["petroleo"]},
                        "label": {"fontSize": 10, "fontFace": FONT, "color": C["grafite"]}},
        "visualStyles": {
            "*": {"*": {
                "background": [{"show": True, "color": S(C["branco"]), "transparency": 0}],
                "border": [{"show": True, "color": S(C["borda"]), "radius": 12, "width": 1}],
                "dropShadow": [{"show": True, "color": S(C["petroleo"]), "position": "Outer", "preset": "Custom", "shadowSpread": 0,
                                "shadowBlur": 10, "angle": 90, "shadowDistance": 2, "transparency": 90}],
                "title": [{"show": True, "fontColor": S(C["petroleo"]), "fontSize": 13, "fontFamily": FONTB, "alignment": "left"}],
                "padding": [{"top": 10, "bottom": 10, "left": 14, "right": 14}],
                "visualTooltip": [{"fontSize": 10, "fontFamily": FONT}]}},
            "page": {"*": {"background": [{"color": S(C["gelo"]), "transparency": 0}],
                           "outspace": [{"color": S("#E6EEEC"), "transparency": 0}]}},
            "textbox": {"*": {"background": [{"show": False}], "border": [{"show": False}], "dropShadow": [{"show": False}],
                              "padding": [{"top": 0, "bottom": 0, "left": 0, "right": 0}]}},
            "actionButton": {"*": {"background": [{"show": False}], "border": [{"show": False}], "dropShadow": [{"show": False}]}},
            "slicer": {"*": {"dropShadow": [{"show": False}], "border": [{"show": True, "color": S(C["borda"]), "radius": 8, "width": 1}],
                             "padding": [{"top": 4, "bottom": 4, "left": 10, "right": 10}]}},
            "card": {"*": {"labels": [{"color": S(C["petroleo"]), "fontSize": 24, "fontFamily": FONTB}], "categoryLabels": [{"show": False}]}},
            "clusteredBarChart": {"*": {"labels": [{"show": True}], "valueAxis": [{"show": False}]}},
            "clusteredColumnChart": {"*": {"labels": [{"show": True}], "valueAxis": [{"show": False}]}},
            "tableEx": {"*": {"columnHeaders": [{"fontColor": S(C["branco"]), "backColor": S(C["petroleo"]), "fontFamily": FONTB}],
                              "values": [{"backColorSecondary": S("#F4FAF8")}]}},
            "pivotTable": {"*": {"columnHeaders": [{"fontColor": S(C["branco"]), "backColor": S(C["petroleo"]), "fontFamily": FONTB}]}},
        }
    }

# ------------------------------------------------------------------ escrita
def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def write_report(base, model_folder_name, logo_path):
    defs = os.path.join(base, "definition")
    res = os.path.join(base, "StaticResources", "RegisteredResources")
    bgs = draw_backgrounds(res, logo_path)
    wj(os.path.join(res, "FarmaVitta_Tema.json"), theme())
    wj(os.path.join(base, "definition.pbir"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
                                              "version": "4.0", "datasetReference": {"byPath": {"path": f"../{model_folder_name}"}}})
    items = [{"name": "FarmaVitta_Tema.json", "path": "FarmaVitta_Tema.json", "type": "CustomTheme"}] + \
            [{"name": f, "path": f, "type": "Image"} for f in bgs]
    wj(os.path.join(defs, "report.json"), {
        "$schema": f"{SCH}/report/{V_REP}/schema.json",
        "themeCollection": {"customTheme": {"name": "FarmaVitta_Tema.json", "reportVersionAtImport": {"visual": "2.2.0", "report": "3.0.0", "page": "2.0.0"},
                                            "type": "RegisteredResources"}},
        "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources", "items": items}],
        "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized", "defaultDrillFilterOtherVisuals": True,
                     "allowChangeFilterTypes": True, "useEnhancedTooltips": True},
    })
    wj(os.path.join(defs, "version.json"), {"$schema": f"{SCH}/versionMetadata/{V_VER}/schema.json", "version": "2.0.0"})
    pages = build_pages()
    wj(os.path.join(defs, "pages", "pages.json"), {"$schema": f"{SCH}/pagesMetadata/{V_PAGES}/schema.json",
                                                   "pageOrder": [p.name for p in pages], "activePageName": pages[0].name})
    nvis = 0
    for p in pages:
        pj = {"$schema": f"{SCH}/page/{V_PAGE}/schema.json", "name": p.name, "displayName": p.display,
              "displayOption": "FitToPage", "height": p.h, "width": p.w}
        if p.bg:
            pj["objects"] = {"background": [P(image={"image": {"name": L(p.bg), "url": {"expr": {"ResourcePackageItem": {
                "PackageName": "RegisteredResources", "PackageType": 1, "ItemName": p.bg}}}, "scaling": L("Fit")}}, transparency=N(0))]}
        if p.tooltip:
            pj["type"] = "Tooltip"
            pj["pageBinding"] = {"name": hid("bind", p.key), "type": "Tooltip", "referenceScope": "Default"}
        if p.hidden: pj["visibility"] = "HiddenInViewMode"
        wj(os.path.join(defs, "pages", p.name, "page.json"), pj)
        for v in p.visuals:
            wj(os.path.join(defs, "pages", p.name, "visuals", v["name"], "visual.json"), v); nvis += 1
    pbi = os.path.join(base, ".pbi"); os.makedirs(pbi, exist_ok=True)
    return pages, nvis
