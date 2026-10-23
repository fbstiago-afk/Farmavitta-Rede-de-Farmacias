# GATE A — Auditoria de dados FarmaVitta

Executado por script `10_Scripts/01_auditoria_gate_a.py`. Originais não alterados.

**Resultado:** 64 PASS · 0 FAIL

| Área | Teste | Resultado | Severidade | Detalhe |
|---|---|---|---|---|
| Chaves | dim_calendario único por data | PASS | - | 0 duplicados |
| Chaves | dim_clientes único por id_cliente | PASS | - | 0 duplicados |
| Chaves | dim_fornecedores único por id_fornecedor | PASS | - | 0 duplicados |
| Chaves | dim_lojas único por id_loja | PASS | - | 0 duplicados |
| Chaves | dim_produtos único por id_produto | PASS | - | 0 duplicados |
| Chaves | f_vendas único por id_venda | PASS | - | 0 duplicados |
| Chaves | f_itens_venda único por id_item | PASS | - | 0 duplicados |
| Chaves | f_estoque_inicial único por id_loja+id_produto | PASS | - | 0 duplicados |
| Chaves | f_estoque_mensal único por ano_mes+id_loja+id_produto | PASS | - | 0 duplicados |
| Chaves | f_metas_mensais único por ano_mes+id_loja | PASS | - | 0 duplicados |
| Chaves | f_despesas_mensais único por ano_mes+id_loja | PASS | - | 0 duplicados |
| Chaves | ponte_produto_fornecedor único por id_produto | PASS | - | 0 duplicados |
| Chaves | f_recebimentos_compras único por id_recebimento | PASS | - | 0 duplicados |
| Chaves | f_lotes_estoque_foto único por id_lote | PASS | - | 0 duplicados |
| Integridade | f_vendas.id_loja → dim_lojas | PASS | - | 0 chaves órfãs |
| Integridade | f_itens_venda.id_loja → dim_lojas | PASS | - | 0 chaves órfãs |
| Integridade | f_estoque_inicial.id_loja → dim_lojas | PASS | - | 0 chaves órfãs |
| Integridade | f_estoque_mensal.id_loja → dim_lojas | PASS | - | 0 chaves órfãs |
| Integridade | f_metas_mensais.id_loja → dim_lojas | PASS | - | 0 chaves órfãs |
| Integridade | f_despesas_mensais.id_loja → dim_lojas | PASS | - | 0 chaves órfãs |
| Integridade | f_itens_venda.id_produto → dim_produtos | PASS | - | 0 chaves órfãs |
| Integridade | f_estoque_inicial.id_produto → dim_produtos | PASS | - | 0 chaves órfãs |
| Integridade | f_estoque_mensal.id_produto → dim_produtos | PASS | - | 0 chaves órfãs |
| Integridade | ponte_produto_fornecedor.id_produto → dim_produtos | PASS | - | 0 chaves órfãs |
| Integridade | f_vendas.id_cliente → dim_clientes (anônimos excluídos) | PASS | - | 0 chaves órfãs |
| Integridade | ponte.id_fornecedor → dim_fornecedores | PASS | - | 0 chaves órfãs |
| Integridade | f_itens_venda.id_venda → f_vendas | PASS | - | 0 chaves órfãs |
| Integridade | f_recebimentos_compras.id_loja → dim_lojas | PASS | - | 0 chaves órfãs |
| Integridade | f_recebimentos_compras.id_produto → dim_produtos | PASS | - | 0 chaves órfãs |
| Integridade | f_lotes_estoque_foto.id_loja → dim_lojas | PASS | - | 0 chaves órfãs |
| Integridade | f_lotes_estoque_foto.id_produto → dim_produtos | PASS | - | 0 chaves órfãs |
| Integridade | f_recebimentos.id_fornecedor → dim_fornecedores | PASS | - | 0 chaves órfãs |
| Integridade | Recebimentos respeitam ponte_produto_fornecedor | PASS | - | 0 linhas com fornecedor diferente da ponte |
| Modelo | Ponte: 1 fornecedor por SKU (permite levar fornecedor para dProduto) | PASS | - |  |
| Escopo | 4 lojas | PASS | - | 4 |
| Escopo | 5.000 SKUs | PASS | - | 5000 |
| Escopo | Distribuição de categorias | PASS | - | {'Medicamentos': 2100, 'Higiene e Beleza': 900, 'Suplementos': 850, 'Perfumaria': 600, 'Baby': 550} |
| Escopo | 143.399 vendas / 322.277 itens | PASS | - | 143399 / 322277 |
| Escopo | Período de vendas 2024-10-01 a 2026-09-30 | PASS | - | 2024-10-01 a 2026-09-30 |
| Escopo | Calendário 730 dias contínuos | PASS | - |  |
| Escopo | f_metas_mensais completo (24 meses × 4 lojas) | PASS | - | 96 |
| Escopo | f_despesas_mensais completo (24 meses × 4 lojas) | PASS | - | 96 |
| Monetário | Receita líquida = R$ 35.060.712,00 (RESUMO_BASE) | PASS | - | 35,060,712.00 |
| Monetário | CMV = R$ 21.252.002,94 (RESUMO_BASE) | PASS | - | 21,252,002.94 |
| Monetário | Cupom: bruto − desconto = líquido (±0,01) | PASS | - | 0 cupons fora |
| Monetário | Sem valores negativos em vendas | PASS | - | 0 |
| Reconciliação | Cabeçalho × itens: líquido (±0,05 por cupom) | PASS | - | 0 cupons fora; dif. total -0.00 |
| Reconciliação | Cabeçalho × itens: custo (±0,05 por cupom) | PASS | - | 0 cupons fora; dif. total 0.00 |
| Reconciliação | Cabeçalho × itens: desconto (±0,05 por cupom) | PASS | - | 0 cupons fora; dif. total 0.00 |
| Reconciliação | qtd_itens_distintos = SKUs distintos nos itens | PASS | - | 0 cupons |
| Reconciliação | Itens: id_loja e data iguais ao cabeçalho | PASS | - |  |
| Clientes | Proporção de cupons anônimos documentada | PASS | - | 17.1% anônimos |
| Estoque | Linha: inicial + entradas − vendida − perdas = final | PASS | - | 0 linhas |
| Estoque | Sem saldo final negativo | PASS | - | 0 |
| Estoque | Encadeamento: inicial do mês = último final conhecido | PASS | - | 0 quebras |
| Reconciliação | Quantidade vendida (itens) = qtd_vendida (estoque) por mês/loja/SKU | PASS | - | 0 combinações divergentes; itens=422215 estoque=422215 |
| Estoque | Todo par loja/SKU do mensal existe no estoque inicial | PASS | - | 0 |
| Financeiro | Despesa total = soma das rubricas | PASS | - | 0 |
| Complementar | Recebimentos = entradas do estoque (mês/loja/SKU) | PASS | - | 0 |
| Complementar | valor_recebido = quantidade × custo | PASS | - | 0 |
| Plausibilidade | Compras recebidas plausíveis frente ao CMV (≥ 50% do CMV em 24 meses) | PASS | - | Compras R$ 13,360,752.12 = 62.9% do CMV. Entradas físicas: 265,510 un vs vendidas 422,215 un |
| Complementar | Resultado gerencial: receita/CMV = f_vendas por mês/loja | PASS | - |  |
| Complementar | Lotes 30/09/2026 = saldo final por loja/SKU | PASS | - | 0 pares; saldo=245,063 lotes=245,063 |
| Complementar | Taxa de entrega no prazo documentada | PASS | - | 42.4% |

## Perfil das tabelas

| Tabela | Linhas | Colunas | Nulos |
|---|---|---|---|
| dim_calendario | 730 | 7 | - |
| dim_clientes | 22,000 | 5 | - |
| dim_fornecedores | 60 | 4 | - |
| dim_lojas | 4 | 6 | - |
| dim_produtos | 5,000 | 11 | - |
| f_despesas_mensais | 96 | 7 | - |
| f_estoque_inicial | 16,562 | 4 | - |
| f_estoque_mensal | 222,238 | 9 | - |
| f_itens_venda | 322,277 | 11 | - |
| f_metas_mensais | 96 | 4 | - |
| f_vendas | 143,399 | 11 | {'id_cliente': 24543} |
| ponte_produto_fornecedor | 5,000 | 2 | - |
| d_cenarios_previsao | 3 | 5 | - |
| f_compras_mensais | 96 | 4 | - |
| f_lotes_estoque_foto | 33,114 | 9 | - |
| f_orcamento_compras | 96 | 6 | - |
| f_recebimentos_compras | 14,547 | 13 | - |
| f_resultado_gerencial_mensal | 96 | 8 | - |

## Totais de referência (para reconciliar com DAX)

- receita_bruta: 36,821,295.17
- descontos: 1,760,583.17
- receita_liquida: 35,060,712.0
- cmv: 21,252,002.94
- lucro_bruto: 13,808,709.06
- despesas: 6,061,566.28
- meta_receita: 36,987,069.12
- cupons: 143,399
- unidades: 422,215
- clientes_identificados: 19,038
- compras_recebidas: 13,360,752.12
- pct_anonimo: 0.1712
- receita_2025: 16,997,629.12