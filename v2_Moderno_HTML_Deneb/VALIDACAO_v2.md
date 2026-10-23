# Validação — FarmaVitta v2 (HTML Content + Deneb + PBIP)

Projeto: `v2_Moderno_HTML_Deneb\FarmaVitta_v2.pbip` · Gerado por `10_Scripts/pbip/build_v2.py` (skill powerbi-moderno-html-deneb-pbip). A v1 continua intacta em `v1_Classico\FarmaVitta.pbip`.

## O que mudou em relação à v1

| Item | v1 | v2 |
|---|---|---|
| Visual | Claro, header petróleo | Escuro com as cores da marca, vidro/neon, logo negativo |
| Navegação | Botões no header | Menu lateral em vidro (8 páginas), Home com botão **Iniciar** |
| KPIs | Cartões nativos + texto de variação | 1 HTML Content por página: 6 cards com valor, comparação, cor semântica (verde/âmbar/coral) e sparkline SVG de 12 meses animada em CSS |
| Gráficos principais | Nativos | 7 Deneb/Vega-Lite: receita mensal com destaque do maior mês, mapa de calor dia × mês, Pareto, mapa de calor de pontualidade, dot plot de cobertura, waterfall da DRE, previsão com faixa |
| Filtros | Barra visível | Painel oculto por bookmarks (abrir/fechar por página), botões Aplicar e fechar / Limpar dentro do painel, chips HTML com filtros ativos no topo |
| Tabelas | Texto | Barras SVG por linha (ImageUrl) |
| Tooltip | Página com cartões | Página com HTML |
| Medidas | 183 | 248 (+65 em `11 SVG & HTML`, cores, narrativas HTML) |

## Testes

| # | Teste | Resultado |
|---|---|---|
| 1 | 222 JSON vs esquemas oficiais Microsoft | PASS, 0 erros |
| 2 | TMDL v2 importado pelo motor tabular | PASS |
| 3 | GUIDs dos visuais personalizados, conferidos no código-fonte oficial | PASS: HTML Content `htmlContent443BE3AD55E043BF878BED274D3A6855` (papel `content`); Deneb `deneb7E15AEF80B9E4D4F8E12924291ECE89A` (papel `dataset`, objeto `vega`) |
| 4 | Sparkline DAX no modelo com dados (Ano = 2026) | PASS: 12 pontos, out/25 a set/26 |
| 5 | Ano anterior corrigido (jan–set/2025) | PASS: R$ 12.250.944,38 |
| 6 | Waterfall Deneb (linhas 3 a 10) | PASS: fecha em R$ 7.747.142,78 = resultado operacional simplificado |
| 7 | Barra SVG proporcional na tabela de categorias | PASS: Medicamentos 116 px, Baby 57 px |
| 8 | Destaque inteligente do maior mês | PASS: só mai/26 (R$ 1,85 mi) fica turquesa |
| 9 | Abrir a v2 no Desktop, baixar Deneb/HTML do AppSource, renderizar cards e specs | **NÃO VALIDADO**: tela do computador indisponível durante a sessão |
| 10 | Bookmarks do painel de filtros (abrir, aplicar, limpar), Iniciar, menu lateral | **NÃO VALIDADO** (mesmo motivo) |
| 11 | Tempo dos cards HTML (alvo < 200 ms) | **NÃO MEDIDO** |
| 12 | Serviço / PDF / mobile | NÃO VALIDADO. No Serviço e no PDF a animação CSS aparece estática |

## Roteiro de validação (5 minutos)

1. Feche qualquer Power BI com a FarmaVitta aberta **sem salvar**.
2. Abra `v2_Moderno_HTML_Deneb\FarmaVitta_v2.pbip` com internet (os visuais Deneb e HTML Content são baixados do AppSource; o tenant precisa permitir visuais do AppSource).
3. Clique em **Atualizar**.
4. Home → **Iniciar** (Ctrl+clique no modo de edição) → percorra o menu lateral.
5. Em cada página: **Filtros** → escolha um Ano → **Aplicar e fechar** → confira os chips no topo e os cards.
6. Se algum Deneb mostrar o editor vazio, abra *Editar* e confira se `provider = Vega-Lite`. As specs estão em `v2_Moderno_HTML_Deneb\Deneb\*.vl.json`.

## Limitações conhecidas

- Deneb e HTML Content não fazem filtro cruzado por padrão. Os gráficos nativos (barras por loja/canal/categoria e tabelas) mantêm a interação.
- O botão Limpar (ClearAllSlicers) limpa apenas as segmentações da página.
- O âmbar `#F2C46D` foi adicionado para o estado de atenção (o manual só tem coral para alerta). É uma decisão a homologar no manual de marca.
- O logo negativo foi derivado do PNG (o lettering petróleo virou branco, mantendo alfa e turquesa). O manual pede uma versão oficial clara; esta é provisória.
