# FarmaVitta Intelligence — Power BI (PBIP)

Rede fictícia de 4 farmácias (Campinas, Jundiaí, Sorocaba, Piracicaba) · 5.000 SKUs · 01/10/2024 a 30/09/2026 · **dados 100% sintéticos**.

## Como abrir

1. Abra `v1_Classico\FarmaVitta.pbip` no Power BI Desktop (versão de 2025 ou mais recente: o relatório usa PBIR com esquema de visual 2.2.0 e o modelo usa TMDL).
2. Se a pasta do projeto **não** for `E:\Projetos BI\17 - Farmavitta\`, vá em *Transformar dados → Editar parâmetros* e troque `PastaProjeto` para o novo caminho (com `\` no final).
3. Clique em **Atualizar**. A carga lê 19 consultas a partir dos CSV em `01_Dados_Originais` e `02_Dados_Tratados` e leva cerca de 30 a 60 segundos.

Para regerar tudo do zero: rode, nesta ordem, `10_Scripts/01_auditoria_gate_a.py`, `02_dados_tratados.py` e `03_rfv_abc.py` (todos recebem a pasta raiz), depois `10_Scripts/pbip/build.py <saida> <logo.png> [json-schemas]`. A saída é determinística, sem números aleatórios.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| 00_Governanca | Prompt mestre, documentação funcional original, CHANGELOG, checklist |
| 01_Dados_Originais | CSV originais e complementares, **imutáveis** |
| 02_Dados_Tratados | Saldo de estoque completo, previsão com backtest, RFV, ABC (derivados, reprodutíveis) |
| v1_Classico · v2_Moderno_HTML_Deneb | Os dois projetos Power BI, cada um com sua validação |
| 05_Design_System | Manual de identidade, logo, tokens |
| 06_Mockups | Referência visual original (não é wireframe validado) |
| 07_Testes | GATE A (auditoria dos dados) |
| 08_Documentacao | Este README, dicionário, relacionamentos, contrato de métricas, páginas, limitações |
| 10_Scripts | Todos os geradores (dados, modelo, relatório, documentação) |

## O que tem no modelo

- 19 tabelas (6 dimensões, 10 fatos, 2 desconectadas, tabela de medidas), 27 relacionamentos 1:N de direção única e 183 medidas em 11 pastas (`00 Base` a `99 Auditoria`).
- 9 páginas: Home, Visão Executiva, Comercial & Clientes, Produtos & Rentabilidade, Compras & Fornecedores, Estoque & Validade, Financeiro & Resultado, Forecast & Planejamento e uma página de tooltip.

## Números de referência (todos conferidos com DAX no modelo aberto)

| Indicador | Valor |
|---|---|
| Receita líquida | R$ 35.060.712,00 |
| CMV | R$ 21.252.002,94 |
| Lucro bruto / margem | R$ 13,81 mi / 39,4% |
| Despesas modeladas | R$ 6,06 mi |
| Resultado operacional simplificado | R$ 7,75 mi (22,1%), **não é EBITDA** |
| Cupons / ticket médio | 143.399 / R$ 244,50 |
| Receita 2026 (jan–set) vs jan–set/2025 | R$ 13,90 mi vs R$ 12,25 mi (+13,5%) |
| Estoque final 30/09/2026 | R$ 12,52 mi · 245.063 un · cobertura ~414 dias |
| Previsão out/26–mar/27 (cenário base) | R$ 9,99 mi · WAPE do backtest 8,1% |
