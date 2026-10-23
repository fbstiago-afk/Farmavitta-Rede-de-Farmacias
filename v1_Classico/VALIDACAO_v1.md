# GATE D — Validação do PBIP

Data: 22/10/2026 · Power BI Desktop local do usuário (esquema de visual nativo 2.14.0) · Ferramenta: powerbi-modeling-mcp + controle de tela.

| # | Teste | Resultado | Evidência |
|---|---|---|---|
| 1 | 261 JSON do relatório validados contra microsoft/json-schemas (Draft-07) | PASS, 0 erros | `build.py`. O validador foi provado com erro injetado. |
| 2 | Pasta TMDL importada pelo motor tabular | PASS | 19 tabelas, 165 colunas, 182 medidas, 27 relações (v1) |
| 3 | Abertura no Desktop (v1) | FAIL → corrigido | `editorSettings.json` com `settings` fora do esquema |
| 4 | Abertura no Desktop (v1, após correção) + Atualizar | PASS | Home com R$ 35,06 mi, 4 lojas, 5.000 SKUs, 143 mil cupons |
| 5 | Todas as medidas executadas via DAX (4 consultas, contexto total e Ano = 2026) | PASS, sem erro de execução | Resultados abaixo |
| 6 | Receita líquida = R$ 35.060.712,00; CMV = R$ 21.252.002,94 | PASS | Bate com RESUMO_BASE.json e GATE A |
| 7 | Receita de itens = receita de cupons | PASS | 35.060.712 nas duas granularidades |
| 8 | Saldo final (un) = soma dos lotes em 30/09/2026 | PASS | 245.063 = 245.063 |
| 9 | Ano anterior com Ano = 2026 | FAIL → corrigido | Dava R$ 16,99 mi (2025 inteiro). Após a correção: R$ 12.250.944,38 = jan–set/2025, conferido com DATESBETWEEN |
| 10 | Loja Curta única | FAIL → corrigido | "Centro" duplicado; agora usa a cidade |
| 11 | Navegação: texto dos botões | FAIL → corrigido no código | Formato confirmado em botão criado pelo próprio Desktop (seletor `id: default`) |
| 12 | Revisão visual das 8 páginas (v1) | PASS com ajustes | Narrativa sem quebra de linha, eixo da ABC, escala do estoque e "Total" vazio na DRE: todos corrigidos na v1.1 |
| 13 | Reabrir a v1.1 no Desktop e conferir visualmente | **NÃO VALIDADO** | A tela do computador ficou indisponível para controle. Roteiro: abrir `v1_Classico\FarmaVitta.pbip` → Atualizar → percorrer as 8 páginas e clicar nos botões do header. |
| 14 | Power BI Service, Performance Analyzer, DAX Studio | NÃO VALIDADO | Nenhuma medição feita |

## Valores obtidos por DAX (contexto total, v1)

Margem bruta 39,4% · Ticket R$ 244,50 · Itens/cupom 2,94 · Desconto 4,8% · Atingimento da meta 94,8% · Clientes ativos 19.038 (contexto total) · Cupons identificados 82,9% · Frequência 6,24 · Recompra 85,2% · Compras recebidas R$ 13,36 mi · Pontualidade 42,4% · Lead time 29,4 dias · Concentração top 5 10,0% · Estoque final R$ 12,52 mi · Cobertura 414 dias · Giro 0,71x · Perdas R$ 628 mil (2,96% do CMV) · Valor em risco de validade R$ 1,76 mi (14,1%) · Resultado operacional simplificado R$ 7,75 mi (22,1%) · Previsão de 6 meses R$ 9,99 mi (+9,2% vs mesmos meses do ano anterior) · WAPE 8,1% · Viés +3,0%.
