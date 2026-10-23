# -*- coding: utf-8 -*-
"""Gera o modelo semântico TMDL da FarmaVitta (FarmaVitta.SemanticModel)."""
import os, uuid

NS = uuid.UUID("6f3b0e2a-9d1c-4c55-9a77-1f0a2b3c4d5e")
def tag(*k): return str(uuid.uuid5(NS, "|".join(k)))
def q(n):  # nome TMDL
    return n if n.replace("_", "").isalnum() and not n[0].isdigit() else "'" + n.replace("'", "''") + "'"

ORIG = "01_Dados_Originais\\base_original\\"
COMP = "01_Dados_Originais\\base_complementar\\"
TRAT = "02_Dados_Tratados\\"

# ---------------------------------------------------------------- tabelas
# coluna: (nome_modelo, sourceColumn, dataType, opções)
def col(n, s=None, t="string", **o): return dict(n=n, s=s or n, t=t, **o)

M_TIPOS = {"string": "type text", "int64": "Int64.Type", "double": "type number", "dateTime": "type date", "boolean": "type logical"}

def m_csv(path, cols, extra_steps="", keep=None):
    """Lê CSV via fnCsv, tipa (cultura en-US), executa passos extras e seleciona colunas finais."""
    tipos = ", ".join('{"%s", %s}' % (c["s"], M_TIPOS[c["t"]]) for c in cols if not c.get("calc"))
    sel = ", ".join('"%s"' % c["s"] for c in cols)
    return f'''let
    Fonte = fnCsv("{path}"),
    Tipado = Table.TransformColumnTypes(Fonte, {{{tipos}}}, "en-US"){extra_steps}
    Final = Table.SelectColumns(Ultimo, {{{sel}}})
in
    Final'''

T = {}  # nome -> dict(cols, m, opts)

T["dCalendario"] = dict(desc="Calendário diário 01/10/2024–31/03/2027 (inclui horizonte de previsão). Dia útil vem de dim_calendario; datas futuras: seg–sex.",
    dataCategory="Time",
    cols=[col("Data", t="dateTime", key=True, fmt="dd/MM/yyyy"),
          col("Ano", t="int64"), col("Mes Num", t="int64", hidden=True), col("Mes Nome", sort="Mes Num"),
          col("Mes Ano", sort="AnoMes Num"), col("AnoMes Num", t="int64", hidden=True), col("Ano Mes"),
          col("Trimestre"), col("Dia Semana Num", t="int64", hidden=True), col("Dia Semana", sort="Dia Semana Num"),
          col("Dia Util", t="boolean"), col("Inicio Mes", t="dateTime", fmt="dd/MM/yyyy"), col("Periodo")],
    m=f'''let
    Inicio = #date(2024, 10, 1),
    Fim = #date(2027, 3, 31),
    Datas = List.Dates(Inicio, Duration.Days(Fim - Inicio) + 1, #duration(1, 0, 0, 0)),
    Base = Table.FromList(Datas, Splitter.SplitByNothing(), type table [Data = date]),
    Meses = {{"jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"}},
    Dias = {{"dom","seg","ter","qua","qui","sex","sáb"}},
    Ano = Table.AddColumn(Base, "Ano", each Date.Year([Data]), Int64.Type),
    MesNum = Table.AddColumn(Ano, "Mes Num", each Date.Month([Data]), Int64.Type),
    MesNome = Table.AddColumn(MesNum, "Mes Nome", each Meses{{[Mes Num] - 1}}, type text),
    MesAno = Table.AddColumn(MesNome, "Mes Ano", each [Mes Nome] & "/" & Text.End(Text.From([Ano]), 2), type text),
    AnoMesNum = Table.AddColumn(MesAno, "AnoMes Num", each [Ano] * 100 + [Mes Num], Int64.Type),
    AnoMes = Table.AddColumn(AnoMesNum, "Ano Mes", each Text.From([Ano]) & "-" & Text.PadStart(Text.From([Mes Num]), 2, "0"), type text),
    Tri = Table.AddColumn(AnoMes, "Trimestre", each "T" & Text.From(Date.QuarterOfYear([Data])), type text),
    DiaNum = Table.AddColumn(Tri, "Dia Semana Num", each Date.DayOfWeek([Data], Day.Sunday), Int64.Type),
    DiaNome = Table.AddColumn(DiaNum, "Dia Semana", each Dias{{[Dia Semana Num]}}, type text),
    Csv = Table.TransformColumnTypes(fnCsv("{ORIG}dim_calendario.csv"), {{{{"data", type date}}, {{"dia_util", Int64.Type}}}}, "en-US"),
    Junta = Table.NestedJoin(DiaNome, "Data", Csv, "data", "c", JoinKind.LeftOuter),
    Exp = Table.ExpandTableColumn(Junta, "c", {{"dia_util"}}),
    DiaUtil = Table.AddColumn(Exp, "Dia Util", each if [dia_util] <> null then [dia_util] = 1 else [Dia Semana Num] >= 1 and [Dia Semana Num] <= 5, type logical),
    IniMes = Table.AddColumn(DiaUtil, "Inicio Mes", each Date.StartOfMonth([Data]), type date),
    Periodo = Table.AddColumn(IniMes, "Periodo", each if [Data] <= #date(2026, 9, 30) then "Realizado" else "Projeção", type text),
    Final = Table.SelectColumns(Periodo, {{"Data","Ano","Mes Num","Mes Nome","Mes Ano","AnoMes Num","Ano Mes","Trimestre","Dia Semana Num","Dia Semana","Dia Util","Inicio Mes","Periodo"}})
in
    Final''')

c = [col("id_loja", hidden=True, key=True), col("Loja", "nome_loja"), col("Loja Curta", calc=True), col("Cidade", "cidade"), col("UF", "uf"),
     col("Data Abertura", "data_abertura", "dateTime", fmt="dd/MM/yyyy"), col("Indice Demanda", "indice_demanda", "double", fmt="0.00")]
T["dLoja"] = dict(desc="Lojas (4).", cols=c, m=m_csv(ORIG + "dim_lojas.csv", c, ''',
    Curta = Table.AddColumn(Tipado, "Loja Curta", each [cidade], type text),
    Ultimo = Curta,'''))

c = [col("id_produto", hidden=True, key=True), col("Produto", "nome_produto"), col("Categoria", "categoria"), col("Subcategoria", "subcategoria"),
     col("Marca", "marca"), col("Preco Lista Ref", "preco_lista_referencia", "double", fmt=r"\R\$ #,0.00"),
     col("Custo Ref", "custo_unitario_referencia", "double", fmt=r"\R\$ #,0.00"),
     col("Generico", "eh_generico"), col("Controlado", "eh_controlado"), col("Exige Receita", "exige_receita"), col("Status", "status"),
     col("id_fornecedor", hidden=True), col("Classe ABC", "classe_abc"), col("Rank Receita", "rank_receita", "int64")]
T["dProduto"] = dict(desc="SKUs (5.000) com fornecedor único (ponte 1:1 validada no GATE A) e Classe ABC estática do período completo.",
    cols=c, m=f'''let
    Fonte = fnCsv("{ORIG}dim_produtos.csv"),
    Tipado = Table.TransformColumnTypes(Fonte, {{{{"preco_lista_referencia", type number}}, {{"custo_unitario_referencia", type number}}}}, "en-US"),
    SimNao = Table.TransformColumns(Tipado, {{{{"eh_generico", each if _ = "1" then "Sim" else "Não", type text}}, {{"eh_controlado", each if _ = "1" then "Sim" else "Não", type text}}, {{"exige_receita", each if _ = "1" then "Sim" else "Não", type text}}}}),
    Ponte = fnCsv("{ORIG}ponte_produto_fornecedor.csv"),
    J1 = Table.NestedJoin(SimNao, "id_produto", Ponte, "id_produto", "p", JoinKind.LeftOuter),
    E1 = Table.ExpandTableColumn(J1, "p", {{"id_fornecedor"}}),
    Abc = Table.TransformColumnTypes(fnCsv("{TRAT}d_produto_abc.csv"), {{{{"rank_receita", Int64.Type}}}}, "en-US"),
    J2 = Table.NestedJoin(E1, "id_produto", Abc, "id_produto", "a", JoinKind.LeftOuter),
    E2 = Table.ExpandTableColumn(J2, "a", {{"classe_abc", "rank_receita"}}),
    Final = Table.SelectColumns(E2, {{{", ".join('"%s"' % x["s"] for x in c)}}})
in
    Final''')

c = [col("id_fornecedor", hidden=True, key=True), col("Fornecedor", "razao_social_ficticia"), col("UF Fornecedor", "uf"),
     col("Prazo Medio Dias", "prazo_medio_dias", "int64")]
T["dFornecedor"] = dict(desc="Fornecedores fictícios (60). Filtra fatos via dProduto (snowflake 1:N).", cols=c,
    m=m_csv(ORIG + "dim_fornecedores.csv", c, ''',
    Ultimo = Tipado,'''))

c = [col("id_cliente", hidden=True, key=True), col("Cidade Cadastro", "cidade_cadastro"), col("Data Cadastro", "data_cadastro", "dateTime", fmt="dd/MM/yyyy"),
     col("Segmento Cadastro", "segmento_cadastro"), col("Faixa Etaria", "faixa_etaria"), col("Tipo Cliente"),
     col("Segmento RFV", "segmento_rfv", sort="Ordem RFV"), col("Ordem RFV", "ordem_segmento", "int64", hidden=True),
     col("Recencia Dias", "recencia_dias", "int64"), col("Frequencia RFV", "frequencia", "int64"), col("Valor RFV", "valor", "double", fmt=r"\R\$ #,0.00"),
     col("Score R", "score_r", "int64"), col("Score F", "score_f", "int64"), col("Score V", "score_v", "int64"),
     col("Data Primeira Compra", "data_primeira_compra", "dateTime", fmt="dd/MM/yyyy")]
T["dCliente"] = dict(desc="Clientes sintéticos (22.000) + membro 'NI' para cupons anônimos. RFV é fotografia em 30/09/2026.", cols=c,
    m=f'''let
    Fonte = Table.TransformColumnTypes(fnCsv("{ORIG}dim_clientes.csv"), {{{{"data_cadastro", type date}}}}, "en-US"),
    Rfv = Table.TransformColumnTypes(fnCsv("{TRAT}d_cliente_rfv.csv"), {{{{"recencia_dias", Int64.Type}}, {{"frequencia", Int64.Type}}, {{"valor", type number}}, {{"score_r", Int64.Type}}, {{"score_f", Int64.Type}}, {{"score_v", Int64.Type}}, {{"ordem_segmento", Int64.Type}}, {{"data_primeira_compra", type date}}}}, "en-US"),
    J = Table.NestedJoin(Fonte, "id_cliente", Rfv, "id_cliente", "r", JoinKind.LeftOuter),
    E = Table.ExpandTableColumn(J, "r", {{"recencia_dias","frequencia","valor","score_r","score_f","score_v","segmento_rfv","ordem_segmento","data_primeira_compra"}}),
    SemCompra = Table.TransformColumns(E, {{{{"segmento_rfv", each if _ = null then "Sem compra" else _, type text}}, {{"ordem_segmento", each if _ = null then 7 else _, Int64.Type}}}}),
    Tipo = Table.AddColumn(SemCompra, "Tipo Cliente", each "Identificado", type text),
    NI = #table(Table.ColumnNames(Tipo), {{List.Transform(Table.ColumnNames(Tipo), each if _ = "id_cliente" then "NI" else if _ = "Tipo Cliente" then "Não identificado" else if _ = "segmento_rfv" then "Não identificado" else if _ = "ordem_segmento" then 8 else if List.Contains({{"cidade_cadastro","segmento_cadastro","faixa_etaria"}}, _) then "Não identificado" else null)}}),
    Uniao = Table.Combine({{Tipo, NI}}),
    Tipos = Table.TransformColumnTypes(Uniao, {{{{"ordem_segmento", Int64.Type}}, {{"recencia_dias", Int64.Type}}, {{"frequencia", Int64.Type}}, {{"valor", type number}}, {{"score_r", Int64.Type}}, {{"score_f", Int64.Type}}, {{"score_v", Int64.Type}}, {{"data_primeira_compra", type date}}, {{"data_cadastro", type date}}}}),
    Final = Table.SelectColumns(Tipos, {{{", ".join('"%s"' % x["s"] for x in c)}}})
in
    Final''')

T["dCanal"] = dict(desc="Canais de venda (estático, validado no GATE A).",
    cols=[col("Canal", key=True), col("Ordem Canal", t="int64", hidden=True)],
    m='''let
    Fonte = #table(type table [Canal = text, Ordem Canal = Int64.Type], {{"Loja física", 1}, {"Aplicativo", 2}, {"Site", 3}, {"Delivery", 4}})
in
    Fonte''')
T["dCanal"]["cols"][0]["sort"] = "Ordem Canal"

c = [col("id_venda", hidden=True), col("data_venda", t="dateTime", hidden=True, fmt="dd/MM/yyyy"), col("id_loja", hidden=True),
     col("id_cliente", hidden=True), col("canal", hidden=True), col("Forma Pagamento", "forma_pagamento"),
     col("qtd_itens_distintos", t="int64", hidden=True), col("valor_bruto", t="double", hidden=True), col("valor_desconto", t="double", hidden=True),
     col("valor_liquido", t="double", hidden=True), col("custo_mercadoria", t="double", hidden=True),
     col("cliente_identificado", t="boolean", hidden=True, calc=True), col("primeira_compra", t="boolean", hidden=True, calc=True)]
T["fVendas"] = dict(desc="Fato cupom (1 linha por venda). Fonte oficial de receita, desconto e CMV da rede.", cols=c,
    m=m_csv(ORIG + "f_vendas.csv", c, f''',
    Anon = Table.ReplaceValue(Tipado, "", "NI", Replacer.ReplaceValue, {{"id_cliente"}}),
    Ident = Table.AddColumn(Anon, "cliente_identificado", each [id_cliente] <> "NI", type logical),
    Rfv = Table.TransformColumnTypes(Table.SelectColumns(fnCsv("{TRAT}d_cliente_rfv.csv"), {{"id_cliente", "data_primeira_compra"}}), {{{{"data_primeira_compra", type date}}}}, "en-US"),
    J = Table.NestedJoin(Ident, "id_cliente", Rfv, "id_cliente", "r", JoinKind.LeftOuter),
    E = Table.ExpandTableColumn(J, "r", {{"data_primeira_compra"}}),
    Primeira = Table.AddColumn(E, "primeira_compra", each [data_primeira_compra] <> null and [data_venda] = [data_primeira_compra], type logical),
    Ultimo = Primeira,'''))

c = [col("id_item", hidden=True), col("id_venda", hidden=True), col("id_loja", hidden=True), col("id_produto", hidden=True),
     col("data_venda", t="dateTime", hidden=True, fmt="dd/MM/yyyy"), col("quantidade", t="int64", hidden=True),
     col("preco_unitario_bruto", t="double", hidden=True), col("taxa_desconto", t="double", hidden=True), col("valor_desconto", t="double", hidden=True),
     col("valor_liquido", t="double", hidden=True), col("custo_total", t="double", hidden=True),
     col("canal", hidden=True, calc=True), col("id_cliente", hidden=True, calc=True)]
T["fItensVenda"] = dict(desc="Fato item de cupom. Fonte de receita/margem por produto. Canal e cliente herdados do cupom no Power Query (sem relação fato–fato).", cols=c,
    m=m_csv(ORIG + "f_itens_venda.csv", c, f''',
    Cupom = Table.Buffer(Table.SelectColumns(fnCsv("{ORIG}f_vendas.csv"), {{"id_venda", "canal", "id_cliente"}})),
    J = Table.NestedJoin(Tipado, "id_venda", Cupom, "id_venda", "v", JoinKind.LeftOuter),
    E = Table.ExpandTableColumn(J, "v", {{"canal", "id_cliente"}}),
    Anon = Table.ReplaceValue(E, "", "NI", Replacer.ReplaceValue, {{"id_cliente"}}),
    Ultimo = Anon,'''))

def mensal(path, cols, passo=""):
    return m_csv(path, cols, f''',
    DataMes = Table.AddColumn(Tipado, "data_mes", each Date.FromText([ano_mes] & "-01"), type date),{passo}
    Ultimo = {"Passo2" if passo else "DataMes"},''')

c = [col("ano_mes", hidden=True), col("data_mes", t="dateTime", hidden=True, calc=True, fmt="dd/MM/yyyy"), col("id_loja", hidden=True), col("id_produto", hidden=True),
     col("saldo_inicial", t="int64", hidden=True), col("qtd_entradas", t="int64", hidden=True), col("qtd_vendida", t="int64", hidden=True),
     col("qtd_perdas", t="int64", hidden=True), col("saldo_final", t="int64", hidden=True), col("custo_unitario", t="double", hidden=True),
     col("valor_saldo_final", t="double", hidden=True), col("valor_perdas", t="double", hidden=True), col("teve_movimento", t="int64", hidden=True),
     col("venda_media_3m", t="double", hidden=True), col("Meses Sem Venda", "meses_sem_venda", "int64"), col("cobertura_dias", t="double", hidden=True),
     col("Status Estoque", "status_estoque")]
T["fEstoque"] = dict(desc="Saldo de estoque reconstruído (grade completa loja×SKU×mês, 02_Dados_Tratados). Semiaditivo: usar medidas de snapshot.", cols=c,
    m=mensal(TRAT + "f_estoque_saldo_mensal.csv", c))

c = [col("ano_mes", hidden=True), col("data_mes", t="dateTime", hidden=True, calc=True, fmt="dd/MM/yyyy"), col("id_loja", hidden=True),
     col("meta_receita", t="double", hidden=True), col("meta_lucro_bruto", t="double", hidden=True)]
T["fMetas"] = dict(desc="Metas mensais por loja.", cols=c, m=mensal(ORIG + "f_metas_mensais.csv", c))

c = [col("ano_mes", hidden=True), col("data_mes", t="dateTime", hidden=True, calc=True, fmt="dd/MM/yyyy"), col("id_loja", hidden=True),
     col("aluguel", t="double", hidden=True), col("pessoal", t="double", hidden=True), col("operacionais", t="double", hidden=True),
     col("marketing_canais", t="double", hidden=True), col("despesa_total", t="double", hidden=True)]
T["fDespesas"] = dict(desc="Despesas operacionais mensais por loja (rubricas modeladas; não inclui impostos/depreciação).", cols=c,
    m=mensal(ORIG + "f_despesas_mensais.csv", c))

c = [col("id_recebimento", hidden=True), col("data_recebimento", t="dateTime", hidden=True, fmt="dd/MM/yyyy"), col("id_loja", hidden=True),
     col("id_produto", hidden=True), col("id_fornecedor", hidden=True), col("quantidade_recebida", t="int64", hidden=True),
     col("custo_unitario", t="double", hidden=True), col("valor_recebido", t="double", hidden=True), col("prazo_previsto_dias", t="int64", hidden=True),
     col("prazo_real_dias", t="int64", hidden=True), col("entrega_no_prazo", t="int64", hidden=True), col("atraso_dias", t="int64", hidden=True, calc=True)]
T["fRecebimentos"] = dict(desc="Recebimentos de compras (base complementar), conciliados com entradas do estoque. Não representa pedidos emitidos.", cols=c,
    m=m_csv(COMP + "f_recebimentos_compras.csv", c, ''',
    Atraso = Table.AddColumn(Tipado, "atraso_dias", each List.Max({0, [prazo_real_dias] - [prazo_previsto_dias]}), Int64.Type),
    Ultimo = Atraso,'''))

c = [col("ano_mes", hidden=True), col("data_mes", t="dateTime", hidden=True, calc=True, fmt="dd/MM/yyyy"), col("id_loja", hidden=True),
     col("orcamento_compras", t="double", hidden=True)]
T["fOrcamentoCompras"] = dict(desc="Orçamento sintético de compras por loja/mês.", cols=c, m=mensal(COMP + "f_orcamento_compras.csv", c))

c = [col("id_lote", hidden=True), col("id_loja", hidden=True), col("id_produto", hidden=True), col("quantidade_lote", t="int64", hidden=True),
     col("Data Validade", "data_validade_simulada", "dateTime", fmt="dd/MM/yyyy"), col("Faixa Validade", "faixa_validade", sort="Ordem Faixa"),
     col("custo_unitario_referencia", t="double", hidden=True), col("valor_lote", t="double", hidden=True, calc=True),
     col("Ordem Faixa", t="int64", hidden=True, calc=True)]
T["fLotes"] = dict(desc="Fotografia de lotes em 30/09/2026 (simulada). Não é histórico: sem relação com calendário.", cols=c,
    m=m_csv(COMP + "f_lotes_estoque_foto.csv", c, ''',
    Valor = Table.AddColumn(Tipado, "valor_lote", each [quantidade_lote] * [custo_unitario_referencia], type number),
    Ordem = Table.AddColumn(Valor, "Ordem Faixa", each if [faixa_validade] = "Vencido" then 1 else if [faixa_validade] = "Até 90 dias" then 2 else if [faixa_validade] = "91-180 dias" then 3 else 4, Int64.Type),
    Ultimo = Ordem,'''))

c = [col("ano_mes", hidden=True), col("data_mes", t="dateTime", hidden=True, calc=True, fmt="dd/MM/yyyy"), col("id_loja", hidden=True),
     col("Tipo Serie", "tipo"), col("Metodo", "metodo"), col("valor_real", t="double", hidden=True), col("previsao", t="double", hidden=True),
     col("limite_inferior", t="double", hidden=True), col("limite_superior", t="double", hidden=True), col("wape_backtest", t="double", hidden=True)]
T["fForecast"] = dict(desc="Previsão de receita mensal por loja (6 meses, v1.0, treino até 30/09/2026). Projeção não é meta nem fato.", cols=c,
    m=mensal(TRAT + "f_forecast_receita.csv", c))

c = [col("origem", hidden=True), col("ano_mes_alvo", hidden=True), col("Horizonte", "horizonte", "int64"), col("id_loja", hidden=True),
     col("Metodo", "metodo"), col("real", t="double", hidden=True), col("previsto", t="double", hidden=True), col("erro_abs", t="double", hidden=True),
     col("erro_pct", t="double", hidden=True), col("metodo_selecionado", t="int64", hidden=True)]
T["fBacktest"] = dict(desc="Backtest rolling-origin (h=1..3) dos métodos de previsão.", cols=c, m=m_csv(TRAT + "f_forecast_backtest.csv", c, ''',
    Ultimo = Tipado,'''))

c = [col("id_cenario", hidden=True), col("Cenario", "cenario", sort="id_cenario"), col("Fator Receita", "fator_receita", "double", fmt="0.00"),
     col("Fator Custo", "fator_custo", "double", fmt="0.00"), col("Descricao Cenario", "descricao")]
T["dCenario"] = dict(desc="Cenários what-if (desconectada). Fatores aplicados sobre a previsão; não são modelo preditivo.", cols=c,
    m=m_csv(COMP + "d_cenarios_previsao.csv", c, ''',
    Ultimo = Tipado,'''))

T["dDRE"] = dict(desc="Linhas da DRE gerencial simplificada (desconectada).",
    cols=[col("Ordem DRE", t="int64", hidden=True), col("Linha DRE", sort="Ordem DRE"), col("Tipo Linha")],
    m='''let
    Fonte = #table(type table [Ordem DRE = Int64.Type, Linha DRE = text, Tipo Linha = text], {
        {1, "Receita bruta", "Item"}, {2, "(−) Descontos", "Item"}, {3, "Receita líquida", "Subtotal"},
        {4, "(−) CMV", "Item"}, {5, "Lucro bruto", "Subtotal"}, {6, "(−) Pessoal", "Item"}, {7, "(−) Aluguel", "Item"},
        {8, "(−) Operacionais", "Item"}, {9, "(−) Marketing e canais", "Item"}, {10, "Resultado operacional simplificado", "Total"}})
in
    Fonte''')

T["_Medidas"] = dict(desc="Tabela de medidas.", cols=[col("_", hidden=True)],
    m='''let
    Fonte = #table(type table [_ = text], {})
in
    Fonte''')

REL = [  # (fromTable, fromCol, toTable, toCol, active)
    ("fVendas", "data_venda", "dCalendario", "Data"), ("fItensVenda", "data_venda", "dCalendario", "Data"),
    ("fEstoque", "data_mes", "dCalendario", "Data"), ("fMetas", "data_mes", "dCalendario", "Data"),
    ("fDespesas", "data_mes", "dCalendario", "Data"), ("fRecebimentos", "data_recebimento", "dCalendario", "Data"),
    ("fOrcamentoCompras", "data_mes", "dCalendario", "Data"), ("fForecast", "data_mes", "dCalendario", "Data"),
    ("fVendas", "id_loja", "dLoja", "id_loja"), ("fItensVenda", "id_loja", "dLoja", "id_loja"), ("fEstoque", "id_loja", "dLoja", "id_loja"),
    ("fMetas", "id_loja", "dLoja", "id_loja"), ("fDespesas", "id_loja", "dLoja", "id_loja"), ("fRecebimentos", "id_loja", "dLoja", "id_loja"),
    ("fOrcamentoCompras", "id_loja", "dLoja", "id_loja"), ("fLotes", "id_loja", "dLoja", "id_loja"), ("fForecast", "id_loja", "dLoja", "id_loja"),
    ("fBacktest", "id_loja", "dLoja", "id_loja"),
    ("fItensVenda", "id_produto", "dProduto", "id_produto"), ("fEstoque", "id_produto", "dProduto", "id_produto"),
    ("fRecebimentos", "id_produto", "dProduto", "id_produto"), ("fLotes", "id_produto", "dProduto", "id_produto"),
    ("dProduto", "id_fornecedor", "dFornecedor", "id_fornecedor"),
    ("fVendas", "id_cliente", "dCliente", "id_cliente"), ("fItensVenda", "id_cliente", "dCliente", "id_cliente"),
    ("fVendas", "canal", "dCanal", "Canal"), ("fItensVenda", "canal", "dCanal", "Canal"),
]

# ---------------------------------------------------------------- medidas
BRL = r"\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00"
BRL0 = r"\R\$ #,0;-\R\$ #,0;\R\$ #,0"
PCT = "0.0%;-0.0%;0.0%"
INT = "#,0"
DEC1 = "#,0.0"
DEC2 = "#,0.00"
PP = '+0.0 "p.p.";-0.0 "p.p.";0.0 "p.p."'
DIAS = '#,0 "dias"'
GIRO = '0.0"x"'
DB = "DATE(2026, 9, 30)"

MED = []
def m(nome, pasta, fmt, dax, desc=""): MED.append(dict(n=nome, f=pasta, fmt=fmt, dax=dax.strip(), d=desc))

# 00 Base
m("Receita Bruta", "00 Base", BRL, "SUM ( fVendas[valor_bruto] )", "Soma do valor bruto dos cupons (f_vendas).")
m("Descontos", "00 Base", BRL, "SUM ( fVendas[valor_desconto] )")
m("Receita Líquida", "00 Base", BRL, "SUM ( fVendas[valor_liquido] )", "Receita líquida oficial da rede (f_vendas). Não somar com itens.")
m("CMV", "00 Base", BRL, "SUM ( fVendas[custo_mercadoria] )", "Custo da mercadoria vendida (f_vendas).")
m("Cupons", "00 Base", INT, "COUNTROWS ( fVendas )", "Número de cupons (vendas). id_venda é único (GATE A).")
m("Unidades Vendidas", "00 Base", INT, "SUM ( fItensVenda[quantidade] )")
m("Qtd Lojas", "00 Base", INT, "COUNTROWS ( dLoja )")
m("Clientes Cadastrados", "00 Base", INT, "CALCULATE ( COUNTROWS ( dCliente ), dCliente[id_cliente] <> \"NI\" )")
m("Despesas", "00 Base", BRL, "IF ( NOT [_Filtro Sem Despesa], SUM ( fDespesas[despesa_total] ) )", "Despesas modeladas (loja/mês). Em branco quando filtrado por produto, canal, cliente ou fornecedor.")
m("Meta Receita", "00 Base", BRL, "IF ( NOT [_Filtro Sem Despesa], SUM ( fMetas[meta_receita] ) )")
m("Meta Lucro Bruto", "00 Base", BRL, "IF ( NOT [_Filtro Sem Despesa], SUM ( fMetas[meta_lucro_bruto] ) )")
m("_Filtro Sem Despesa", "99 Auditoria", "", "ISFILTERED ( dProduto ) || ISFILTERED ( dCanal ) || ISFILTERED ( dCliente ) || ISFILTERED ( dFornecedor )",
  "Verdadeiro quando há filtro em dimensão que não existe nas fatos de meta/despesa (evita números enganosos).")

# 01 Tempo
m("_Data Base", "01 Tempo", "dd/MM/yyyy", "CALCULATE ( MAX ( fVendas[data_venda] ), REMOVEFILTERS () )", "Último dia com venda na base (limita comparações com o ano anterior).")
m("_Periodo Comparavel LY", "01 Tempo", "", f"""
VAR _ini = CALCULATE ( MIN ( fVendas[data_venda] ) )
RETURN NOT ISBLANK ( _ini ) && EDATE ( _ini, -12 ) >= DATE ( 2024, 10, 1 )""",
  "Verdadeiro quando o mesmo período do ano anterior está inteiramente coberto pela base (≥ 01/10/2024).")
m("Receita Líquida LY", "01 Tempo", BRL, "IF ( [_Periodo Comparavel LY], CALCULATE ( [Receita Líquida], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )")
m("Receita YoY %", "01 Tempo", PCT, "DIVIDE ( [Receita Líquida] - [Receita Líquida LY], [Receita Líquida LY] )")
m("Lucro Bruto LY", "01 Tempo", BRL, "IF ( [_Periodo Comparavel LY], CALCULATE ( [Lucro Bruto], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )")
m("Lucro Bruto YoY %", "01 Tempo", PCT, "DIVIDE ( [Lucro Bruto] - [Lucro Bruto LY], [Lucro Bruto LY] )")
m("Margem Bruta LY", "01 Tempo", PCT, "DIVIDE ( [Lucro Bruto LY], [Receita Líquida LY] )")
m("Margem Bruta Var pp", "01 Tempo", PP, "IF ( NOT ISBLANK ( [Margem Bruta LY] ), ( [Margem Bruta %] - [Margem Bruta LY] ) * 100 )")
m("Cupons LY", "01 Tempo", INT, "IF ( [_Periodo Comparavel LY], CALCULATE ( [Cupons], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )")
m("Cupons YoY %", "01 Tempo", PCT, "DIVIDE ( [Cupons] - [Cupons LY], [Cupons LY] )")
m("Ticket Médio LY", "01 Tempo", BRL, "DIVIDE ( [Receita Líquida LY], [Cupons LY] )")
m("Ticket Médio YoY %", "01 Tempo", PCT, "DIVIDE ( [Ticket Médio] - [Ticket Médio LY], [Ticket Médio LY] )")
m("Resultado Op Simplificado LY", "01 Tempo", BRL, "IF ( [_Periodo Comparavel LY], CALCULATE ( [Resultado Operacional Simplificado], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )")
m("Resultado Op Simplificado YoY %", "01 Tempo", PCT, "DIVIDE ( [Resultado Operacional Simplificado] - [Resultado Op Simplificado LY], ABS ( [Resultado Op Simplificado LY] ) )")
m("Receita Mês Anterior", "01 Tempo", BRL, "CALCULATE ( [Receita Líquida], DATEADD ( dCalendario[Data], -1, MONTH ) )")
m("Receita MoM %", "01 Tempo", PCT, "DIVIDE ( [Receita Líquida] - [Receita Mês Anterior], [Receita Mês Anterior] )")
m("Receita Acumulada Ano", "01 Tempo", BRL, "TOTALYTD ( [Receita Líquida], dCalendario[Data] )")
m("Meses com Venda", "01 Tempo", INT, "COUNTROWS ( FILTER ( VALUES ( dCalendario[AnoMes Num] ), CALCULATE ( NOT ISEMPTY ( fVendas ) ) ) )")
m("Período Selecionado", "01 Tempo", "", """
VAR _i = CALCULATE ( MIN ( fVendas[data_venda] ) )
VAR _f = CALCULATE ( MAX ( fVendas[data_venda] ) )
RETURN IF ( ISBLANK ( _i ), "Sem vendas no período", FORMAT ( _i, "dd/mm/yyyy" ) & " a " & FORMAT ( _f, "dd/mm/yyyy" ) )""")

# 02 Comercial
m("Lucro Bruto", "02 Comercial", BRL, "[Receita Líquida] - [CMV]", "Receita líquida − CMV (f_vendas).")
m("Margem Bruta %", "02 Comercial", PCT, "DIVIDE ( [Lucro Bruto], [Receita Líquida] )")
m("Ticket Médio", "02 Comercial", BRL, "DIVIDE ( [Receita Líquida], [Cupons] )")
m("Itens por Cupom", "02 Comercial", DEC2, "DIVIDE ( [Unidades Vendidas], [Cupons] )", "Unidades por cupom (não confundir com SKUs distintos).")
m("SKUs por Cupom", "02 Comercial", DEC2, "DIVIDE ( SUM ( fVendas[qtd_itens_distintos] ), [Cupons] )")
m("Desconto %", "02 Comercial", PCT, "DIVIDE ( [Descontos], [Receita Bruta] )")
m("Atingimento Meta %", "02 Comercial", PCT, "DIVIDE ( [Receita Líquida], [Meta Receita] )", "Receita líquida / meta. Em branco com filtro de produto/canal/cliente.")
m("Gap Meta", "02 Comercial", BRL, "IF ( NOT ISBLANK ( [Meta Receita] ), [Receita Líquida] - [Meta Receita] )")
m("Share Receita %", "02 Comercial", PCT, "DIVIDE ( [Receita Líquida], CALCULATE ( [Receita Líquida], ALLSELECTED () ) )")
m("Lojas na Meta", "02 Comercial", INT, "COUNTROWS ( FILTER ( VALUES ( dLoja[id_loja] ), [Atingimento Meta %] >= 1 ) )")

# 03 Clientes
m("Cupons Identificados", "03 Clientes", INT, "CALCULATE ( [Cupons], fVendas[cliente_identificado] = TRUE () )")
m("% Cupons Identificados", "03 Clientes", PCT, "DIVIDE ( [Cupons Identificados], [Cupons] )")
m("Clientes Ativos", "03 Clientes", INT, "CALCULATE ( DISTINCTCOUNT ( fVendas[id_cliente] ), fVendas[cliente_identificado] = TRUE () )", "Clientes identificados com ao menos 1 cupom no período. Cupom anônimo não é cliente.")
m("Clientes Ativos LY", "03 Clientes", INT, "IF ( [_Periodo Comparavel LY], CALCULATE ( [Clientes Ativos], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )")
m("Clientes Ativos YoY %", "03 Clientes", PCT, "DIVIDE ( [Clientes Ativos] - [Clientes Ativos LY], [Clientes Ativos LY] )")
m("Clientes Novos", "03 Clientes", INT, "CALCULATE ( DISTINCTCOUNT ( fVendas[id_cliente] ), fVendas[primeira_compra] = TRUE () )", "Primeira compra observada na base (desde 01/10/2024): nos primeiros meses quase todos aparecem como novos.")
m("Clientes Recorrentes", "03 Clientes", INT, "[Clientes Ativos] - [Clientes Novos]")
m("% Clientes Novos", "03 Clientes", PCT, "DIVIDE ( [Clientes Novos], [Clientes Ativos] )")
m("Frequência Média", "03 Clientes", DEC2, "DIVIDE ( [Cupons Identificados], [Clientes Ativos] )", "Cupons por cliente identificado no período.")
m("Taxa de Recompra %", "03 Clientes", PCT, """
VAR _rec = COUNTROWS ( FILTER ( CALCULATETABLE ( VALUES ( fVendas[id_cliente] ), fVendas[cliente_identificado] = TRUE () ), CALCULATE ( COUNTROWS ( fVendas ) ) >= 2 ) )
RETURN DIVIDE ( _rec, [Clientes Ativos] )""", "% de clientes ativos com 2+ cupons no período.")
m("Ticket Médio Identificado", "03 Clientes", BRL, "CALCULATE ( [Ticket Médio], fVendas[cliente_identificado] = TRUE () )")
m("Ticket Médio Anônimo", "03 Clientes", BRL, "CALCULATE ( [Ticket Médio], fVendas[cliente_identificado] = FALSE () )")
m("Receita por Cliente", "03 Clientes", BRL, "DIVIDE ( CALCULATE ( [Receita Líquida], fVendas[cliente_identificado] = TRUE () ), [Clientes Ativos] )")

# 04 Produtos
m("Receita Líquida Itens", "04 Produtos", BRL, "SUM ( fItensVenda[valor_liquido] )", "Receita líquida na granularidade de item (para produto/categoria).")
m("CMV Itens", "04 Produtos", BRL, "SUM ( fItensVenda[custo_total] )")
m("Descontos Itens", "04 Produtos", BRL, "SUM ( fItensVenda[valor_desconto] )")
m("Lucro Bruto Itens", "04 Produtos", BRL, "[Receita Líquida Itens] - [CMV Itens]")
m("Margem Bruta Itens %", "04 Produtos", PCT, "DIVIDE ( [Lucro Bruto Itens], [Receita Líquida Itens] )")
m("Desconto Itens %", "04 Produtos", PCT, "DIVIDE ( [Descontos Itens], [Receita Líquida Itens] + [Descontos Itens] )")
m("SKUs Vendidos", "04 Produtos", INT, "DISTINCTCOUNT ( fItensVenda[id_produto] )")
m("SKUs no Catálogo", "04 Produtos", INT, "COUNTROWS ( dProduto )")
m("% SKUs com Venda", "04 Produtos", PCT, "DIVIDE ( [SKUs Vendidos], [SKUs no Catálogo] )")
m("Preço Médio Unitário", "04 Produtos", BRL, "DIVIDE ( [Receita Líquida Itens], [Unidades Vendidas] )")
m("Share Receita Itens %", "04 Produtos", PCT, "DIVIDE ( [Receita Líquida Itens], CALCULATE ( [Receita Líquida Itens], ALLSELECTED ( dProduto ) ) )")
m("% SKUs Vendidos", "04 Produtos", PCT, "DIVIDE ( [SKUs Vendidos], CALCULATE ( [SKUs Vendidos], ALLSELECTED ( dProduto ) ) )")
m("Contribuição Lucro %", "04 Produtos", PCT, "DIVIDE ( [Lucro Bruto Itens], CALCULATE ( [Lucro Bruto Itens], ALLSELECTED ( dProduto ) ) )")
m("Receita Itens LY", "04 Produtos", BRL, "IF ( [_Periodo Comparavel LY], CALCULATE ( [Receita Líquida Itens], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )")
m("Receita Itens YoY %", "04 Produtos", PCT, "DIVIDE ( [Receita Líquida Itens] - [Receita Itens LY], [Receita Itens LY] )")
m("Receita Itens Var LY", "04 Produtos", BRL, "IF ( NOT ISBLANK ( [Receita Itens LY] ), [Receita Líquida Itens] - [Receita Itens LY] )")
m("Margem Itens LY", "04 Produtos", PCT, "IF ( [_Periodo Comparavel LY], CALCULATE ( [Margem Bruta Itens %], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )")
m("Margem Itens Var pp", "04 Produtos", PP, "IF ( NOT ISBLANK ( [Margem Itens LY] ), ( [Margem Bruta Itens %] - [Margem Itens LY] ) * 100 )")
m("Ranking SKU", "04 Produtos", INT, "IF ( NOT ISBLANK ( [Receita Líquida Itens] ), RANKX ( ALLSELECTED ( dProduto ), [Receita Líquida Itens],, DESC, DENSE ) )")
m("Receita Acumulada % (Pareto)", "04 Produtos", PCT, """
VAR _r = [Receita Líquida Itens]
VAR _t = ADDCOLUMNS ( ALLSELECTED ( dProduto[id_produto] ), "@r", [Receita Líquida Itens] )
VAR _acc = SUMX ( FILTER ( _t, [@r] >= _r ), [@r] )
RETURN IF ( NOT ISBLANK ( _r ), DIVIDE ( _acc, SUMX ( _t, [@r] ) ) )""", "Pareto dinâmico por SKU dentro da seleção. Custoso: usar em tabelas, não em gráficos com 5.000 pontos.")

# 05 Compras
m("Valor Recebido", "05 Compras", BRL, "SUM ( fRecebimentos[valor_recebido] )", "Compras recebidas valorizadas (base complementar). Não somar ao CMV.")
m("Qtd Recebida", "05 Compras", INT, "SUM ( fRecebimentos[quantidade_recebida] )")
m("Recebimentos", "05 Compras", INT, "COUNTROWS ( fRecebimentos )")
m("Lead Time Médio", "05 Compras", '#,0.0 "dias"', "AVERAGE ( fRecebimentos[prazo_real_dias] )", "Prazo real médio (dias) informado no recebimento.")
m("Prazo Previsto Médio", "05 Compras", '#,0.0 "dias"', "AVERAGE ( fRecebimentos[prazo_previsto_dias] )")
m("Atraso Médio", "05 Compras", '#,0.0 "dias"', "AVERAGEX ( FILTER ( fRecebimentos, fRecebimentos[atraso_dias] > 0 ), fRecebimentos[atraso_dias] )", "Média de dias de atraso apenas entre entregas atrasadas.")
m("Pontualidade %", "05 Compras", PCT, "DIVIDE ( SUM ( fRecebimentos[entrega_no_prazo] ), [Recebimentos] )", "Entregas no prazo / recebimentos (OTD). Não é OTIF: não há pedido/quantidade prometida.")
m("Custo Médio Recebido", "05 Compras", BRL, "DIVIDE ( [Valor Recebido], [Qtd Recebida] )")
m("Variação Custo vs Referência %", "05 Compras", PCT, "DIVIDE ( [Valor Recebido], SUMX ( fRecebimentos, fRecebimentos[quantidade_recebida] * RELATED ( dProduto[Custo Ref] ) ) ) - 1",
  "Custo pago vs custo de referência do cadastro. Não é saving (não há baseline negociado).")
m("Fornecedores Ativos", "05 Compras", INT, "DISTINCTCOUNT ( fRecebimentos[id_fornecedor] )")
m("Concentração Top 5 %", "05 Compras", PCT, """
VAR _top = TOPN ( 5, VALUES ( dFornecedor[id_fornecedor] ), [Valor Recebido], DESC )
RETURN DIVIDE ( CALCULATE ( [Valor Recebido], KEEPFILTERS ( _top ) ), [Valor Recebido] )""")
m("Share Compras %", "05 Compras", PCT, "DIVIDE ( [Valor Recebido], CALCULATE ( [Valor Recebido], ALLSELECTED () ) )")
m("Orçamento Compras", "05 Compras", BRL, "IF ( NOT [_Filtro Sem Despesa], SUM ( fOrcamentoCompras[orcamento_compras] ) )")
m("Desvio vs Orçamento", "05 Compras", BRL, "IF ( NOT ISBLANK ( [Orçamento Compras] ), [Valor Recebido] - [Orçamento Compras] )")
m("Desvio vs Orçamento %", "05 Compras", PCT, "DIVIDE ( [Desvio vs Orçamento], [Orçamento Compras] )")
m("Compras / CMV %", "05 Compras", PCT, "DIVIDE ( [Valor Recebido], [CMV Itens] )", "Compras recebidas / CMV de itens. < 100% indica consumo de estoque inicial.")

# 06 Estoque
m("_Mes Snapshot", "06 Estoque", "dd/MM/yyyy", "CALCULATE ( MAX ( fEstoque[data_mes] ) )", "Último mês com saldo dentro do filtro de datas.")
m("Estoque Final (R$)", "06 Estoque", BRL, """
VAR _m = [_Mes Snapshot]
RETURN CALCULATE ( SUM ( fEstoque[valor_saldo_final] ), REMOVEFILTERS ( dCalendario ), fEstoque[data_mes] = _m )""",
  "Saldo valorizado no último mês do período (semiaditivo; nunca soma meses).")
m("Estoque Final (un)", "06 Estoque", INT, """
VAR _m = [_Mes Snapshot]
RETURN CALCULATE ( SUM ( fEstoque[saldo_final] ), REMOVEFILTERS ( dCalendario ), fEstoque[data_mes] = _m )""")
m("Estoque Médio (R$)", "06 Estoque", BRL, "AVERAGEX ( FILTER ( VALUES ( dCalendario[AnoMes Num] ), CALCULATE ( NOT ISEMPTY ( fEstoque ) ) ), CALCULATE ( SUM ( fEstoque[valor_saldo_final] ) ) )")
m("Meses Estoque", "06 Estoque", INT, "COUNTROWS ( FILTER ( VALUES ( dCalendario[AnoMes Num] ), CALCULATE ( NOT ISEMPTY ( fEstoque ) ) ) )")
m("Entradas (un)", "06 Estoque", INT, "SUM ( fEstoque[qtd_entradas] )")
m("Perdas (un)", "06 Estoque", INT, "SUM ( fEstoque[qtd_perdas] )")
m("Perdas (R$)", "06 Estoque", BRL, "SUM ( fEstoque[valor_perdas] )", "Perdas valorizadas ao custo de referência do mês.")
m("Perdas % CMV", "06 Estoque", PCT, "DIVIDE ( [Perdas (R$)], [CMV Itens] )")
m("Giro Anualizado", "06 Estoque", GIRO, "DIVIDE ( [CMV Itens], [Estoque Médio (R$)] ) * DIVIDE ( 12, [Meses Estoque] )", "CMV de itens / estoque médio, anualizado.")
m("Cobertura (dias)", "06 Estoque", DIAS, """
VAR _m = [_Mes Snapshot]
VAR _v3 = CALCULATE ( SUM ( fEstoque[qtd_vendida] ), REMOVEFILTERS ( dCalendario ), fEstoque[data_mes] > EDATE ( _m, -3 ), fEstoque[data_mes] <= _m )
RETURN DIVIDE ( [Estoque Final (un)], _v3 / 91.25 )""", "Saldo final / venda média diária dos últimos 3 meses. Estimativa, não previsão de ruptura.")
m("Posições de Estoque", "06 Estoque", INT, """
VAR _m = [_Mes Snapshot]
RETURN CALCULATE ( COUNTROWS ( fEstoque ), REMOVEFILTERS ( dCalendario ), fEstoque[data_mes] = _m )""", "Pares loja×SKU no último mês do período.")
m("Posições Sem Giro", "06 Estoque", INT, "CALCULATE ( [Posições de Estoque], fEstoque[Status Estoque] = \"Sem giro\" )")
m("Posições em Excesso", "06 Estoque", INT, "CALCULATE ( [Posições de Estoque], fEstoque[Status Estoque] = \"Excesso\" )")
m("Valor em Excesso (R$)", "06 Estoque", BRL, "CALCULATE ( [Estoque Final (R$)], fEstoque[Status Estoque] = \"Excesso\" )")
m("% Valor em Excesso", "06 Estoque", PCT, "DIVIDE ( [Valor em Excesso (R$)], [Estoque Final (R$)] )")
m("Valor Sem Giro (R$)", "06 Estoque", BRL, "CALCULATE ( [Estoque Final (R$)], fEstoque[Status Estoque] = \"Sem giro\" )")
m("Valor em Lotes (R$)", "06 Estoque", BRL, "SUM ( fLotes[valor_lote] )", "Foto de 30/09/2026 (não responde a filtros de data).")
m("Valor em Risco Validade (R$)", "06 Estoque", BRL, "CALCULATE ( [Valor em Lotes (R$)], fLotes[Faixa Validade] IN { \"Vencido\", \"Até 90 dias\" } )")
m("% Valor em Risco Validade", "06 Estoque", PCT, "DIVIDE ( [Valor em Risco Validade (R$)], [Valor em Lotes (R$)] )")
m("Valor Vencido (R$)", "06 Estoque", BRL, "CALCULATE ( [Valor em Lotes (R$)], fLotes[Faixa Validade] = \"Vencido\" )")

# 07 Financeiro
m("Pessoal", "07 Financeiro", BRL, "IF ( NOT [_Filtro Sem Despesa], SUM ( fDespesas[pessoal] ) )")
m("Aluguel", "07 Financeiro", BRL, "IF ( NOT [_Filtro Sem Despesa], SUM ( fDespesas[aluguel] ) )")
m("Despesas Operacionais", "07 Financeiro", BRL, "IF ( NOT [_Filtro Sem Despesa], SUM ( fDespesas[operacionais] ) )")
m("Marketing e Canais", "07 Financeiro", BRL, "IF ( NOT [_Filtro Sem Despesa], SUM ( fDespesas[marketing_canais] ) )")
m("Resultado Operacional Simplificado", "07 Financeiro", BRL, "IF ( NOT [_Filtro Sem Despesa], [Lucro Bruto] - [Despesas] )",
  "Lucro bruto − despesas modeladas. NÃO é EBITDA, lucro líquido nem fluxo de caixa.")
m("Margem Operacional Simplificada %", "07 Financeiro", PCT, "DIVIDE ( [Resultado Operacional Simplificado], [Receita Líquida] )")
m("Despesas % Receita", "07 Financeiro", PCT, "DIVIDE ( [Despesas], [Receita Líquida] )")
m("Atingimento Lucro Bruto %", "07 Financeiro", PCT, "DIVIDE ( [Lucro Bruto], [Meta Lucro Bruto] )")
m("Valor DRE", "07 Financeiro", BRL, """
SWITCH ( SELECTEDVALUE ( dDRE[Ordem DRE] ),
    1, [Receita Bruta], 2, - [Descontos], 3, [Receita Líquida], 4, - [CMV], 5, [Lucro Bruto],
    6, - [Pessoal], 7, - [Aluguel], 8, - [Despesas Operacionais], 9, - [Marketing e Canais],
    10, [Resultado Operacional Simplificado] )""")
m("% Receita Líquida (DRE)", "07 Financeiro", PCT, "DIVIDE ( [Valor DRE], [Receita Líquida] )")
m("Valor Ponte Resultado", "07 Financeiro", BRL, """
SWITCH ( SELECTEDVALUE ( dDRE[Ordem DRE] ),
    3, [Receita Líquida], 4, - [CMV], 6, - [Pessoal], 7, - [Aluguel], 8, - [Despesas Operacionais], 9, - [Marketing e Canais] )""",
  "Valores para o waterfall: receita líquida até resultado operacional simplificado (total automático).")

# 08 Forecast
m("Receita Prevista", "08 Forecast", BRL, "SUM ( fForecast[previsao] )", "Previsão do método com menor WAPE no backtest de cada loja.")
m("Limite Inferior", "08 Forecast", BRL, "SUM ( fForecast[limite_inferior] )", "Intervalo empírico ~80% a partir dos erros do backtest. Soma de lojas é conservadora.")
m("Limite Superior", "08 Forecast", BRL, "SUM ( fForecast[limite_superior] )")
m("Receita Real (Série)", "08 Forecast", BRL, f"IF ( MIN ( dCalendario[Data] ) <= {DB}, [Receita Líquida] )")
m("Fator Receita Cenário", "08 Forecast", "0.00", "SELECTEDVALUE ( dCenario[Fator Receita], 1 )")
m("Fator Custo Cenário", "08 Forecast", "0.00", "SELECTEDVALUE ( dCenario[Fator Custo], 1 )")
m("Cenário Ativo", "08 Forecast", "", "SELECTEDVALUE ( dCenario[Cenario], \"Base\" )")
m("Receita Prevista Cenário", "08 Forecast", BRL, "[Receita Prevista] * [Fator Receita Cenário]")
m("Limite Inferior Cenário", "08 Forecast", BRL, "[Limite Inferior] * [Fator Receita Cenário]")
m("Limite Superior Cenário", "08 Forecast", BRL, "[Limite Superior] * [Fator Receita Cenário]")
m("CMV % Últimos 12m", "08 Forecast", PCT, "CALCULATE ( DIVIDE ( [CMV], [Receita Líquida] ), DATESBETWEEN ( dCalendario[Data], DATE ( 2025, 10, 1 ), DATE ( 2026, 9, 30 ) ) )")
m("Lucro Bruto Previsto Cenário", "08 Forecast", BRL, "[Receita Prevista Cenário] * ( 1 - [CMV % Últimos 12m] * [Fator Custo Cenário] )",
  "Receita prevista × (1 − CMV% dos últimos 12 meses × fator de custo). Premissa, não previsão de margem.")
m("Receita LY dos Meses Previstos", "08 Forecast", BRL, """
SUMX (
    FILTER ( VALUES ( dCalendario[AnoMes Num] ), CALCULATE ( NOT ISEMPTY ( fForecast ) ) && CALCULATE ( SUM ( fForecast[previsao] ) ) > 0 ),
    CALCULATE ( [Receita Líquida], SAMEPERIODLASTYEAR ( dCalendario[Data] ) )
)""")
m("Crescimento Previsto vs LY %", "08 Forecast", PCT, "DIVIDE ( [Receita Prevista Cenário], [Receita LY dos Meses Previstos] ) - 1")
m("WAPE Backtest %", "08 Forecast", PCT, "DIVIDE ( CALCULATE ( SUM ( fBacktest[erro_abs] ), fBacktest[metodo_selecionado] = 1 ), CALCULATE ( SUM ( fBacktest[real] ), fBacktest[metodo_selecionado] = 1 ) )",
  "Erro absoluto ponderado do método selecionado (rolling-origin, h=1..3).")
m("MAPE Backtest %", "08 Forecast", PCT, "CALCULATE ( AVERAGEX ( fBacktest, ABS ( fBacktest[erro_pct] ) ), fBacktest[metodo_selecionado] = 1 )")
m("WAPE por Método %", "08 Forecast", PCT, "DIVIDE ( SUM ( fBacktest[erro_abs] ), SUM ( fBacktest[real] ) )")
m("Viés Backtest %", "08 Forecast", PCT, "DIVIDE ( CALCULATE ( SUMX ( fBacktest, fBacktest[previsto] - fBacktest[real] ), fBacktest[metodo_selecionado] = 1 ), CALCULATE ( SUM ( fBacktest[real] ), fBacktest[metodo_selecionado] = 1 ) )")
m("Métodos Selecionados", "08 Forecast", "", "CONCATENATEX ( SUMMARIZE ( FILTER ( fBacktest, fBacktest[metodo_selecionado] = 1 ), dLoja[Loja Curta], fBacktest[Metodo] ), dLoja[Loja Curta] & \": \" & fBacktest[Metodo], \" · \" )")

# 10 UI & Formatação
def var_txt(nome, medida, sufixo="vs ano anterior", fmt="0.0%", pp=False):
    vfmt = '"0.0", "pt-BR"' if pp else f'"{fmt}", "pt-BR"'
    m(f"Txt {nome}", "10 UI & Formatação", "", f"""
VAR _v = [{medida}]
RETURN IF ( ISBLANK ( _v ), "sem base comparável no ano anterior",
    IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), {vfmt} ){' & " p.p."' if pp else ''} & " {sufixo}" )""")
    m(f"Cor {nome}", "10 UI & Formatação", "", f"""
VAR _v = [{medida}]
RETURN IF ( ISBLANK ( _v ), "#71858A", IF ( _v >= 0, "#0E8F7B", "#A34F39" ) )""")
var_txt("Receita", "Receita YoY %"); var_txt("Lucro", "Lucro Bruto YoY %"); var_txt("Margem", "Margem Bruta Var pp", pp=True)
var_txt("Ticket", "Ticket Médio YoY %"); var_txt("Cupons", "Cupons YoY %"); var_txt("Clientes", "Clientes Ativos YoY %")
var_txt("ROS", "Resultado Op Simplificado YoY %"); var_txt("Receita Itens", "Receita Itens YoY %"); var_txt("Margem Itens", "Margem Itens Var pp", pp=True)
m("Txt Meta", "10 UI & Formatação", "", """
VAR _g = [Gap Meta]
RETURN IF ( ISBLANK ( _g ), "meta indisponível p/ este filtro", IF ( _g >= 0, "▲ R$ ", "▼ R$ " ) & FORMAT ( ABS ( _g ) / 1000, "#,0", "pt-BR" ) & " mil vs meta" )""")
m("Cor Meta", "10 UI & Formatação", "", "IF ( ISBLANK ( [Gap Meta] ), \"#71858A\", IF ( [Gap Meta] >= 0, \"#0E8F7B\", \"#A34F39\" ) )")
m("Txt Margem Op", "10 UI & Formatação", "", "IF ( ISBLANK ( [Margem Operacional Simplificada %] ), \"indisponível p/ este filtro\", \"margem op. \" & FORMAT ( [Margem Operacional Simplificada %], \"0.0%\", \"pt-BR\" ) & \" · não é EBITDA\" )")
m("Txt Novos", "10 UI & Formatação", "", "FORMAT ( [% Clientes Novos], \"0.0%\", \"pt-BR\" ) & \" dos ativos (1ª compra observada)\"")
m("Txt SKUs", "10 UI & Formatação", "", "FORMAT ( [% SKUs com Venda], \"0.0%\", \"pt-BR\" ) & \" do catálogo filtrado\"")
m("Txt Perdas", "10 UI & Formatação", "", "FORMAT ( [Perdas % CMV], \"0.00%\", \"pt-BR\" ) & \" do CMV de itens\"")
m("Txt Validade", "10 UI & Formatação", "", "FORMAT ( [% Valor em Risco Validade], \"0.0%\", \"pt-BR\" ) & \" do valor · foto 30/09/2026\"")
m("Txt Cobertura", "10 UI & Formatação", "", "FORMAT ( [% Valor em Excesso], \"0%\", \"pt-BR\" ) & \" do valor com cobertura > 120 dias\"")
m("Txt Pontualidade", "10 UI & Formatação", "", "\"prazo previsto médio \" & FORMAT ( [Prazo Previsto Médio], \"0.0\", \"pt-BR\" ) & \" dias\"")
m("Txt Orçamento", "10 UI & Formatação", "", "IF ( ISBLANK ( [Desvio vs Orçamento %] ), \"orçamento indisponível p/ este filtro\", IF ( [Desvio vs Orçamento %] >= 0, \"▲ \", \"▼ \" ) & FORMAT ( ABS ( [Desvio vs Orçamento %] ), \"0.0%\", \"pt-BR\" ) & \" vs orçamento\" )")
m("Txt Período", "10 UI & Formatação", "", "\"Período: \" & [Período Selecionado]")
m("Txt Forecast Intervalo", "10 UI & Formatação", "", "\"intervalo ~80%: R$ \" & FORMAT ( [Limite Inferior Cenário] / 1000000, \"#,0.00\", \"pt-BR\" ) & \" a \" & FORMAT ( [Limite Superior Cenário] / 1000000, \"#,0.00\", \"pt-BR\" ) & \" mi\"")
m("Txt Neutro", "10 UI & Formatação", "", "\"#71858A\"")

# 09 Narrativas (determinísticas; derivam dos filtros atuais)
MI = 'FORMAT ( {x} / 1000000, "#,0.00", "pt-BR" ) & " mi"'
m("Narrativa Executiva", "09 Narrativas", "", f"""
VAR _rec = [Receita Líquida]
VAR _yoy = [Receita YoY %]
VAR _mg = [Margem Bruta %]
VAR _pp = [Margem Bruta Var pp]
VAR _at = [Atingimento Meta %]
VAR _t = ADDCOLUMNS ( VALUES ( dLoja[Loja Curta] ), "@d", [Receita Líquida] - [Receita Líquida LY] )
VAR _top = TOPN ( 1, _t, [@d], DESC )
VAR _loja = MAXX ( _top, dLoja[Loja Curta] )
VAR _dl = MAXX ( _top, [@d] )
VAR _f1 = "Receita líquida de R$ " & {MI.format(x="_rec")}
    & IF ( ISBLANK ( _yoy ), " (sem período comparável completo no ano anterior).",
        ", " & IF ( _yoy >= 0, "alta", "queda" ) & " de " & FORMAT ( ABS ( _yoy ), "0.0%", "pt-BR" ) & " vs mesmo período do ano anterior." )
VAR _f2 = IF ( NOT ISBLANK ( _yoy ) && COUNTROWS ( _t ) > 1,
    " Maior contribuição: " & _loja & " (" & IF ( _dl >= 0, "+", "−" ) & "R$ " & FORMAT ( ABS ( _dl ) / 1000, "#,0", "pt-BR" ) & " mil).", "" )
VAR _f3 = " Margem bruta de " & FORMAT ( _mg, "0.0%", "pt-BR" )
    & IF ( ISBLANK ( _pp ), "", " (" & FORMAT ( _pp, "+0.0;-0.0", "pt-BR" ) & " p.p.)" )
    & IF ( ISBLANK ( _at ), ".", "; meta de receita " & FORMAT ( _at, "0%", "pt-BR" ) & " atingida." )
RETURN IF ( ISBLANK ( _rec ), "Sem vendas para os filtros selecionados.", _f1 & _f2 & _f3 )""",
  "Fato derivado dos filtros. Não atribui causa.")
m("Narrativa Clientes", "09 Narrativas", "", """
VAR _id = [% Cupons Identificados]
VAR _fr = [Frequência Média]
VAR _ti = [Ticket Médio Identificado]
VAR _ta = [Ticket Médio Anônimo]
VAR _rc = [Taxa de Recompra %]
RETURN IF ( ISBLANK ( [Cupons] ), "Sem vendas para os filtros selecionados.",
    FORMAT ( _id, "0%", "pt-BR" ) & " dos cupons têm cliente identificado; cada cliente ativo comprou em média " & FORMAT ( _fr, "0.0", "pt-BR" )
    & " vezes e " & FORMAT ( _rc, "0%", "pt-BR" ) & " recompraram no período."
    & IF ( NOT ISBLANK ( _ta ), " Ticket identificado R$ " & FORMAT ( _ti, "#,0.00", "pt-BR" ) & " vs anônimo R$ " & FORMAT ( _ta, "#,0.00", "pt-BR" ) & ".", "" )
    & " Hipótese a testar: ampliar identificação no balcão." )""")
m("Narrativa Produtos", "09 Narrativas", "", """
VAR _c = ADDCOLUMNS ( VALUES ( dProduto[Categoria] ), "@r", [Receita Líquida Itens], "@pp", [Margem Itens Var pp] )
VAR _maior = TOPN ( 1, _c, [@r], DESC )
VAR _pior = TOPN ( 1, FILTER ( _c, NOT ISBLANK ( [@pp] ) ), [@pp], ASC )
VAR _f1 = MAXX ( _maior, dProduto[Categoria] ) & " lidera com " & FORMAT ( DIVIDE ( MAXX ( _maior, [@r] ), [Receita Líquida Itens] ), "0%", "pt-BR" ) & " da receita de itens; margem bruta geral de " & FORMAT ( [Margem Bruta Itens %], "0.0%", "pt-BR" ) & "."
VAR _f2 = IF ( COUNTROWS ( _pior ) = 1 && MAXX ( _pior, [@pp] ) < 0, " Maior perda de margem: " & MAXX ( _pior, dProduto[Categoria] ) & " (" & FORMAT ( MAXX ( _pior, [@pp] ), "+0.0;-0.0", "pt-BR" ) & " p.p.) — investigar desconto e mix.", "" )
RETURN IF ( ISBLANK ( [Receita Líquida Itens] ), "Sem vendas para os filtros selecionados.", _f1 & _f2 )""")
m("Narrativa Compras", "09 Narrativas", "", """
VAR _f = ADDCOLUMNS ( VALUES ( dFornecedor[Fornecedor] ), "@v", [Valor Recebido], "@p", [Pontualidade %] )
VAR _pior = TOPN ( 1, FILTER ( _f, [@v] >= 0.01 * [Valor Recebido] ), [@p], ASC )
RETURN IF ( ISBLANK ( [Valor Recebido] ), "Sem recebimentos para os filtros selecionados.",
    "Compras recebidas de R$ " & FORMAT ( [Valor Recebido] / 1000000, "#,0.00", "pt-BR" ) & " mi; " & FORMAT ( [Pontualidade %], "0%", "pt-BR" ) & " das entregas no prazo, atraso médio de "
    & FORMAT ( [Atraso Médio], "0.0", "pt-BR" ) & " dias quando atrasa. Menor pontualidade (≥1% do valor): " & MAXX ( _pior, dFornecedor[Fornecedor] ) & " (" & FORMAT ( MAXX ( _pior, [@p] ), "0%", "pt-BR" ) & ")." )""")
m("Narrativa Estoque", "09 Narrativas", "", """
IF ( ISBLANK ( [Estoque Final (R$)] ), "Sem estoque para os filtros selecionados.",
    "Estoque de R$ " & FORMAT ( [Estoque Final (R$)] / 1000000, "#,0.00", "pt-BR" ) & " mi em " & FORMAT ( [_Mes Snapshot], "mm/yyyy" ) & " cobre ~" & FORMAT ( [Cobertura (dias)], "#,0", "pt-BR" )
    & " dias de venda; " & FORMAT ( [% Valor em Excesso], "0%", "pt-BR" ) & " do valor está acima de 120 dias de cobertura. Recomendação: revisar parâmetros de reposição antes de comprar." )""")
m("Narrativa Financeiro", "09 Narrativas", "", """
VAR _ros = [Resultado Operacional Simplificado]
VAR _pes = DIVIDE ( [Pessoal], [Despesas] )
RETURN IF ( ISBLANK ( _ros ), "Resultado indisponível para filtros de produto, canal, cliente ou fornecedor (despesas são por loja/mês).",
    "Resultado operacional simplificado de R$ " & FORMAT ( _ros / 1000000, "#,0.00", "pt-BR" ) & " mi (margem " & FORMAT ( [Margem Operacional Simplificada %], "0.0%", "pt-BR" )
    & "). Pessoal é " & FORMAT ( _pes, "0%", "pt-BR" ) & " das despesas modeladas. Indicador gerencial: não é EBITDA nem lucro líquido." )""")
m("Narrativa Forecast", "09 Narrativas", "", """
"Cenário " & [Cenário Ativo] & ": receita prevista de R$ " & FORMAT ( [Receita Prevista Cenário] / 1000000, "#,0.00", "pt-BR" ) & " mi nos próximos 6 meses ("
    & FORMAT ( [Crescimento Previsto vs LY %], "+0.0%;-0.0%", "pt-BR" ) & " vs mesmos meses do ano anterior). Erro histórico (WAPE) de " & FORMAT ( [WAPE Backtest %], "0.0%", "pt-BR" )
    & " com só 24 meses de histórico: use como faixa, não como meta." """)

# 99 Auditoria
m("Check Receita Cupom vs Itens", "99 Auditoria", BRL, "[Receita Líquida] - [Receita Líquida Itens]", "Deve ser 0 com filtros de loja/data/canal/cliente.")
m("Check Receita Referência", "99 Auditoria", BRL, "CALCULATE ( [Receita Líquida], REMOVEFILTERS () ) - 35060712", "Deve ser 0 (RESUMO_BASE.json).")
m("Check CMV Referência", "99 Auditoria", BRL, "CALCULATE ( [CMV], REMOVEFILTERS () ) - 21252002.94")
m("Check Lotes vs Saldo Final", "99 Auditoria", INT, f"CALCULATE ( SUM ( fLotes[quantidade_lote] ), REMOVEFILTERS () ) - CALCULATE ( SUM ( fEstoque[saldo_final] ), REMOVEFILTERS (), fEstoque[data_mes] = DATE ( 2026, 9, 1 ) )")

# ---------------------------------------------------------------- escrita
def indent(txt, n): return "\n".join(("\t" * n + l) if l.strip() else "" for l in txt.splitlines())

def write_model(base):
    d = os.path.join(base, "definition"); os.makedirs(os.path.join(d, "tables"), exist_ok=True)
    open(os.path.join(d, "database.tmdl"), "w", encoding="utf-8").write("database\n\tcompatibilityLevel: 1600\n\n")
    refs = "\n".join(f"ref table {q(n)}" for n in T)
    open(os.path.join(d, "model.tmdl"), "w", encoding="utf-8").write(f"""model Model
\tculture: pt-BR
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tdiscourageImplicitMeasures
\tsourceQueryCulture: pt-BR
\tdataAccessOptions
\t\tlegacyRedirects
\t\treturnErrorValuesAsNull

annotation __PBI_TimeIntelligenceEnabled = 0

annotation PBI_QueryOrder = ["PastaProjeto","fnCsv",{",".join('"%s"' % n for n in T)}]

{refs}

""")
    open(os.path.join(d, "expressions.tmdl"), "w", encoding="utf-8").write(f"""expression PastaProjeto = "E:\\Projetos BI\\17 - Farmavitta\\" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
\tlineageTag: {tag('expr', 'PastaProjeto')}

\tannotation PBI_ResultType = Text

expression fnCsv =
\t\t(caminho as text) as table =>
\t\tlet
\t\t    Fonte = Csv.Document(File.Contents(PastaProjeto & caminho), [Delimiter = ";", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
\t\t    Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true])
\t\tin
\t\t    Cabecalho
\tlineageTag: {tag('expr', 'fnCsv')}

\tannotation PBI_ResultType = Function

""")
    rels = []
    for i, (ft, fc, tt, tc) in enumerate(REL):
        rels.append(f"relationship {tag('rel', ft, fc, tt, tc)}\n\tfromColumn: {q(ft)}.{q(fc)}\n\ttoColumn: {q(tt)}.{q(tc)}\n")
    open(os.path.join(d, "relationships.tmdl"), "w", encoding="utf-8").write("\n".join(rels) + "\n")
    for n, t in T.items():
        L = [f"/// {t['desc']}", f"table {q(n)}", f"\tlineageTag: {tag('t', n)}"]
        if t.get("dataCategory"): L.append(f"\tdataCategory: {t['dataCategory']}")
        L.append("")
        if n == "_Medidas":
            for x in MED:
                expr = x["dax"]
                if x["d"]: L.append(f"\t/// {x['d']}")
                if "\n" in expr:
                    L.append(f"\tmeasure {q(x['n'])} =")
                    L.append(indent(expr, 3))
                else:
                    L.append(f"\tmeasure {q(x['n'])} = {expr}")
                if x["fmt"]: L.append(f"\t\tformatString: {x['fmt']}")
                if x.get("cat"): L.append(f"\t\tdataCategory: {x['cat']}")
                L.append(f"\t\tdisplayFolder: {x['f']}")
                if x.get("hidden") or x["n"].startswith("_") or x["n"].startswith("Cor ") or x["n"] == "Txt Neutro": L.append("\t\tisHidden")
                L.append(f"\t\tlineageTag: {tag('m', x['n'])}")
                L.append("")
        for c_ in t["cols"]:
            dt = c_["t"]
            L.append(f"\tcolumn {q(c_['n'])}")
            L.append(f"\t\tdataType: {dt}")
            if c_.get("fmt"): L.append(f"\t\tformatString: {c_['fmt']}")
            if c_.get("hidden"): L.append("\t\tisHidden")
            if c_.get("key"): L.append("\t\tisKey") if n == "dCalendario" else None
            L.append(f"\t\tlineageTag: {tag('c', n, c_['n'])}")
            L.append(f"\t\tsummarizeBy: none")
            L.append(f"\t\tsourceColumn: {c_['s']}")
            if c_.get("sort"): L.append(f"\t\tsortByColumn: {q(c_['sort'])}")
            L.append("")
            L.append("\t\tannotation SummarizationSetBy = Automatic")
            if dt == "dateTime": L.append("\n\t\tannotation UnderlyingDateTimeDataType = Date")
            L.append("")
        L.append(f"\tpartition {q(n)} = m")
        L.append("\t\tmode: import")
        L.append("\t\tsource =")
        L.append(indent(t["m"], 4))
        L.append("")
        L.append("\tannotation PBI_ResultType = Table")
        L.append("")
        open(os.path.join(d, "tables", f"{n}.tmdl"), "w", encoding="utf-8").write("\n".join(L))
    # dCalendario: marcar como tabela de datas é feito por dataCategory: Time + isKey em Data.
    return len(MED)

def write_semantic_model_root(base):
    import json
    os.makedirs(base, exist_ok=True)
    json.dump({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
               "version": "4.2", "settings": {}}, open(os.path.join(base, "definition.pbism"), "w", encoding="utf-8"), indent=2)
    pbi = os.path.join(base, ".pbi"); os.makedirs(pbi, exist_ok=True)
    json.dump({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/editorSettings/1.0.0/schema.json",
               "autodetectRelationships": False, "parallelQueryLoading": True, "typeDetectionEnabled": False},
              open(os.path.join(pbi, "editorSettings.json"), "w"), indent=2)
