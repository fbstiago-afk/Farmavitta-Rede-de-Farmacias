# -*- coding: utf-8 -*-
"""FarmaVitta v2 — relatório PBIR moderno: tema escuro da marca, menu lateral em vidro, Home com Iniciar,
cards HTML Content + SVG, Deneb (Vega-Lite), painel de filtros oculto por bookmarks, chips, tooltip HTML."""
import os, json
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import relatorio as R
from relatorio import L, N, COL, M, CLM, MCOL, P, PS, proj, Page, hid, SCH
import deneb_specs as DS

W, H = 1920, 1080
HTML_VT = "htmlContent443BE3AD55E043BF878BED274D3A6855"
DENEB_VT = "deneb7E15AEF80B9E4D4F8E12924291ECE89A"
K = dict(fundo="#071E23", fundo2="#0B2A30", vidro="#0E3138", petroleo="#103D45", petroleo2="#125F61", turquesa="#18B89F",
         menta="#DDF5EB", texto="#E8F3F1", sub="#9FC9C1", coral="#EF9277", ambar="#F2C46D", branco="#FFFFFF")
FONT, FONTB = "Segoe UI", "Segoe UI Semibold"
NONE = {"background": [P(show=L(False))], "border": [P(show=L(False))], "dropShadow": [P(show=L(False))]}

PAGES = [("home", "Home", None), ("exec", "Visão Executiva", "Executiva"), ("com", "Comercial & Clientes", "Clientes"),
         ("prod", "Produtos & Rentabilidade", "Produtos"), ("compras", "Compras & Fornecedores", "Compras"),
         ("estoque", "Estoque & Validade", "Estoque"), ("fin", "Financeiro & Resultado", "Financeiro"), ("fc", "Forecast & Planejamento", "Forecast")]
SUBT = {"exec": "Quem cresce com margem e onde está o gap de meta", "com": "Canais, ticket, identificação, recompra e RFV",
        "prod": "Mix, margem, descontos e concentração (Pareto)", "compras": "Recebimentos, lead time, pontualidade e orçamento",
        "estoque": "Saldo, cobertura, giro, excesso e validade", "fin": "DRE gerencial e resultado operacional simplificado",
        "fc": "Previsão de 6 meses com backtest e cenários"}

# ------------------------------------------------------------------ grade (mesma para fundo e visuais)
SB = (16, 16, 216, 1048)            # menu lateral
TOP = (248, 16, 1656, 72)           # barra superior
KPI = (248, 104, 1656, 150)
MAIN = (248, 270, 1040, 420)
R1, R2 = (1304, 270, 600, 202), (1304, 488, 600, 202)
B1, B2, B3 = (248, 706, 520, 358), (784, 706, 560, 358), (1360, 706, 544, 358)
FP = (1488, 96, 416, 968)           # painel de filtros (overlay)
B23 = (B2[0], B2[1], B2[2] + B3[2] + 16, B2[3]); B12 = (B1[0], B1[1], B1[2] + B2[2] + 16, B1[3]); R12 = (R1[0], R1[1], R1[2], R1[3] + R2[3] + 16)
PANELS_BY = {"fin": [MAIN, R12, B1, B2, B3], "fc": [MAIN, R1, R2, B12, B3]}
PANELS = [MAIN, R1, R2, B1, B23]
NAV_Y0, NAV_H, NAV_GAP = 132, 58, 8

def inner(box, pad=10): x, y, w, h = box; return x + pad, y + pad, w - 2 * pad, h - 2 * pad

# ------------------------------------------------------------------ componentes
def tb(pg, key, box, runs, align="left", z=None, hidden=False):
    x, y, w, h = box
    paras = [{"textRuns": [{"value": t, "textStyle": {"fontFamily": FONTB if b else FONT, "fontSize": f"{s}pt", "color": c}} for t, s, c, b in para],
              "horizontalTextAlignment": align} for para in runs]
    v = pg.add(key, "textbox", x, y, w, h, objects={"general": [P(paragraphs=paras)]}, vco=dict(NONE), z=z)
    if hidden: v["isHidden"] = True
    return v

def html(pg, key, box, measure, title=None, z=None, hidden=False):
    x, y, w, h = box
    vco = dict(NONE, padding=[P(top=N(4), bottom=N(4), left=N(4), right=N(4))])
    v = pg.add(key, HTML_VT, x, y, w, h, query={"content": [M(measure)]},
               objects={"contentFormatting": [P(showRawHtml=L(False), fontFamily=L(FONT), fontSize=N(11), fontColour=COL(K["texto"]),
                                                align=L("left"), noDataMessage=L(""))]},
               vco=vco, title=title, z=z)
    if title: v["visual"]["visualContainerObjects"]["title"] = [P(show=L(True), text=L(title), fontColor=COL(K["menta"]), fontSize=N(12), fontFamily=L(FONTB))]
    if hidden: v["isHidden"] = True
    return v

def deneb(pg, key, box, fields, spec, title, subtitle=None):
    x, y, w, h = inner(box, 6)
    vco = dict(NONE)
    vco["title"] = [P(show=L(True), text=L(title), fontColor=COL(K["menta"]), fontSize=N(12), fontFamily=L(FONTB))]
    if subtitle: vco["subTitle"] = [P(show=L(True), text=L(subtitle), fontColor=COL(K["sub"]), fontSize=N(9))]
    pg.add(key, DENEB_VT, x, y, w, h, query={"dataset": [(f, a) for f, a in fields]},
           objects={"vega": [P(jsonSpec=L(DS.spec_json(spec)), jsonConfig=L(DS.config_json()), provider=L("vegaLite"), renderMode=L("svg"),
                               enableTooltips=L(True), enableContextMenu=L(True), enableSelection=L(False), enableHighlight=L(False))]},
           vco=vco)

def vtitle(text, sub=None):
    o = {"title": [P(show=L(True), text=L(text), fontColor=COL(K["menta"]), fontSize=N(12), fontFamily=L(FONTB))]}
    if sub: o["subTitle"] = [P(show=L(True), text=L(sub), fontColor=COL(K["sub"]), fontSize=N(9))]
    return o

def bar(pg, key, box, cat, ms, title, sub=None, color=None, sort_cat=False, tooltip_page=None, cor_measure=None):
    x, y, w, h = inner(box, 6)
    obj = {"labels": [P(show=L(True), color=COL(K["texto"]), fontSize=N(10))],
           "valueAxis": [P(show=L(False), gridlineShow=L(False))],
           "categoryAxis": [P(show=L(True), fontSize=N(10), labelColor=COL(K["sub"]))],
           "legend": [P(show=L(False))]}
    if cor_measure:
        obj["dataPoint"] = [PS({"data": [{"dataViewWildcard": {"matchingOption": 1}}]}, fill=MCOL(cor_measure))]
    else:
        obj["dataPoint"] = [PS({"metadata": R.qref(M(m_))}, fill=COL(color or K["turquesa"])) for m_ in ms]
    vco = dict(NONE, **vtitle(title, sub))
    if tooltip_page: vco["visualTooltip"] = [P(show=L(True), type=L("ReportPage"), section=L(tooltip_page.name))]
    srt = [(cat, "Ascending")] if sort_cat else [(M(ms[0]), "Descending")]
    pg.add(key, "clusteredBarChart", x, y, w, h, query={"Category": [cat], "Y": [M(m_) for m_ in ms]}, objects=obj, vco=vco, sort=srt)

TBL = lambda: {"columnHeaders": [P(fontColor=COL(K["menta"]), backColor=COL(K["petroleo"]), fontFamily=L(FONTB), fontSize=N(10), alignment=L("Center"), wordWrap=L(True))],
               "values": [P(fontColor=COL(K["texto"]), backColor=COL(K["fundo2"]), backColorSecondary=COL(K["vidro"]), fontSize=N(10), fontFamily=L(FONT))],
               "total": [P(fontColor=COL(K["turquesa"]), backColor=COL(K["petroleo"]), fontFamily=L(FONTB))],
               "grid": [P(gridHorizontal=L(True), gridHorizontalColor=COL("#1B4A51"), gridVertical=L(False), outlineColor=COL("#1B4A51"), rowPadding=N(3), imageHeight=N(18), imageWidth=N(120))]}

def table(pg, key, box, fields, title, sort=None, sub=None, center=True):
    x, y, w, h = inner(box, 6)
    obj = TBL()
    if center:
        for f in fields:
            if "Measure" in f["field"]:
                obj["columnFormatting"] = obj.get("columnFormatting", []) + [PS({"metadata": f["queryRef"]}, alignment=L("Center"))]
    svg = [f for f in fields if "Measure" in f["field"] and f["field"]["Measure"]["Property"].startswith("SVG")]
    if svg: obj["columnWidth"] = [PS({"metadata": f["queryRef"]}, value=N(132)) for f in svg]
    pg.add(key, "tableEx", x, y, w, h, query={"Values": fields}, objects=obj, vco=dict(NONE, **vtitle(title, sub)), sort=sort)

def matrix(pg, key, box, rows, cols, values, title, sub=None, no_row_total=False):
    x, y, w, h = inner(box, 6)
    obj = TBL(); obj["rowHeaders"] = [P(fontColor=COL(K["menta"]), fontFamily=L(FONTB), fontSize=N(10))]
    obj["subTotals"] = [P(fontColor=COL(K["turquesa"]), backColor=COL(K["petroleo"]), fontFamily=L(FONTB))]
    if no_row_total: obj["subTotals"].append(P(rowSubtotals=L(False)))
    q = {"Rows": rows, "Values": [M(v) for v in values]}
    if cols: q["Columns"] = cols
    pg.add(key, "pivotTable", x, y, w, h, query=q, objects=obj, vco=dict(NONE, **vtitle(title, sub)))

def button(pg, key, box, label, link, z, fill=None, fill_hover=None, color=None, size=11, align="center", outline=None, hidden=False, tooltip=None):
    x, y, w, h = box
    D_, HV = {"id": "default"}, {"id": "hover"}
    obj = {"icon": [P(show=L(False))], "shape": [P(roundEdge=N(10))],
           "fill": [P(show=L(True)), PS(D_, fillColor=COL(fill or K["petroleo2"]), transparency=N(0 if fill else 100)),
                    PS(HV, fillColor=COL(fill_hover or K["petroleo2"]), transparency=N(0))],
           "outline": [P(show=L(bool(outline)))] + ([PS(D_, lineColor=COL(outline), weight=N(1))] if outline else []),
           "text": [P(show=L(True))] + [PS(s, text=L(label), fontColor=COL(color or K["texto"]), fontSize=N(size), fontFamily=L(FONTB),
                                           horizontalAlignment=L(align), verticalAlignment=L("middle"), leftMargin=N(14 if align == "left" else 0)) for s in (D_, HV)]}
    vco = dict(NONE)
    vco["visualLink"] = [P(show=L(True), **link, **({"tooltip": L(tooltip)} if tooltip else {}))]
    v = pg.add(key, "actionButton", x, y, w, h, objects=obj, vco=vco, z=z)
    if hidden: v["isHidden"] = True
    return v

def nav_link(pg): return {"type": L("PageNavigation"), "navigationSection": L(pg.name)}
def bm_link(name): return {"type": L("Bookmark"), "bookmark": L(name)}

def slicer(pg, key, box, ent, prop, label, single=False, hidden=False, z=None):
    x, y, w, h = box
    sel = [P(singleSelect=L(True))] if single else [P(selectAllCheckboxEnabled=L(True))]
    v = pg.add(key, "slicer", x, y, w, h, query={"Values": [(CLM(ent, prop), label)]},
               objects={"data": [P(mode=L("Dropdown"))], "selection": sel,
                        "header": [P(show=L(True), fontColor=COL(K["sub"]), textSize=N(10), fontFamily=L(FONT))],
                        "items": [P(fontColor=COL(K["branco"]), background=COL(K["vidro"]), textSize=N(11), fontFamily=L(FONT))]},
               vco=dict(background=[P(show=L(True), color=COL(K["vidro"]), transparency=N(0))],
                        border=[P(show=L(True), color=COL("#1F5A60"), radius=N(10))], dropShadow=[P(show=L(False))]),
               sync=f"{ent}.{prop}", z=z)
    if hidden: v["isHidden"] = True
    return v

# ------------------------------------------------------------------ páginas
def build():
    pages = {k: Page(k, d, bg=f"v2_{k}.png") for k, d, _ in PAGES}
    tt = Page("tt_receita", "TT Receita", w=380, h=200, tooltip=True, hidden=True)
    bookmarks = []
    D, Lj, Pr, Fo, Cl, Ca = "dCalendario", "dLoja", "dProduto", "dFornecedor", "dCliente", "dCanal"
    mes, ordm = (CLM(D, "Mes Ano"), "mes"), (CLM(D, "AnoMes Num"), "ord")

    html(tt, "tt_html", (6, 6, 368, 188), "HTML Tooltip Receita")
    tt.bg = None

    def chrome(pg, sigla):
        # menu lateral
        for i, (k, d, _) in enumerate(PAGES):
            y = NAV_Y0 + i * (NAV_H + NAV_GAP)
            act = k == pg.key
            button(pg, f"nav_{k}", (28, y, 176, NAV_H), ("●  " if act else "    ") + d.replace(" & ", " & "), nav_link(pages[k]), 50000 + i,
                   fill=K["petroleo2"] if act else None, fill_hover="#1A6E6F", color=K["turquesa"] if act else K["texto"], size=10, align="left",
                   tooltip=SUBT.get(k, "Página inicial"))
        # barra superior
        tb(pg, "titulo", (TOP[0] + 20, 22, 560, 60), [[(pg.display, 15, K["branco"], True)], [(SUBT[pg.key], 9, K["sub"], False)]], z=49000)
        html(pg, "chips", (820, 26, 860, 52), "HTML Chips Filtros", z=49001)
        button(pg, "btn_filtros", (1724, 30, 164, 44), "⚲  Filtros", bm_link(hid("bm", pg.key, "abrir")), 49002,
               fill=K["turquesa"], fill_hover="#21D1B4", color=K["fundo"], size=11, tooltip="Abrir painel de filtros")

    def painel(pg, extra):
        """Painel de filtros oculto + bookmarks abrir/fechar."""
        names = []
        x, y, w, h = FP
        shp = pg.add("fp_bg", "shape", x, y, w, h, objects={"shape": [P(tileShape=L("rectangleRounded"), roundEdge=N(16))],
                                                            "fill": [P(show=L(False))], "outline": [P(show=L(False))]},
                     vco={"background": [P(show=L(True), color=COL("#0A262C"), transparency=N(2))],
                          "border": [P(show=L(True), color=COL(K["turquesa"]), radius=N(16), width=N(1))],
                          "dropShadow": [P(show=L(True), color=COL("#000000"), transparency=N(40), position=L("Outer"), preset=L("Custom"),
                                           shadowBlur=N(30), shadowDistance=N(0), shadowSpread=N(4))],
                          "title": [P(show=L(False))]}, z=70000)
        shp["isHidden"] = True; names.append(shp)
        names.append(tb(pg, "fp_t", (x + 24, y + 18, w - 90, 56), [[("Filtros", 16, K["branco"], True)], [("Sincronizados entre as páginas", 9, K["sub"], False)]], z=70010, hidden=True))
        names.append(button(pg, "fp_x", (x + w - 56, y + 18, 36, 36), "✕", bm_link(hid("bm", pg.key, "fechar")), 70020, fill_hover="#1A6E6F", size=12, hidden=True, tooltip="Fechar"))
        campos = [(D, "Ano", "Ano"), (D, "Mes Nome", "Mês"), (Lj, "Loja", "Loja")] + extra
        for i, (ent, prop, lab, *opt) in enumerate(campos):
            names.append(slicer(pg, f"fp_s{i}", (x + 24, y + 92 + i * 84, w - 48, 72), ent, prop, lab, single=bool(opt), hidden=True, z=70100 + i))
        names.append(button(pg, "fp_ok", (x + 24, y + h - 76, (w - 64) // 2 + 20, 48), "Aplicar e fechar", bm_link(hid("bm", pg.key, "fechar")), 70200,
                            fill=K["turquesa"], fill_hover="#21D1B4", color=K["fundo"], hidden=True))
        names.append(button(pg, "fp_clear", (x + 44 + (w - 64) // 2 + 20, y + h - 76, (w - 64) // 2 - 20, 48), "Limpar", {"type": L("ClearAllSlicers")}, 70201,
                            outline=K["turquesa"], fill_hover="#1A6E6F", color=K["turquesa"], hidden=True, tooltip="Limpar as segmentações do painel"))
        for estado in ("abrir", "fechar"):
            vcs = {}
            for v in names:
                sv = {"visualType": v["visual"]["visualType"]}
                if estado == "fechar": sv["display"] = {"mode": "hidden"}
                vcs[v["name"]] = {"singleVisual": sv}
            bookmarks.append({"$schema": f"{SCH}/bookmark/1.4.0/schema.json", "displayName": f"{pg.display} · filtros {estado}",
                              "name": hid("bm", pg.key, estado),
                              "options": {"applyOnlyToTargetVisuals": True, "targetVisualNames": [v["name"] for v in names], "suppressData": True},
                              "explorationState": {"version": "1.3", "activeSection": pg.name, "sections": {pg.name: {"visualContainers": vcs}}},
                              "_grupo": pg.display})

    # ---------------- HOME
    pg = pages["home"]
    tb(pg, "h1", (120, 330, 900, 60), [[("Inteligência de negócio para farmácias", 22, K["menta"], False)]])
    tb(pg, "h2", (120, 384, 1100, 90), [[("Cuidar bem é viver melhor.", 40, K["branco"], True)]])
    tb(pg, "h3", (120, 470, 900, 70), [[("Receita, clientes, mix, compras, estoque, resultado e previsão das 4 farmácias da rede, em um só lugar.", 14, K["sub"], False)]])
    button(pg, "iniciar", (120, 566, 240, 60), "Iniciar  ›", nav_link(pages["exec"]), 60000, fill=K["turquesa"], fill_hover="#21D1B4",
           color=K["fundo"], size=15, tooltip="Começar pela Visão Executiva")
    html(pg, "h_kpis", (120, 700, 1680, 150), "HTML KPIs Home")
    tb(pg, "h4", (120, 990, 1680, 40), [[("Dados 100% sintéticos para portfólio · base 01/10/2024 a 30/09/2026 · resultado operacional simplificado não é EBITDA · previsões são faixas, não metas.", 10, K["sub"], False)]])

    # ---------------- EXECUTIVA
    pg = pages["exec"]; chrome(pg, "Executiva"); painel(pg, [(Ca, "Canal", "Canal")])
    html(pg, "kpis", KPI, "HTML KPIs Executiva")
    deneb(pg, "d_rec", MAIN, [mes, ordm, (M("Receita Líquida"), "receita"), (M("Receita Líquida LY"), "ly"), (M("Meta Receita"), "meta"),
                              (M("Cor Destaque Receita Mes"), "cor")], "exec_receita",
          "Receita líquida mensal", "Barra = realizado (destaque: maior mês) · linha clara = ano anterior · tracejado coral = meta")
    bar(pg, "lojas", R1, CLM(Lj, "Loja Curta"), ["Receita Líquida"], "Receita líquida por loja", tooltip_page=tt)
    bar(pg, "ating", R2, CLM(Lj, "Loja Curta"), ["Atingimento Meta %"], "Atingimento da meta por loja", "verde ≥ 100% · âmbar ≥ 95% · coral < 95%", cor_measure="Cor Atingimento")
    html(pg, "narr", inner(B1, 14), "HTML Narrativa Executiva")
    table(pg, "cats", (B2[0], B2[1], B2[2] + B3[2] + 16, B2[3]),
          [proj(CLM(Pr, "Categoria")), proj(M("SVG Barra Receita Categoria"), "Receita"), proj(M("Receita Líquida Itens"), "Receita (R$)"),
           proj(M("Share Receita Itens %"), "Part."), proj(M("Margem Bruta Itens %"), "Margem"), proj(M("Margem Itens Var pp"), "Margem vs LY"),
           proj(M("Desconto Itens %"), "Desconto"), proj(M("Receita Itens YoY %"), "Receita vs LY")],
          "Onde agir: categorias por receita, margem e desconto", sort=[(M("Receita Líquida Itens"), "Descending")])

    # ---------------- COMERCIAL & CLIENTES
    pg = pages["com"]; chrome(pg, "Clientes"); painel(pg, [(Ca, "Canal", "Canal"), (Cl, "Segmento RFV", "Segmento RFV")])
    html(pg, "kpis", KPI, "HTML KPIs Clientes")
    deneb(pg, "d_heat", MAIN, [mes, ordm, (CLM(D, "Dia Semana"), "dia"), (CLM(D, "Dia Semana Num"), "dord"), (M("Cupons"), "cupons")], "com_heatmap",
          "Mapa de calor: cupons por dia da semana e mês", "Base sem horário de venda: o recorte mais fino possível é o dia")
    bar(pg, "canal", R1, CLM(Ca, "Canal"), ["Receita Líquida"], "Receita líquida por canal", tooltip_page=tt)
    bar(pg, "rfv", R2, CLM(Cl, "Segmento RFV"), ["Clientes Ativos"], "Clientes ativos por segmento RFV", "Foto em 30/09/2026", color=K["petroleo2"], sort_cat=True)
    html(pg, "narr", inner(B1, 14), "HTML Narrativa Clientes")
    matrix(pg, "ticket", (B2[0], B2[1], B2[2] + B3[2] + 16, B2[3]), [proj(CLM(Ca, "Canal"))], None,
           ["Cupons", "% Cupons Identificados", "Ticket Médio Identificado", "Ticket Médio Anônimo", "Itens por Cupom", "Frequência Média", "Taxa de Recompra %"],
           "Identificado vs anônimo por canal")

    # ---------------- PRODUTOS
    pg = pages["prod"]; chrome(pg, "Produtos"); painel(pg, [(Pr, "Categoria", "Categoria"), (Pr, "Subcategoria", "Subcategoria"), (Pr, "Classe ABC", "Classe ABC")])
    html(pg, "kpis", KPI, "HTML KPIs Produtos")
    deneb(pg, "d_par", MAIN, [(CLM(Pr, "Subcategoria"), "sub"), (M("Receita Líquida Itens"), "rec")], "prod_pareto",
          "Pareto de receita por subcategoria", "Barras turquesa = subcategorias que somam até 80% da receita · linha = % acumulado")
    bar(pg, "mix", R1, CLM(Pr, "Categoria"), ["Receita Líquida Itens"], "Receita por categoria", tooltip_page=tt)
    bar(pg, "mg", R2, CLM(Pr, "Categoria"), ["Margem Bruta Itens %"], "Margem bruta por categoria", color=K["petroleo2"])
    html(pg, "narr", inner(B1, 14), "HTML Narrativa Produtos")
    table(pg, "skus", (B2[0], B2[1], B2[2] + B3[2] + 16, B2[3]),
          [proj(M("Ranking SKU"), "#"), proj(CLM(Pr, "Produto")), proj(CLM(Pr, "Categoria")), proj(CLM(Pr, "Classe ABC"), "ABC"),
           proj(M("SVG Barra Receita SKU"), "Receita"), proj(M("Receita Líquida Itens"), "Receita (R$)"), proj(M("Margem Bruta Itens %"), "Margem"),
           proj(M("Desconto Itens %"), "Desconto"), proj(M("Unidades Vendidas"), "Unidades")],
          "Ranking de SKUs · ordene por margem para ver detratores", sort=[(M("Receita Líquida Itens"), "Descending")])

    # ---------------- COMPRAS
    pg = pages["compras"]; chrome(pg, "Compras"); painel(pg, [(Pr, "Categoria", "Categoria"), (Fo, "Fornecedor", "Fornecedor")])
    html(pg, "kpis", KPI, "HTML KPIs Compras")
    deneb(pg, "d_heat", MAIN, [(CLM(Lj, "Loja Curta"), "loja"), (CLM(Pr, "Categoria"), "cat"), (M("Pontualidade %"), "pont"), (M("Recebimentos"), "rec")],
          "compras_heat", "Pontualidade das entregas: loja × categoria", "Coral = pior · âmbar = intermediário · turquesa = melhor (relativo à seleção) · OTD, não OTIF")
    bar(pg, "cat", R1, CLM(Pr, "Categoria"), ["Valor Recebido"], "Compras recebidas por categoria")
    bar(pg, "pont", R2, CLM(Lj, "Loja Curta"), ["Pontualidade %"], "Pontualidade por loja", "referência saudável ≥ 90%", cor_measure="Cor Pontualidade")
    html(pg, "narr", inner(B1, 14), "HTML Narrativa Compras")
    table(pg, "forn", (B2[0], B2[1], B2[2] + B3[2] + 16, B2[3]),
          [proj(CLM(Fo, "Fornecedor")), proj(CLM(Fo, "UF Fornecedor"), "UF"), proj(M("SVG Barra Compras Fornecedor"), "Compras"),
           proj(M("Valor Recebido"), "Compras (R$)"), proj(M("Share Compras %"), "Part."), proj(M("Lead Time Médio"), "Lead time"),
           proj(M("Prazo Previsto Médio"), "Prazo previsto"), proj(M("Pontualidade %"), "Pontualidade"), proj(M("Atraso Médio"), "Atraso médio")],
          "Fornecedores", sort=[(M("Valor Recebido"), "Descending")])

    # ---------------- ESTOQUE
    pg = pages["estoque"]; chrome(pg, "Estoque"); painel(pg, [(Pr, "Categoria", "Categoria"), ("fEstoque", "Status Estoque", "Status do estoque")])
    html(pg, "kpis", KPI, "HTML KPIs Estoque")
    deneb(pg, "d_dot", MAIN, [(CLM(Pr, "Categoria"), "cat"), (CLM(Lj, "Loja Curta"), "loja"), (M("Cobertura (dias)"), "cob")], "estoque_dot",
          "Cobertura estimada por categoria e loja", "Saldo final ÷ venda média diária dos últimos 3 meses · tracejado = limite de excesso")
    bar(pg, "status", R1, CLM("fEstoque", "Status Estoque"), ["Estoque Final (R$)"], "Valor por status de estoque", "Excesso > 120 d · Baixo < 15 d · Sem giro = 3+ meses sem venda", color=K["coral"])
    bar(pg, "val", R2, CLM("fLotes", "Faixa Validade"), ["Valor em Lotes (R$)"], "Validade · foto 30/09/2026", "Lotes simulados · não responde a filtro de data", color=K["ambar"], sort_cat=True)
    html(pg, "narr", inner(B1, 14), "HTML Narrativa Estoque")
    table(pg, "acao", (B2[0], B2[1], B2[2] + B3[2] + 16, B2[3]),
          [proj(CLM(Pr, "Produto")), proj(CLM(Lj, "Loja Curta"), "Loja"), proj(CLM("fEstoque", "Status Estoque"), "Status"),
           proj(M("SVG Barra Estoque SKU"), "Valor"), proj(M("Estoque Final (R$)"), "Estoque (R$)"), proj(M("Estoque Final (un)"), "Unidades"),
           proj(M("Cobertura (dias)"), "Cobertura")],
          "Tabela de ação: maiores saldos valorizados", sort=[(M("Estoque Final (R$)"), "Descending")])

    # ---------------- FINANCEIRO
    pg = pages["fin"]; chrome(pg, "Financeiro"); painel(pg, [])
    html(pg, "kpis", KPI, "HTML KPIs Financeiro")
    deneb(pg, "d_wf", MAIN, [(CLM("dDRE", "Linha DRE"), "linha"), (CLM("dDRE", "Ordem DRE"), "ord"), (M("Valor Ponte Deneb"), "val")], "fin_waterfall",
          "Da receita líquida ao resultado operacional simplificado", "Resultado = lucro bruto − despesas modeladas · não é EBITDA")
    matrix(pg, "dre", (R1[0], R1[1], R1[2], R1[3] + R2[3] + 16), [proj(CLM("dDRE", "Linha DRE"))], [proj(CLM(Lj, "Loja Curta"))], ["Valor DRE (R$ mil)"],
           "DRE gerencial simplificada por loja (R$ mil)", no_row_total=True)
    html(pg, "narr", inner(B1, 14), "HTML Narrativa Financeiro")
    bar(pg, "desp", B2, CLM(Lj, "Loja Curta"), ["Despesas % Receita"], "Despesas sobre receita por loja", color=K["coral"])
    bar(pg, "mgop", B3, CLM(Lj, "Loja Curta"), ["Margem Operacional Simplificada %"], "Margem op. simplificada por loja", "verde ≥ 20% · âmbar ≥ 10%", cor_measure="Cor Margem Op")

    # ---------------- FORECAST
    pg = pages["fc"]; chrome(pg, "Forecast"); painel(pg, [("dCenario", "Cenario", "Cenário", True)])
    html(pg, "kpis", KPI, "HTML KPIs Forecast")
    deneb(pg, "d_fc", MAIN, [mes, ordm, (M("Receita Real (Série)"), "real"), (M("Receita Prevista Cenário"), "prev"),
                             (M("Limite Inferior Cenário"), "lo"), (M("Limite Superior Cenário"), "hi")], "fc_banda",
          "Receita real e prevista com faixa de incerteza", "Faixa ~80% empírica do backtest · projeção ≠ meta ≠ fato")
    bar(pg, "wape", R1, CLM("fBacktest", "Metodo"), ["WAPE por Método %"], "Erro por método no backtest (WAPE)", "menor é melhor", color=K["petroleo2"])
    html(pg, "metodo", inner(R2, 14), "HTML Narrativa Forecast")
    matrix(pg, "tab", (B1[0], B1[1], B1[2] + B2[2] + 16, B1[3]), [proj(CLM(D, "Mes Ano"))], [proj(CLM(Lj, "Loja Curta"))], ["Receita Prevista Cenário"],
           "Previsão mensal por loja (cenário ativo)")
    tb(pg, "met", inner(B3, 18), [[("Como a previsão foi feita", 12, K["turquesa"], True)],
                                   [("• 3 métodos simples (sazonal YoY, Holt amortecido, média móvel 3m) comparados por backtest rolling-origin, horizontes 1–3.", 10, K["texto"], False)],
                                   [("• Por loja, vence o menor WAPE. Faixa = quantis 10–90% dos erros do backtest; meses 4–6 ampliam 10%/mês.", 10, K["texto"], False)],
                                   [("• Cenários aplicam fatores de receita/custo (dCenario). São premissas, não previsões.", 10, K["texto"], False)],
                                   [("• Só 24 meses de histórico: use como faixa de planejamento.", 10, K["coral"], True)]])

    return [pages[k] for k, _, _ in PAGES] + [tt], bookmarks

# ------------------------------------------------------------------ fundos
def logo_negativo(path):
    lg = Image.open(path).convert("RGBA"); lg = lg.crop(lg.getbbox())
    px = lg.load()
    for yy in range(lg.height):
        for xx in range(lg.width):
            r, g, b, a = px[xx, yy]
            if a > 0 and (0.299 * r + 0.587 * g + 0.114 * b) < 70 and g < 110:   # lettering petróleo escuro → branco (preserva turquesa/alpha)
                px[xx, yy] = (255, 255, 255, a)
    return lg

def rr(d, box, r, fill=None, outline=None, width=1): x, y, w, h = box; d.rounded_rectangle((x, y, x + w, y + h), r, fill=fill, outline=outline, width=width)

def fundo_base():
    im = Image.new("RGB", (W, H), K["fundo"])
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse((1100, -500, 2300, 600), fill=(24, 184, 159, 38)); gd.ellipse((-400, 600, 700, 1500), fill=(18, 95, 97, 60))
    g = g.filter(ImageFilter.GaussianBlur(160))
    return Image.alpha_composite(im.convert("RGBA"), g)

def glass(im, box, r=16, a=18, border=(24, 184, 159, 60)):
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    x, y, w, h = box
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((x, y + 6, x + w, y + h + 6), r, fill=(0, 0, 0, 90))
    im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(12)))
    od.rounded_rectangle((x, y, x + w, y + h), r, fill=(255, 255, 255, a), outline=border, width=1)
    od.line((x + r, y + 1, x + w - r, y + 1), fill=(255, 255, 255, 40), width=1)
    return Image.alpha_composite(im, ov)

def backgrounds(out, logo_path):
    os.makedirs(out, exist_ok=True)
    lg = logo_negativo(logo_path)
    files = []
    for i, (k, d, _) in enumerate(PAGES):
        im = fundo_base()
        if k == "home":
            big = lg.resize((int(lg.width * 170 / lg.height), 170), Image.LANCZOS)
            im.alpha_composite(big, (110, 110))
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            cx, cy, s = 1560, 420, 150
            od.rounded_rectangle((cx - s // 2, cy - int(s * 1.6), cx + s // 2, cy + int(s * 1.6)), 60, fill=(24, 184, 159, 34))
            od.rounded_rectangle((cx - int(s * 1.6), cy - s // 2, cx + int(s * 1.6), cy + s // 2), 60, fill=(24, 184, 159, 34))
            od.ellipse((cx + 60, cy - 330, cx + 330, cy - 60), fill=(221, 245, 235, 22))
            im = Image.alpha_composite(im, ov.filter(ImageFilter.GaussianBlur(2)))
            im = glass(im, (100, 684, 1720, 182), r=20, a=8)
        else:
            im = glass(im, SB, r=20, a=14)
            sm = lg.resize((176, int(lg.height * 176 / lg.width)), Image.LANCZOS)
            im.alpha_composite(sm, (28, 40))
            dr = ImageDraw.Draw(im)
            dr.line((36, 112, 196, 112), fill=(24, 184, 159, 90), width=1)
            ay = NAV_Y0 + i * (NAV_H + NAV_GAP)
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).rounded_rectangle((22, ay + 8, 26, ay + NAV_H - 8), 2, fill=(24, 184, 159, 255))
            im = Image.alpha_composite(im, ov)
            f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 12)
            ImageDraw.Draw(im).text((32, 990), "Base sintética · dados fictícios", fill=(159, 201, 193, 255), font=f)
            ImageDraw.Draw(im).text((32, 1010), "01/10/2024 a 30/09/2026", fill=(221, 245, 235, 255), font=f)
            im = glass(im, TOP, r=16, a=10)
            for b in PANELS_BY.get(k, PANELS): im = glass(im, b, r=16, a=12)
        fn = f"v2_{k}.png"; im.convert("RGB").save(os.path.join(out, fn), optimize=True); files.append(fn)
    lg.save(os.path.join(out, "logo_negativo.png"))
    return files

def theme():
    S = lambda c: {"solid": {"color": c}}
    return {"name": "FarmaVitta Dark",
            "dataColors": [K["turquesa"], K["menta"], K["ambar"], K["coral"], "#5FA8A0", "#2E8C7E", "#B7C4C7", "#F4C2B3"],
            "foreground": K["texto"], "foregroundNeutralSecondary": K["sub"], "foregroundNeutralTertiary": "#5E8580",
            "background": K["fundo2"], "backgroundLight": K["vidro"], "backgroundNeutral": "#1B4A51",
            "tableAccent": K["turquesa"], "good": K["turquesa"], "neutral": K["ambar"], "bad": K["coral"],
            "maximum": K["turquesa"], "center": K["ambar"], "minimum": K["coral"], "hyperlink": K["turquesa"],
            "textClasses": {"callout": {"fontSize": 24, "fontFace": FONTB, "color": K["branco"]},
                            "title": {"fontSize": 12, "fontFace": FONTB, "color": K["menta"]},
                            "header": {"fontSize": 11, "fontFace": FONTB, "color": K["menta"]},
                            "label": {"fontSize": 10, "fontFace": FONT, "color": K["texto"]}},
            "visualStyles": {
                "*": {"*": {"background": [{"show": False}], "border": [{"show": False}], "dropShadow": [{"show": False}],
                            "title": [{"show": True, "fontColor": S(K["menta"]), "fontSize": 12, "fontFamily": FONTB}],
                            "visualHeader": [{"show": True, "background": S(K["fundo2"]), "foreground": S(K["sub"]), "border": S(K["fundo2"])}],
                            "visualTooltip": [{"background": S(K["fundo2"]), "titleFontColor": S(K["sub"]), "valueFontColor": S(K["texto"]), "fontSize": 10}],
                            "padding": [{"top": 8, "bottom": 8, "left": 12, "right": 12}]}},
                "page": {"*": {"background": [{"color": S(K["fundo"]), "transparency": 0}], "outspace": [{"color": S("#04161A"), "transparency": 0}]}},
                "slicer": {"*": {"items": [{"fontColor": S(K["branco"]), "background": S(K["vidro"])}], "header": [{"fontColor": S(K["sub"])}]}},
            }}

def write_report_v2(base, model_folder, logo_path):
    defs = os.path.join(base, "definition"); res = os.path.join(base, "StaticResources", "RegisteredResources")
    bgs = backgrounds(res, logo_path)
    R.wj(os.path.join(res, "FarmaVitta_Tema_Dark.json"), theme())
    R.wj(os.path.join(base, "definition.pbir"), {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
                                                "version": "4.0", "datasetReference": {"byPath": {"path": f"../{model_folder}"}}})
    items = [{"name": "FarmaVitta_Tema_Dark.json", "path": "FarmaVitta_Tema_Dark.json", "type": "CustomTheme"}] + \
            [{"name": f, "path": f, "type": "Image"} for f in bgs + ["logo_negativo.png"]]
    R.wj(os.path.join(defs, "report.json"), {
        "$schema": f"{SCH}/report/{R.V_REP}/schema.json",
        "themeCollection": {"customTheme": {"name": "FarmaVitta_Tema_Dark.json", "reportVersionAtImport": {"visual": "2.2.0", "report": "3.0.0", "page": "2.0.0"}, "type": "RegisteredResources"}},
        "publicCustomVisuals": [DENEB_VT, HTML_VT],
        "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources", "items": items}],
        "settings": {"useStylableVisualContainerHeader": True, "exportDataMode": "AllowSummarized", "defaultDrillFilterOtherVisuals": True}})
    R.wj(os.path.join(defs, "version.json"), {"$schema": f"{SCH}/versionMetadata/{R.V_VER}/schema.json", "version": "2.0.0"})
    pages, bms = build()
    R.wj(os.path.join(defs, "pages", "pages.json"), {"$schema": f"{SCH}/pagesMetadata/{R.V_PAGES}/schema.json",
                                                     "pageOrder": [p.name for p in pages], "activePageName": pages[0].name})
    nvis = 0
    for p in pages:
        pj = {"$schema": f"{SCH}/page/{R.V_PAGE}/schema.json", "name": p.name, "displayName": p.display, "displayOption": "FitToPage", "height": p.h, "width": p.w}
        if p.bg:
            pj["objects"] = {"background": [P(image={"image": {"name": L(p.bg), "url": {"expr": {"ResourcePackageItem": {
                "PackageName": "RegisteredResources", "PackageType": 1, "ItemName": p.bg}}}, "scaling": L("Fit")}}, transparency=N(0))]}
        else:
            pj["objects"] = {"background": [P(color=COL(K["fundo2"]), transparency=N(0))]}
        if p.tooltip:
            pj["type"] = "Tooltip"; pj["pageBinding"] = {"name": hid("bind", p.key), "type": "Tooltip", "referenceScope": "Default"}
        if p.hidden: pj["visibility"] = "HiddenInViewMode"
        R.wj(os.path.join(defs, "pages", p.name, "page.json"), pj)
        for v in p.visuals:
            R.wj(os.path.join(defs, "pages", p.name, "visuals", v["name"], "visual.json"), v); nvis += 1
    grupos = {}
    for b in bms:
        g = b.pop("_grupo"); grupos.setdefault(g, []).append(b["name"])
        R.wj(os.path.join(defs, "bookmarks", f"{b['name']}.bookmark.json"), b)
    R.wj(os.path.join(defs, "bookmarks", "bookmarks.json"), {"$schema": f"{SCH}/bookmarksMetadata/1.0.0/schema.json",
         "items": [{"name": hid("grp", g), "displayName": f"Filtros · {g}", "children": c} for g, c in grupos.items()]})
    # specs Deneb versionados
    dd = os.path.join(os.path.dirname(base), "Deneb"); os.makedirs(dd, exist_ok=True)
    for k_, s_ in DS.SPECS.items(): R.wj(os.path.join(dd, f"{k_}.vl.json"), s_)
    R.wj(os.path.join(dd, "_config.json"), DS.CONFIG)
    return pages, nvis, len(bms)
