# -*- coding: utf-8 -*-
"""RFV de clientes identificados e Curva ABC de produtos (fotografia em 30/09/2026, período completo).
Uso: python3 03_rfv_abc.py <pasta_raiz_projeto>
Saída: 02_Dados_Tratados/d_cliente_rfv.csv, d_produto_abc.csv
Regras:
  RFV — quintis (1–5) de Recência (dias desde última compra, invertido), Frequência (nº cupons) e Valor (receita líquida).
        Segmentos: Campeões (R>=4,F>=4), Leais (F>=4), Potenciais (R>=4,F<=3), Em risco (R<=2,F>=3), Hibernando (R<=2,F<=2), Regulares (demais).
  ABC — receita líquida de itens acumulada: A até 80%, B até 95%, C restante; SKUs sem venda = 'Sem venda'.
"""
import sys, os
import numpy as np, pandas as pd
root = sys.argv[1]
O = os.path.join(root, "01_Dados_Originais", "base_original"); OUT = os.path.join(root, "02_Dados_Tratados")
rd = lambda f, **k: pd.read_csv(os.path.join(O, f), sep=";", encoding="utf-8-sig", **k)
V = rd("f_vendas.csv").dropna(subset=["id_cliente"])
ref = pd.Timestamp("2026-09-30")
V["data_venda"] = pd.to_datetime(V["data_venda"])
r = V.groupby("id_cliente").agg(ultima=("data_venda", "max"), primeira=("data_venda", "min"),
                                frequencia=("id_venda", "nunique"), valor=("valor_liquido", "sum")).reset_index()
r["recencia_dias"] = (ref - r["ultima"]).dt.days
q = lambda s, asc=True: pd.qcut(s.rank(method="first", ascending=asc), 5, labels=[1, 2, 3, 4, 5]).astype(int)
r["score_r"], r["score_f"], r["score_v"] = q(r.recencia_dias, False), q(r.frequencia), q(r.valor)
def seg(x):
    if x.score_r >= 4 and x.score_f >= 4: return "Campeões"
    if x.score_f >= 4: return "Leais"
    if x.score_r >= 4: return "Potenciais"
    if x.score_r <= 2 and x.score_f >= 3: return "Em risco"
    if x.score_r <= 2: return "Hibernando"
    return "Regulares"
r["segmento_rfv"] = [seg(x) for x in r.itertuples()]
ordem = {"Campeões": 1, "Leais": 2, "Potenciais": 3, "Regulares": 4, "Em risco": 5, "Hibernando": 6}
r["ordem_segmento"] = r.segmento_rfv.map(ordem)
r["data_primeira_compra"], r["data_ultima_compra"] = r.primeira.dt.date, r.ultima.dt.date
r["valor"] = r["valor"].round(2)
r[["id_cliente", "data_primeira_compra", "data_ultima_compra", "recencia_dias", "frequencia", "valor", "score_r", "score_f", "score_v", "segmento_rfv", "ordem_segmento"]] \
    .to_csv(os.path.join(OUT, "d_cliente_rfv.csv"), sep=";", index=False, encoding="utf-8-sig")
print(r.segmento_rfv.value_counts().to_dict())

I, P = rd("f_itens_venda.csv"), rd("dim_produtos.csv")
a = I.groupby("id_produto")["valor_liquido"].sum().reindex(P.id_produto).fillna(0).sort_values(ascending=False)
pct = a.cumsum() / a.sum()
cls = np.where(a == 0, "Sem venda", np.where(pct.shift(fill_value=0) < 0.80, "A", np.where(pct.shift(fill_value=0) < 0.95, "B", "C")))
d = pd.DataFrame({"id_produto": a.index, "receita_periodo": a.values.round(2), "pct_acumulado": pct.values.round(6),
                  "rank_receita": np.arange(1, len(a) + 1), "classe_abc": cls})
d.to_csv(os.path.join(OUT, "d_produto_abc.csv"), sep=";", index=False, encoding="utf-8-sig")
print(d.classe_abc.value_counts().to_dict())
