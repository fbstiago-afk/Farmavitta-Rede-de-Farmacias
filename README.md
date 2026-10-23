# FarmaVitta — Rede de Farmácias · Power BI (PBIP)

Projeto de portfólio em **Power BI (PBIP / PBIR / TMDL)** para uma rede fictícia de 4 farmácias no interior de SP (Campinas, Jundiaí, Sorocaba e Piracicaba): vendas, clientes, mix, compras, estoque e validade, resultado e previsão.

> Empresa e dados **100% sintéticos**. Período: 01/10/2024 a 30/09/2026 · 5.000 SKUs · 22 mil clientes · 143.399 cupons.

## Duas versões no mesmo projeto

As duas versões usam **o mesmo modelo de dados e os mesmos CSVs** (`01_Dados_Originais`, `02_Dados_Tratados`). A diferença está na camada visual e nas medidas de apresentação.

| | [v1 · Clássico](v1_Classico/) | [v2 · Moderno (HTML + Deneb)](v2_Moderno_HTML_Deneb/) |
|---|---|---|
| Arquivo | `v1_Classico/FarmaVitta.pbip` | `v2_Moderno_HTML_Deneb/FarmaVitta_v2.pbip` |
| Visual | Claro, fiel ao manual da marca (60% branco gelo) | Escuro com as cores da marca, vidro/neon |
| Navegação | Botões no cabeçalho | Menu lateral + Home com botão **Iniciar** |
| KPIs | Cartões nativos com variação colorida | Cards **HTML Content** com sparkline SVG animada e cor semântica |
| Gráficos | Nativos | 7 **Deneb / Vega-Lite** (waterfall, heatmaps, Pareto, faixa de previsão…) + nativos para filtro cruzado |
| Filtros | Barra visível + "Limpar filtros" | Painel oculto por **bookmarks** + chips de filtros ativos |
| Visuais externos | Nenhum | Deneb e HTML Content (AppSource) |
| Medidas DAX | 183 | 248 |
| Validação no Desktop | ✅ v1.0 aberta, atualizada e auditada ([prints](v1_Classico/prints)) | ⚠️ Pendente de abertura no Desktop ([detalhes](v2_Moderno_HTML_Deneb/VALIDACAO_v2.md)) |

## Como abrir

1. Clone o repositório (ou baixe o ZIP).
2. Abra o `.pbip` da versão desejada no **Power BI Desktop 2025/2026** (formato PBIR).
3. Em *Transformar dados → Editar parâmetros*, troque **`PastaProjeto`** pelo caminho da pasta raiz do clone, **terminando com `\`** (ex.: `C:\repos\Farmavitta-Rede-de-Farmacias\`), e clique em **Atualizar**.
4. Na v2, abra com internet: os visuais Deneb e HTML Content são baixados do AppSource, e o tenant precisa permitir visuais do AppSource.
5. No modo de edição, use **Ctrl + clique** nos botões.

## Modelo semântico

- Esquema estrela: 19 tabelas, 27 relacionamentos 1:N de direção única, sem bidirecional, sem N:N e sem relação fato–fato.
- Receita e CMV da rede vêm de `fVendas` (cupom); produto e categoria vêm de `fItensVenda`. As duas granularidades nunca são somadas juntas.
- O estoque é **semiaditivo**: um saldo completo loja × SKU × mês foi reconstruído para que meses sem movimento carreguem o saldo anterior.
- **Resultado operacional simplificado = lucro bruto − despesas modeladas** (não é EBITDA).
- Previsão de 6 meses: 3 métodos simples comparados por backtest rolling-origin, com faixa empírica de ~80%.

## Números de referência (reconciliados com DAX)

| Indicador | Valor |
|---|---|
| Receita líquida | R$ 35.060.712,00 |
| Lucro bruto / margem | R$ 13,81 mi / 39,4% |
| Resultado operacional simplificado | R$ 7,75 mi (22,1%) |
| Receita jan–set/2026 vs jan–set/2025 | +13,5% |
| Estoque final 30/09/2026 | R$ 12,52 mi · cobertura de ~414 dias |
| Previsão out/26–mar/27 | R$ 9,99 mi · WAPE do backtest de 8,1% |

**Achado principal:** a rede está com estoque superdimensionado. 88% do valor em estoque tem cobertura acima de 120 dias.

## Estrutura

```
├── 01_Dados_Originais/      CSVs originais e complementares (imutáveis)
├── 02_Dados_Tratados/       saldo de estoque, previsão + backtest, RFV, ABC (reprodutíveis)
├── v1_Classico/             PBIP v1 + validação + prints
├── v2_Moderno_HTML_Deneb/   PBIP v2 + specs Deneb + validação + prévia dos fundos
├── 00_Governanca/           prompt mestre, documentação funcional, CHANGELOG, checklist
├── 05_Design_System/        manual de identidade e logo
├── 06_Mockups/              referência visual original
├── 07_Testes/               GATE A: auditoria dos dados (64 testes, todos PASS)
├── 08_Documentacao/         README técnico, limitações, design system, dicionário/contrato de métricas (v1 e v2)
└── 10_Scripts/              geradores Python (dados, auditoria, modelo TMDL, relatório PBIR, docs)
```

## Regenerar

```bash
python 10_Scripts/01_auditoria_gate_a.py .
python 10_Scripts/02_dados_tratados.py .
python 10_Scripts/03_rfv_abc.py .
python 10_Scripts/pbip/build.py    saida_v1 05_Design_System/a_clean_transparent_background_logo_graphic_png_l.png
python 10_Scripts/pbip/build_v2.py saida_v2 05_Design_System/a_clean_transparent_background_logo_graphic_png_l.png
```

Os builds são determinísticos. Passe a pasta clonada de `microsoft/json-schemas` como 3º argumento para validar todos os JSON do relatório contra os esquemas oficiais.

## Limitações

Não há EBITDA, impostos, fluxo de caixa, OTIF (sem pedidos de compra), ruptura real nem histórico de validade (os lotes são uma foto simulada de 30/09/2026). Detalhes em [08_Documentacao/06_Limitacoes_e_Backlog.md](08_Documentacao/06_Limitacoes_e_Backlog.md).
