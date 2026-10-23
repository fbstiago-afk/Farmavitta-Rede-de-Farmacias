# FARMAVITTA — PACOTE PARA CLAUDE

Projeto fictício de rede farmacêutica para desenvolvimento de Power BI PBIP.

## Conteúdo
- 01_Base_Original: ZIP com CSVs de 24 meses, gerador Python e LEIA-ME.
- 02_Base_Complementar: ZIP com recebimentos, compras mensais, orçamento, resultado gerencial, cenários e fotografia de lotes.
- 03_Documentacao: documentação funcional/técnica em Markdown e Word.
- 04_Identidade_Visual: manual de identidade e arte de logo.
- 05_Referencias_Visuais: composição visual de referência (não é wireframe técnico validado).
- 06_Prompt_Claude: instrução mestre para implementação.

## Como começar no Claude
1. Extraia este pacote para uma pasta local.
2. Abra o arquivo 06_Prompt_Claude/FarmaVitta_PROMPT_MESTRE_CLAUDE_PBIP.md e use-o como instrução principal.
3. Informe ao Claude o caminho absoluto da pasta extraída.
4. Extraia também os dois ZIPs de dados e leia os LEIA-ME antes de modelar.
5. Valide o modelo, relacionamentos e reconciliações antes de criar medidas e páginas.

## Alertas
- Dados 100% sintéticos, 4 lojas, 5.000 SKUs, outubro/2024 a setembro/2026.
- Não somar compras ao CMV nem duplicar receita entre cabeçalho e itens.
- Fotografia de lotes representa apenas 30/09/2026, não histórico de validade.
- Resultado operacional simplificado não é EBITDA contábil.
- Imagem de referência visual não equivale a wireframes individuais finalizados.
- Arquivos PBIP/PBIX ainda não existem neste pacote.
