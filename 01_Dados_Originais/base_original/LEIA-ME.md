# FarmaVitta — Base sintética BI 24 meses

**Dados totalmente fictícios; não representam operações, pessoas ou empresas reais.**

## Recorte
- Período: 2024-10-01 a 2026-09-30 (24 meses fechados).
- Lojas: Campinas, Jundiaí, Sorocaba e Piracicaba (SP).
- Produtos: exatamente 5.000 SKUs: medicamentos 2.100, suplementos 850, higiene e beleza 900, baby 550 e perfumaria 600.
- Clientes sintéticos: 22,000.
- Vendas: 143,399; itens de venda: 322,277.
- Estoque: snapshot mensal por loja/produto com movimentação de entrada, saída, perdas e saldo inicial/final.

## Regras de negócio / granularidade
- `f_vendas`: 1 linha por venda/cupom. `valor_liquido = valor_bruto - valor_desconto`; `custo_mercadoria` é soma do custo dos itens.
- `f_itens_venda`: 1 linha por SKU do cupom. **Não somar `f_vendas` e `f_itens_venda` no mesmo indicador**.
- `f_estoque_mensal`: 1 linha por loja/SKU/mês para itens com movimento; `estoque_final = estoque_inicial + qtd_entradas - qtd_vendida - qtd_perdas`. Para snapshots de SKUs sem movimento, carregar o saldo do mês anterior ou usar `f_estoque_inicial`; não presumir ausência como saldo zero.
- `f_despesas_mensais`: 1 linha por loja/mês. Margem bruta = receita líquida - CMV. Resultado operacional simplificado = margem bruta - despesas; **não é EBITDA contábil auditado**.
- `f_metas_mensais`: 1 linha por loja/mês, metas construídas sinteticamente.
- `dim_produtos`: preços e custos de referência são fictícios e não representam CMED, PMC ou preços regulados efetivos.
- Campos `eh_controlado` e `exige_receita` são simulações de classificação e não constituem informação farmacológica.
- Clientes possuem IDs artificiais; não há nomes, CPF, informação clínica nem dados pessoais reais.
- `f_vendas.id_cliente` vazio = compra anônima. Evitar usar número de cupons como número de clientes.
- CSV: UTF-8 com BOM, separador ponto e vírgula, números com ponto decimal e datas ISO 8601.
- Moeda: BRL.

## Modelo recomendado
- `dim_calendario[data]` → `f_vendas[data_venda]` / `f_itens_venda[data_venda]`; usar `ano_mes` (padrão YYYY-MM) para snapshots e metas.
- `dim_lojas[id_loja]` → todas as fatos aplicáveis.
- `dim_produtos[id_produto]` → `f_itens_venda` / `f_estoque_mensal`.
- `dim_clientes[id_cliente]` → `f_vendas[id_cliente]` (excluir ID em branco do lado da dimensão).
- `f_vendas[id_venda]` → `f_itens_venda[id_venda]` (1:N, direção única); cuidado com caminhos ambíguos via data e loja.
- `ponte_produto_fornecedor` liga produtos e fornecedores; preferir trazer fornecedor padrão à dimensão produto no Power Query se a relação for 1 fornecedor/SKU.

## Indicadores
Receita líquida, CMV, lucro bruto, margem bruta %, descontos %, ticket médio, itens por cupom, vendas por canal, crescimento YoY, clientes identificados, frequência, produtos/categorias, estoque final, cobertura estimada, ruptura potencial, perdas, despesas e resultado operacional simplificado.

## Limitações de simulação
- Estoque mensal agregado, não representa eventos individuais de recebimento, lote e vencimento.
- Não há devoluções, impostos, tarifas específicas por transação ou detalhamento de receitas médicas.
- Produtos são descrições comerciais sintéticas, não medicamentos registrados.
- `quantidade_inicial` em 2024-09-30 garante reconciliação de movimentação.
