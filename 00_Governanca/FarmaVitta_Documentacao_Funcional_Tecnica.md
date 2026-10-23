# FarmaVitta — Especificação funcional e técnica de Power BI
**Versão:** 1.0 | **Data:** 22/10/2026 | **Status:** especificação para desenvolvimento
**Fonte oficial:** pacote FarmaVitta_Base_Dados_24_Meses.zip
**Natureza:** projeto sintético e fictício.

## 1. Visão geral

FarmaVitta é uma rede fictícia de varejo farmacêutico usada exclusivamente em portfólio, demonstração e aprendizado de BI. As quatro unidades estão localizadas em Campinas (Cambuí), Jundiaí (Centro), Sorocaba (Campolim) e Piracicaba (Centro). Período fechado: 01/10/2024 a 30/09/2026. Moeda BRL; granularidade diária de vendas e mensal de estoque, despesas e metas. Dados fictícios, sem informações pessoais identificáveis ou medicamentos reais certificados.

## 2. Objetivos e perguntas de negócio

Objetivos: acompanhar faturamento, mix, margem, desconto, comportamento de compra, canais, giro de estoque, perdas, custos operacionais e produtividade das lojas. Perguntas centrais: quem cresce com margem? Qual loja atinge a meta e sustenta resultado? Quais categorias puxam receita, mas destroem margem? Quais SKUs têm excesso ou risco de ruptura? Clientes identificados recompram com que frequência?

## 3. Escopo e números de referência

4 lojas; 5.000 SKUs; 22.000 clientes sintéticos; 143,399 vendas; 322,277 linhas de itens; 222,238 registros de estoque; receita líquida R$ 35,060,712.00; CMV R$ 21,252,002.94. Categorias: medicamentos 2.100; suplementos 850; higiene e beleza 900; baby 550; perfumaria 600. Totais são referência de auditoria e devem reconciliar com medidas DAX.

## 4. Inventário e dicionário técnico

Cada linha abaixo descreve um CSV da entrega, a granularidade esperada e sua estrutura exata. Nomes de campos devem ser preservados na etapa de ingestão; eventuais nomes amigáveis pertencem à camada semântica.

## 4 · dim_calendario

Grão: Uma linha por dia. Linhas: 730. Campos (7): `data`, `ano`, `mes`, `ano_mes`, `dia_semana_domingo_zero`, `dia_semana_iso`, `dia_util`.

## 4 · dim_clientes

Grão: Uma linha por cliente sintético. Linhas: 22,000. Campos (5): `id_cliente`, `cidade_cadastro`, `data_cadastro`, `segmento_cadastro`, `faixa_etaria`.

## 4 · dim_fornecedores

Grão: Uma linha por fornecedor fictício. Linhas: 60. Campos (4): `id_fornecedor`, `razao_social_ficticia`, `uf`, `prazo_medio_dias`.

## 4 · dim_lojas

Grão: Uma linha por loja. Linhas: 4. Campos (6): `id_loja`, `cidade`, `uf`, `nome_loja`, `data_abertura`, `indice_demanda`.

## 4 · dim_produtos

Grão: Uma linha por SKU. Linhas: 5,000. Campos (11): `id_produto`, `nome_produto`, `categoria`, `subcategoria`, `marca`, `preco_lista_referencia`, `custo_unitario_referencia`, `eh_generico`, `eh_controlado`, `exige_receita`, `status`.

## 4 · f_despesas_mensais

Grão: Uma linha por loja e mês. Linhas: 96. Campos (7): `ano_mes`, `id_loja`, `aluguel`, `pessoal`, `operacionais`, `marketing_canais`, `despesa_total`.

## 4 · f_estoque_inicial

Grão: Uma linha por loja/SKU em 30/09/2024. Linhas: 16,562. Campos (4): `id_loja`, `id_produto`, `quantidade_inicial`, `data_base`.

## 4 · f_estoque_mensal

Grão: Uma linha por loja/SKU/mês com movimento. Linhas: 222,238. Campos (9): `ano_mes`, `id_loja`, `id_produto`, `estoque_inicial`, `qtd_entradas`, `qtd_vendida`, `qtd_perdas`, `estoque_final`, `custo_unitario_referencia`.

## 4 · f_itens_venda

Grão: Uma linha por SKU em um cupom. Linhas: 322,277. Campos (11): `id_item`, `id_venda`, `id_loja`, `id_produto`, `data_venda`, `quantidade`, `preco_unitario_bruto`, `taxa_desconto`, `valor_desconto`, `valor_liquido`, `custo_total`.

## 4 · f_metas_mensais

Grão: Uma linha por loja e mês. Linhas: 96. Campos (4): `ano_mes`, `id_loja`, `meta_receita`, `meta_lucro_bruto`.

## 4 · f_vendas

Grão: Uma linha por cupom. Linhas: 143,399. Campos (11): `id_venda`, `data_venda`, `id_loja`, `id_cliente`, `canal`, `forma_pagamento`, `qtd_itens_distintos`, `valor_bruto`, `valor_desconto`, `valor_liquido`, `custo_mercadoria`.

## 4 · ponte_produto_fornecedor

Grão: Associação entre produto e fornecedor. Linhas: 5,000. Campos (2): `id_produto`, `id_fornecedor`.

## 5. Modelo semântico e relacionamentos

Modelo em estrela com fatos separados. Ativos, 1:N, direção única: dim_calendario[data] → f_vendas[data_venda]; dim_lojas[id_loja] → f_vendas[id_loja], f_itens_venda[id_loja], f_estoque_mensal[id_loja], f_estoque_inicial[id_loja], f_metas_mensais[id_loja], f_despesas_mensais[id_loja]; dim_produtos[id_produto] → f_itens_venda[id_produto], f_estoque_mensal[id_produto], f_estoque_inicial[id_produto]; dim_clientes[id_cliente] → f_vendas[id_cliente]. Recomenda-se vincular f_vendas[id_venda] → f_itens_venda[id_venda] com direção única de vendas para itens, evitando ativar simultaneamente caminhos ambíguos de filtros via loja/data. Para análise produto→receita, calcular na fato itens; para análise canal→produto, usar uma dimensão separada de venda enriquecida no Power Query ou TREATAS/controlar caminhos de filtro; não habilitar bidirecional indiscriminadamente. Estoque e metas usam ano_mes: criar dim_mes com ano_mes como chave e data_inicio_mes real; ligar em fatos mensais. Datas de fatos de itens podem ficar sem relação ativa com calendário se houver caminho por venda; documentar opção escolhida e testar filtros. Ponte fornecedor: inspecionar cardinalidade (fonnecedor único ou múltiplo por SKU) antes de usar no modelo.

## 6. Regras de negócio

Receita bruta = soma f_vendas[valor_bruto]. Desconto = soma f_vendas[valor_desconto]. Receita líquida = soma f_vendas[valor_liquido] = receita bruta − descontos. CMV = soma f_vendas[custo_mercadoria]. Lucro bruto = receita líquida − CMV. Margem bruta % = lucro bruto / receita líquida. Ticket médio = receita líquida / número distinto de cupons. Itens por cupom = soma f_itens_venda[quantidade] / cupons; NÃO confundir unidades com SKUs distintos. Percentual desconto = desconto / receita bruta. Despesa = soma f_despesas_mensais[despesa_total]. Resultado operacional simplificado = lucro bruto − despesa (não EBITDA contábil). Meta receita = soma f_metas_mensais[meta_receita]; atingimento = receita líquida / meta. Resultado por produto/categoria deve usar f_itens_venda[valor_liquido] e f_itens_venda[custo_total]. Não somar valores das duas granularidades no mesmo cálculo. Cliente identificado = id_cliente não vazio; cupom anônimo NÃO é cliente único. Estoque final = estoque inicial + entradas − vendida − perdas. Estoque é semiaditivo: agregue lojas/SKUs na mesma data de corte, não some saldos de meses diferentes. Ausência no snapshot com movimento não significa estoque zero. Ruptura real e validade de lotes não estão disponíveis; apenas proxies devidamente rotuladas.

## 7. Medidas DAX propostas

Crie pasta 00 Base: [Receita Bruta] = SUM(f_vendas[valor_bruto]); [Descontos] = SUM(f_vendas[valor_desconto]); [Receita Líquida] = SUM(f_vendas[valor_liquido]); [CMV] = SUM(f_vendas[custo_mercadoria]); [Cupons] = DISTINCTCOUNT(f_vendas[id_venda]); [Quantidade Vendida] = SUM(f_itens_venda[quantidade]); [Despesas] = SUM(f_despesas_mensais[despesa_total]); [Meta Receita] = SUM(f_metas_mensais[meta_receita]). Pasta 01 KPIs: [Lucro Bruto] = [Receita Líquida]-[CMV]; [Margem Bruta %] = DIVIDE([Lucro Bruto],[Receita Líquida]); [Ticket Médio] = DIVIDE([Receita Líquida],[Cupons]); [Desconto %] = DIVIDE([Descontos],[Receita Bruta]); [Resultado Operacional Simplificado] = [Lucro Bruto]-[Despesas]; [Atingimento Meta %] = DIVIDE([Receita Líquida],[Meta Receita]); [Itens por Cupom] = DIVIDE([Quantidade Vendida],[Cupons]). Para crescimento YoY utilizar DATEADD(dim_calendario[data],-1,YEAR) com período equivalente e dados fechados. Para produtos construir medidas na fato itens, evitando reuso ingênuo de medidas da fato cupom. Medidas de estoque devem buscar último snapshot disponível por loja/produto e transportar saldos quando não há movimento; implementar e validar antes de habilitar indicadores de cobertura.

## 8. Páginas e experiência analítica

HOME: marca FarmaVitta, período de cobertura, botões para as cinco páginas e aviso de dados fictícios. 01 VISÃO EXECUTIVA: receita, lucro bruto, margem, resultado simplificado, meta, linhas de tendência, ranking das lojas. 02 COMERCIAL & CLIENTES: canal, loja, ticket, frequência, coortes simples, novos versus recorrentes, RFV com recorte de clientes identificados. 03 PRODUTOS & RENTABILIDADE: contribuição categoria/subcategoria/SKU, margem, volume, desconto, Pareto, itens negativos/baixo retorno. 04 ESTOQUE & ABASTECIMENTO: saldo valorizado e unidades, entrada/saída/perda, cobertura estimada por média móvel, excesso e ausência de movimento (não rotular como ruptura observada). 05 LOJAS & PERFORMANCE: comparação das 4 unidades, receita/margem/despesas/metas e evolução mensal. Máximo aproximado de 5–7 objetos analíticos por página; aproveitar tooltips para detalhes, não poluir telas.

## 9. Design system PBIP

Direção visual: petróleo #103D45, turquesa #18B89F, menta #DDF5EB, fundo #F7FAF9, coral #EF9277 para alertas; tipografia Aptos ou Segoe UI. Layout 16:9, 1600×900, espaçamento consistente de 8/16/24 px, conteúdo até 1440 px de largura, poucos elementos bem proporcionados. Cards HTML Content/CSS e Deneb/SVG podem ser usados somente se a configuração PBIP suportar o visual; evitar dependências que impeçam o funcionamento em Power BI Service. Animações leves e opcionais; contraste WCAG, foco de teclado e tooltips contextualizados. Usar formato pt-BR de moeda, quantidade, porcentagens, e explicitar datas e filtros. Navegação com botões ou bookmarks discretos; não esconder filtros críticos do usuário.

## 10. Qualidade, reconciliação e testes

Gate mínimo antes da entrega: unicidade de dimensões e f_vendas[id_venda] e f_itens_venda[id_item]; chaves estrangeiras válidas; 4 lojas/5000 produtos/24 meses; soma receita/custo bate com resumo; em cada venda, soma itens líquido/custo deve bater com cabeçalho dentro de tolerância centesimal; receita_bruta-descontos=líquida; estoques por linha conciliam abertura+entradas−vendida−perdas; despesas totais iguais às rubricas; metas completas por loja/mês; ausência de relações many-to-many não planejadas; validar cortes por ano, loja, canal, produto. Testar datas sem vendas, vendas anônimas, meses sem movimento, SKUs sem vendas, seleções múltiplas e totais. Comparar painel executivo com agregações em Python/SQL. Verificar desempenho via Performance Analyzer, DAX Studio e VertiPaq Analyzer quando disponíveis.

## 11. Limitações e backlog

Não há lotes, vencimento, devoluções, impostos detalhados, impostos sobre vendas, contas a pagar, transações de compra por pedido, prescrições, SNGPC, custo logístico por pedido ou satisfação de cliente. Logo, não afirmar validade, ruptura verdadeira, EBITDA, fluxo de caixa, LTV econômico ou desempenho regulatório. V2 sugerida: f_lotes_validade, f_pedidos_compra, f_entradas_estoque, f_devolucoes, f_preco_historico, f_rupturas_diarias, f_campanhas e tabela de custos por canal. Atualização exigirá revisões de modelagem, reconciliação e versionamento do modelo.

## 12. Handoff para Claude

Entrada: 12 CSVs, LEIA-ME.md, RESUMO_BASE.json, esta documentação. Saída desejada: projeto PBIP funcional, sem alterar qualquer dado-fonte, com Power Query de tipagem explícita/UTF-8 BOM/separador ;/decimal ponto, modelo organizado, measures DAX versionadas, páginas conforme design, documentação de relações e testes, pacote de evidências. Não criar fatos inexistentes nem reportar KPIs indisponíveis. Antes de escrever visuais, documentar arquitetura proposta e verificar tabelas/colunas reais. Usar parâmetros de pasta relativos e preservar portabilidade. Ao finalizar, abrir no Power BI Desktop, atualizar, verificar erros de visuais e capturar screenshots das cinco páginas; exportar PBIX somente após testes e com Desktop compatível.

## 13. Critérios de aceite

Todas as tabelas importam sem erro; 5.000 SKUs e 4 lojas; 24 meses; KPIs principais reconciliados com CSVs; visualizações fazem cross-filter coerente; valores de estoque por período não duplicados; nenhuma métrica não suportada; acessibilidade/legibilidade; Home + 5 páginas; arquivo PBIP reabre e atualiza, com pelo menos 1 evidência de validação por página.