# CHANGELOG — FarmaVitta Intelligence

## v1.1 — 22/10/2026
- Corrigido: o texto dos botões de navegação não aparecia. As propriedades do botão exigem o seletor de estado `{"id":"default"}`, formato confirmado num botão criado pelo próprio Desktop.
- Corrigido: medidas de ano anterior (Receita, Lucro, Cupons, Resultado, Clientes, Itens) com Ano = 2026 comparavam com 2025 inteiro (R$ 17,0 mi), porque o calendário vai até mar/2027. Agora são limitadas pela `_Data Base` (jan–set/2025 = R$ 12,25 mi). Validado por DAX.
- Corrigido: "Loja Curta" duplicava "Centro" (Jundiaí e Piracicaba). Agora usa a cidade.
- Corrigido: `editorSettings.json` com propriedade fora do esquema, que impedia a abertura no Desktop.
- Narrativas passam a usar cartão com quebra de linha. Curva ABC passa a comparar % da receita com % dos SKUs. Estoque com eixo secundário. DRE sem linha "Total" vazia. Gráfico de atingimento da meta por loja substitui o de variação, que ficava vazio sem período comparável.
- Novo botão "Limpar filtros" (ClearAllSlicers) em todas as páginas analíticas.

## v1.0 — 22/10/2026
- GATE A: auditoria com 64 testes, todos PASS.
- Dados tratados: saldo de estoque completo, previsão com backtest, RFV e ABC.
- Modelo TMDL (19 tabelas, 27 relações, 182 medidas) e relatório PBIR (9 páginas), validados contra os esquemas oficiais.

## v2.1 — 23/10/2026
- Primeira abertura da v2 no Power BI Desktop: HTML Content e Deneb renderizam.
- Corrigido: Pareto vazio (ordenação do eixo no Deneb), regra de 120 dias desenhada por categoria, meses de previsão vazios no gráfico de receita.
- Corrigido: linhas altas e barras SVG minúsculas nas tabelas (`imageHeight`, `imageWidth`, `columnWidth`).
- DRE por loja em R$ mil; título da barra superior menor.
- Prints das 8 páginas da v2 publicados.
