# -*- coding: utf-8 -*-
"""Dados tratados FarmaVitta (derivados, determinísticos; originais intactos).
Uso: python3 02_dados_tratados.py <pasta_raiz_projeto>
Gera em 02_Dados_Tratados/:
  f_estoque_saldo_mensal.csv  — grade completa loja×SKU×mês (meses sem movimento carregam saldo)
  f_forecast_receita.csv      — real + previsão 6 meses por loja, intervalo 80% empírico
  f_forecast_backtest.csv     — backtest rolling-origin (h=1..3) de 3 métodos
  d_parametros_estoque.csv    — regras de classificação usadas (documentação)
"""
import sys, os, json
import numpy as np, pandas as pd

root = sys.argv[1]
O = os.path.join(root, "01_Dados_Originais", "base_original")
OUT = os.path.join(root, "02_Dados_Tratados"); os.makedirs(OUT, exist_ok=True)
rd = lambda f: pd.read_csv(os.path.join(O, f), sep=";", encoding="utf-8-sig")
wr = lambda df, f: df.to_csv(os.path.join(OUT, f), sep=";", index=False, encoding="utf-8-sig", float_format="%.4f")

# ---------------- 1. Saldo de estoque completo ----------------
E, B, P = rd("f_estoque_mensal.csv"), rd("f_estoque_inicial.csv"), rd("dim_produtos.csv")
meses = sorted(rd("dim_calendario.csv")["ano_mes"].unique())
pares = B[["id_loja", "id_produto"]]
grid = pares.merge(pd.DataFrame({"ano_mes": meses}), how="cross")
g = grid.merge(E, on=["ano_mes", "id_loja", "id_produto"], how="left")
g["teve_movimento"] = g["estoque_final"].notna().astype(int)
for col in ["qtd_entradas", "qtd_vendida", "qtd_perdas"]:
    g[col] = g[col].fillna(0).astype(int)
g = g.merge(B[["id_loja", "id_produto", "quantidade_inicial"]], on=["id_loja", "id_produto"])
g = g.sort_values(["id_loja", "id_produto", "ano_mes"]).reset_index(drop=True)
# saldo final: carrega último final conhecido; antes do 1º movimento usa estoque inicial base
g["saldo_final"] = g.groupby(["id_loja", "id_produto"])["estoque_final"].ffill()
g["saldo_final"] = g["saldo_final"].fillna(g["quantidade_inicial"]).astype(int)
g["saldo_inicial"] = g.groupby(["id_loja", "id_produto"])["saldo_final"].shift().fillna(g["quantidade_inicial"]).astype(int)
assert ((g.saldo_inicial + g.qtd_entradas - g.qtd_vendida - g.qtd_perdas) == g.saldo_final).all(), "Saldo não fecha"
cref = P.set_index("id_produto")["custo_unitario_referencia"]
g["custo_unitario"] = g.groupby(["id_loja", "id_produto"])["custo_unitario_referencia"].ffill()
g["custo_unitario"] = g["custo_unitario"].fillna(g["id_produto"].map(cref))
g["valor_saldo_final"] = (g["saldo_final"] * g["custo_unitario"]).round(2)
g["valor_perdas"] = (g["qtd_perdas"] * g["custo_unitario"]).round(2)
grp = g.groupby(["id_loja", "id_produto"])
g["venda_media_3m"] = grp["qtd_vendida"].transform(lambda s: s.rolling(3, min_periods=1).mean()).round(4)
# meses consecutivos sem venda (até o mês)
def streak(s):
    out, c = [], 0
    for v in s:
        c = 0 if v > 0 else c + 1; out.append(c)
    return out
g["meses_sem_venda"] = grp["qtd_vendida"].transform(lambda s: pd.Series(streak(s.values), index=s.index))
g["cobertura_dias"] = np.where(g["venda_media_3m"] > 0, g["saldo_final"] / (g["venda_media_3m"] / 30.0), np.nan).round(1)
REG = {"cobertura_baixa_dias": 15, "cobertura_excesso_dias": 120, "meses_sem_giro": 3}
def status(r):
    if r.saldo_final <= 0: return "Sem saldo"
    if r.meses_sem_venda >= REG["meses_sem_giro"]: return "Sem giro"
    if r.cobertura_dias < REG["cobertura_baixa_dias"]: return "Baixo"
    if r.cobertura_dias > REG["cobertura_excesso_dias"]: return "Excesso"
    return "Normal"
g["status_estoque"] = [status(r) for r in g[["saldo_final", "meses_sem_venda", "cobertura_dias"]].itertuples()]
cols = ["ano_mes", "id_loja", "id_produto", "saldo_inicial", "qtd_entradas", "qtd_vendida", "qtd_perdas", "saldo_final",
        "custo_unitario", "valor_saldo_final", "valor_perdas", "teve_movimento", "venda_media_3m", "meses_sem_venda",
        "cobertura_dias", "status_estoque"]
wr(g[cols], "f_estoque_saldo_mensal.csv")
pd.DataFrame([{"parametro": k, "valor": v} for k, v in REG.items()]).pipe(wr, "d_parametros_estoque.csv")
print("estoque:", len(g), "linhas; saldo final 2026-09:", int(g[g.ano_mes == meses[-1]].saldo_final.sum()),
      "status:", g[g.ano_mes == meses[-1]].status_estoque.value_counts().to_dict())

# ---------------- 2. Forecast receita mensal por loja ----------------
V = rd("f_vendas.csv"); V["ano_mes"] = V["data_venda"].str[:7]
Y = V.pivot_table(index="ano_mes", columns="id_loja", values="valor_liquido", aggfunc="sum").sort_index()
idx = list(Y.index)

def m_sazonal_yoy(y, h):
    """Mês do ano anterior × crescimento dos últimos 12m vs 12m anteriores (ou 3m vs 3m LY se < 24)."""
    n = len(y)
    g_ = y[-3:].sum() / y[-15:-12].sum()
    return np.array([y[n - 12 + ((k - 1) % 12)] * g_ for k in range(1, h + 1)])
def m_holt(y, h, a=0.4, b=0.1, phi=0.9):
    l, t = y[0], (y[min(3, len(y) - 1)] - y[0]) / min(3, len(y) - 1)
    for v in y[1:]:
        lp = l; l = a * v + (1 - a) * (l + phi * t); t = b * (l - lp) + (1 - b) * phi * t
    return np.array([l + sum(phi ** i for i in range(1, k + 1)) * t for k in range(1, h + 1)])
def m_media3(y, h):
    return np.repeat(y[-3:].mean(), h)
MET = {"Sazonal YoY": m_sazonal_yoy, "Holt amortecido": m_holt, "Média móvel 3m": m_media3}

bt = []
for o in range(14, len(idx)):           # origem precisa de >= 15 meses p/ sazonal
    for loja in Y.columns:
        y = Y[loja].values[:o]
        for nome, f in MET.items():
            fc = f(y, 3)
            for h in range(1, 4):
                if o + h - 1 < len(idx):
                    real = Y[loja].values[o + h - 1]
                    bt.append({"origem": idx[o - 1], "ano_mes_alvo": idx[o + h - 1], "horizonte": h, "id_loja": loja,
                               "metodo": nome, "real": round(real, 2), "previsto": round(fc[h - 1], 2),
                               "erro_abs": round(abs(real - fc[h - 1]), 2), "erro_pct": round((fc[h - 1] - real) / real, 6)})
BT = pd.DataFrame(bt)
wape = BT.groupby(["id_loja", "metodo"]).apply(lambda d: d.erro_abs.sum() / d.real.sum(), include_groups=False).rename("wape").reset_index()
melhor = wape.loc[wape.groupby("id_loja")["wape"].idxmin()].set_index("id_loja")
BT["metodo_selecionado"] = (BT["metodo"] == BT["id_loja"].map(melhor["metodo"])).astype(int)
wr(BT, "f_forecast_backtest.csv")

H = 6
futuro = pd.period_range(pd.Period(idx[-1], "M") + 1, periods=H, freq="M").strftime("%Y-%m").tolist()
rows = []
for loja in Y.columns:
    y = Y[loja].values
    for am, v in zip(idx, y):
        rows.append({"ano_mes": am, "id_loja": loja, "tipo": "Real", "valor_real": round(v, 2)})
    met = melhor.loc[loja, "metodo"]; fc = MET[met](y, H)
    e = BT[(BT.id_loja == loja) & (BT.metodo == met)]
    for k, (am, p) in enumerate(zip(futuro, fc), start=1):
        eh = e[e.horizonte == min(k, 3)].erro_pct     # horizontes > 3 usam erro de h=3 (premissa documentada)
        lo, hi = np.quantile(eh, 0.10), np.quantile(eh, 0.90)
        spread = max(abs(lo), abs(hi)) * (1 + 0.1 * max(0, k - 3))
        rows.append({"ano_mes": am, "id_loja": loja, "tipo": "Previsto", "metodo": met, "previsao": round(p, 2),
                     "limite_inferior": round(p * (1 - spread), 2), "limite_superior": round(p * (1 + spread), 2),
                     "wape_backtest": round(melhor.loc[loja, "wape"], 6)})
F = pd.DataFrame(rows); F["versao"] = "v1.0"; F["data_treino"] = idx[-1] + "-30"
F = F[["ano_mes", "id_loja", "tipo", "metodo", "valor_real", "previsao", "limite_inferior", "limite_superior", "wape_backtest", "versao", "data_treino"]]
wr(F, "f_forecast_receita.csv")
print("WAPE backtest:\n", wape.pivot(index="id_loja", columns="metodo", values="wape").round(4).to_string())
print("Previsão:", F[F.tipo == "Previsto"].groupby("ano_mes").previsao.sum().round(0).to_dict())
json.dump({"melhor_metodo": melhor["metodo"].to_dict(), "wape": melhor["wape"].round(4).to_dict()},
          open(os.path.join(OUT, "forecast_resumo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
