# Design system FarmaVitta (Power BI)

Fonte: `05_Design_System/FarmaVitta_Manual_Identidade_Visual.docx`. Tema aplicado: `FarmaVitta_Tema.json` (registrado no relatório).

## Tokens

| Token | HEX | Uso |
|---|---|---|
| Petróleo profundo | #103D45 | Header, títulos, cabeçalho de tabelas, série de contexto |
| Petróleo secundário | #125F61 | Botão ativo, hover, painéis da Home |
| Turquesa | #18B89F | Série principal, destaque, indicador ativo |
| Menta | #DDF5EB | Totais, textos sobre fundo escuro, seleção |
| Branco gelo | #F7FAF9 | Canvas |
| Coral | #EF9277 | Perdas, desvios, comparativos de alerta (≤ 5% da área) |
| Grafite | #26383B | Texto principal |
| Cinza | #71858A | Legendas, subtítulos, série comparativa |
| Positivo / negativo (texto) | #0E8F7B / #A34F39 | Variações ▲ ▼ (sempre com seta + sinal, nunca só cor) |

## Grade e componentes

- Canvas de 1920×1080, margens de 32 px, espaçamento de 16 px.
- Header de 0 a 88 px (petróleo, logo sobre placa branca e navegação de 8 botões). Barra de filtros de 102 a 162 px. KPIs de 176 a 292 px. Blocos analíticos a partir de 308 px.
- Cartão de KPI: título, valor de 24 pt e uma linha de variação colorida por medida (`Txt …` / `Cor …`).
- Narrativa: cartão com quebra de linha, alimentado por medidas `Narrativa …`. Mostra só fatos derivados do filtro, nunca atribui causa.
- Gráficos de barra: rótulo de dados ligado e eixo de valor desligado. Linhas: comparativo em cinza e meta tracejada em coral.
- Fundos de página (header + painéis da Home) são PNG gerados por `relatorio.py` a partir dos mesmos tokens.
- Tipografia: Segoe UI / Segoe UI Semibold (disponível em qualquer Windows). As fontes Inter/Montserrat do manual não são garantidas no Desktop nem no Service.
