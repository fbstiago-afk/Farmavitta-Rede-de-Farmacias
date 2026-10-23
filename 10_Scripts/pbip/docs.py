# -*- coding: utf-8 -*-
"""Gera a documentação técnica a partir do próprio gerador (fonte única): dicionário, relacionamentos e contrato de métricas.
Uso: python3 docs.py <pasta_saida_08_Documentacao>
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelo, relatorio

out = sys.argv[1]; os.makedirs(out, exist_ok=True)
w = lambda f, t: open(os.path.join(out, f), "w", encoding="utf-8").write(t)

# Dicionário
L = ["# Dicionário de dados — modelo semântico FarmaVitta", "",
     "Gerado de `10_Scripts/pbip/modelo.py` (fonte única do TMDL). Colunas ocultas são chaves ou campos técnicos usados pelas medidas.", ""]
for n, t in modelo.T.items():
    L += [f"## {n}", "", t["desc"], "", "| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |", "|---|---|---|---|---|"]
    L += [f"| {c['n']} | {c['s']} | {c['t']} | {'sim' if c.get('hidden') else ''} | {c.get('sort', '')} |" for c in t["cols"]]
    L.append("")
w("02_Dicionario_de_Dados.md", "\n".join(L))

# Relacionamentos (+ diagrama mermaid)
R = ["# Relacionamentos", "", "Todos 1:N, direção única (dimensão → fato), ativos. Nenhuma relação fato–fato, nenhuma bidirecional, nenhuma N:N.", "",
     "| Fato (N) | Coluna | Dimensão (1) | Coluna |", "|---|---|---|---|"]
R += [f"| {a} | {b} | {c} | {d} |" for a, b, c, d in modelo.REL]
R += ["", "Desconectadas: `dCenario` (what-if), `dDRE` (linhas da DRE), `_Medidas`.",
      "`fLotes` não se liga ao calendário (fotografia de 30/09/2026). `dFornecedor` filtra fatos via `dProduto` (fornecedor único por SKU, validado).", "",
      "```mermaid", "erDiagram"]
for a, b, c, d in modelo.REL:
    R.append(f'    {c} ||--o{{ {a} : "{d}"')
R.append("```")
w("03_Relacionamentos.md", "\n".join(R))

# Contrato de métricas
C = ["# Contrato de métricas e catálogo DAX", "",
     "Regras gerais: receita/CMV da rede vêm de `fVendas` (cupom); por produto/categoria, de `fItensVenda`. Nunca somar as duas granularidades.",
     "Estoque é semiaditivo (último mês do período). Despesas, metas e orçamento só existem por loja/mês: as medidas ficam em branco quando há filtro de produto, canal, cliente ou fornecedor (`_Filtro Sem Despesa`).",
     "Comparações com ano anterior só aparecem quando o mesmo período está inteiramente coberto pela base (`_Periodo Comparavel LY`) e são limitadas ao último dia com venda (`_Data Base`).", ""]
pastas = {}
for x in modelo.MED: pastas.setdefault(x["f"], []).append(x)
for p in sorted(pastas):
    C += [f"## {p}", ""]
    for x in pastas[p]:
        C += [f"### {x['n']}", ""]
        if x["d"]: C += [x["d"], ""]
        if x["fmt"]: C += [f"Formato: `{x['fmt']}`", ""]
        C += ["```dax", x["dax"], "```", ""]
w("04_Contrato_de_Metricas.md", "\n".join(C))

# Páginas
P = ["# Páginas do relatório", ""]
for pg in relatorio.build_pages():
    tipos = {}
    for v in pg.visuals: tipos[v["visual"]["visualType"]] = tipos.get(v["visual"]["visualType"], 0) + 1
    P += [f"## {pg.display}", "", f"Tamanho {pg.w}×{pg.h} · {len(pg.visuals)} objetos · " + ", ".join(f"{k} ({v})" for k, v in sorted(tipos.items())), ""]
w("05_Paginas.md", "\n".join(P))
print("docs ok:", len(modelo.MED), "medidas,", len(modelo.T), "tabelas")
