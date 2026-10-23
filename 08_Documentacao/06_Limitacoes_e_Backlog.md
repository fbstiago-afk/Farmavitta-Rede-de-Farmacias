# Limitações, decisões e backlog

## Achados que contradizem o mockup/briefing (leia antes de apresentar)

1. **Estoque superdimensionado.** O saldo final (245 mil un) cobre ~414 dias de venda e 88% do valor fica acima de 120 dias de cobertura. O mockup mostrava "48 dias", um número sem base nos dados. O painel exibe o valor real.
2. **Os números do mockup são inventados.** Exemplos: lucro bruto de R$ 12,92 mi (real: R$ 13,81 mi) e margem de 36,8% (real: 39,4%).
3. **"Clientes novos" no período completo = 100% dos ativos.** É a primeira compra *observada*: a base começa em out/2024 e não há histórico anterior.
4. **Pontualidade de 42%** nos recebimentos sintéticos. Isso é OTD (entregue no prazo), não OTIF: a base não tem pedido nem quantidade prometida.
5. **Compras recebidas = 62,9% do CMV** em 24 meses. Faz sentido porque o estoque inicial foi sendo consumido: o saldo caiu de ~R$ 20 mi para R$ 12,5 mi.

## Decisões de projeto

| Decisão | Motivo |
|---|---|
| Filtros visíveis numa barra fixa, não num painel oculto com bookmarks | Bookmarks gravam o estado de cada visual pelo ID e quebram a cada edição. O documento funcional também pede para não esconder filtros críticos. |
| Visuais nativos + medidas DAX de texto/cor; **sem Deneb e sem HTML Content** nesta versão | São visuais personalizados do AppSource que precisam ser importados e liberados pelo tenant. Sem testar isso, entregá-los seria prometer algo não validado. Ficam no backlog. |
| Saldo de estoque reconstruído em Python (`02_Dados_Tratados`) | O `f_estoque_mensal` só tem linhas nos meses com movimento. A grade completa com saldo carregado evita somar meses ou tratar ausência como zero. |
| Calendário até 31/03/2027 | Cobre o horizonte da previsão. As medidas do ano anterior são limitadas pela data base (30/09/2026). |
| Classe ABC e RFV estáticos (período completo / foto 30/09/2026) | Recalcular dinamicamente para 5.000 SKUs × 22 mil clientes pesa no Desktop. A medida de Pareto dinâmico existe para uso em tabelas. |
| Previsão: 3 métodos simples comparados por backtest rolling-origin (h = 1 a 3) | Com 24 meses, um ML sofisticado não se justifica. O intervalo é empírico (~80%), e os horizontes 4 a 6 herdam o erro de h = 3 ampliado em 10% por mês (premissa). |
| "Loja Curta" = cidade | O sufixo do nome ("Centro") se repete em Jundiaí e Piracicaba. |

## Não suportado pela base (não aparece como fato no painel)

EBITDA, lucro líquido, fluxo de caixa, impostos, contas a pagar, OTIF, ruptura real (estoque zero não ocorre nos fechamentos mensais), devoluções, preço histórico, horário de venda, histórico de validade (os lotes são uma foto simulada de 30/09/2026).

## Status de validação (GATE D)

| Item | Status |
|---|---|
| JSON do relatório vs esquemas oficiais Microsoft | PASS (261 arquivos, 0 erros) |
| TMDL lido pelo motor tabular (importação de pasta) | PASS |
| Abertura no Power BI Desktop + atualização dos dados | PASS (v1). Erro de `editorSettings.json` encontrado e corrigido. |
| 183 medidas executadas via DAX no modelo aberto | PASS. Bug de ano anterior encontrado e corrigido (ver CHANGELOG). |
| Totais vs CSV (receita, CMV, cupons, saldo de lotes) | PASS |
| Visual da v2 (navegação com texto, narrativas com quebra de linha) | Ver `v1_Classico/VALIDACAO_v1.md` e `v2_Moderno_HTML_Deneb/VALIDACAO_v2.md` |
| Power BI Service / publicação | NÃO VALIDADO |
| Performance Analyzer / DAX Studio / VertiPaq | NÃO VALIDADO (nenhuma medição feita) |

## Backlog priorizado

1. Drillthrough "Detalhe do produto" e "Detalhe da loja".
2. Deneb: Pareto real por SKU e bullet chart de meta (após liberar o visual no tenant).
3. Painel de filtros recolhível por bookmark, só se o time aceitar o custo de manutenção.
4. Tooltips específicos por página (hoje existe um tooltip de receita para loja/canal/categoria).
5. Medição de performance no Desktop e publicação no Service.
6. V2 de dados: pedidos de compra (habilita OTIF), devoluções, preço histórico, lotes com histórico.
