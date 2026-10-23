# Dicionário de dados — modelo semântico FarmaVitta

Gerado de `10_Scripts/pbip/modelo.py` (fonte única do TMDL). Colunas ocultas são chaves ou campos técnicos usados pelas medidas.

## dCalendario

Calendário diário 01/10/2024–31/03/2027 (inclui horizonte de previsão). Dia útil vem de dim_calendario; datas futuras: seg–sex.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| Data | Data | dateTime |  |  |
| Ano | Ano | int64 |  |  |
| Mes Num | Mes Num | int64 | sim |  |
| Mes Nome | Mes Nome | string |  | Mes Num |
| Mes Ano | Mes Ano | string |  | AnoMes Num |
| AnoMes Num | AnoMes Num | int64 | sim |  |
| Ano Mes | Ano Mes | string |  |  |
| Trimestre | Trimestre | string |  |  |
| Dia Semana Num | Dia Semana Num | int64 | sim |  |
| Dia Semana | Dia Semana | string |  | Dia Semana Num |
| Dia Util | Dia Util | boolean |  |  |
| Inicio Mes | Inicio Mes | dateTime |  |  |
| Periodo | Periodo | string |  |  |

## dLoja

Lojas (4).

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| id_loja | id_loja | string | sim |  |
| Loja | nome_loja | string |  |  |
| Loja Curta | Loja Curta | string |  |  |
| Cidade | cidade | string |  |  |
| UF | uf | string |  |  |
| Data Abertura | data_abertura | dateTime |  |  |
| Indice Demanda | indice_demanda | double |  |  |

## dProduto

SKUs (5.000) com fornecedor único (ponte 1:1 validada no GATE A) e Classe ABC estática do período completo.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| id_produto | id_produto | string | sim |  |
| Produto | nome_produto | string |  |  |
| Categoria | categoria | string |  |  |
| Subcategoria | subcategoria | string |  |  |
| Marca | marca | string |  |  |
| Preco Lista Ref | preco_lista_referencia | double |  |  |
| Custo Ref | custo_unitario_referencia | double |  |  |
| Generico | eh_generico | string |  |  |
| Controlado | eh_controlado | string |  |  |
| Exige Receita | exige_receita | string |  |  |
| Status | status | string |  |  |
| id_fornecedor | id_fornecedor | string | sim |  |
| Classe ABC | classe_abc | string |  |  |
| Rank Receita | rank_receita | int64 |  |  |

## dFornecedor

Fornecedores fictícios (60). Filtra fatos via dProduto (snowflake 1:N).

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| id_fornecedor | id_fornecedor | string | sim |  |
| Fornecedor | razao_social_ficticia | string |  |  |
| UF Fornecedor | uf | string |  |  |
| Prazo Medio Dias | prazo_medio_dias | int64 |  |  |

## dCliente

Clientes sintéticos (22.000) + membro 'NI' para cupons anônimos. RFV é fotografia em 30/09/2026.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| id_cliente | id_cliente | string | sim |  |
| Cidade Cadastro | cidade_cadastro | string |  |  |
| Data Cadastro | data_cadastro | dateTime |  |  |
| Segmento Cadastro | segmento_cadastro | string |  |  |
| Faixa Etaria | faixa_etaria | string |  |  |
| Tipo Cliente | Tipo Cliente | string |  |  |
| Segmento RFV | segmento_rfv | string |  | Ordem RFV |
| Ordem RFV | ordem_segmento | int64 | sim |  |
| Recencia Dias | recencia_dias | int64 |  |  |
| Frequencia RFV | frequencia | int64 |  |  |
| Valor RFV | valor | double |  |  |
| Score R | score_r | int64 |  |  |
| Score F | score_f | int64 |  |  |
| Score V | score_v | int64 |  |  |
| Data Primeira Compra | data_primeira_compra | dateTime |  |  |

## dCanal

Canais de venda (estático, validado no GATE A).

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| Canal | Canal | string |  | Ordem Canal |
| Ordem Canal | Ordem Canal | int64 | sim |  |

## fVendas

Fato cupom (1 linha por venda). Fonte oficial de receita, desconto e CMV da rede.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| id_venda | id_venda | string | sim |  |
| data_venda | data_venda | dateTime | sim |  |
| id_loja | id_loja | string | sim |  |
| id_cliente | id_cliente | string | sim |  |
| canal | canal | string | sim |  |
| Forma Pagamento | forma_pagamento | string |  |  |
| qtd_itens_distintos | qtd_itens_distintos | int64 | sim |  |
| valor_bruto | valor_bruto | double | sim |  |
| valor_desconto | valor_desconto | double | sim |  |
| valor_liquido | valor_liquido | double | sim |  |
| custo_mercadoria | custo_mercadoria | double | sim |  |
| cliente_identificado | cliente_identificado | boolean | sim |  |
| primeira_compra | primeira_compra | boolean | sim |  |

## fItensVenda

Fato item de cupom. Fonte de receita/margem por produto. Canal e cliente herdados do cupom no Power Query (sem relação fato–fato).

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| id_item | id_item | string | sim |  |
| id_venda | id_venda | string | sim |  |
| id_loja | id_loja | string | sim |  |
| id_produto | id_produto | string | sim |  |
| data_venda | data_venda | dateTime | sim |  |
| quantidade | quantidade | int64 | sim |  |
| preco_unitario_bruto | preco_unitario_bruto | double | sim |  |
| taxa_desconto | taxa_desconto | double | sim |  |
| valor_desconto | valor_desconto | double | sim |  |
| valor_liquido | valor_liquido | double | sim |  |
| custo_total | custo_total | double | sim |  |
| canal | canal | string | sim |  |
| id_cliente | id_cliente | string | sim |  |

## fEstoque

Saldo de estoque reconstruído (grade completa loja×SKU×mês, 02_Dados_Tratados). Semiaditivo: usar medidas de snapshot.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| ano_mes | ano_mes | string | sim |  |
| data_mes | data_mes | dateTime | sim |  |
| id_loja | id_loja | string | sim |  |
| id_produto | id_produto | string | sim |  |
| saldo_inicial | saldo_inicial | int64 | sim |  |
| qtd_entradas | qtd_entradas | int64 | sim |  |
| qtd_vendida | qtd_vendida | int64 | sim |  |
| qtd_perdas | qtd_perdas | int64 | sim |  |
| saldo_final | saldo_final | int64 | sim |  |
| custo_unitario | custo_unitario | double | sim |  |
| valor_saldo_final | valor_saldo_final | double | sim |  |
| valor_perdas | valor_perdas | double | sim |  |
| teve_movimento | teve_movimento | int64 | sim |  |
| venda_media_3m | venda_media_3m | double | sim |  |
| Meses Sem Venda | meses_sem_venda | int64 |  |  |
| cobertura_dias | cobertura_dias | double | sim |  |
| Status Estoque | status_estoque | string |  |  |

## fMetas

Metas mensais por loja.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| ano_mes | ano_mes | string | sim |  |
| data_mes | data_mes | dateTime | sim |  |
| id_loja | id_loja | string | sim |  |
| meta_receita | meta_receita | double | sim |  |
| meta_lucro_bruto | meta_lucro_bruto | double | sim |  |

## fDespesas

Despesas operacionais mensais por loja (rubricas modeladas; não inclui impostos/depreciação).

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| ano_mes | ano_mes | string | sim |  |
| data_mes | data_mes | dateTime | sim |  |
| id_loja | id_loja | string | sim |  |
| aluguel | aluguel | double | sim |  |
| pessoal | pessoal | double | sim |  |
| operacionais | operacionais | double | sim |  |
| marketing_canais | marketing_canais | double | sim |  |
| despesa_total | despesa_total | double | sim |  |

## fRecebimentos

Recebimentos de compras (base complementar), conciliados com entradas do estoque. Não representa pedidos emitidos.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| id_recebimento | id_recebimento | string | sim |  |
| data_recebimento | data_recebimento | dateTime | sim |  |
| id_loja | id_loja | string | sim |  |
| id_produto | id_produto | string | sim |  |
| id_fornecedor | id_fornecedor | string | sim |  |
| quantidade_recebida | quantidade_recebida | int64 | sim |  |
| custo_unitario | custo_unitario | double | sim |  |
| valor_recebido | valor_recebido | double | sim |  |
| prazo_previsto_dias | prazo_previsto_dias | int64 | sim |  |
| prazo_real_dias | prazo_real_dias | int64 | sim |  |
| entrega_no_prazo | entrega_no_prazo | int64 | sim |  |
| atraso_dias | atraso_dias | int64 | sim |  |

## fOrcamentoCompras

Orçamento sintético de compras por loja/mês.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| ano_mes | ano_mes | string | sim |  |
| data_mes | data_mes | dateTime | sim |  |
| id_loja | id_loja | string | sim |  |
| orcamento_compras | orcamento_compras | double | sim |  |

## fLotes

Fotografia de lotes em 30/09/2026 (simulada). Não é histórico: sem relação com calendário.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| id_lote | id_lote | string | sim |  |
| id_loja | id_loja | string | sim |  |
| id_produto | id_produto | string | sim |  |
| quantidade_lote | quantidade_lote | int64 | sim |  |
| Data Validade | data_validade_simulada | dateTime |  |  |
| Faixa Validade | faixa_validade | string |  | Ordem Faixa |
| custo_unitario_referencia | custo_unitario_referencia | double | sim |  |
| valor_lote | valor_lote | double | sim |  |
| Ordem Faixa | Ordem Faixa | int64 | sim |  |

## fForecast

Previsão de receita mensal por loja (6 meses, v1.0, treino até 30/09/2026). Projeção não é meta nem fato.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| ano_mes | ano_mes | string | sim |  |
| data_mes | data_mes | dateTime | sim |  |
| id_loja | id_loja | string | sim |  |
| Tipo Serie | tipo | string |  |  |
| Metodo | metodo | string |  |  |
| valor_real | valor_real | double | sim |  |
| previsao | previsao | double | sim |  |
| limite_inferior | limite_inferior | double | sim |  |
| limite_superior | limite_superior | double | sim |  |
| wape_backtest | wape_backtest | double | sim |  |

## fBacktest

Backtest rolling-origin (h=1..3) dos métodos de previsão.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| origem | origem | string | sim |  |
| ano_mes_alvo | ano_mes_alvo | string | sim |  |
| Horizonte | horizonte | int64 |  |  |
| id_loja | id_loja | string | sim |  |
| Metodo | metodo | string |  |  |
| real | real | double | sim |  |
| previsto | previsto | double | sim |  |
| erro_abs | erro_abs | double | sim |  |
| erro_pct | erro_pct | double | sim |  |
| metodo_selecionado | metodo_selecionado | int64 | sim |  |

## dCenario

Cenários what-if (desconectada). Fatores aplicados sobre a previsão; não são modelo preditivo.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| id_cenario | id_cenario | string | sim |  |
| Cenario | cenario | string |  | id_cenario |
| Fator Receita | fator_receita | double |  |  |
| Fator Custo | fator_custo | double |  |  |
| Descricao Cenario | descricao | string |  |  |

## dDRE

Linhas da DRE gerencial simplificada (desconectada).

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| Ordem DRE | Ordem DRE | int64 | sim |  |
| Linha DRE | Linha DRE | string |  | Ordem DRE |
| Tipo Linha | Tipo Linha | string |  |  |

## _Medidas

Tabela de medidas.

| Coluna (modelo) | Coluna de origem | Tipo | Oculta | Ordenada por |
|---|---|---|---|---|
| _ | _ | string | sim |  |
