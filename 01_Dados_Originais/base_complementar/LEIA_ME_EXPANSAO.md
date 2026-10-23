# FarmaVitta — Expansão da base sintética (v1.0)
Período histórico: 2024-10 a 2026-09. Quatro lojas. Base original preservada.

## Arquivos adicionais
- `f_recebimentos_compras.csv`: recebimentos por produto/loja/mês e fornecedor. Quantidades **exatamente conciliadas** com `f_estoque_mensal.qtd_entradas`. Datas intramês e lead times simulados. Não representa pedidos emitidos.
- `f_compras_mensais.csv`: agregação mensal por loja dos recebimentos valorizados.
- `f_orcamento_compras.csv`: orçamento sintético mensal, com realizado derivado de recebimentos.
- `f_resultado_gerencial_mensal.csv`: receita, CMV, lucro bruto, despesas e resultado operacional simplificado. **Não é EBITDA ou DRE contábil**. Compras não devem ser subtraídas novamente do CMV.
- `d_cenarios_previsao.csv`: parâmetros para simulação what-if, **não previsões prontas**.
- `f_lotes_estoque_foto.csv`: lotes artificiais alocados ao estoque final em 2026-09-30. A soma de quantidades por loja e produto coincide com o saldo final original. Datas de validade são simuladas, e a foto NÃO deve ser usada para histórico de vencimentos.

## Relacionamentos
`id_loja` → `dim_lojas`; `id_produto` → `dim_produtos`; `id_fornecedor` → `dim_fornecedores`; `ano_mes` → dimensão mês (criar em Power BI), ou derivar `data_inicio_mes` e ligar ao calendário com cautela.
A dimensão de cenários é desconectada para medidas what-if.
As tabelas agregadas mensais são auxiliares e **não devem ser somadas junto com fatos detalhados** para evitar dupla contagem.

## Medidas e limitações
Receita e CMV oficiais: usar `f_vendas`; estoque: `f_estoque_mensal`; compras: `f_recebimentos_compras`; validade: `f_lotes_estoque_foto` apenas para snapshot de 2026-09-30.
OTIF verdadeiro não é possível: há prazo simulado, mas não há data real de pedido e promessa original.
Fluxo de caixa, contas a pagar efetivas, tributação, transferências e devoluções reais NÃO estão representados.
Previsão: treinar com vendas reais simuladas, avaliar por janela temporal e apresentar intervalo de incerteza; nunca tratar fatores de cenário como modelo preditivo.

## Testes realizados
- Recebimentos vs. entradas do estoque: conciliação exata por mês, loja e produto.
- Quantidades dos lotes vs. saldo final: conciliação exata por loja e produto.
- Histórico original não alterado.

Dados 100% fictícios. Separador CSV `;`, codificação UTF-8 com BOM, valores decimais com ponto.
