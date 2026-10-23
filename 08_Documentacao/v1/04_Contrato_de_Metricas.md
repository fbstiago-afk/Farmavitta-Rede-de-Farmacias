# Contrato de métricas e catálogo DAX

Regras gerais: receita/CMV da rede vêm de `fVendas` (cupom); por produto/categoria, de `fItensVenda`. Nunca somar as duas granularidades.
Estoque é semiaditivo (último mês do período). Despesas, metas e orçamento só existem por loja/mês: as medidas ficam em branco quando há filtro de produto, canal, cliente ou fornecedor (`_Filtro Sem Despesa`).
Comparações com ano anterior só aparecem quando o mesmo período está inteiramente coberto pela base (`_Periodo Comparavel LY`) e são limitadas ao último dia com venda (`_Data Base`).

## 00 Base

### Receita Bruta

Soma do valor bruto dos cupons (f_vendas).

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fVendas[valor_bruto] )
```

### Descontos

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fVendas[valor_desconto] )
```

### Receita Líquida

Receita líquida oficial da rede (f_vendas). Não somar com itens.

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fVendas[valor_liquido] )
```

### CMV

Custo da mercadoria vendida (f_vendas).

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fVendas[custo_mercadoria] )
```

### Cupons

Número de cupons (vendas). id_venda é único (GATE A).

Formato: `#,0`

```dax
COUNTROWS ( fVendas )
```

### Unidades Vendidas

Formato: `#,0`

```dax
SUM ( fItensVenda[quantidade] )
```

### Qtd Lojas

Formato: `#,0`

```dax
COUNTROWS ( dLoja )
```

### Clientes Cadastrados

Formato: `#,0`

```dax
CALCULATE ( COUNTROWS ( dCliente ), dCliente[id_cliente] <> "NI" )
```

### Despesas

Despesas modeladas (loja/mês). Em branco quando filtrado por produto, canal, cliente ou fornecedor.

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT [_Filtro Sem Despesa], SUM ( fDespesas[despesa_total] ) )
```

### Meta Receita

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT [_Filtro Sem Despesa], SUM ( fMetas[meta_receita] ) )
```

### Meta Lucro Bruto

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT [_Filtro Sem Despesa], SUM ( fMetas[meta_lucro_bruto] ) )
```

## 01 Tempo

### _Data Base

Último dia com venda na base (limita comparações com o ano anterior).

Formato: `dd/MM/yyyy`

```dax
CALCULATE ( MAX ( fVendas[data_venda] ), REMOVEFILTERS () )
```

### _Periodo Comparavel LY

Verdadeiro quando o mesmo período do ano anterior está inteiramente coberto pela base (≥ 01/10/2024).

```dax
VAR _ini = CALCULATE ( MIN ( fVendas[data_venda] ) )
RETURN NOT ISBLANK ( _ini ) && EDATE ( _ini, -12 ) >= DATE ( 2024, 10, 1 )
```

### Receita Líquida LY

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( [_Periodo Comparavel LY], CALCULATE ( [Receita Líquida], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )
```

### Receita YoY %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Receita Líquida] - [Receita Líquida LY], [Receita Líquida LY] )
```

### Lucro Bruto LY

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( [_Periodo Comparavel LY], CALCULATE ( [Lucro Bruto], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )
```

### Lucro Bruto YoY %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Lucro Bruto] - [Lucro Bruto LY], [Lucro Bruto LY] )
```

### Margem Bruta LY

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Lucro Bruto LY], [Receita Líquida LY] )
```

### Margem Bruta Var pp

Formato: `+0.0 "p.p.";-0.0 "p.p.";0.0 "p.p."`

```dax
IF ( NOT ISBLANK ( [Margem Bruta LY] ), ( [Margem Bruta %] - [Margem Bruta LY] ) * 100 )
```

### Cupons LY

Formato: `#,0`

```dax
IF ( [_Periodo Comparavel LY], CALCULATE ( [Cupons], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )
```

### Cupons YoY %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Cupons] - [Cupons LY], [Cupons LY] )
```

### Ticket Médio LY

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
DIVIDE ( [Receita Líquida LY], [Cupons LY] )
```

### Ticket Médio YoY %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Ticket Médio] - [Ticket Médio LY], [Ticket Médio LY] )
```

### Resultado Op Simplificado LY

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( [_Periodo Comparavel LY], CALCULATE ( [Resultado Operacional Simplificado], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )
```

### Resultado Op Simplificado YoY %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Resultado Operacional Simplificado] - [Resultado Op Simplificado LY], ABS ( [Resultado Op Simplificado LY] ) )
```

### Receita Mês Anterior

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
CALCULATE ( [Receita Líquida], DATEADD ( dCalendario[Data], -1, MONTH ) )
```

### Receita MoM %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Receita Líquida] - [Receita Mês Anterior], [Receita Mês Anterior] )
```

### Receita Acumulada Ano

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
TOTALYTD ( [Receita Líquida], dCalendario[Data] )
```

### Meses com Venda

Formato: `#,0`

```dax
COUNTROWS ( FILTER ( VALUES ( dCalendario[AnoMes Num] ), CALCULATE ( NOT ISEMPTY ( fVendas ) ) ) )
```

### Período Selecionado

```dax
VAR _i = CALCULATE ( MIN ( fVendas[data_venda] ) )
VAR _f = CALCULATE ( MAX ( fVendas[data_venda] ) )
RETURN IF ( ISBLANK ( _i ), "Sem vendas no período", FORMAT ( _i, "dd/mm/yyyy" ) & " a " & FORMAT ( _f, "dd/mm/yyyy" ) )
```

## 02 Comercial

### Lucro Bruto

Receita líquida − CMV (f_vendas).

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
[Receita Líquida] - [CMV]
```

### Margem Bruta %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Lucro Bruto], [Receita Líquida] )
```

### Ticket Médio

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
DIVIDE ( [Receita Líquida], [Cupons] )
```

### Itens por Cupom

Unidades por cupom (não confundir com SKUs distintos).

Formato: `#,0.00`

```dax
DIVIDE ( [Unidades Vendidas], [Cupons] )
```

### SKUs por Cupom

Formato: `#,0.00`

```dax
DIVIDE ( SUM ( fVendas[qtd_itens_distintos] ), [Cupons] )
```

### Desconto %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Descontos], [Receita Bruta] )
```

### Atingimento Meta %

Receita líquida / meta. Em branco com filtro de produto/canal/cliente.

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Receita Líquida], [Meta Receita] )
```

### Gap Meta

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT ISBLANK ( [Meta Receita] ), [Receita Líquida] - [Meta Receita] )
```

### Share Receita %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Receita Líquida], CALCULATE ( [Receita Líquida], ALLSELECTED () ) )
```

### Lojas na Meta

Formato: `#,0`

```dax
COUNTROWS ( FILTER ( VALUES ( dLoja[id_loja] ), [Atingimento Meta %] >= 1 ) )
```

## 03 Clientes

### Cupons Identificados

Formato: `#,0`

```dax
CALCULATE ( [Cupons], fVendas[cliente_identificado] = TRUE () )
```

### % Cupons Identificados

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Cupons Identificados], [Cupons] )
```

### Clientes Ativos

Clientes identificados com ao menos 1 cupom no período. Cupom anônimo não é cliente.

Formato: `#,0`

```dax
CALCULATE ( DISTINCTCOUNT ( fVendas[id_cliente] ), fVendas[cliente_identificado] = TRUE () )
```

### Clientes Ativos LY

Formato: `#,0`

```dax
IF ( [_Periodo Comparavel LY], CALCULATE ( [Clientes Ativos], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )
```

### Clientes Ativos YoY %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Clientes Ativos] - [Clientes Ativos LY], [Clientes Ativos LY] )
```

### Clientes Novos

Primeira compra observada na base (desde 01/10/2024): nos primeiros meses quase todos aparecem como novos.

Formato: `#,0`

```dax
CALCULATE ( DISTINCTCOUNT ( fVendas[id_cliente] ), fVendas[primeira_compra] = TRUE () )
```

### Clientes Recorrentes

Formato: `#,0`

```dax
[Clientes Ativos] - [Clientes Novos]
```

### % Clientes Novos

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Clientes Novos], [Clientes Ativos] )
```

### Frequência Média

Cupons por cliente identificado no período.

Formato: `#,0.00`

```dax
DIVIDE ( [Cupons Identificados], [Clientes Ativos] )
```

### Taxa de Recompra %

% de clientes ativos com 2+ cupons no período.

Formato: `0.0%;-0.0%;0.0%`

```dax
VAR _rec = COUNTROWS ( FILTER ( CALCULATETABLE ( VALUES ( fVendas[id_cliente] ), fVendas[cliente_identificado] = TRUE () ), CALCULATE ( COUNTROWS ( fVendas ) ) >= 2 ) )
RETURN DIVIDE ( _rec, [Clientes Ativos] )
```

### Ticket Médio Identificado

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
CALCULATE ( [Ticket Médio], fVendas[cliente_identificado] = TRUE () )
```

### Ticket Médio Anônimo

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
CALCULATE ( [Ticket Médio], fVendas[cliente_identificado] = FALSE () )
```

### Receita por Cliente

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
DIVIDE ( CALCULATE ( [Receita Líquida], fVendas[cliente_identificado] = TRUE () ), [Clientes Ativos] )
```

## 04 Produtos

### Receita Líquida Itens

Receita líquida na granularidade de item (para produto/categoria).

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fItensVenda[valor_liquido] )
```

### CMV Itens

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fItensVenda[custo_total] )
```

### Descontos Itens

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fItensVenda[valor_desconto] )
```

### Lucro Bruto Itens

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
[Receita Líquida Itens] - [CMV Itens]
```

### Margem Bruta Itens %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Lucro Bruto Itens], [Receita Líquida Itens] )
```

### Desconto Itens %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Descontos Itens], [Receita Líquida Itens] + [Descontos Itens] )
```

### SKUs Vendidos

Formato: `#,0`

```dax
DISTINCTCOUNT ( fItensVenda[id_produto] )
```

### SKUs no Catálogo

Formato: `#,0`

```dax
COUNTROWS ( dProduto )
```

### % SKUs com Venda

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [SKUs Vendidos], [SKUs no Catálogo] )
```

### Preço Médio Unitário

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
DIVIDE ( [Receita Líquida Itens], [Unidades Vendidas] )
```

### Share Receita Itens %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Receita Líquida Itens], CALCULATE ( [Receita Líquida Itens], ALLSELECTED ( dProduto ) ) )
```

### % SKUs Vendidos

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [SKUs Vendidos], CALCULATE ( [SKUs Vendidos], ALLSELECTED ( dProduto ) ) )
```

### Contribuição Lucro %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Lucro Bruto Itens], CALCULATE ( [Lucro Bruto Itens], ALLSELECTED ( dProduto ) ) )
```

### Receita Itens LY

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( [_Periodo Comparavel LY], CALCULATE ( [Receita Líquida Itens], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )
```

### Receita Itens YoY %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Receita Líquida Itens] - [Receita Itens LY], [Receita Itens LY] )
```

### Receita Itens Var LY

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT ISBLANK ( [Receita Itens LY] ), [Receita Líquida Itens] - [Receita Itens LY] )
```

### Margem Itens LY

Formato: `0.0%;-0.0%;0.0%`

```dax
IF ( [_Periodo Comparavel LY], CALCULATE ( [Margem Bruta Itens %], SAMEPERIODLASTYEAR ( VAR _db = [_Data Base] RETURN CALCULATETABLE ( VALUES ( dCalendario[Data] ), KEEPFILTERS ( dCalendario[Data] <= _db ) ) ) ) )
```

### Margem Itens Var pp

Formato: `+0.0 "p.p.";-0.0 "p.p.";0.0 "p.p."`

```dax
IF ( NOT ISBLANK ( [Margem Itens LY] ), ( [Margem Bruta Itens %] - [Margem Itens LY] ) * 100 )
```

### Ranking SKU

Formato: `#,0`

```dax
IF ( NOT ISBLANK ( [Receita Líquida Itens] ), RANKX ( ALLSELECTED ( dProduto ), [Receita Líquida Itens],, DESC, DENSE ) )
```

### Receita Acumulada % (Pareto)

Pareto dinâmico por SKU dentro da seleção. Custoso: usar em tabelas, não em gráficos com 5.000 pontos.

Formato: `0.0%;-0.0%;0.0%`

```dax
VAR _r = [Receita Líquida Itens]
VAR _t = ADDCOLUMNS ( ALLSELECTED ( dProduto[id_produto] ), "@r", [Receita Líquida Itens] )
VAR _acc = SUMX ( FILTER ( _t, [@r] >= _r ), [@r] )
RETURN IF ( NOT ISBLANK ( _r ), DIVIDE ( _acc, SUMX ( _t, [@r] ) ) )
```

## 05 Compras

### Valor Recebido

Compras recebidas valorizadas (base complementar). Não somar ao CMV.

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fRecebimentos[valor_recebido] )
```

### Qtd Recebida

Formato: `#,0`

```dax
SUM ( fRecebimentos[quantidade_recebida] )
```

### Recebimentos

Formato: `#,0`

```dax
COUNTROWS ( fRecebimentos )
```

### Lead Time Médio

Prazo real médio (dias) informado no recebimento.

Formato: `#,0.0 "dias"`

```dax
AVERAGE ( fRecebimentos[prazo_real_dias] )
```

### Prazo Previsto Médio

Formato: `#,0.0 "dias"`

```dax
AVERAGE ( fRecebimentos[prazo_previsto_dias] )
```

### Atraso Médio

Média de dias de atraso apenas entre entregas atrasadas.

Formato: `#,0.0 "dias"`

```dax
AVERAGEX ( FILTER ( fRecebimentos, fRecebimentos[atraso_dias] > 0 ), fRecebimentos[atraso_dias] )
```

### Pontualidade %

Entregas no prazo / recebimentos (OTD). Não é OTIF: não há pedido/quantidade prometida.

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( SUM ( fRecebimentos[entrega_no_prazo] ), [Recebimentos] )
```

### Custo Médio Recebido

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
DIVIDE ( [Valor Recebido], [Qtd Recebida] )
```

### Variação Custo vs Referência %

Custo pago vs custo de referência do cadastro. Não é saving (não há baseline negociado).

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Valor Recebido], SUMX ( fRecebimentos, fRecebimentos[quantidade_recebida] * RELATED ( dProduto[Custo Ref] ) ) ) - 1
```

### Fornecedores Ativos

Formato: `#,0`

```dax
DISTINCTCOUNT ( fRecebimentos[id_fornecedor] )
```

### Concentração Top 5 %

Formato: `0.0%;-0.0%;0.0%`

```dax
VAR _top = TOPN ( 5, VALUES ( dFornecedor[id_fornecedor] ), [Valor Recebido], DESC )
RETURN DIVIDE ( CALCULATE ( [Valor Recebido], KEEPFILTERS ( _top ) ), [Valor Recebido] )
```

### Share Compras %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Valor Recebido], CALCULATE ( [Valor Recebido], ALLSELECTED () ) )
```

### Orçamento Compras

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT [_Filtro Sem Despesa], SUM ( fOrcamentoCompras[orcamento_compras] ) )
```

### Desvio vs Orçamento

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT ISBLANK ( [Orçamento Compras] ), [Valor Recebido] - [Orçamento Compras] )
```

### Desvio vs Orçamento %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Desvio vs Orçamento], [Orçamento Compras] )
```

### Compras / CMV %

Compras recebidas / CMV de itens. < 100% indica consumo de estoque inicial.

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Valor Recebido], [CMV Itens] )
```

## 06 Estoque

### _Mes Snapshot

Último mês com saldo dentro do filtro de datas.

Formato: `dd/MM/yyyy`

```dax
CALCULATE ( MAX ( fEstoque[data_mes] ) )
```

### Estoque Final (R$)

Saldo valorizado no último mês do período (semiaditivo; nunca soma meses).

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
VAR _m = [_Mes Snapshot]
RETURN CALCULATE ( SUM ( fEstoque[valor_saldo_final] ), REMOVEFILTERS ( dCalendario ), fEstoque[data_mes] = _m )
```

### Estoque Final (un)

Formato: `#,0`

```dax
VAR _m = [_Mes Snapshot]
RETURN CALCULATE ( SUM ( fEstoque[saldo_final] ), REMOVEFILTERS ( dCalendario ), fEstoque[data_mes] = _m )
```

### Estoque Médio (R$)

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
AVERAGEX ( FILTER ( VALUES ( dCalendario[AnoMes Num] ), CALCULATE ( NOT ISEMPTY ( fEstoque ) ) ), CALCULATE ( SUM ( fEstoque[valor_saldo_final] ) ) )
```

### Meses Estoque

Formato: `#,0`

```dax
COUNTROWS ( FILTER ( VALUES ( dCalendario[AnoMes Num] ), CALCULATE ( NOT ISEMPTY ( fEstoque ) ) ) )
```

### Entradas (un)

Formato: `#,0`

```dax
SUM ( fEstoque[qtd_entradas] )
```

### Perdas (un)

Formato: `#,0`

```dax
SUM ( fEstoque[qtd_perdas] )
```

### Perdas (R$)

Perdas valorizadas ao custo de referência do mês.

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fEstoque[valor_perdas] )
```

### Perdas % CMV

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Perdas (R$)], [CMV Itens] )
```

### Giro Anualizado

CMV de itens / estoque médio, anualizado.

Formato: `0.0"x"`

```dax
DIVIDE ( [CMV Itens], [Estoque Médio (R$)] ) * DIVIDE ( 12, [Meses Estoque] )
```

### Cobertura (dias)

Saldo final / venda média diária dos últimos 3 meses. Estimativa, não previsão de ruptura.

Formato: `#,0 "dias"`

```dax
VAR _m = [_Mes Snapshot]
VAR _v3 = CALCULATE ( SUM ( fEstoque[qtd_vendida] ), REMOVEFILTERS ( dCalendario ), fEstoque[data_mes] > EDATE ( _m, -3 ), fEstoque[data_mes] <= _m )
RETURN DIVIDE ( [Estoque Final (un)], _v3 / 91.25 )
```

### Posições de Estoque

Pares loja×SKU no último mês do período.

Formato: `#,0`

```dax
VAR _m = [_Mes Snapshot]
RETURN CALCULATE ( COUNTROWS ( fEstoque ), REMOVEFILTERS ( dCalendario ), fEstoque[data_mes] = _m )
```

### Posições Sem Giro

Formato: `#,0`

```dax
CALCULATE ( [Posições de Estoque], fEstoque[Status Estoque] = "Sem giro" )
```

### Posições em Excesso

Formato: `#,0`

```dax
CALCULATE ( [Posições de Estoque], fEstoque[Status Estoque] = "Excesso" )
```

### Valor em Excesso (R$)

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
CALCULATE ( [Estoque Final (R$)], fEstoque[Status Estoque] = "Excesso" )
```

### % Valor em Excesso

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Valor em Excesso (R$)], [Estoque Final (R$)] )
```

### Valor Sem Giro (R$)

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
CALCULATE ( [Estoque Final (R$)], fEstoque[Status Estoque] = "Sem giro" )
```

### Valor em Lotes (R$)

Foto de 30/09/2026 (não responde a filtros de data).

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fLotes[valor_lote] )
```

### Valor em Risco Validade (R$)

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
CALCULATE ( [Valor em Lotes (R$)], fLotes[Faixa Validade] IN { "Vencido", "Até 90 dias" } )
```

### % Valor em Risco Validade

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Valor em Risco Validade (R$)], [Valor em Lotes (R$)] )
```

### Valor Vencido (R$)

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
CALCULATE ( [Valor em Lotes (R$)], fLotes[Faixa Validade] = "Vencido" )
```

## 07 Financeiro

### Pessoal

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT [_Filtro Sem Despesa], SUM ( fDespesas[pessoal] ) )
```

### Aluguel

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT [_Filtro Sem Despesa], SUM ( fDespesas[aluguel] ) )
```

### Despesas Operacionais

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT [_Filtro Sem Despesa], SUM ( fDespesas[operacionais] ) )
```

### Marketing e Canais

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT [_Filtro Sem Despesa], SUM ( fDespesas[marketing_canais] ) )
```

### Resultado Operacional Simplificado

Lucro bruto − despesas modeladas. NÃO é EBITDA, lucro líquido nem fluxo de caixa.

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( NOT [_Filtro Sem Despesa], [Lucro Bruto] - [Despesas] )
```

### Margem Operacional Simplificada %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Resultado Operacional Simplificado], [Receita Líquida] )
```

### Despesas % Receita

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Despesas], [Receita Líquida] )
```

### Atingimento Lucro Bruto %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Lucro Bruto], [Meta Lucro Bruto] )
```

### Valor DRE

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SWITCH ( SELECTEDVALUE ( dDRE[Ordem DRE] ),
    1, [Receita Bruta], 2, - [Descontos], 3, [Receita Líquida], 4, - [CMV], 5, [Lucro Bruto],
    6, - [Pessoal], 7, - [Aluguel], 8, - [Despesas Operacionais], 9, - [Marketing e Canais],
    10, [Resultado Operacional Simplificado] )
```

### % Receita Líquida (DRE)

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Valor DRE], [Receita Líquida] )
```

### Valor Ponte Resultado

Valores para o waterfall: receita líquida até resultado operacional simplificado (total automático).

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SWITCH ( SELECTEDVALUE ( dDRE[Ordem DRE] ),
    3, [Receita Líquida], 4, - [CMV], 6, - [Pessoal], 7, - [Aluguel], 8, - [Despesas Operacionais], 9, - [Marketing e Canais] )
```

## 08 Forecast

### Receita Prevista

Previsão do método com menor WAPE no backtest de cada loja.

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fForecast[previsao] )
```

### Limite Inferior

Intervalo empírico ~80% a partir dos erros do backtest. Soma de lojas é conservadora.

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fForecast[limite_inferior] )
```

### Limite Superior

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUM ( fForecast[limite_superior] )
```

### Receita Real (Série)

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
IF ( MIN ( dCalendario[Data] ) <= DATE(2026, 9, 30), [Receita Líquida] )
```

### Fator Receita Cenário

Formato: `0.00`

```dax
SELECTEDVALUE ( dCenario[Fator Receita], 1 )
```

### Fator Custo Cenário

Formato: `0.00`

```dax
SELECTEDVALUE ( dCenario[Fator Custo], 1 )
```

### Cenário Ativo

```dax
SELECTEDVALUE ( dCenario[Cenario], "Base" )
```

### Receita Prevista Cenário

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
[Receita Prevista] * [Fator Receita Cenário]
```

### Limite Inferior Cenário

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
[Limite Inferior] * [Fator Receita Cenário]
```

### Limite Superior Cenário

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
[Limite Superior] * [Fator Receita Cenário]
```

### CMV % Últimos 12m

Formato: `0.0%;-0.0%;0.0%`

```dax
CALCULATE ( DIVIDE ( [CMV], [Receita Líquida] ), DATESBETWEEN ( dCalendario[Data], DATE ( 2025, 10, 1 ), DATE ( 2026, 9, 30 ) ) )
```

### Lucro Bruto Previsto Cenário

Receita prevista × (1 − CMV% dos últimos 12 meses × fator de custo). Premissa, não previsão de margem.

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
[Receita Prevista Cenário] * ( 1 - [CMV % Últimos 12m] * [Fator Custo Cenário] )
```

### Receita LY dos Meses Previstos

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SUMX (
    FILTER ( VALUES ( dCalendario[AnoMes Num] ), CALCULATE ( NOT ISEMPTY ( fForecast ) ) && CALCULATE ( SUM ( fForecast[previsao] ) ) > 0 ),
    CALCULATE ( [Receita Líquida], SAMEPERIODLASTYEAR ( dCalendario[Data] ) )
)
```

### Crescimento Previsto vs LY %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( [Receita Prevista Cenário], [Receita LY dos Meses Previstos] ) - 1
```

### WAPE Backtest %

Erro absoluto ponderado do método selecionado (rolling-origin, h=1..3).

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( CALCULATE ( SUM ( fBacktest[erro_abs] ), fBacktest[metodo_selecionado] = 1 ), CALCULATE ( SUM ( fBacktest[real] ), fBacktest[metodo_selecionado] = 1 ) )
```

### MAPE Backtest %

Formato: `0.0%;-0.0%;0.0%`

```dax
CALCULATE ( AVERAGEX ( fBacktest, ABS ( fBacktest[erro_pct] ) ), fBacktest[metodo_selecionado] = 1 )
```

### WAPE por Método %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( SUM ( fBacktest[erro_abs] ), SUM ( fBacktest[real] ) )
```

### Viés Backtest %

Formato: `0.0%;-0.0%;0.0%`

```dax
DIVIDE ( CALCULATE ( SUMX ( fBacktest, fBacktest[previsto] - fBacktest[real] ), fBacktest[metodo_selecionado] = 1 ), CALCULATE ( SUM ( fBacktest[real] ), fBacktest[metodo_selecionado] = 1 ) )
```

### Métodos Selecionados

```dax
CONCATENATEX ( SUMMARIZE ( FILTER ( fBacktest, fBacktest[metodo_selecionado] = 1 ), dLoja[Loja Curta], fBacktest[Metodo] ), dLoja[Loja Curta] & ": " & fBacktest[Metodo], " · " )
```

## 09 Narrativas

### Narrativa Executiva

Fato derivado dos filtros. Não atribui causa.

```dax
VAR _rec = [Receita Líquida]
VAR _yoy = [Receita YoY %]
VAR _mg = [Margem Bruta %]
VAR _pp = [Margem Bruta Var pp]
VAR _at = [Atingimento Meta %]
VAR _t = ADDCOLUMNS ( VALUES ( dLoja[Loja Curta] ), "@d", [Receita Líquida] - [Receita Líquida LY] )
VAR _top = TOPN ( 1, _t, [@d], DESC )
VAR _loja = MAXX ( _top, dLoja[Loja Curta] )
VAR _dl = MAXX ( _top, [@d] )
VAR _f1 = "Receita líquida de R$ " & FORMAT ( _rec / 1000000, "#,0.00", "pt-BR" ) & " mi"
    & IF ( ISBLANK ( _yoy ), " (sem período comparável completo no ano anterior).",
        ", " & IF ( _yoy >= 0, "alta", "queda" ) & " de " & FORMAT ( ABS ( _yoy ), "0.0%", "pt-BR" ) & " vs mesmo período do ano anterior." )
VAR _f2 = IF ( NOT ISBLANK ( _yoy ) && COUNTROWS ( _t ) > 1,
    " Maior contribuição: " & _loja & " (" & IF ( _dl >= 0, "+", "−" ) & "R$ " & FORMAT ( ABS ( _dl ) / 1000, "#,0", "pt-BR" ) & " mil).", "" )
VAR _f3 = " Margem bruta de " & FORMAT ( _mg, "0.0%", "pt-BR" )
    & IF ( ISBLANK ( _pp ), "", " (" & FORMAT ( _pp, "+0.0;-0.0", "pt-BR" ) & " p.p.)" )
    & IF ( ISBLANK ( _at ), ".", "; meta de receita " & FORMAT ( _at, "0%", "pt-BR" ) & " atingida." )
RETURN IF ( ISBLANK ( _rec ), "Sem vendas para os filtros selecionados.", _f1 & _f2 & _f3 )
```

### Narrativa Clientes

```dax
VAR _id = [% Cupons Identificados]
VAR _fr = [Frequência Média]
VAR _ti = [Ticket Médio Identificado]
VAR _ta = [Ticket Médio Anônimo]
VAR _rc = [Taxa de Recompra %]
RETURN IF ( ISBLANK ( [Cupons] ), "Sem vendas para os filtros selecionados.",
    FORMAT ( _id, "0%", "pt-BR" ) & " dos cupons têm cliente identificado; cada cliente ativo comprou em média " & FORMAT ( _fr, "0.0", "pt-BR" )
    & " vezes e " & FORMAT ( _rc, "0%", "pt-BR" ) & " recompraram no período."
    & IF ( NOT ISBLANK ( _ta ), " Ticket identificado R$ " & FORMAT ( _ti, "#,0.00", "pt-BR" ) & " vs anônimo R$ " & FORMAT ( _ta, "#,0.00", "pt-BR" ) & ".", "" )
    & " Hipótese a testar: ampliar identificação no balcão." )
```

### Narrativa Produtos

```dax
VAR _c = ADDCOLUMNS ( VALUES ( dProduto[Categoria] ), "@r", [Receita Líquida Itens], "@pp", [Margem Itens Var pp] )
VAR _maior = TOPN ( 1, _c, [@r], DESC )
VAR _pior = TOPN ( 1, FILTER ( _c, NOT ISBLANK ( [@pp] ) ), [@pp], ASC )
VAR _f1 = MAXX ( _maior, dProduto[Categoria] ) & " lidera com " & FORMAT ( DIVIDE ( MAXX ( _maior, [@r] ), [Receita Líquida Itens] ), "0%", "pt-BR" ) & " da receita de itens; margem bruta geral de " & FORMAT ( [Margem Bruta Itens %], "0.0%", "pt-BR" ) & "."
VAR _f2 = IF ( COUNTROWS ( _pior ) = 1 && MAXX ( _pior, [@pp] ) < 0, " Maior perda de margem: " & MAXX ( _pior, dProduto[Categoria] ) & " (" & FORMAT ( MAXX ( _pior, [@pp] ), "+0.0;-0.0", "pt-BR" ) & " p.p.) — investigar desconto e mix.", "" )
RETURN IF ( ISBLANK ( [Receita Líquida Itens] ), "Sem vendas para os filtros selecionados.", _f1 & _f2 )
```

### Narrativa Compras

```dax
VAR _f = ADDCOLUMNS ( VALUES ( dFornecedor[Fornecedor] ), "@v", [Valor Recebido], "@p", [Pontualidade %] )
VAR _pior = TOPN ( 1, FILTER ( _f, [@v] >= 0.01 * [Valor Recebido] ), [@p], ASC )
RETURN IF ( ISBLANK ( [Valor Recebido] ), "Sem recebimentos para os filtros selecionados.",
    "Compras recebidas de R$ " & FORMAT ( [Valor Recebido] / 1000000, "#,0.00", "pt-BR" ) & " mi; " & FORMAT ( [Pontualidade %], "0%", "pt-BR" ) & " das entregas no prazo, atraso médio de "
    & FORMAT ( [Atraso Médio], "0.0", "pt-BR" ) & " dias quando atrasa. Menor pontualidade (≥1% do valor): " & MAXX ( _pior, dFornecedor[Fornecedor] ) & " (" & FORMAT ( MAXX ( _pior, [@p] ), "0%", "pt-BR" ) & ")." )
```

### Narrativa Estoque

```dax
IF ( ISBLANK ( [Estoque Final (R$)] ), "Sem estoque para os filtros selecionados.",
    "Estoque de R$ " & FORMAT ( [Estoque Final (R$)] / 1000000, "#,0.00", "pt-BR" ) & " mi em " & FORMAT ( [_Mes Snapshot], "mm/yyyy" ) & " cobre ~" & FORMAT ( [Cobertura (dias)], "#,0", "pt-BR" )
    & " dias de venda; " & FORMAT ( [% Valor em Excesso], "0%", "pt-BR" ) & " do valor está acima de 120 dias de cobertura. Recomendação: revisar parâmetros de reposição antes de comprar." )
```

### Narrativa Financeiro

```dax
VAR _ros = [Resultado Operacional Simplificado]
VAR _pes = DIVIDE ( [Pessoal], [Despesas] )
RETURN IF ( ISBLANK ( _ros ), "Resultado indisponível para filtros de produto, canal, cliente ou fornecedor (despesas são por loja/mês).",
    "Resultado operacional simplificado de R$ " & FORMAT ( _ros / 1000000, "#,0.00", "pt-BR" ) & " mi (margem " & FORMAT ( [Margem Operacional Simplificada %], "0.0%", "pt-BR" )
    & "). Pessoal é " & FORMAT ( _pes, "0%", "pt-BR" ) & " das despesas modeladas. Indicador gerencial: não é EBITDA nem lucro líquido." )
```

### Narrativa Forecast

```dax
"Cenário " & [Cenário Ativo] & ": receita prevista de R$ " & FORMAT ( [Receita Prevista Cenário] / 1000000, "#,0.00", "pt-BR" ) & " mi nos próximos 6 meses ("
    & FORMAT ( [Crescimento Previsto vs LY %], "+0.0%;-0.0%", "pt-BR" ) & " vs mesmos meses do ano anterior). Erro histórico (WAPE) de " & FORMAT ( [WAPE Backtest %], "0.0%", "pt-BR" )
    & " com só 24 meses de histórico: use como faixa, não como meta."
```

## 10 UI & Formatação

### Txt Receita

```dax
VAR _v = [Receita YoY %]
RETURN IF ( ISBLANK ( _v ), "sem base comparável no ano anterior",
    IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0%", "pt-BR" ) & " vs ano anterior" )
```

### Cor Receita

```dax
VAR _v = [Receita YoY %]
RETURN IF ( ISBLANK ( _v ), "#71858A", IF ( _v >= 0, "#0E8F7B", "#A34F39" ) )
```

### Txt Lucro

```dax
VAR _v = [Lucro Bruto YoY %]
RETURN IF ( ISBLANK ( _v ), "sem base comparável no ano anterior",
    IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0%", "pt-BR" ) & " vs ano anterior" )
```

### Cor Lucro

```dax
VAR _v = [Lucro Bruto YoY %]
RETURN IF ( ISBLANK ( _v ), "#71858A", IF ( _v >= 0, "#0E8F7B", "#A34F39" ) )
```

### Txt Margem

```dax
VAR _v = [Margem Bruta Var pp]
RETURN IF ( ISBLANK ( _v ), "sem base comparável no ano anterior",
    IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0", "pt-BR" ) & " p.p." & " vs ano anterior" )
```

### Cor Margem

```dax
VAR _v = [Margem Bruta Var pp]
RETURN IF ( ISBLANK ( _v ), "#71858A", IF ( _v >= 0, "#0E8F7B", "#A34F39" ) )
```

### Txt Ticket

```dax
VAR _v = [Ticket Médio YoY %]
RETURN IF ( ISBLANK ( _v ), "sem base comparável no ano anterior",
    IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0%", "pt-BR" ) & " vs ano anterior" )
```

### Cor Ticket

```dax
VAR _v = [Ticket Médio YoY %]
RETURN IF ( ISBLANK ( _v ), "#71858A", IF ( _v >= 0, "#0E8F7B", "#A34F39" ) )
```

### Txt Cupons

```dax
VAR _v = [Cupons YoY %]
RETURN IF ( ISBLANK ( _v ), "sem base comparável no ano anterior",
    IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0%", "pt-BR" ) & " vs ano anterior" )
```

### Cor Cupons

```dax
VAR _v = [Cupons YoY %]
RETURN IF ( ISBLANK ( _v ), "#71858A", IF ( _v >= 0, "#0E8F7B", "#A34F39" ) )
```

### Txt Clientes

```dax
VAR _v = [Clientes Ativos YoY %]
RETURN IF ( ISBLANK ( _v ), "sem base comparável no ano anterior",
    IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0%", "pt-BR" ) & " vs ano anterior" )
```

### Cor Clientes

```dax
VAR _v = [Clientes Ativos YoY %]
RETURN IF ( ISBLANK ( _v ), "#71858A", IF ( _v >= 0, "#0E8F7B", "#A34F39" ) )
```

### Txt ROS

```dax
VAR _v = [Resultado Op Simplificado YoY %]
RETURN IF ( ISBLANK ( _v ), "sem base comparável no ano anterior",
    IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0%", "pt-BR" ) & " vs ano anterior" )
```

### Cor ROS

```dax
VAR _v = [Resultado Op Simplificado YoY %]
RETURN IF ( ISBLANK ( _v ), "#71858A", IF ( _v >= 0, "#0E8F7B", "#A34F39" ) )
```

### Txt Receita Itens

```dax
VAR _v = [Receita Itens YoY %]
RETURN IF ( ISBLANK ( _v ), "sem base comparável no ano anterior",
    IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0%", "pt-BR" ) & " vs ano anterior" )
```

### Cor Receita Itens

```dax
VAR _v = [Receita Itens YoY %]
RETURN IF ( ISBLANK ( _v ), "#71858A", IF ( _v >= 0, "#0E8F7B", "#A34F39" ) )
```

### Txt Margem Itens

```dax
VAR _v = [Margem Itens Var pp]
RETURN IF ( ISBLANK ( _v ), "sem base comparável no ano anterior",
    IF ( _v >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( _v ), "0.0", "pt-BR" ) & " p.p." & " vs ano anterior" )
```

### Cor Margem Itens

```dax
VAR _v = [Margem Itens Var pp]
RETURN IF ( ISBLANK ( _v ), "#71858A", IF ( _v >= 0, "#0E8F7B", "#A34F39" ) )
```

### Txt Meta

```dax
VAR _g = [Gap Meta]
RETURN IF ( ISBLANK ( _g ), "meta indisponível p/ este filtro", IF ( _g >= 0, "▲ R$ ", "▼ R$ " ) & FORMAT ( ABS ( _g ) / 1000, "#,0", "pt-BR" ) & " mil vs meta" )
```

### Cor Meta

```dax
IF ( ISBLANK ( [Gap Meta] ), "#71858A", IF ( [Gap Meta] >= 0, "#0E8F7B", "#A34F39" ) )
```

### Txt Margem Op

```dax
IF ( ISBLANK ( [Margem Operacional Simplificada %] ), "indisponível p/ este filtro", "margem op. " & FORMAT ( [Margem Operacional Simplificada %], "0.0%", "pt-BR" ) & " · não é EBITDA" )
```

### Txt Novos

```dax
FORMAT ( [% Clientes Novos], "0.0%", "pt-BR" ) & " dos ativos (1ª compra observada)"
```

### Txt SKUs

```dax
FORMAT ( [% SKUs com Venda], "0.0%", "pt-BR" ) & " do catálogo filtrado"
```

### Txt Perdas

```dax
FORMAT ( [Perdas % CMV], "0.00%", "pt-BR" ) & " do CMV de itens"
```

### Txt Validade

```dax
FORMAT ( [% Valor em Risco Validade], "0.0%", "pt-BR" ) & " do valor · foto 30/09/2026"
```

### Txt Cobertura

```dax
FORMAT ( [% Valor em Excesso], "0%", "pt-BR" ) & " do valor com cobertura > 120 dias"
```

### Txt Pontualidade

```dax
"prazo previsto médio " & FORMAT ( [Prazo Previsto Médio], "0.0", "pt-BR" ) & " dias"
```

### Txt Orçamento

```dax
IF ( ISBLANK ( [Desvio vs Orçamento %] ), "orçamento indisponível p/ este filtro", IF ( [Desvio vs Orçamento %] >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( [Desvio vs Orçamento %] ), "0.0%", "pt-BR" ) & " vs orçamento" )
```

### Txt Período

```dax
"Período: " & [Período Selecionado]
```

### Txt Forecast Intervalo

```dax
"intervalo ~80%: R$ " & FORMAT ( [Limite Inferior Cenário] / 1000000, "#,0.00", "pt-BR" ) & " a " & FORMAT ( [Limite Superior Cenário] / 1000000, "#,0.00", "pt-BR" ) & " mi"
```

### Txt Neutro

```dax
"#71858A"
```

## 99 Auditoria

### _Filtro Sem Despesa

Verdadeiro quando há filtro em dimensão que não existe nas fatos de meta/despesa (evita números enganosos).

```dax
ISFILTERED ( dProduto ) || ISFILTERED ( dCanal ) || ISFILTERED ( dCliente ) || ISFILTERED ( dFornecedor )
```

### Check Receita Cupom vs Itens

Deve ser 0 com filtros de loja/data/canal/cliente.

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
[Receita Líquida] - [Receita Líquida Itens]
```

### Check Receita Referência

Deve ser 0 (RESUMO_BASE.json).

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
CALCULATE ( [Receita Líquida], REMOVEFILTERS () ) - 35060712
```

### Check CMV Referência

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
CALCULATE ( [CMV], REMOVEFILTERS () ) - 21252002.94
```

### Check Lotes vs Saldo Final

Formato: `#,0`

```dax
CALCULATE ( SUM ( fLotes[quantidade_lote] ), REMOVEFILTERS () ) - CALCULATE ( SUM ( fEstoque[saldo_final] ), REMOVEFILTERS (), fEstoque[data_mes] = DATE ( 2026, 9, 1 ) )
```
