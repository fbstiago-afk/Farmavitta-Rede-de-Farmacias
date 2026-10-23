# -*- coding: utf-8 -*-
"""GATE A — Auditoria dos dados FarmaVitta. Não altera originais.
Uso: python3 01_auditoria_gate_a.py <pasta_raiz_projeto>
Saída: 07_Testes/GATE_A_auditoria.md e GATE_A_auditoria.json
"""
import sys, json, os
import pandas as pd, numpy as np

root = sys.argv[1]
O = os.path.join(root, "01_Dados_Originais", "base_original")
C = os.path.join(root, "01_Dados_Originais", "base_complementar")
rd = lambda p, f, **k: pd.read_csv(os.path.join(p, f), sep=";", encoding="utf-8-sig", **k)

t = {n: rd(O, n + ".csv", dtype={"id_cliente": str}) for n in [
    "dim_calendario", "dim_clientes", "dim_fornecedores", "dim_lojas", "dim_produtos",
    "f_despesas_mensais", "f_estoque_inicial", "f_estoque_mensal", "f_itens_venda",
    "f_metas_mensais", "f_vendas", "ponte_produto_fornecedor"]}
c = {n: rd(C, n + ".csv") for n in [
    "d_cenarios_previsao", "f_compras_mensais", "f_lotes_estoque_foto", "f_orcamento_compras",
    "f_recebimentos_compras", "f_resultado_gerencial_mensal"]}

res = []
def chk(gate, nome, ok, sev, det=""):
    res.append({"area": gate, "teste": nome, "resultado": "PASS" if ok else "FAIL",
                "severidade": "-" if ok else sev, "detalhe": str(det)})

# Perfil
perfil = []
for n, df in {**t, **c}.items():
    perfil.append({"tabela": n, "linhas": len(df), "colunas": len(df.columns),
                   "nulos": {k: int(v) for k, v in df.isna().sum().items() if v}})

# Chaves únicas
for n, k in [("dim_calendario", ["data"]), ("dim_clientes", ["id_cliente"]), ("dim_fornecedores", ["id_fornecedor"]),
             ("dim_lojas", ["id_loja"]), ("dim_produtos", ["id_produto"]), ("f_vendas", ["id_venda"]),
             ("f_itens_venda", ["id_item"]), ("f_estoque_inicial", ["id_loja", "id_produto"]),
             ("f_estoque_mensal", ["ano_mes", "id_loja", "id_produto"]), ("f_metas_mensais", ["ano_mes", "id_loja"]),
             ("f_despesas_mensais", ["ano_mes", "id_loja"]), ("ponte_produto_fornecedor", ["id_produto"])]:
    d = int(t[n].duplicated(k).sum())
    chk("Chaves", f"{n} único por {'+'.join(k)}", d == 0, "Alta", f"{d} duplicados")
for n, k in [("f_recebimentos_compras", ["id_recebimento"]), ("f_lotes_estoque_foto", ["id_lote"])]:
    d = int(c[n].duplicated(k).sum()); chk("Chaves", f"{n} único por {k[0]}", d == 0, "Alta", f"{d} duplicados")

# Integridade referencial
def fk(df, col, dim, dcol, nome, allow_blank=False):
    s = df[col].dropna() if allow_blank else df[col]
    miss = set(s) - set(dim[dcol]); chk("Integridade", nome, not miss, "Alta", f"{len(miss)} chaves órfãs")
L, P, CL, F = t["dim_lojas"], t["dim_produtos"], t["dim_clientes"], t["dim_fornecedores"]
for n in ["f_vendas", "f_itens_venda", "f_estoque_inicial", "f_estoque_mensal", "f_metas_mensais", "f_despesas_mensais"]:
    fk(t[n], "id_loja", L, "id_loja", f"{n}.id_loja → dim_lojas")
for n in ["f_itens_venda", "f_estoque_inicial", "f_estoque_mensal", "ponte_produto_fornecedor"]:
    fk(t[n], "id_produto", P, "id_produto", f"{n}.id_produto → dim_produtos")
fk(t["f_vendas"], "id_cliente", CL, "id_cliente", "f_vendas.id_cliente → dim_clientes (anônimos excluídos)", True)
fk(t["ponte_produto_fornecedor"], "id_fornecedor", F, "id_fornecedor", "ponte.id_fornecedor → dim_fornecedores")
fk(t["f_itens_venda"], "id_venda", t["f_vendas"], "id_venda", "f_itens_venda.id_venda → f_vendas")
for n in ["f_recebimentos_compras", "f_lotes_estoque_foto"]:
    fk(c[n], "id_loja", L, "id_loja", f"{n}.id_loja → dim_lojas"); fk(c[n], "id_produto", P, "id_produto", f"{n}.id_produto → dim_produtos")
fk(c["f_recebimentos_compras"], "id_fornecedor", F, "id_fornecedor", "f_recebimentos.id_fornecedor → dim_fornecedores")
# Recebimentos respeitam a ponte?
pr = c["f_recebimentos_compras"].merge(t["ponte_produto_fornecedor"], on="id_produto", suffixes=("", "_ponte"))
nao = int((pr["id_fornecedor"] != pr["id_fornecedor_ponte"]).sum())
chk("Integridade", "Recebimentos respeitam ponte_produto_fornecedor", nao == 0, "Média", f"{nao} linhas com fornecedor diferente da ponte")

# Cardinalidade da ponte
chk("Modelo", "Ponte: 1 fornecedor por SKU (permite levar fornecedor para dProduto)",
    t["ponte_produto_fornecedor"]["id_produto"].is_unique and len(t["ponte_produto_fornecedor"]) == 5000, "Média")

# Escopo
V, I = t["f_vendas"], t["f_itens_venda"]
chk("Escopo", "4 lojas", len(L) == 4, "Alta", len(L))
chk("Escopo", "5.000 SKUs", len(P) == 5000, "Alta", len(P))
cat = P["categoria"].value_counts().to_dict()
chk("Escopo", "Distribuição de categorias", cat == {"Medicamentos": 2100, "Higiene e Beleza": 900, "Suplementos": 850, "Perfumaria": 600, "Baby": 550}, "Média", cat)
chk("Escopo", "143.399 vendas / 322.277 itens", len(V) == 143399 and len(I) == 322277, "Alta", f"{len(V)} / {len(I)}")
dmin, dmax = V["data_venda"].min(), V["data_venda"].max()
chk("Escopo", "Período de vendas 2024-10-01 a 2026-09-30", dmin >= "2024-10-01" and dmax <= "2026-09-30", "Alta", f"{dmin} a {dmax}")
chk("Escopo", "Calendário 730 dias contínuos", len(t["dim_calendario"]) == 730 and set(V["data_venda"]) <= set(t["dim_calendario"]["data"]), "Alta")
for n in ["f_metas_mensais", "f_despesas_mensais"]:
    chk("Escopo", f"{n} completo (24 meses × 4 lojas)", len(t[n]) == 96 and t[n]["ano_mes"].nunique() == 24, "Alta", len(t[n]))

# Monetário
rl, cmv = round(V["valor_liquido"].sum(), 2), round(V["custo_mercadoria"].sum(), 2)
chk("Monetário", "Receita líquida = R$ 35.060.712,00 (RESUMO_BASE)", abs(rl - 35060712.0) < 0.5, "Alta", f"{rl:,.2f}")
chk("Monetário", "CMV = R$ 21.252.002,94 (RESUMO_BASE)", abs(cmv - 21252002.94) < 0.5, "Alta", f"{cmv:,.2f}")
dif = (V["valor_bruto"] - V["valor_desconto"] - V["valor_liquido"]).abs()
chk("Monetário", "Cupom: bruto − desconto = líquido (±0,01)", int((dif > 0.011).sum()) == 0, "Alta", f"{int((dif>0.011).sum())} cupons fora")
neg = int((V[["valor_bruto", "valor_liquido", "custo_mercadoria"]] < 0).any(axis=1).sum())
chk("Monetário", "Sem valores negativos em vendas", neg == 0, "Média", neg)
agg = I.groupby("id_venda").agg(li=("valor_liquido", "sum"), cu=("custo_total", "sum"), de=("valor_desconto", "sum"), n=("id_produto", "nunique")).reset_index()
m = V.merge(agg, on="id_venda", how="left")
for a, b, nome in [("valor_liquido", "li", "líquido"), ("custo_mercadoria", "cu", "custo"), ("valor_desconto", "de", "desconto")]:
    d = (m[a] - m[b]).abs(); fora = int((d > 0.05).sum())
    chk("Reconciliação", f"Cabeçalho × itens: {nome} (±0,05 por cupom)", fora == 0, "Alta", f"{fora} cupons fora; dif. total {(m[a]-m[b]).sum():,.2f}")
fora = int((m["qtd_itens_distintos"] != m["n"]).sum())
chk("Reconciliação", "qtd_itens_distintos = SKUs distintos nos itens", fora == 0, "Baixa", f"{fora} cupons")
chk("Reconciliação", "Itens: id_loja e data iguais ao cabeçalho",
    int((I.merge(V[["id_venda", "id_loja", "data_venda"]], on="id_venda", suffixes=("", "_v")).pipe(lambda x: (x.id_loja != x.id_loja_v) | (x.data_venda != x.data_venda_v))).sum()) == 0, "Alta")
anon = V["id_cliente"].isna().mean()
chk("Clientes", "Proporção de cupons anônimos documentada", True, "-", f"{anon:.1%} anônimos")

# Estoque
E = t["f_estoque_mensal"]
d = int((E["estoque_inicial"] + E["qtd_entradas"] - E["qtd_vendida"] - E["qtd_perdas"] != E["estoque_final"]).sum())
chk("Estoque", "Linha: inicial + entradas − vendida − perdas = final", d == 0, "Alta", f"{d} linhas")
chk("Estoque", "Sem saldo final negativo", int((E["estoque_final"] < 0).sum()) == 0, "Alta", int((E["estoque_final"] < 0).sum()))
# Encadeamento: inicial do mês = final do último mês com linha (ou estoque_inicial base)
Es = E.sort_values(["id_loja", "id_produto", "ano_mes"]).copy()
Es["prev_final"] = Es.groupby(["id_loja", "id_produto"])["estoque_final"].shift()
base = t["f_estoque_inicial"].set_index(["id_loja", "id_produto"])["quantidade_inicial"]
first = Es["prev_final"].isna()
Es.loc[first, "prev_final"] = [base.get((a, b), 0) for a, b in zip(Es.loc[first, "id_loja"], Es.loc[first, "id_produto"])]
quebra = int((Es["estoque_inicial"] != Es["prev_final"]).sum())
chk("Estoque", "Encadeamento: inicial do mês = último final conhecido", quebra == 0, "Alta", f"{quebra} quebras")
# Vendas de itens × qtd_vendida
Iv = I.assign(ano_mes=I["data_venda"].str[:7]).groupby(["ano_mes", "id_loja", "id_produto"])["quantidade"].sum()
Ev = E.set_index(["ano_mes", "id_loja", "id_produto"])["qtd_vendida"]
j = pd.concat([Iv.rename("itens"), Ev.rename("estoque")], axis=1).fillna(0)
fora = int((j["itens"] != j["estoque"]).sum())
chk("Reconciliação", "Quantidade vendida (itens) = qtd_vendida (estoque) por mês/loja/SKU", fora == 0, "Alta", f"{fora} combinações divergentes; itens={int(j.itens.sum())} estoque={int(j.estoque.sum())}")
pares_sem_base = len(set(zip(E.id_loja, E.id_produto)) - set(base.index))
chk("Estoque", "Todo par loja/SKU do mensal existe no estoque inicial", pares_sem_base == 0, "Média", pares_sem_base)

# Despesas e metas
D = t["f_despesas_mensais"]
d = int(((D[["aluguel", "pessoal", "operacionais", "marketing_canais"]].sum(axis=1) - D["despesa_total"]).abs() > 0.011).sum())
chk("Financeiro", "Despesa total = soma das rubricas", d == 0, "Alta", d)

# Complementares
R = c["f_recebimentos_compras"]
rv = R.groupby(["ano_mes", "id_loja", "id_produto"])["quantidade_recebida"].sum()
ev = E[E.qtd_entradas > 0].set_index(["ano_mes", "id_loja", "id_produto"])["qtd_entradas"]
j = pd.concat([rv.rename("r"), ev.rename("e")], axis=1).fillna(0)
chk("Complementar", "Recebimentos = entradas do estoque (mês/loja/SKU)", int((j.r != j.e).sum()) == 0, "Alta", int((j.r != j.e).sum()))
d = int(((R["quantidade_recebida"] * R["custo_unitario"] - R["valor_recebido"]).abs() > 0.011).sum())
chk("Complementar", "valor_recebido = quantidade × custo", d == 0, "Média", d)
comp, cmv_m = R["valor_recebido"].sum(), cmv
ratio = comp / cmv_m
chk("Plausibilidade", "Compras recebidas plausíveis frente ao CMV (≥ 50% do CMV em 24 meses)", ratio >= 0.5, "Alta",
    f"Compras R$ {comp:,.2f} = {ratio:.1%} do CMV. Entradas físicas: {int(E.qtd_entradas.sum()):,} un vs vendidas {int(E.qtd_vendida.sum()):,} un")
G = c["f_resultado_gerencial_mensal"]
vm = V.assign(ano_mes=V.data_venda.str[:7]).groupby(["ano_mes", "id_loja"])[["valor_liquido", "custo_mercadoria"]].sum()
g = G.set_index(["ano_mes", "id_loja"])
chk("Complementar", "Resultado gerencial: receita/CMV = f_vendas por mês/loja",
    bool(((g.receita_liquida - vm.valor_liquido).abs() < 0.05).all() and ((g.cmv - vm.custo_mercadoria).abs() < 0.05).all()), "Média")
LT = c["f_lotes_estoque_foto"]
fim = E.sort_values("ano_mes").groupby(["id_loja", "id_produto"]).last()
fim = fim[fim.index.isin(fim.index)]  # último conhecido
saldo_fim = fim["estoque_final"]
# pares sem movimento: saldo base
todos = pd.Series(base).copy(); todos.update(saldo_fim)
lt = LT.groupby(["id_loja", "id_produto"])["quantidade_lote"].sum()
jj = pd.concat([todos.rename("s"), lt.rename("l")], axis=1).fillna(0)
chk("Complementar", "Lotes 30/09/2026 = saldo final por loja/SKU", int((jj.s != jj.l).sum()) == 0, "Média", f"{int((jj.s != jj.l).sum())} pares; saldo={int(jj.s.sum()):,} lotes={int(jj.l.sum()):,}")
pz = R["entrega_no_prazo"].mean(); chk("Complementar", "Taxa de entrega no prazo documentada", True, "-", f"{pz:.1%}")

out = {"perfil": perfil, "testes": res,
       "totais_referencia": {"receita_bruta": round(V.valor_bruto.sum(), 2), "descontos": round(V.valor_desconto.sum(), 2),
                             "receita_liquida": rl, "cmv": cmv, "lucro_bruto": round(rl - cmv, 2),
                             "despesas": round(D.despesa_total.sum(), 2), "meta_receita": round(t["f_metas_mensais"].meta_receita.sum(), 2),
                             "cupons": int(len(V)), "unidades": int(I.quantidade.sum()), "clientes_identificados": int(V.id_cliente.nunique()),
                             "compras_recebidas": round(comp, 2), "pct_anonimo": round(anon, 4),
                             "receita_2025": round(V[V.data_venda.str[:4] == "2025"].valor_liquido.sum(), 2)}}
os.makedirs(os.path.join(root, "07_Testes"), exist_ok=True)
json.dump(out, open(os.path.join(root, "07_Testes", "GATE_A_auditoria.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2, default=str)
md = ["# GATE A — Auditoria de dados FarmaVitta", "", f"Executado por script `10_Scripts/01_auditoria_gate_a.py`. Originais não alterados.", "",
      f"**Resultado:** {sum(r['resultado']=='PASS' for r in res)} PASS · {sum(r['resultado']=='FAIL' for r in res)} FAIL", "",
      "| Área | Teste | Resultado | Severidade | Detalhe |", "|---|---|---|---|---|"]
md += [f"| {r['area']} | {r['teste']} | {r['resultado']} | {r['severidade']} | {r['detalhe']} |" for r in res]
md += ["", "## Perfil das tabelas", "", "| Tabela | Linhas | Colunas | Nulos |", "|---|---|---|---|"]
md += [f"| {p['tabela']} | {p['linhas']:,} | {p['colunas']} | {p['nulos'] or '-'} |" for p in perfil]
md += ["", "## Totais de referência (para reconciliar com DAX)", ""] + [f"- {k}: {v:,}" if isinstance(v, (int, float)) else f"- {k}: {v}" for k, v in out["totais_referencia"].items()]
open(os.path.join(root, "07_Testes", "GATE_A_auditoria.md"), "w", encoding="utf-8").write("\n".join(md))
print("\n".join(md[:len(res) + 8])); print(json.dumps(out["totais_referencia"], indent=1))
