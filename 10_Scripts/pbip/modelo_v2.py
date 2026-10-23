# -*- coding: utf-8 -*-
"""v2: estende o modelo v1 com medidas HTML (cards + sparkline SVG), chips de filtro, narrativas HTML,
barras SVG (ImageUrl) e cores inteligentes para Deneb. Importa modelo.py e acrescenta em modelo.MED."""
import modelo
from modelo import m, BRL, PCT, INT

MED = modelo.MED
def mi(nome, pasta, dax, desc="", cat=None, hidden=False):
    m(nome, pasta, "", dax, desc)
    if cat: MED[-1]["cat"] = cat
    if hidden: MED[-1]["hidden"] = True

# ---------------------------------------------------------------- cores semânticas (tokens)
OK, ATN, BAD, NEU = "#18B89F", "#F2C46D", "#EF9277", "#9FC9C1"

# ---------------------------------------------------------------- formatação de valor (texto DAX)
def fmt(kind, v):
    return {
        "brl": f'IF ( ABS ( {v} ) >= 1000000, "R$ " & FORMAT ( {v} / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( {v} / 1000, "#,0.0", "pt-BR" ) & " mil" )',
        "brl2": f'"R$ " & FORMAT ( {v}, "#,0.00", "pt-BR" )',
        "pct": f'FORMAT ( {v}, "0.0%", "pt-BR" )',
        "int": f'IF ( {v} >= 1000000, FORMAT ( {v} / 1000000, "#,0.00", "pt-BR" ) & " mi", IF ( {v} >= 10000, FORMAT ( {v} / 1000, "#,0.0", "pt-BR" ) & " mil", FORMAT ( {v}, "#,0", "pt-BR" ) ) )',
        "dec": f'FORMAT ( {v}, "#,0.00", "pt-BR" )',
        "dias": f'FORMAT ( {v}, "#,0", "pt-BR" ) & " dias"',
        "dias1": f'FORMAT ( {v}, "#,0.0", "pt-BR" ) & " dias"',
        "x": f'FORMAT ( {v}, "0.00", "pt-BR" ) & "x"',
        "txt": f'{v}',
    }[kind]

# ---------------------------------------------------------------- sparkline (12 meses até o fim do contexto)
SPARKED = set()
def spark(measure):
    nome = f"_Spark {measure}"
    if nome in SPARKED: return nome
    SPARKED.add(nome)
    mi(nome, "11 SVG & HTML", f"""
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [{measure}] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )""", "Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.", hidden=True)
    return nome

CSS_CARDS = ("<style>"
    ".g{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:14px;font-family:Segoe UI,sans-serif;padding:2px}"
    ".k{position:relative;background:linear-gradient(160deg,rgba(255,255,255,.08),rgba(255,255,255,.02));border:1px solid rgba(24,184,159,.28);"
    "border-radius:14px;padding:12px 14px 4px 18px;overflow:hidden;animation:up .6s ease both;box-shadow:0 8px 24px rgba(0,0,0,.25)}"
    ".k:before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c);box-shadow:0 0 12px var(--c)}"
    ".t{font-size:12px;color:#9FC9C1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.2px}"
    ".v{font-size:25px;font-weight:600;color:#FFFFFF;margin-top:2px;white-space:nowrap}"
    ".d{font-size:11px;color:var(--c);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}"
    ".k svg{width:100%;height:30px;margin-top:2px;display:block}"
    ".k polyline{fill:none;stroke:var(--c);stroke-width:2;stroke-linejoin:round;stroke-dasharray:400;stroke-dashoffset:400;animation:dr 1.6s ease forwards .3s;vector-effect:non-scaling-stroke}"
    ".k:nth-child(2){animation-delay:.08s}.k:nth-child(3){animation-delay:.16s}.k:nth-child(4){animation-delay:.24s}.k:nth-child(5){animation-delay:.32s}.k:nth-child(6){animation-delay:.4s}"
    "@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
    "@keyframes dr{to{stroke-dashoffset:0}}"
    "@media (prefers-reduced-motion:reduce){.k,.k polyline{animation:none;stroke-dashoffset:0;opacity:1}}"
    "</style>")

def html_cards(nome, pasta, cards, desc=""):
    """cards: dicts t(título), v(medida), f(formato), var(medida de variação|None), vk('pct'|'pp'|'txt'), up(+1/-1),
    sp(medida p/ sparkline|None), cor(medida de cor opcional), sub(texto quando sem variação)."""
    vars_, parts = [], []
    for i, c in enumerate(cards):
        vars_.append(f"VAR _v{i} = [{c['v']}]")
        if c.get("var"):
            vars_.append(f"VAR _d{i} = [{c['var']}]")
            up = c.get("up", 1)
            if c.get("vk") == "pp":
                txt = f'IF ( _d{i} >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d{i} ), "0.0", "pt-BR" ) & " p.p. vs ano anterior"'
            elif c.get("vk") == "txt":
                txt = f'_d{i}'
            else:
                txt = f'IF ( _d{i} >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d{i} ), "0.0%", "pt-BR" ) & " vs ano anterior"'
            vars_.append(f'VAR _x{i} = IF ( ISBLANK ( _d{i} ), "{c.get("sub", "sem base comparável no ano anterior")}", {txt} )')
            if c.get("vk") == "txt":
                vars_.append(f'VAR _c{i} = [{c["cor"]}]' if c.get("cor") else f'VAR _c{i} = "{NEU}"')
            else:
                thr = 0 if c.get("vk") == "pp" else 0
                warn = "-0.5" if c.get("vk") == "pp" else "-0.03"
                g = f"_d{i} * {up}"
                vars_.append(f'VAR _c{i} = IF ( ISBLANK ( _d{i} ), "{NEU}", IF ( {g} >= {thr}, "{OK}", IF ( {g} >= {warn}, "{ATN}", "{BAD}" ) ) )')
        else:
            vars_.append(f'VAR _x{i} = "{c.get("sub", "")}"')
            vars_.append(f'VAR _c{i} = [{c["cor"]}]' if c.get("cor") else f'VAR _c{i} = "{OK}"')
        if c.get("sp"):
            vars_.append(f"VAR _s{i} = [{spark(c['sp'])}]")
            svg = f'IF ( ISBLANK ( _s{i} ), "", "<svg viewBox=\'0 0 100 30\' preserveAspectRatio=\'none\'><polyline points=\'" & _s{i} & "\'/></svg>" )'
        else:
            svg = '""'
        parts.append(f'"<div class=\'k\' style=\'--c:" & _c{i} & "\'><div class=\'t\'>{c["t"]}</div><div class=\'v\'>" & IF ( ISBLANK ( _v{i} ), "–", {fmt(c["f"], f"_v{i}")} ) & "</div><div class=\'d\'>" & _x{i} & "</div>" & {svg} & "</div>"')
    body = "\n".join(vars_) + "\nRETURN\n\"" + CSS_CARDS.replace('"', '""') + f"<div class='g' style='--n:{len(cards)}'>\"\n    & " + "\n    & ".join(parts) + "\n    & \"</div>\""
    mi(nome, pasta, body, desc or "Cards HTML (HTML Content) com valor, comparação, cor semântica e sparkline SVG animada.")

# ---------------------------------------------------------------- helpers de cor/status
m("Cor Atingimento", "10 UI & Formatação", "", f'VAR _a = [Atingimento Meta %] RETURN IF ( ISBLANK ( _a ), "{NEU}", IF ( _a >= 1, "{OK}", IF ( _a >= 0.95, "{ATN}", "{BAD}" ) ) )')
m("Cor Cobertura", "10 UI & Formatação", "", f'VAR _c = [Cobertura (dias)] RETURN IF ( ISBLANK ( _c ), "{NEU}", IF ( _c <= 60, "{OK}", IF ( _c <= 120, "{ATN}", "{BAD}" ) ) )')
m("Cor Pontualidade", "10 UI & Formatação", "", f'VAR _p = [Pontualidade %] RETURN IF ( ISBLANK ( _p ), "{NEU}", IF ( _p >= 0.9, "{OK}", IF ( _p >= 0.7, "{ATN}", "{BAD}" ) ) )')
m("Cor Margem Op", "10 UI & Formatação", "", f'VAR _p = [Margem Operacional Simplificada %] RETURN IF ( ISBLANK ( _p ), "{NEU}", IF ( _p >= 0.2, "{OK}", IF ( _p >= 0.1, "{ATN}", "{BAD}" ) ) )')
m("Cor Validade", "10 UI & Formatação", "", f'VAR _p = [% Valor em Risco Validade] RETURN IF ( ISBLANK ( _p ), "{NEU}", IF ( _p <= 0.05, "{OK}", IF ( _p <= 0.1, "{ATN}", "{BAD}" ) ) )')
m("Cor Perdas", "10 UI & Formatação", "", f'VAR _p = [Perdas % CMV] RETURN IF ( ISBLANK ( _p ), "{NEU}", IF ( _p <= 0.01, "{OK}", IF ( _p <= 0.02, "{ATN}", "{BAD}" ) ) )')
m("Cor WAPE", "10 UI & Formatação", "", f'VAR _p = [WAPE Backtest %] RETURN IF ( ISBLANK ( _p ), "{NEU}", IF ( _p <= 0.08, "{OK}", IF ( _p <= 0.15, "{ATN}", "{BAD}" ) ) )')
m("Txt Atingimento", "10 UI & Formatação", "", '[Txt Meta]')
m("Txt Cobertura Dias", "10 UI & Formatação", "", 'IF ( ISBLANK ( [Cobertura (dias)] ), "", IF ( [Cobertura (dias)] > 120, "excesso: acima de 120 dias", IF ( [Cobertura (dias)] > 60, "atenção: 60 a 120 dias", "saudável: até 60 dias" ) ) )')
m("Txt Pontualidade Meta", "10 UI & Formatação", "", '"referência saudável ≥ 90%"')
m("Txt WAPE", "10 UI & Formatação", "", '"erro histórico · rolling-origin"')
m("Txt Giro", "10 UI & Formatação", "", 'IF ( [Giro Anualizado] < 2, "baixo para varejo farma", "adequado" )')
m("Txt ROS Margem", "10 UI & Formatação", "", '"margem " & FORMAT ( [Margem Operacional Simplificada %], "0.0%", "pt-BR" ) & " · não é EBITDA"')

# Deneb: destaque inteligente (maior valor da seleção)
m("Cor Destaque Receita Mes", "11 SVG & HTML", "", f"""
VAR _mx = CALCULATE ( MAXX ( VALUES ( dCalendario[AnoMes Num] ), [Receita Líquida] ), ALLSELECTED ( dCalendario ) )
RETURN IF ( NOT ISBLANK ( [Receita Líquida] ), IF ( [Receita Líquida] = _mx, "{OK}", "#2E7F78" ) )""", "Destaca o mês de maior receita na seleção (Deneb).")
m("Valor Ponte Deneb", "07 Financeiro", BRL, """
SWITCH ( SELECTEDVALUE ( dDRE[Ordem DRE] ),
    3, [Receita Líquida], 4, - [CMV], 6, - [Pessoal], 7, - [Aluguel], 8, - [Despesas Operacionais], 9, - [Marketing e Canais],
    10, [Resultado Operacional Simplificado] )""", "Waterfall Deneb: inclui a linha 10 (total) explicitamente.")

m("Valor DRE (R$ mil)", "07 Financeiro", '#,0;-#,0;0', "DIVIDE ( [Valor DRE], 1000 )", "DRE em R$ mil para tabelas largas.")

# ---------------------------------------------------------------- barras SVG em tabela (ImageUrl)
def svg_bar(nome, measure, dim, color=OK):
    c = color.replace("#", "%23")
    mi(nome, "11 SVG & HTML", f"""
VAR _v = [{measure}]
VAR _mx = CALCULATE ( MAXX ( ALLSELECTED ( {dim} ), [{measure}] ), ALLSELECTED ( {dim} ) )
VAR _w = IF ( _mx > 0, MAX ( 2, DIVIDE ( _v, _mx ) * 116 ), 0 )
RETURN IF ( NOT ISBLANK ( _v ),
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='18'><rect x='0' y='5' width='120' height='8' rx='4' fill='%23FFFFFF' fill-opacity='0.08'/><rect x='0' y='5' width='" & FORMAT ( _w, "0", "en-US" ) & "' height='8' rx='4' fill='{c}'/></svg>" )""",
       "Barra SVG para coluna de tabela (categoria de dados ImageUrl).", cat="ImageUrl")
svg_bar("SVG Barra Receita Categoria", "Receita Líquida Itens", "dProduto[Categoria]")
svg_bar("SVG Barra Receita SKU", "Receita Líquida Itens", "dProduto[Produto]")
svg_bar("SVG Barra Compras Fornecedor", "Valor Recebido", "dFornecedor[Fornecedor]")
svg_bar("SVG Barra Estoque SKU", "Estoque Final (R$)", "dProduto[Produto]", BAD)

# ---------------------------------------------------------------- chips de filtros ativos
def chip(col, rot):
    return (f'IF ( ISFILTERED ( {col} ), "<span class=\'c\'><b>{rot}</b> " & '
            f'IF ( COUNTROWS ( VALUES ( {col} ) ) > 3, FORMAT ( COUNTROWS ( VALUES ( {col} ) ), "0" ) & " itens", CONCATENATEX ( VALUES ( {col} ), {col}, ", " ) ) & "</span>" )')
CHIPS = [("dCalendario[Ano]", "Ano"), ("dCalendario[Mes Nome]", "Mês"), ("dLoja[Loja]", "Loja"), ("dCanal[Canal]", "Canal"),
         ("dProduto[Categoria]", "Categoria"), ("dProduto[Subcategoria]", "Subcategoria"), ("dFornecedor[Fornecedor]", "Fornecedor"),
         ("dCliente[Segmento RFV]", "RFV"), ("fEstoque[Status Estoque]", "Status"), ("dCenario[Cenario]", "Cenário")]
CSS_CHIP = ("<style>.w{font-family:Segoe UI,sans-serif;display:flex;flex-wrap:wrap;gap:6px;align-items:center;height:100%}"
            ".c{background:rgba(24,184,159,.16);border:1px solid rgba(24,184,159,.45);color:#DDF5EB;border-radius:20px;padding:3px 10px;font-size:11px;animation:f .4s ease both}"
            ".c b{color:#18B89F;font-weight:600;margin-right:3px}.z{color:#9FC9C1;font-size:11px}"
            "@keyframes f{from{opacity:0}to{opacity:1}}</style>")
mi("HTML Chips Filtros", "11 SVG & HTML", "VAR _c = " + "\n    & ".join(chip(c, r) for c, r in CHIPS) +
   f'\nRETURN "{CSS_CHIP}<div class=\'w\'>" & IF ( _c = "", "<span class=\'z\'>Sem filtros ativos · período completo 01/10/2024 a 30/09/2026</span>", _c ) & "</div>"',
   "Chips HTML com os filtros ativos (inclusive os do painel oculto).")

# ---------------------------------------------------------------- narrativa HTML
CSS_N = ("<style>.n{font-family:Segoe UI,sans-serif;color:#E8F3F1;height:100%;display:flex;flex-direction:column;animation:f .6s ease both}"
         ".h{font-size:13px;font-weight:600;color:#18B89F;letter-spacing:.3px;margin-bottom:8px}"
         ".h:before{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:#18B89F;box-shadow:0 0 10px #18B89F;margin-right:8px}"
         ".p{font-size:13.5px;line-height:1.55}.ft{margin-top:auto;font-size:10.5px;color:#9FC9C1;border-top:1px solid rgba(255,255,255,.08);padding-top:6px}"
         "@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style>")
for p in ["Executiva", "Clientes", "Produtos", "Compras", "Estoque", "Financeiro", "Forecast"]:
    mi(f"HTML Narrativa {p}", "09 Narrativas",
       f'"{CSS_N}<div class=\'n\'><div class=\'h\'>Leitura automática</div><div class=\'p\'>" & [Narrativa {p}] & "</div><div class=\'ft\'>Fato derivado dos filtros atuais · hipótese e ação a validar · não indica causa</div></div>"')

# ---------------------------------------------------------------- tooltip HTML
mi("HTML Tooltip Receita", "11 SVG & HTML", f"""
VAR _r = [Receita Líquida]
VAR _y = [Receita YoY %]
VAR _c = IF ( ISBLANK ( _y ), "{NEU}", IF ( _y >= 0, "{OK}", "{BAD}" ) )
RETURN "<style>.tt{{font-family:Segoe UI,sans-serif;color:#E8F3F1;padding:4px}}.tt .l{{font-size:11px;color:#9FC9C1}}.tt .b{{font-size:22px;font-weight:600}}.tt .r{{display:flex;gap:18px;margin-top:8px}}.tt .s{{font-size:10px;color:#9FC9C1;margin-top:10px;border-top:1px solid rgba(255,255,255,.1);padding-top:6px}}</style>"
    & "<div class='tt'><div class='l'>Receita líquida</div><div class='b'>" & {fmt("brl", "_r")} & "</div>"
    & "<div class='r'><div><div class='l'>Margem bruta</div><b>" & FORMAT ( [Margem Bruta %], "0.0%", "pt-BR" ) & "</b></div>"
    & "<div><div class='l'>Participação</div><b>" & FORMAT ( [Share Receita %], "0.0%", "pt-BR" ) & "</b></div>"
    & "<div><div class='l'>vs ano anterior</div><b style='color:" & _c & "'>" & IF ( ISBLANK ( _y ), "s/ base", FORMAT ( _y, "+0.0%;-0.0%", "pt-BR" ) ) & "</b></div></div>"
    & "<div class='s'>Receita = bruto − descontos (f_vendas). Variação só com período comparável.</div></div>" """)

# ---------------------------------------------------------------- cards por página
P = {}
P["Home"] = [dict(t="Farmácias", v="Qtd Lojas", f="int", sub="Campinas · Jundiaí · Sorocaba · Piracicaba"),
             dict(t="SKUs no catálogo", v="SKUs no Catálogo", f="int", sub="5 categorias"),
             dict(t="Clientes cadastrados", v="Clientes Cadastrados", f="int", sub="IDs sintéticos"),
             dict(t="Vendas (cupons)", v="Cupons", f="int", sp="Cupons", sub="24 meses"),
             dict(t="Receita líquida", v="Receita Líquida", f="brl", sp="Receita Líquida", sub="out/24 – set/26")]
P["Executiva"] = [dict(t="Receita líquida", v="Receita Líquida", f="brl", var="Receita YoY %", sp="Receita Líquida"),
                  dict(t="Lucro bruto", v="Lucro Bruto", f="brl", var="Lucro Bruto YoY %", sp="Lucro Bruto"),
                  dict(t="Margem bruta", v="Margem Bruta %", f="pct", var="Margem Bruta Var pp", vk="pp", sp="Margem Bruta %"),
                  dict(t="Resultado op. simplificado", v="Resultado Operacional Simplificado", f="brl", var="Txt ROS Margem", vk="txt", cor="Cor Margem Op", sp="Resultado Operacional Simplificado"),
                  dict(t="Atingimento da meta", v="Atingimento Meta %", f="pct", var="Txt Atingimento", vk="txt", cor="Cor Atingimento", sp="Atingimento Meta %"),
                  dict(t="Ticket médio", v="Ticket Médio", f="brl2", var="Ticket Médio YoY %", sp="Ticket Médio")]
P["Clientes"] = [dict(t="Cupons", v="Cupons", f="int", var="Cupons YoY %", sp="Cupons"),
                 dict(t="Clientes ativos", v="Clientes Ativos", f="int", var="Clientes Ativos YoY %", sp="Clientes Ativos"),
                 dict(t="Clientes novos", v="Clientes Novos", f="int", var="Txt Novos", vk="txt", sp="Clientes Novos"),
                 dict(t="Frequência (cupons/cliente)", v="Frequência Média", f="dec", sp="Frequência Média", sub="cupons por cliente identificado"),
                 dict(t="Ticket médio", v="Ticket Médio", f="brl2", var="Ticket Médio YoY %", sp="Ticket Médio"),
                 dict(t="Cupons identificados", v="% Cupons Identificados", f="pct", sp="% Cupons Identificados", sub="cupom anônimo não é cliente")]
P["Produtos"] = [dict(t="Receita líquida (itens)", v="Receita Líquida Itens", f="brl", var="Receita Itens YoY %", sp="Receita Líquida Itens"),
                 dict(t="Lucro bruto (itens)", v="Lucro Bruto Itens", f="brl", sp="Lucro Bruto Itens", sub="receita − CMV de itens"),
                 dict(t="Margem bruta (itens)", v="Margem Bruta Itens %", f="pct", var="Margem Itens Var pp", vk="pp", sp="Margem Bruta Itens %"),
                 dict(t="Desconto sobre bruto", v="Desconto Itens %", f="pct", var=None, sp="Desconto Itens %", sub="quanto menor, melhor", cor="Txt Neutro"),
                 dict(t="SKUs com venda", v="SKUs Vendidos", f="int", var="Txt SKUs", vk="txt", sp="SKUs Vendidos"),
                 dict(t="Preço médio por unidade", v="Preço Médio Unitário", f="brl2", sp="Preço Médio Unitário", sub="receita / unidades")]
P["Compras"] = [dict(t="Compras recebidas", v="Valor Recebido", f="brl", var="Txt Orçamento", vk="txt", sp="Valor Recebido"),
                dict(t="Recebimentos", v="Recebimentos", f="int", sp="Recebimentos", sub="entregas registradas"),
                dict(t="Lead time médio", v="Lead Time Médio", f="dias1", var="Txt Pontualidade", vk="txt", sp="Lead Time Médio"),
                dict(t="Pontualidade (OTD)", v="Pontualidade %", f="pct", var="Txt Pontualidade Meta", vk="txt", cor="Cor Pontualidade", sp="Pontualidade %"),
                dict(t="Atraso médio quando atrasa", v="Atraso Médio", f="dias1", sp="Atraso Médio", sub="só entregas atrasadas", cor="Cor Pontualidade"),
                dict(t="Concentração top 5", v="Concentração Top 5 %", f="pct", sub="fornecedores por valor")]
P["Estoque"] = [dict(t="Estoque final (custo)", v="Estoque Final (R$)", f="brl", var="Txt Cobertura", vk="txt", cor="Cor Cobertura", sp="Estoque Final (R$)"),
                dict(t="Estoque final (unidades)", v="Estoque Final (un)", f="int", sp="Estoque Final (un)", sub="saldo no fim do período", cor="Cor Cobertura"),
                dict(t="Cobertura estimada", v="Cobertura (dias)", f="dias", var="Txt Cobertura Dias", vk="txt", cor="Cor Cobertura", sp="Cobertura (dias)"),
                dict(t="Giro anualizado", v="Giro Anualizado", f="x", var="Txt Giro", vk="txt", cor="Cor Cobertura"),
                dict(t="Perdas (custo)", v="Perdas (R$)", f="brl", var="Txt Perdas", vk="txt", cor="Cor Perdas", sp="Perdas (R$)"),
                dict(t="Risco de validade", v="Valor em Risco Validade (R$)", f="brl", var="Txt Validade", vk="txt", cor="Cor Validade")]
P["Financeiro"] = [dict(t="Receita líquida", v="Receita Líquida", f="brl", var="Receita YoY %", sp="Receita Líquida"),
                   dict(t="Lucro bruto", v="Lucro Bruto", f="brl", var="Lucro Bruto YoY %", sp="Lucro Bruto"),
                   dict(t="Despesas modeladas", v="Despesas", f="brl", sp="Despesas", sub="pessoal, aluguel, operação, marketing", cor="Txt Neutro"),
                   dict(t="Resultado op. simplificado", v="Resultado Operacional Simplificado", f="brl", var="Resultado Op Simplificado YoY %", sp="Resultado Operacional Simplificado"),
                   dict(t="Margem op. simplificada", v="Margem Operacional Simplificada %", f="pct", var="Txt Margem Op", vk="txt", cor="Cor Margem Op", sp="Margem Operacional Simplificada %"),
                   dict(t="Atingimento meta de lucro", v="Atingimento Lucro Bruto %", f="pct", sp="Atingimento Lucro Bruto %", sub="lucro bruto / meta", cor="Cor Atingimento")]
P["Forecast"] = [dict(t="Receita prevista · 6 meses", v="Receita Prevista Cenário", f="brl", var="Txt Forecast Intervalo", vk="txt"),
                 dict(t="Lucro bruto previsto", v="Lucro Bruto Previsto Cenário", f="brl", sub="premissa: CMV% últimos 12m × fator"),
                 dict(t="Crescimento vs LY", v="Crescimento Previsto vs LY %", f="pct", sub="mesmos meses do ano anterior"),
                 dict(t="WAPE do backtest", v="WAPE Backtest %", f="pct", var="Txt WAPE", vk="txt", cor="Cor WAPE"),
                 dict(t="Viés do backtest", v="Viés Backtest %", f="pct", sub="+ = superestima", cor="Txt Neutro"),
                 dict(t="Cenário ativo", v="Cenário Ativo", f="txt", sub="Conservador · Base · Otimista")]
# Txt Neutro devolve o hex neutro: reaproveitado como cor
for k, cards in P.items():
    html_cards(f"HTML KPIs {k}", "11 SVG & HTML", cards)
