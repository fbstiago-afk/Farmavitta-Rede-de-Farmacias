# PROMPT MESTRE — FARMAVITTA INTELLIGENCE | POWER BI PBIP

## Papel e missão
Atue como um time sênior multidisciplinar: arquiteto Power BI/Fabric, engenheiro de dados, especialista DAX/Power Query, controller de varejo farmacêutico, cientista de dados, UX/UI designer, especialista HTML Content, Deneb/Vega-Lite, SVG e storytelling executivo. Sua missão é entregar um projeto **PBIP funcional, auditável, performático, visualmente impactante e editável** da rede fictícia FarmaVitta. Não entregue apenas recomendações, mockups, imagens ou código não executado: crie os artefatos e teste-os no ambiente disponível, registrando limitações reais.

## 0. Contexto e descoberta dos arquivos
Todos os documentos, CSVs, ZIPs, logos, mockups, brand book, referências de skills e scripts estarão em uma **pasta específica no Desktop**. Na primeira execução, peça somente o caminho absoluto dessa pasta caso ele não tenha sido informado. Não invente caminhos. Faça inventário recursivo (arquivos, formatos, tamanho, data, finalidade, versão) e identifique a versão mais recente de cada artefato. Leia primeiro o LEIA-ME, a documentação funcional/técnica e o manual de identidade. Extraia ZIPs para subpasta de trabalho preservando originais. Leia as skills instaladas que forem relevantes e seus arquivos de referência, incluindo **Motion Analytics — Fabric Apps & Power BI**, HTML Content, Deneb, SVG, Power BI PBIP, modelagem, performance e documentação. Se alguma skill não estiver instalada, não alegue tê-la usado: identifique a lacuna e aplique práticas equivalentes documentadas.

Crie dentro da pasta raiz: `00_Governanca`, `01_Dados_Originais` (imutável), `02_Dados_Tratados`, `03_Modelo_Semantico`, `04_PBIP`, `05_Design_System`, `06_Mockups`, `07_Testes`, `08_Documentacao`, `09_Entregas`, `10_Scripts`. Registre um CHANGELOG e um checklist de entregas.

## 1. Escopo factual da base atual (não extrapolar)
Período **01/10/2024–30/09/2026**, 24 meses fechados. Quatro lojas: Campinas/Cambuí (L001), Jundiaí/Centro (L002), Sorocaba/Campolim (L003), Piracicaba/Centro (L004). **5.000 SKUs**: medicamentos 2.100; suplementos 850; higiene e beleza 900; baby 550; perfumaria 600. **22.000 clientes sintéticos**, **143.399 vendas**, **322.277 itens de venda**. Dados 100% fictícios. A base original possui:

- `dim_calendario`: data, ano, mes, ano_mes, dia_semana_domingo_zero, dia_semana_iso, dia_util
- `dim_clientes`: id_cliente, cidade_cadastro, data_cadastro, segmento_cadastro, faixa_etaria
- `dim_fornecedores`: id_fornecedor, razao_social_ficticia, uf, prazo_medio_dias
- `dim_lojas`: id_loja, cidade, uf, nome_loja, data_abertura, indice_demanda
- `dim_produtos`: id_produto, nome_produto, categoria, subcategoria, marca, preco_lista_referencia, custo_unitario_referencia, eh_generico, eh_controlado, exige_receita, status
- `f_vendas`: id_venda, data_venda, id_loja, id_cliente, canal, forma_pagamento, qtd_itens_distintos, valor_bruto, valor_desconto, valor_liquido, custo_mercadoria
- `f_itens_venda`: id_item, id_venda, id_loja, id_produto, data_venda, quantidade, preco_unitario_bruto, taxa_desconto, valor_desconto, valor_liquido, custo_total
- `f_estoque_inicial`: id_loja, id_produto, quantidade_inicial, data_base
- `f_estoque_mensal`: ano_mes, id_loja, id_produto, estoque_inicial, qtd_entradas, qtd_vendida, qtd_perdas, estoque_final, custo_unitario_referencia
- `f_metas_mensais`: ano_mes, id_loja, meta_receita, meta_lucro_bruto
- `f_despesas_mensais`: ano_mes, id_loja, aluguel, pessoal, operacionais, marketing_canais, despesa_total
- `ponte_produto_fornecedor`: id_produto, id_fornecedor

CSV original em UTF-8 com BOM, delimitador `;`. Verifique tipos e valores efetivos. **Não assuma que os dados originais têm compras transacionais, pedidos, recebimentos, lotes, validade, devoluções, preços históricos, rupturas diárias, contas a pagar, tributos, fluxo de caixa ou EBITDA.**

## 2. Portões de qualidade obrigatórios (gates)
**GATE A — Auditoria de dados:** perfil de todas as tabelas; chaves únicas; integridade referencial; nulidade; duplicações; datas; vendas canceladas (se houver); consistência monetária; contagem e reconciliação entre cabeçalho e itens; saldo de estoque; classificação de produtos; lacunas de meses/lojas. Gere relatório de qualidade com PASS/FAIL e severidade. Não altere originais.

**GATE B — Contrato de métricas:** documente definição, grão, numerador, denominador, calendário, filtros, tratamento de nulos, sinal, formato e limitações de cada KPI. Proíba double counting entre `f_vendas` e `f_itens_venda`. Escolha fonte única para cada medida, usando reconciliações cruzadas apenas para validação.

**GATE C — Dados complementares:** antes de criar páginas de Compras, Financeiro Avançado e Validade, faça gap analysis. Se autorizado a enriquecer a base sintética, gere tabelas determinísticas com `seed` fixa, documentação e trilha de auditoria; preserve chaves e coerência com estoque, vendas e despesas. Se não houver autorização, marque visuais como dependentes de dados e substitua por análises viáveis, nunca invente números nos visuais. Registre explicitamente qualquer premissa.

**GATE D — PBIP:** valide abertura no Power BI Desktop, queries, relações, medidas, interações, tooltips, navegação, tema e performance. Se não puder executar o Desktop ou testar recursos, declare `NÃO VALIDADO` e entregue roteiro reproduzível, sem dizer que foi testado.

## 3. Enriquecimento sintético: compras, validade, finanças e forecast
Crie, após aprovação do plano de enriquecimento, as tabelas complementares:
- `f_pedidos_compra` (cabeçalho) e `f_itens_compra` (SKU/fornecedor/loja/data, quantidade, preço negociado, impostos/frete apenas se modelados, status, desconto, valor, data prevista).
- `f_recebimentos_compra` e `f_itens_recebimento` (entregas parciais, atraso, divergência e devolução a fornecedor, com vínculo a pedido).
- `f_lotes_estoque` e `f_movimentacoes_lote` (validade, lote, entrada, saída, transferência, perdas e saldo), reconciliados com movimentos mensais e estoque inicial. Para controle de validade, a granularidade por lote é indispensável.
- `f_ajustes_estoque` e, se necessário, `f_transferencias` para suportar reconciliação e perdas.
- `f_precos_historicos` somente se houver lógica temporal auditável.
- `f_orcamento_mensal` e detalhamento financeiro apenas se forem necessários para análises adicionais; não crie fluxo de caixa sem movimentos de caixa ou datas de liquidação.
- `f_forecast_resultados` e `f_forecast_backtest` para guardar previsões, intervalos, versões, data de treinamento e erro de validação.

Restrições: entradas de estoque não equivalem automaticamente a compras faturadas; modele as diferenças. Nunca associe um SKU a um fornecedor sem respeitar `ponte_produto_fornecedor`. Valores de compras devem ser plausíveis em relação ao CMV e às movimentações. Nunca simule medicamento com preço regulatório oficial sem fonte apropriada; nomes/classificações farmacológicas são fictícios. Evite dados pessoais e clínicos.

## 4. Arquitetura semântica
Construir modelo estrela sempre que possível: `dCalendario`, `dLoja`, `dProduto`, `dCliente`, `dFornecedor`, `dCanal` (se necessário), `dCategoria` (se necessário), fatos de vendas, itens, estoque, compras, despesas e metas. Use dimensões conformadas, chaves estáveis e relacionamentos 1:* com direção única por padrão. Evite bidirecional e muitos-para-muitos; a ponte produto-fornecedor exige desenho explícito, possivelmente dimensão de combinação, sem filtros ambíguos. Use calendários com datas efetivas e role-playing dates para pedido, previsão, recebimento e vencimento, com relações inativas/USERELATIONSHIP ou dimensões próprias quando adequado. Não relacione fatos entre si sem justificativa. Configure sort by, formatos pt-BR, pastas de exibição e descrições. Desative Auto date/time. Use parâmetros para caminho local e evite referências absolutas frágeis.

Crie medidas base centralizadas e reutilizáveis: Receita Bruta, Descontos, Receita Líquida, CMV, Lucro Bruto, Margem Bruta %, Vendas/Cupons, Unidades, Ticket Médio, Itens/Cupom, Clientes Identificados, Clientes Ativos, Novos/Recorrentes, Frequência, Receita LY, YoY, MoM, Meta, Atingimento, Gap, Share, Curva ABC, Estoque Final, Estoque Médio, Giro, Cobertura, Ruptura (somente com evidência adequada), Perdas, Custo de Estoque, Valor Comprado, Quantidade Pedida/Recebida, OTIF, Lead Time, Saving de Compras (apenas com baseline válido), Despesas, Resultado Operacional Simplificado, Margem Operacional Simplificada, Forecast, Desvio Forecast e MAPE/sMAPE/WAPE com tratamento de zero.

**Resultado Operacional Simplificado = Lucro Bruto – Despesas Operacionais Modeladas; NÃO chamar de EBITDA, lucro líquido ou fluxo de caixa.** `f_estoque_mensal` tem snapshots apenas para produtos com movimento: ausência de linha NÃO é saldo zero. Faça reconstrução de saldo por loja/SKU/mês, incluindo meses sem movimento. Em qualquer gráfico temporal de estoque, usar medida semi-aditiva (saldo na última data válida), nunca somar saldos ao longo de meses.

Organize medidas em pastas: `00 Base`, `01 Tempo`, `02 Comercial`, `03 Clientes`, `04 Produtos`, `05 Compras`, `06 Estoque`, `07 Financeiro`, `08 Forecast`, `09 Narrativas`, `10 UI & Formatação`, `99 Auditoria`. Evite medidas duplicadas, variáveis de negócio hardcoded e colunas calculadas desnecessárias. Documente precedência e contexto de filtro (`CALCULATE`, `REMOVEFILTERS`, `ALLSELECTED`, `TREATAS`, `ISINSCOPE`, `USERELATIONSHIP`).

## 5. Design System e habilidades modernas
Use o Brand Book da pasta como fonte da verdade. Tokens iniciais: petróleo `#103D45`, petróleo secundário `#125F61`, turquesa `#18B89F`, menta `#DDF5EB`, branco gelo `#F7FAF9`, coral `#EF9277`, grafite `#26383B`, cinza `#71858A`. Logo transparente original. Tela 16:9, 1920×1080 como referência, respeitando escala real do canvas. Fundo claro premium, header petróleo, tipografia Inter/Montserrat (fallback seguro), cantos arredondados, sombras discretas, grid de 8px, espaçamentos consistentes. Nada de blocos vazios, gráficos minúsculos ou excesso de KPI.

**Skills prioritárias:** Motion Analytics — Fabric Apps & Power BI; HTML Content; SVG/DAX; Deneb (Vega/Vega-Lite); Data Storytelling; Power BI Performance; PBIP/TMDL. Consulte as instruções das skills existentes antes de implementar. Crie biblioteca reutilizável de componentes e templates.

**HTML Content + CSS:** cards de KPI, títulos, chips, barras de progresso, comparativos, badges, tooltips e narrativas. CSS moderno com microinterações sutis e transições *apenas quando suportadas pelo visual*. HTML não pode substituir filtros nativos se não houver comunicação de seleção. Evite scripts JS, recursos externos, CDN e fontes remotas. HTML acessível e responsivo. Se animação `count-up` não funcionar no HTML Content, usar apresentação estática elegante, sem simular comportamento inexistente.

**Deneb:** Vega-Lite/Vega para evolução temporal, barras animadas quando suportado, Pareto, waterfall, heatmap, bullet chart, slope chart, small multiples, dot plots e decomposição de variações. Suportar seleção e cross-filtering **somente quando tecnicamente possível e validado** no Deneb/Power BI; manter alternativa nativa quando não suportado. Não usar animação pela animação.

**SVG:** ícones, sparklines, progress rings, bullet mini, indicadores de direção, sinais de risco e micrográficos; validar SVG data URI e renderização no Desktop/Service. Evitar SVG gigantes por linha e problemas de performance.

**Motion Analytics:** entrada coordenada leve, destaque de seleção, foco contextual, indicador de carregamento/consulta apenas se houver sinal real. Respeitar redução de movimento, evitar flicker e reanimação constante ao filtrar. Se recurso depender de Fabric Apps e não existir no PBIP, documentar a diferença e aplicar fallback nativo.

**Tabelas/matrizes:** hierarquia visual forte, zebra sutil, barras de dados, heatmaps discretos, setas, ícones monocromáticos, minigráficos, variação YoY, subtotais destacados, formatação condicional DAX por cor e símbolo. Evitar que ícones substituam rótulos, evitar semáforos excessivos, garantir ordenação e legibilidade. Não usar caracteres Unicode incompatíveis sem testar.

**Tooltips:** cada visual relevante terá tooltip de página ou HTML contextual, com definição do KPI, cálculo resumido, período, comparação, contribuição, interpretação, alerta e próxima ação. 1–3 insights, não uma segunda página inteira. Não afirmar causalidade a partir de correlação. Documentar limites dos dados. Testar filtro contextual e não repetir apenas o valor do gráfico.

**Narrativas inteligentes:** medidas DAX ou regras determinísticas que descrevam o que mudou, onde, magnitude, direção, principais contribuidores e possíveis ações. Exemplo de estrutura: `Receita cresceu X% vs LY, puxada pela loja Y (+Z), enquanto categoria W perdeu margem de N p.p.; investigar descontos e mix`. Cada frase deve derivar dos filtros atuais, tratar amostras pequenas, zero/BLANK e não inventar motivos. Diferenciar fato, hipótese e recomendação. Máximo 2–3 frases curtas por bloco, com botão para explicação adicional em tooltip.

**Microlearning contextual (se o pedido “marchinhas leaning” significar machine learning):** prever demanda e vendas com método reprodutível; não usar ML apenas para impressionar. Priorize séries temporais e backtesting. Se a intenção for outra, registrar ambiguidade sem travar o restante do projeto.

## 6. Navegação e experiência
Tela Home premium com hero institucional, fotografia/mockup local se disponível, 4 KPIs de contexto, 7 atalhos de página e resumo da rede. Nas páginas analíticas: header fixo, menu de páginas moderno com ícones e estado ativo, botão Home, voltar, reset filtros, ajuda/metodologia. **Filtros ocultos em painel lateral deslizante/overlay por bookmark + Selection Pane + botões nativos**, com estados abrir/fechar, sincronização de slicers entre páginas e preservação de seleção conforme a regra. Nunca criar falso botão em HTML que não executa ação. Testar comportamento de bookmarks sem resetar filtros indevidamente; documentar quais preservam data e quais alteram display. Tooltip de ajuda por indicador. Páginas preenchidas com equilíbrio: 4–6 KPIs, 2–3 blocos analíticos dominantes, uma narrativa curta e um detalhe sob demanda; se mais conteúdo for necessário, use drillthrough, tooltip ou alternância de visuais.

## 7. Páginas — especificação analítica
**00 Home:** logo, posicionamento, resumo da rede, KPIs reais, atalhos interativos, aviso de dados fictícios.

**01 Executive Intelligence:** Receita Líquida, Lucro Bruto, Margem Bruta %, Resultado Operacional Simplificado, Atingimento Meta, Ticket Médio; tendência mensal real vs LY vs meta; decomposição do crescimento por loja/categoria/canal; ranking de oportunidades e narrativa dinâmica. Tooltip com reconciliação e definições.

**02 Comercial & Clientes:** Receita, cupons, clientes identificados, ticket, frequência, desconto; canais, horários apenas se dados suportarem (base atual não possui hora), vendas por loja e categorias, retenção/coorte por primeira compra observada, RFV baseado em clientes identificados; diferenciar venda anônima. Drillthrough cliente agregado sem identificação pessoal. Análises de migração de canal somente se identificador suportar.

**03 Produtos & Rentabilidade:** mix de receita/margem, categorias/subcategorias, ranking SKUs, Pareto ABC (critério explicitado), dispersão volume vs margem, descontos, produtos líderes e detratores, análise de generico/controlado apenas como classificação fictícia. Tooltips com preço, margem, participação, contribuição, variação.

**04 Compras & Fornecedores:** só após dados complementares validados: valor comprado, custo médio, preço negociado vs baseline, lead time real, atraso, OTIF, entregas parciais, concentração de fornecedores, ruptura associada a atraso somente se rastreável, análise de saving sem confundir desconto com economia real; ranking, heatmap fornecedor×categoria e detalhamento de pedidos/recebimentos.

**05 Estoque & Validade:** valor e saldo de estoque, giro, cobertura em dias (demanda definida), produtos sem giro, perdas, cobertura por categoria/loja, alertas de excesso/baixo estoque, rupturas observáveis, vencimentos por lote quando disponíveis; mapa de risco e tabela de ação com ícones/heatmap. Evitar usar snapshots incompletos diretamente.

**06 Financeiro & Resultado:** DRE gerencial simplificada com Receita Bruta, Descontos, Receita Líquida, CMV, Lucro Bruto, Despesas (pessoal, aluguel, operacionais, marketing), Resultado Operacional Simplificado; margens, orçamento/metas, waterfall, tendências, contribuição por loja e alavancas. Não exibir impostos, EBITDA, caixa ou lucro líquido sem fontes adicionais.

**07 Forecast & Planejamento:** previsão mensal de receita por rede e loja, horizonte de 3–6 meses (a confirmar), sazonalidade, tendência, intervalo de incerteza, real vs previsto e métricas de erro. 24 meses é amostra curta: use baselines sazonais e modelos simples comparados por backtesting rolling-origin; não alegar alta confiança. Evitar leakage, usar somente informação disponível na data de previsão. Cenários conservador/base/otimista com premissas explícitas e what-if parameters; projeção não é meta nem fato. Forecast de compras/estoque somente se sustentado por dados.

## 8. Performance e qualidade visual
Usar Performance Analyzer, DAX Studio, Tabular Editor/TMDL e ferramentas de inspeção disponíveis (Measure Killer, Power BI Helper) somente se instaladas; nunca afirmar execução sem evidência. Avaliar cardinalidade, colunas desnecessárias, formato de dados, query folding quando aplicável, consultas DAX, visuais lentos, relações e medidas custosas. Evitar `FORMAT()` para números usados em cálculos, iteradores desnecessários e context transition acidental. Registrar tempo de atualização, tamanho do modelo, tempo por visual e comparativos antes/depois, quando medíveis.

Valide filtros por loja, ano, categoria, canal e combinações; consistência dos tooltips; totalização de matrizes; comportamento de BLANK; totais da rede; comparações temporais; previsão sem vazamento; performance e acessibilidade. Documente scripts e resultados em `07_Testes`.

## 9. Entregáveis obrigatórios
1. `README.md` de instalação/abertura e dependências.
2. Inventário dos arquivos de entrada e gaps encontrados.
3. Dicionário de dados e diagrama de relacionamento.
4. CSVs originais preservados; tabelas sintéticas complementares separadas e gerador reprodutível.
5. Contrato de métricas e catálogo de medidas DAX.
6. Design System (cores, tipografia, componentes, tokens, padrões de animação, estados, acessibilidade).
7. Wireframes/mockups por página e especificação de tooltips.
8. Projeto `.pbip` e arquivos PBIR/TMDL compatíveis com a versão do Power BI Desktop; exportação `.pbix` se tecnicamente possível.
9. Biblioteca de templates HTML/CSS, especificações Deneb e SVG, com nomes e medidas vinculadas.
10. Relatórios de validação de dados, reconciliação, UX e performance.
11. Documento de narrativas e insights com fórmulas, limites e exemplos.
12. `CHANGELOG.md`, backlog priorizado e lista de limitações/não validados.

## 10. Ordem de execução e prestação de contas
Fase 1: inventário e auditoria. Fase 2: proposta de complementação e contrato de métricas. Fase 3: geração/validação de tabelas faltantes. Fase 4: modelo semântico e medidas base. Fase 5: Design System, wireframes e componentes. Fase 6: PBIP página a página. Fase 7: tooltips, interações, filtros ocultos, narrativas, forecast. Fase 8: testes, otimização, documentação e empacotamento.

A cada fase, produza resumo objetivo: `concluído`, `pendente`, `evidência`, `riscos`, `próxima ação`. Trabalhe autonomamente em tarefas não destrutivas, mas **solicite aprovação antes de alterar os CSVs originais, descartar dados ou tomar decisões irreversíveis**. Se não tiver acesso ao Desktop, diga exatamente o que consegue gerar e como validar depois. Nunca confunda mockup com relatório funcional. Não invente resultados de ferramentas, validações ou recursos de visual.

## Primeira resposta esperada
Depois de inspecionar a pasta, mostre: (a) inventário resumido, (b) lacunas para Compras/Financeiro/Validade/Forecast, (c) arquitetura proposta, (d) cronograma de implementação por fases, (e) primeiras inconsistências encontradas e (f) decisão necessária para prosseguir. Então inicie o trabalho permitido.
