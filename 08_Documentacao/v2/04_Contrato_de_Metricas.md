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

### Valor Ponte Deneb

Waterfall Deneb: inclui a linha 10 (total) explicitamente.

Formato: `\R\$ #,0.00;-\R\$ #,0.00;\R\$ #,0.00`

```dax
SWITCH ( SELECTEDVALUE ( dDRE[Ordem DRE] ),
    3, [Receita Líquida], 4, - [CMV], 6, - [Pessoal], 7, - [Aluguel], 8, - [Despesas Operacionais], 9, - [Marketing e Canais],
    10, [Resultado Operacional Simplificado] )
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

### HTML Narrativa Executiva

```dax
"<style>.n{font-family:Segoe UI,sans-serif;color:#E8F3F1;height:100%;display:flex;flex-direction:column;animation:f .6s ease both}.h{font-size:13px;font-weight:600;color:#18B89F;letter-spacing:.3px;margin-bottom:8px}.h:before{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:#18B89F;box-shadow:0 0 10px #18B89F;margin-right:8px}.p{font-size:13.5px;line-height:1.55}.ft{margin-top:auto;font-size:10.5px;color:#9FC9C1;border-top:1px solid rgba(255,255,255,.08);padding-top:6px}@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style><div class='n'><div class='h'>Leitura automática</div><div class='p'>" & [Narrativa Executiva] & "</div><div class='ft'>Fato derivado dos filtros atuais · hipótese e ação a validar · não indica causa</div></div>"
```

### HTML Narrativa Clientes

```dax
"<style>.n{font-family:Segoe UI,sans-serif;color:#E8F3F1;height:100%;display:flex;flex-direction:column;animation:f .6s ease both}.h{font-size:13px;font-weight:600;color:#18B89F;letter-spacing:.3px;margin-bottom:8px}.h:before{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:#18B89F;box-shadow:0 0 10px #18B89F;margin-right:8px}.p{font-size:13.5px;line-height:1.55}.ft{margin-top:auto;font-size:10.5px;color:#9FC9C1;border-top:1px solid rgba(255,255,255,.08);padding-top:6px}@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style><div class='n'><div class='h'>Leitura automática</div><div class='p'>" & [Narrativa Clientes] & "</div><div class='ft'>Fato derivado dos filtros atuais · hipótese e ação a validar · não indica causa</div></div>"
```

### HTML Narrativa Produtos

```dax
"<style>.n{font-family:Segoe UI,sans-serif;color:#E8F3F1;height:100%;display:flex;flex-direction:column;animation:f .6s ease both}.h{font-size:13px;font-weight:600;color:#18B89F;letter-spacing:.3px;margin-bottom:8px}.h:before{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:#18B89F;box-shadow:0 0 10px #18B89F;margin-right:8px}.p{font-size:13.5px;line-height:1.55}.ft{margin-top:auto;font-size:10.5px;color:#9FC9C1;border-top:1px solid rgba(255,255,255,.08);padding-top:6px}@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style><div class='n'><div class='h'>Leitura automática</div><div class='p'>" & [Narrativa Produtos] & "</div><div class='ft'>Fato derivado dos filtros atuais · hipótese e ação a validar · não indica causa</div></div>"
```

### HTML Narrativa Compras

```dax
"<style>.n{font-family:Segoe UI,sans-serif;color:#E8F3F1;height:100%;display:flex;flex-direction:column;animation:f .6s ease both}.h{font-size:13px;font-weight:600;color:#18B89F;letter-spacing:.3px;margin-bottom:8px}.h:before{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:#18B89F;box-shadow:0 0 10px #18B89F;margin-right:8px}.p{font-size:13.5px;line-height:1.55}.ft{margin-top:auto;font-size:10.5px;color:#9FC9C1;border-top:1px solid rgba(255,255,255,.08);padding-top:6px}@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style><div class='n'><div class='h'>Leitura automática</div><div class='p'>" & [Narrativa Compras] & "</div><div class='ft'>Fato derivado dos filtros atuais · hipótese e ação a validar · não indica causa</div></div>"
```

### HTML Narrativa Estoque

```dax
"<style>.n{font-family:Segoe UI,sans-serif;color:#E8F3F1;height:100%;display:flex;flex-direction:column;animation:f .6s ease both}.h{font-size:13px;font-weight:600;color:#18B89F;letter-spacing:.3px;margin-bottom:8px}.h:before{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:#18B89F;box-shadow:0 0 10px #18B89F;margin-right:8px}.p{font-size:13.5px;line-height:1.55}.ft{margin-top:auto;font-size:10.5px;color:#9FC9C1;border-top:1px solid rgba(255,255,255,.08);padding-top:6px}@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style><div class='n'><div class='h'>Leitura automática</div><div class='p'>" & [Narrativa Estoque] & "</div><div class='ft'>Fato derivado dos filtros atuais · hipótese e ação a validar · não indica causa</div></div>"
```

### HTML Narrativa Financeiro

```dax
"<style>.n{font-family:Segoe UI,sans-serif;color:#E8F3F1;height:100%;display:flex;flex-direction:column;animation:f .6s ease both}.h{font-size:13px;font-weight:600;color:#18B89F;letter-spacing:.3px;margin-bottom:8px}.h:before{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:#18B89F;box-shadow:0 0 10px #18B89F;margin-right:8px}.p{font-size:13.5px;line-height:1.55}.ft{margin-top:auto;font-size:10.5px;color:#9FC9C1;border-top:1px solid rgba(255,255,255,.08);padding-top:6px}@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style><div class='n'><div class='h'>Leitura automática</div><div class='p'>" & [Narrativa Financeiro] & "</div><div class='ft'>Fato derivado dos filtros atuais · hipótese e ação a validar · não indica causa</div></div>"
```

### HTML Narrativa Forecast

```dax
"<style>.n{font-family:Segoe UI,sans-serif;color:#E8F3F1;height:100%;display:flex;flex-direction:column;animation:f .6s ease both}.h{font-size:13px;font-weight:600;color:#18B89F;letter-spacing:.3px;margin-bottom:8px}.h:before{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:#18B89F;box-shadow:0 0 10px #18B89F;margin-right:8px}.p{font-size:13.5px;line-height:1.55}.ft{margin-top:auto;font-size:10.5px;color:#9FC9C1;border-top:1px solid rgba(255,255,255,.08);padding-top:6px}@keyframes f{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}</style><div class='n'><div class='h'>Leitura automática</div><div class='p'>" & [Narrativa Forecast] & "</div><div class='ft'>Fato derivado dos filtros atuais · hipótese e ação a validar · não indica causa</div></div>"
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

### Cor Atingimento

```dax
VAR _a = [Atingimento Meta %] RETURN IF ( ISBLANK ( _a ), "#9FC9C1", IF ( _a >= 1, "#18B89F", IF ( _a >= 0.95, "#F2C46D", "#EF9277" ) ) )
```

### Cor Cobertura

```dax
VAR _c = [Cobertura (dias)] RETURN IF ( ISBLANK ( _c ), "#9FC9C1", IF ( _c <= 60, "#18B89F", IF ( _c <= 120, "#F2C46D", "#EF9277" ) ) )
```

### Cor Pontualidade

```dax
VAR _p = [Pontualidade %] RETURN IF ( ISBLANK ( _p ), "#9FC9C1", IF ( _p >= 0.9, "#18B89F", IF ( _p >= 0.7, "#F2C46D", "#EF9277" ) ) )
```

### Cor Margem Op

```dax
VAR _p = [Margem Operacional Simplificada %] RETURN IF ( ISBLANK ( _p ), "#9FC9C1", IF ( _p >= 0.2, "#18B89F", IF ( _p >= 0.1, "#F2C46D", "#EF9277" ) ) )
```

### Cor Validade

```dax
VAR _p = [% Valor em Risco Validade] RETURN IF ( ISBLANK ( _p ), "#9FC9C1", IF ( _p <= 0.05, "#18B89F", IF ( _p <= 0.1, "#F2C46D", "#EF9277" ) ) )
```

### Cor Perdas

```dax
VAR _p = [Perdas % CMV] RETURN IF ( ISBLANK ( _p ), "#9FC9C1", IF ( _p <= 0.01, "#18B89F", IF ( _p <= 0.02, "#F2C46D", "#EF9277" ) ) )
```

### Cor WAPE

```dax
VAR _p = [WAPE Backtest %] RETURN IF ( ISBLANK ( _p ), "#9FC9C1", IF ( _p <= 0.08, "#18B89F", IF ( _p <= 0.15, "#F2C46D", "#EF9277" ) ) )
```

### Txt Atingimento

```dax
[Txt Meta]
```

### Txt Cobertura Dias

```dax
IF ( ISBLANK ( [Cobertura (dias)] ), "", IF ( [Cobertura (dias)] > 120, "excesso: acima de 120 dias", IF ( [Cobertura (dias)] > 60, "atenção: 60 a 120 dias", "saudável: até 60 dias" ) ) )
```

### Txt Pontualidade Meta

```dax
"referência saudável ≥ 90%"
```

### Txt WAPE

```dax
"erro histórico · rolling-origin"
```

### Txt Giro

```dax
IF ( [Giro Anualizado] < 2, "baixo para varejo farma", "adequado" )
```

### Txt ROS Margem

```dax
"margem " & FORMAT ( [Margem Operacional Simplificada %], "0.0%", "pt-BR" ) & " · não é EBITDA"
```

## 11 SVG & HTML

### Cor Destaque Receita Mes

Destaca o mês de maior receita na seleção (Deneb).

```dax
VAR _mx = CALCULATE ( MAXX ( VALUES ( dCalendario[AnoMes Num] ), [Receita Líquida] ), ALLSELECTED ( dCalendario ) )
RETURN IF ( [Receita Líquida] = _mx, "#18B89F", "#2E7F78" )
```

### SVG Barra Receita Categoria

Barra SVG para coluna de tabela (categoria de dados ImageUrl).

```dax
VAR _v = [Receita Líquida Itens]
VAR _mx = CALCULATE ( MAXX ( ALLSELECTED ( dProduto[Categoria] ), [Receita Líquida Itens] ), ALLSELECTED ( dProduto[Categoria] ) )
VAR _w = IF ( _mx > 0, MAX ( 2, DIVIDE ( _v, _mx ) * 116 ), 0 )
RETURN IF ( NOT ISBLANK ( _v ),
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='18'><rect x='0' y='5' width='120' height='8' rx='4' fill='%23FFFFFF' fill-opacity='0.08'/><rect x='0' y='5' width='" & FORMAT ( _w, "0", "en-US" ) & "' height='8' rx='4' fill='%2318B89F'/></svg>" )
```

### SVG Barra Receita SKU

Barra SVG para coluna de tabela (categoria de dados ImageUrl).

```dax
VAR _v = [Receita Líquida Itens]
VAR _mx = CALCULATE ( MAXX ( ALLSELECTED ( dProduto[Produto] ), [Receita Líquida Itens] ), ALLSELECTED ( dProduto[Produto] ) )
VAR _w = IF ( _mx > 0, MAX ( 2, DIVIDE ( _v, _mx ) * 116 ), 0 )
RETURN IF ( NOT ISBLANK ( _v ),
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='18'><rect x='0' y='5' width='120' height='8' rx='4' fill='%23FFFFFF' fill-opacity='0.08'/><rect x='0' y='5' width='" & FORMAT ( _w, "0", "en-US" ) & "' height='8' rx='4' fill='%2318B89F'/></svg>" )
```

### SVG Barra Compras Fornecedor

Barra SVG para coluna de tabela (categoria de dados ImageUrl).

```dax
VAR _v = [Valor Recebido]
VAR _mx = CALCULATE ( MAXX ( ALLSELECTED ( dFornecedor[Fornecedor] ), [Valor Recebido] ), ALLSELECTED ( dFornecedor[Fornecedor] ) )
VAR _w = IF ( _mx > 0, MAX ( 2, DIVIDE ( _v, _mx ) * 116 ), 0 )
RETURN IF ( NOT ISBLANK ( _v ),
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='18'><rect x='0' y='5' width='120' height='8' rx='4' fill='%23FFFFFF' fill-opacity='0.08'/><rect x='0' y='5' width='" & FORMAT ( _w, "0", "en-US" ) & "' height='8' rx='4' fill='%2318B89F'/></svg>" )
```

### SVG Barra Estoque SKU

Barra SVG para coluna de tabela (categoria de dados ImageUrl).

```dax
VAR _v = [Estoque Final (R$)]
VAR _mx = CALCULATE ( MAXX ( ALLSELECTED ( dProduto[Produto] ), [Estoque Final (R$)] ), ALLSELECTED ( dProduto[Produto] ) )
VAR _w = IF ( _mx > 0, MAX ( 2, DIVIDE ( _v, _mx ) * 116 ), 0 )
RETURN IF ( NOT ISBLANK ( _v ),
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='18'><rect x='0' y='5' width='120' height='8' rx='4' fill='%23FFFFFF' fill-opacity='0.08'/><rect x='0' y='5' width='" & FORMAT ( _w, "0", "en-US" ) & "' height='8' rx='4' fill='%23EF9277'/></svg>" )
```

### HTML Chips Filtros

Chips HTML com os filtros ativos (inclusive os do painel oculto).

```dax
VAR _c = IF ( ISFILTERED ( dCalendario[Ano] ), "<span class='c'><b>Ano</b> " & IF ( COUNTROWS ( VALUES ( dCalendario[Ano] ) ) > 3, FORMAT ( COUNTROWS ( VALUES ( dCalendario[Ano] ) ), "0" ) & " itens", CONCATENATEX ( VALUES ( dCalendario[Ano] ), dCalendario[Ano], ", " ) ) & "</span>" )
    & IF ( ISFILTERED ( dCalendario[Mes Nome] ), "<span class='c'><b>Mês</b> " & IF ( COUNTROWS ( VALUES ( dCalendario[Mes Nome] ) ) > 3, FORMAT ( COUNTROWS ( VALUES ( dCalendario[Mes Nome] ) ), "0" ) & " itens", CONCATENATEX ( VALUES ( dCalendario[Mes Nome] ), dCalendario[Mes Nome], ", " ) ) & "</span>" )
    & IF ( ISFILTERED ( dLoja[Loja] ), "<span class='c'><b>Loja</b> " & IF ( COUNTROWS ( VALUES ( dLoja[Loja] ) ) > 3, FORMAT ( COUNTROWS ( VALUES ( dLoja[Loja] ) ), "0" ) & " itens", CONCATENATEX ( VALUES ( dLoja[Loja] ), dLoja[Loja], ", " ) ) & "</span>" )
    & IF ( ISFILTERED ( dCanal[Canal] ), "<span class='c'><b>Canal</b> " & IF ( COUNTROWS ( VALUES ( dCanal[Canal] ) ) > 3, FORMAT ( COUNTROWS ( VALUES ( dCanal[Canal] ) ), "0" ) & " itens", CONCATENATEX ( VALUES ( dCanal[Canal] ), dCanal[Canal], ", " ) ) & "</span>" )
    & IF ( ISFILTERED ( dProduto[Categoria] ), "<span class='c'><b>Categoria</b> " & IF ( COUNTROWS ( VALUES ( dProduto[Categoria] ) ) > 3, FORMAT ( COUNTROWS ( VALUES ( dProduto[Categoria] ) ), "0" ) & " itens", CONCATENATEX ( VALUES ( dProduto[Categoria] ), dProduto[Categoria], ", " ) ) & "</span>" )
    & IF ( ISFILTERED ( dProduto[Subcategoria] ), "<span class='c'><b>Subcategoria</b> " & IF ( COUNTROWS ( VALUES ( dProduto[Subcategoria] ) ) > 3, FORMAT ( COUNTROWS ( VALUES ( dProduto[Subcategoria] ) ), "0" ) & " itens", CONCATENATEX ( VALUES ( dProduto[Subcategoria] ), dProduto[Subcategoria], ", " ) ) & "</span>" )
    & IF ( ISFILTERED ( dFornecedor[Fornecedor] ), "<span class='c'><b>Fornecedor</b> " & IF ( COUNTROWS ( VALUES ( dFornecedor[Fornecedor] ) ) > 3, FORMAT ( COUNTROWS ( VALUES ( dFornecedor[Fornecedor] ) ), "0" ) & " itens", CONCATENATEX ( VALUES ( dFornecedor[Fornecedor] ), dFornecedor[Fornecedor], ", " ) ) & "</span>" )
    & IF ( ISFILTERED ( dCliente[Segmento RFV] ), "<span class='c'><b>RFV</b> " & IF ( COUNTROWS ( VALUES ( dCliente[Segmento RFV] ) ) > 3, FORMAT ( COUNTROWS ( VALUES ( dCliente[Segmento RFV] ) ), "0" ) & " itens", CONCATENATEX ( VALUES ( dCliente[Segmento RFV] ), dCliente[Segmento RFV], ", " ) ) & "</span>" )
    & IF ( ISFILTERED ( fEstoque[Status Estoque] ), "<span class='c'><b>Status</b> " & IF ( COUNTROWS ( VALUES ( fEstoque[Status Estoque] ) ) > 3, FORMAT ( COUNTROWS ( VALUES ( fEstoque[Status Estoque] ) ), "0" ) & " itens", CONCATENATEX ( VALUES ( fEstoque[Status Estoque] ), fEstoque[Status Estoque], ", " ) ) & "</span>" )
    & IF ( ISFILTERED ( dCenario[Cenario] ), "<span class='c'><b>Cenário</b> " & IF ( COUNTROWS ( VALUES ( dCenario[Cenario] ) ) > 3, FORMAT ( COUNTROWS ( VALUES ( dCenario[Cenario] ) ), "0" ) & " itens", CONCATENATEX ( VALUES ( dCenario[Cenario] ), dCenario[Cenario], ", " ) ) & "</span>" )
RETURN "<style>.w{font-family:Segoe UI,sans-serif;display:flex;flex-wrap:wrap;gap:6px;align-items:center;height:100%}.c{background:rgba(24,184,159,.16);border:1px solid rgba(24,184,159,.45);color:#DDF5EB;border-radius:20px;padding:3px 10px;font-size:11px;animation:f .4s ease both}.c b{color:#18B89F;font-weight:600;margin-right:3px}.z{color:#9FC9C1;font-size:11px}@keyframes f{from{opacity:0}to{opacity:1}}</style><div class='w'>" & IF ( _c = "", "<span class='z'>Sem filtros ativos · período completo 01/10/2024 a 30/09/2026</span>", _c ) & "</div>"
```

### HTML Tooltip Receita

```dax
VAR _r = [Receita Líquida]
VAR _y = [Receita YoY %]
VAR _c = IF ( ISBLANK ( _y ), "#9FC9C1", IF ( _y >= 0, "#18B89F", "#EF9277" ) )
RETURN "<style>.tt{font-family:Segoe UI,sans-serif;color:#E8F3F1;padding:4px}.tt .l{font-size:11px;color:#9FC9C1}.tt .b{font-size:22px;font-weight:600}.tt .r{display:flex;gap:18px;margin-top:8px}.tt .s{font-size:10px;color:#9FC9C1;margin-top:10px;border-top:1px solid rgba(255,255,255,.1);padding-top:6px}</style>"
    & "<div class='tt'><div class='l'>Receita líquida</div><div class='b'>" & IF ( ABS ( _r ) >= 1000000, "R$ " & FORMAT ( _r / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _r / 1000, "#,0.0", "pt-BR" ) & " mil" ) & "</div>"
    & "<div class='r'><div><div class='l'>Margem bruta</div><b>" & FORMAT ( [Margem Bruta %], "0.0%", "pt-BR" ) & "</b></div>"
    & "<div><div class='l'>Participação</div><b>" & FORMAT ( [Share Receita %], "0.0%", "pt-BR" ) & "</b></div>"
    & "<div><div class='l'>vs ano anterior</div><b style='color:" & _c & "'>" & IF ( ISBLANK ( _y ), "s/ base", FORMAT ( _y, "+0.0%;-0.0%", "pt-BR" ) ) & "</b></div></div>"
    & "<div class='s'>Receita = bruto − descontos (f_vendas). Variação só com período comparável.</div></div>"
```

### _Spark Cupons

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Cupons] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Receita Líquida

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Receita Líquida] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### HTML KPIs Home

Cards HTML (HTML Content) com valor, comparação, cor semântica e sparkline SVG animada.

```dax
VAR _v0 = [Qtd Lojas]
VAR _x0 = "Campinas · Jundiaí · Sorocaba · Piracicaba"
VAR _c0 = "#18B89F"
VAR _v1 = [SKUs no Catálogo]
VAR _x1 = "5 categorias"
VAR _c1 = "#18B89F"
VAR _v2 = [Clientes Cadastrados]
VAR _x2 = "IDs sintéticos"
VAR _c2 = "#18B89F"
VAR _v3 = [Cupons]
VAR _x3 = "24 meses"
VAR _c3 = "#18B89F"
VAR _s3 = [_Spark Cupons]
VAR _v4 = [Receita Líquida]
VAR _x4 = "out/24 – set/26"
VAR _c4 = "#18B89F"
VAR _s4 = [_Spark Receita Líquida]
RETURN
"<style>.g{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:14px;font-family:Segoe UI,sans-serif;padding:2px}.k{position:relative;background:linear-gradient(160deg,rgba(255,255,255,.08),rgba(255,255,255,.02));border:1px solid rgba(24,184,159,.28);border-radius:14px;padding:12px 14px 4px 18px;overflow:hidden;animation:up .6s ease both;box-shadow:0 8px 24px rgba(0,0,0,.25)}.k:before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c);box-shadow:0 0 12px var(--c)}.t{font-size:12px;color:#9FC9C1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.2px}.v{font-size:25px;font-weight:600;color:#FFFFFF;margin-top:2px;white-space:nowrap}.d{font-size:11px;color:var(--c);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.k svg{width:100%;height:30px;margin-top:2px;display:block}.k polyline{fill:none;stroke:var(--c);stroke-width:2;stroke-linejoin:round;stroke-dasharray:400;stroke-dashoffset:400;animation:dr 1.6s ease forwards .3s;vector-effect:non-scaling-stroke}.k:nth-child(2){animation-delay:.08s}.k:nth-child(3){animation-delay:.16s}.k:nth-child(4){animation-delay:.24s}.k:nth-child(5){animation-delay:.32s}.k:nth-child(6){animation-delay:.4s}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}@keyframes dr{to{stroke-dashoffset:0}}@media (prefers-reduced-motion:reduce){.k,.k polyline{animation:none;stroke-dashoffset:0;opacity:1}}</style><div class='g' style='--n:5'>"
    & "<div class='k' style='--c:" & _c0 & "'><div class='t'>Farmácias</div><div class='v'>" & IF ( ISBLANK ( _v0 ), "–", IF ( _v0 >= 1000000, FORMAT ( _v0 / 1000000, "#,0.00", "pt-BR" ) & " mi", IF ( _v0 >= 10000, FORMAT ( _v0 / 1000, "#,0.0", "pt-BR" ) & " mil", FORMAT ( _v0, "#,0", "pt-BR" ) ) ) ) & "</div><div class='d'>" & _x0 & "</div>" & "" & "</div>"
    & "<div class='k' style='--c:" & _c1 & "'><div class='t'>SKUs no catálogo</div><div class='v'>" & IF ( ISBLANK ( _v1 ), "–", IF ( _v1 >= 1000000, FORMAT ( _v1 / 1000000, "#,0.00", "pt-BR" ) & " mi", IF ( _v1 >= 10000, FORMAT ( _v1 / 1000, "#,0.0", "pt-BR" ) & " mil", FORMAT ( _v1, "#,0", "pt-BR" ) ) ) ) & "</div><div class='d'>" & _x1 & "</div>" & "" & "</div>"
    & "<div class='k' style='--c:" & _c2 & "'><div class='t'>Clientes cadastrados</div><div class='v'>" & IF ( ISBLANK ( _v2 ), "–", IF ( _v2 >= 1000000, FORMAT ( _v2 / 1000000, "#,0.00", "pt-BR" ) & " mi", IF ( _v2 >= 10000, FORMAT ( _v2 / 1000, "#,0.0", "pt-BR" ) & " mil", FORMAT ( _v2, "#,0", "pt-BR" ) ) ) ) & "</div><div class='d'>" & _x2 & "</div>" & "" & "</div>"
    & "<div class='k' style='--c:" & _c3 & "'><div class='t'>Vendas (cupons)</div><div class='v'>" & IF ( ISBLANK ( _v3 ), "–", IF ( _v3 >= 1000000, FORMAT ( _v3 / 1000000, "#,0.00", "pt-BR" ) & " mi", IF ( _v3 >= 10000, FORMAT ( _v3 / 1000, "#,0.0", "pt-BR" ) & " mil", FORMAT ( _v3, "#,0", "pt-BR" ) ) ) ) & "</div><div class='d'>" & _x3 & "</div>" & IF ( ISBLANK ( _s3 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s3 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c4 & "'><div class='t'>Receita líquida</div><div class='v'>" & IF ( ISBLANK ( _v4 ), "–", IF ( ABS ( _v4 ) >= 1000000, "R$ " & FORMAT ( _v4 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v4 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x4 & "</div>" & IF ( ISBLANK ( _s4 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s4 & "'/></svg>" ) & "</div>"
    & "</div>"
```

### _Spark Lucro Bruto

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Lucro Bruto] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Margem Bruta %

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Margem Bruta %] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Resultado Operacional Simplificado

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Resultado Operacional Simplificado] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Atingimento Meta %

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Atingimento Meta %] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Ticket Médio

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Ticket Médio] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### HTML KPIs Executiva

Cards HTML (HTML Content) com valor, comparação, cor semântica e sparkline SVG animada.

```dax
VAR _v0 = [Receita Líquida]
VAR _d0 = [Receita YoY %]
VAR _x0 = IF ( ISBLANK ( _d0 ), "sem base comparável no ano anterior", IF ( _d0 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d0 ), "0.0%", "pt-BR" ) & " vs ano anterior" )
VAR _c0 = IF ( ISBLANK ( _d0 ), "#9FC9C1", IF ( _d0 * 1 >= 0, "#18B89F", IF ( _d0 * 1 >= -0.03, "#F2C46D", "#EF9277" ) ) )
VAR _s0 = [_Spark Receita Líquida]
VAR _v1 = [Lucro Bruto]
VAR _d1 = [Lucro Bruto YoY %]
VAR _x1 = IF ( ISBLANK ( _d1 ), "sem base comparável no ano anterior", IF ( _d1 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d1 ), "0.0%", "pt-BR" ) & " vs ano anterior" )
VAR _c1 = IF ( ISBLANK ( _d1 ), "#9FC9C1", IF ( _d1 * 1 >= 0, "#18B89F", IF ( _d1 * 1 >= -0.03, "#F2C46D", "#EF9277" ) ) )
VAR _s1 = [_Spark Lucro Bruto]
VAR _v2 = [Margem Bruta %]
VAR _d2 = [Margem Bruta Var pp]
VAR _x2 = IF ( ISBLANK ( _d2 ), "sem base comparável no ano anterior", IF ( _d2 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d2 ), "0.0", "pt-BR" ) & " p.p. vs ano anterior" )
VAR _c2 = IF ( ISBLANK ( _d2 ), "#9FC9C1", IF ( _d2 * 1 >= 0, "#18B89F", IF ( _d2 * 1 >= -0.5, "#F2C46D", "#EF9277" ) ) )
VAR _s2 = [_Spark Margem Bruta %]
VAR _v3 = [Resultado Operacional Simplificado]
VAR _d3 = [Txt ROS Margem]
VAR _x3 = IF ( ISBLANK ( _d3 ), "sem base comparável no ano anterior", _d3 )
VAR _c3 = [Cor Margem Op]
VAR _s3 = [_Spark Resultado Operacional Simplificado]
VAR _v4 = [Atingimento Meta %]
VAR _d4 = [Txt Atingimento]
VAR _x4 = IF ( ISBLANK ( _d4 ), "sem base comparável no ano anterior", _d4 )
VAR _c4 = [Cor Atingimento]
VAR _s4 = [_Spark Atingimento Meta %]
VAR _v5 = [Ticket Médio]
VAR _d5 = [Ticket Médio YoY %]
VAR _x5 = IF ( ISBLANK ( _d5 ), "sem base comparável no ano anterior", IF ( _d5 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d5 ), "0.0%", "pt-BR" ) & " vs ano anterior" )
VAR _c5 = IF ( ISBLANK ( _d5 ), "#9FC9C1", IF ( _d5 * 1 >= 0, "#18B89F", IF ( _d5 * 1 >= -0.03, "#F2C46D", "#EF9277" ) ) )
VAR _s5 = [_Spark Ticket Médio]
RETURN
"<style>.g{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:14px;font-family:Segoe UI,sans-serif;padding:2px}.k{position:relative;background:linear-gradient(160deg,rgba(255,255,255,.08),rgba(255,255,255,.02));border:1px solid rgba(24,184,159,.28);border-radius:14px;padding:12px 14px 4px 18px;overflow:hidden;animation:up .6s ease both;box-shadow:0 8px 24px rgba(0,0,0,.25)}.k:before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c);box-shadow:0 0 12px var(--c)}.t{font-size:12px;color:#9FC9C1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.2px}.v{font-size:25px;font-weight:600;color:#FFFFFF;margin-top:2px;white-space:nowrap}.d{font-size:11px;color:var(--c);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.k svg{width:100%;height:30px;margin-top:2px;display:block}.k polyline{fill:none;stroke:var(--c);stroke-width:2;stroke-linejoin:round;stroke-dasharray:400;stroke-dashoffset:400;animation:dr 1.6s ease forwards .3s;vector-effect:non-scaling-stroke}.k:nth-child(2){animation-delay:.08s}.k:nth-child(3){animation-delay:.16s}.k:nth-child(4){animation-delay:.24s}.k:nth-child(5){animation-delay:.32s}.k:nth-child(6){animation-delay:.4s}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}@keyframes dr{to{stroke-dashoffset:0}}@media (prefers-reduced-motion:reduce){.k,.k polyline{animation:none;stroke-dashoffset:0;opacity:1}}</style><div class='g' style='--n:6'>"
    & "<div class='k' style='--c:" & _c0 & "'><div class='t'>Receita líquida</div><div class='v'>" & IF ( ISBLANK ( _v0 ), "–", IF ( ABS ( _v0 ) >= 1000000, "R$ " & FORMAT ( _v0 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v0 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x0 & "</div>" & IF ( ISBLANK ( _s0 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s0 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c1 & "'><div class='t'>Lucro bruto</div><div class='v'>" & IF ( ISBLANK ( _v1 ), "–", IF ( ABS ( _v1 ) >= 1000000, "R$ " & FORMAT ( _v1 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v1 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x1 & "</div>" & IF ( ISBLANK ( _s1 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s1 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c2 & "'><div class='t'>Margem bruta</div><div class='v'>" & IF ( ISBLANK ( _v2 ), "–", FORMAT ( _v2, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x2 & "</div>" & IF ( ISBLANK ( _s2 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s2 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c3 & "'><div class='t'>Resultado op. simplificado</div><div class='v'>" & IF ( ISBLANK ( _v3 ), "–", IF ( ABS ( _v3 ) >= 1000000, "R$ " & FORMAT ( _v3 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v3 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x3 & "</div>" & IF ( ISBLANK ( _s3 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s3 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c4 & "'><div class='t'>Atingimento da meta</div><div class='v'>" & IF ( ISBLANK ( _v4 ), "–", FORMAT ( _v4, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x4 & "</div>" & IF ( ISBLANK ( _s4 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s4 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c5 & "'><div class='t'>Ticket médio</div><div class='v'>" & IF ( ISBLANK ( _v5 ), "–", "R$ " & FORMAT ( _v5, "#,0.00", "pt-BR" ) ) & "</div><div class='d'>" & _x5 & "</div>" & IF ( ISBLANK ( _s5 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s5 & "'/></svg>" ) & "</div>"
    & "</div>"
```

### _Spark Clientes Ativos

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Clientes Ativos] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Clientes Novos

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Clientes Novos] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Frequência Média

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Frequência Média] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark % Cupons Identificados

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [% Cupons Identificados] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### HTML KPIs Clientes

Cards HTML (HTML Content) com valor, comparação, cor semântica e sparkline SVG animada.

```dax
VAR _v0 = [Cupons]
VAR _d0 = [Cupons YoY %]
VAR _x0 = IF ( ISBLANK ( _d0 ), "sem base comparável no ano anterior", IF ( _d0 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d0 ), "0.0%", "pt-BR" ) & " vs ano anterior" )
VAR _c0 = IF ( ISBLANK ( _d0 ), "#9FC9C1", IF ( _d0 * 1 >= 0, "#18B89F", IF ( _d0 * 1 >= -0.03, "#F2C46D", "#EF9277" ) ) )
VAR _s0 = [_Spark Cupons]
VAR _v1 = [Clientes Ativos]
VAR _d1 = [Clientes Ativos YoY %]
VAR _x1 = IF ( ISBLANK ( _d1 ), "sem base comparável no ano anterior", IF ( _d1 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d1 ), "0.0%", "pt-BR" ) & " vs ano anterior" )
VAR _c1 = IF ( ISBLANK ( _d1 ), "#9FC9C1", IF ( _d1 * 1 >= 0, "#18B89F", IF ( _d1 * 1 >= -0.03, "#F2C46D", "#EF9277" ) ) )
VAR _s1 = [_Spark Clientes Ativos]
VAR _v2 = [Clientes Novos]
VAR _d2 = [Txt Novos]
VAR _x2 = IF ( ISBLANK ( _d2 ), "sem base comparável no ano anterior", _d2 )
VAR _c2 = "#9FC9C1"
VAR _s2 = [_Spark Clientes Novos]
VAR _v3 = [Frequência Média]
VAR _x3 = "cupons por cliente identificado"
VAR _c3 = "#18B89F"
VAR _s3 = [_Spark Frequência Média]
VAR _v4 = [Ticket Médio]
VAR _d4 = [Ticket Médio YoY %]
VAR _x4 = IF ( ISBLANK ( _d4 ), "sem base comparável no ano anterior", IF ( _d4 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d4 ), "0.0%", "pt-BR" ) & " vs ano anterior" )
VAR _c4 = IF ( ISBLANK ( _d4 ), "#9FC9C1", IF ( _d4 * 1 >= 0, "#18B89F", IF ( _d4 * 1 >= -0.03, "#F2C46D", "#EF9277" ) ) )
VAR _s4 = [_Spark Ticket Médio]
VAR _v5 = [% Cupons Identificados]
VAR _x5 = "cupom anônimo não é cliente"
VAR _c5 = "#18B89F"
VAR _s5 = [_Spark % Cupons Identificados]
RETURN
"<style>.g{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:14px;font-family:Segoe UI,sans-serif;padding:2px}.k{position:relative;background:linear-gradient(160deg,rgba(255,255,255,.08),rgba(255,255,255,.02));border:1px solid rgba(24,184,159,.28);border-radius:14px;padding:12px 14px 4px 18px;overflow:hidden;animation:up .6s ease both;box-shadow:0 8px 24px rgba(0,0,0,.25)}.k:before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c);box-shadow:0 0 12px var(--c)}.t{font-size:12px;color:#9FC9C1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.2px}.v{font-size:25px;font-weight:600;color:#FFFFFF;margin-top:2px;white-space:nowrap}.d{font-size:11px;color:var(--c);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.k svg{width:100%;height:30px;margin-top:2px;display:block}.k polyline{fill:none;stroke:var(--c);stroke-width:2;stroke-linejoin:round;stroke-dasharray:400;stroke-dashoffset:400;animation:dr 1.6s ease forwards .3s;vector-effect:non-scaling-stroke}.k:nth-child(2){animation-delay:.08s}.k:nth-child(3){animation-delay:.16s}.k:nth-child(4){animation-delay:.24s}.k:nth-child(5){animation-delay:.32s}.k:nth-child(6){animation-delay:.4s}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}@keyframes dr{to{stroke-dashoffset:0}}@media (prefers-reduced-motion:reduce){.k,.k polyline{animation:none;stroke-dashoffset:0;opacity:1}}</style><div class='g' style='--n:6'>"
    & "<div class='k' style='--c:" & _c0 & "'><div class='t'>Cupons</div><div class='v'>" & IF ( ISBLANK ( _v0 ), "–", IF ( _v0 >= 1000000, FORMAT ( _v0 / 1000000, "#,0.00", "pt-BR" ) & " mi", IF ( _v0 >= 10000, FORMAT ( _v0 / 1000, "#,0.0", "pt-BR" ) & " mil", FORMAT ( _v0, "#,0", "pt-BR" ) ) ) ) & "</div><div class='d'>" & _x0 & "</div>" & IF ( ISBLANK ( _s0 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s0 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c1 & "'><div class='t'>Clientes ativos</div><div class='v'>" & IF ( ISBLANK ( _v1 ), "–", IF ( _v1 >= 1000000, FORMAT ( _v1 / 1000000, "#,0.00", "pt-BR" ) & " mi", IF ( _v1 >= 10000, FORMAT ( _v1 / 1000, "#,0.0", "pt-BR" ) & " mil", FORMAT ( _v1, "#,0", "pt-BR" ) ) ) ) & "</div><div class='d'>" & _x1 & "</div>" & IF ( ISBLANK ( _s1 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s1 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c2 & "'><div class='t'>Clientes novos</div><div class='v'>" & IF ( ISBLANK ( _v2 ), "–", IF ( _v2 >= 1000000, FORMAT ( _v2 / 1000000, "#,0.00", "pt-BR" ) & " mi", IF ( _v2 >= 10000, FORMAT ( _v2 / 1000, "#,0.0", "pt-BR" ) & " mil", FORMAT ( _v2, "#,0", "pt-BR" ) ) ) ) & "</div><div class='d'>" & _x2 & "</div>" & IF ( ISBLANK ( _s2 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s2 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c3 & "'><div class='t'>Frequência (cupons/cliente)</div><div class='v'>" & IF ( ISBLANK ( _v3 ), "–", FORMAT ( _v3, "#,0.00", "pt-BR" ) ) & "</div><div class='d'>" & _x3 & "</div>" & IF ( ISBLANK ( _s3 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s3 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c4 & "'><div class='t'>Ticket médio</div><div class='v'>" & IF ( ISBLANK ( _v4 ), "–", "R$ " & FORMAT ( _v4, "#,0.00", "pt-BR" ) ) & "</div><div class='d'>" & _x4 & "</div>" & IF ( ISBLANK ( _s4 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s4 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c5 & "'><div class='t'>Cupons identificados</div><div class='v'>" & IF ( ISBLANK ( _v5 ), "–", FORMAT ( _v5, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x5 & "</div>" & IF ( ISBLANK ( _s5 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s5 & "'/></svg>" ) & "</div>"
    & "</div>"
```

### _Spark Receita Líquida Itens

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Receita Líquida Itens] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Lucro Bruto Itens

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Lucro Bruto Itens] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Margem Bruta Itens %

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Margem Bruta Itens %] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Desconto Itens %

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Desconto Itens %] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark SKUs Vendidos

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [SKUs Vendidos] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Preço Médio Unitário

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Preço Médio Unitário] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### HTML KPIs Produtos

Cards HTML (HTML Content) com valor, comparação, cor semântica e sparkline SVG animada.

```dax
VAR _v0 = [Receita Líquida Itens]
VAR _d0 = [Receita Itens YoY %]
VAR _x0 = IF ( ISBLANK ( _d0 ), "sem base comparável no ano anterior", IF ( _d0 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d0 ), "0.0%", "pt-BR" ) & " vs ano anterior" )
VAR _c0 = IF ( ISBLANK ( _d0 ), "#9FC9C1", IF ( _d0 * 1 >= 0, "#18B89F", IF ( _d0 * 1 >= -0.03, "#F2C46D", "#EF9277" ) ) )
VAR _s0 = [_Spark Receita Líquida Itens]
VAR _v1 = [Lucro Bruto Itens]
VAR _x1 = "receita − CMV de itens"
VAR _c1 = "#18B89F"
VAR _s1 = [_Spark Lucro Bruto Itens]
VAR _v2 = [Margem Bruta Itens %]
VAR _d2 = [Margem Itens Var pp]
VAR _x2 = IF ( ISBLANK ( _d2 ), "sem base comparável no ano anterior", IF ( _d2 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d2 ), "0.0", "pt-BR" ) & " p.p. vs ano anterior" )
VAR _c2 = IF ( ISBLANK ( _d2 ), "#9FC9C1", IF ( _d2 * 1 >= 0, "#18B89F", IF ( _d2 * 1 >= -0.5, "#F2C46D", "#EF9277" ) ) )
VAR _s2 = [_Spark Margem Bruta Itens %]
VAR _v3 = [Desconto Itens %]
VAR _x3 = "quanto menor, melhor"
VAR _c3 = [Txt Neutro]
VAR _s3 = [_Spark Desconto Itens %]
VAR _v4 = [SKUs Vendidos]
VAR _d4 = [Txt SKUs]
VAR _x4 = IF ( ISBLANK ( _d4 ), "sem base comparável no ano anterior", _d4 )
VAR _c4 = "#9FC9C1"
VAR _s4 = [_Spark SKUs Vendidos]
VAR _v5 = [Preço Médio Unitário]
VAR _x5 = "receita / unidades"
VAR _c5 = "#18B89F"
VAR _s5 = [_Spark Preço Médio Unitário]
RETURN
"<style>.g{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:14px;font-family:Segoe UI,sans-serif;padding:2px}.k{position:relative;background:linear-gradient(160deg,rgba(255,255,255,.08),rgba(255,255,255,.02));border:1px solid rgba(24,184,159,.28);border-radius:14px;padding:12px 14px 4px 18px;overflow:hidden;animation:up .6s ease both;box-shadow:0 8px 24px rgba(0,0,0,.25)}.k:before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c);box-shadow:0 0 12px var(--c)}.t{font-size:12px;color:#9FC9C1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.2px}.v{font-size:25px;font-weight:600;color:#FFFFFF;margin-top:2px;white-space:nowrap}.d{font-size:11px;color:var(--c);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.k svg{width:100%;height:30px;margin-top:2px;display:block}.k polyline{fill:none;stroke:var(--c);stroke-width:2;stroke-linejoin:round;stroke-dasharray:400;stroke-dashoffset:400;animation:dr 1.6s ease forwards .3s;vector-effect:non-scaling-stroke}.k:nth-child(2){animation-delay:.08s}.k:nth-child(3){animation-delay:.16s}.k:nth-child(4){animation-delay:.24s}.k:nth-child(5){animation-delay:.32s}.k:nth-child(6){animation-delay:.4s}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}@keyframes dr{to{stroke-dashoffset:0}}@media (prefers-reduced-motion:reduce){.k,.k polyline{animation:none;stroke-dashoffset:0;opacity:1}}</style><div class='g' style='--n:6'>"
    & "<div class='k' style='--c:" & _c0 & "'><div class='t'>Receita líquida (itens)</div><div class='v'>" & IF ( ISBLANK ( _v0 ), "–", IF ( ABS ( _v0 ) >= 1000000, "R$ " & FORMAT ( _v0 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v0 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x0 & "</div>" & IF ( ISBLANK ( _s0 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s0 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c1 & "'><div class='t'>Lucro bruto (itens)</div><div class='v'>" & IF ( ISBLANK ( _v1 ), "–", IF ( ABS ( _v1 ) >= 1000000, "R$ " & FORMAT ( _v1 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v1 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x1 & "</div>" & IF ( ISBLANK ( _s1 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s1 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c2 & "'><div class='t'>Margem bruta (itens)</div><div class='v'>" & IF ( ISBLANK ( _v2 ), "–", FORMAT ( _v2, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x2 & "</div>" & IF ( ISBLANK ( _s2 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s2 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c3 & "'><div class='t'>Desconto sobre bruto</div><div class='v'>" & IF ( ISBLANK ( _v3 ), "–", FORMAT ( _v3, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x3 & "</div>" & IF ( ISBLANK ( _s3 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s3 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c4 & "'><div class='t'>SKUs com venda</div><div class='v'>" & IF ( ISBLANK ( _v4 ), "–", IF ( _v4 >= 1000000, FORMAT ( _v4 / 1000000, "#,0.00", "pt-BR" ) & " mi", IF ( _v4 >= 10000, FORMAT ( _v4 / 1000, "#,0.0", "pt-BR" ) & " mil", FORMAT ( _v4, "#,0", "pt-BR" ) ) ) ) & "</div><div class='d'>" & _x4 & "</div>" & IF ( ISBLANK ( _s4 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s4 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c5 & "'><div class='t'>Preço médio por unidade</div><div class='v'>" & IF ( ISBLANK ( _v5 ), "–", "R$ " & FORMAT ( _v5, "#,0.00", "pt-BR" ) ) & "</div><div class='d'>" & _x5 & "</div>" & IF ( ISBLANK ( _s5 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s5 & "'/></svg>" ) & "</div>"
    & "</div>"
```

### _Spark Valor Recebido

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Valor Recebido] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Recebimentos

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Recebimentos] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Lead Time Médio

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Lead Time Médio] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Pontualidade %

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Pontualidade %] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Atraso Médio

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Atraso Médio] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### HTML KPIs Compras

Cards HTML (HTML Content) com valor, comparação, cor semântica e sparkline SVG animada.

```dax
VAR _v0 = [Valor Recebido]
VAR _d0 = [Txt Orçamento]
VAR _x0 = IF ( ISBLANK ( _d0 ), "sem base comparável no ano anterior", _d0 )
VAR _c0 = "#9FC9C1"
VAR _s0 = [_Spark Valor Recebido]
VAR _v1 = [Recebimentos]
VAR _x1 = "entregas registradas"
VAR _c1 = "#18B89F"
VAR _s1 = [_Spark Recebimentos]
VAR _v2 = [Lead Time Médio]
VAR _d2 = [Txt Pontualidade]
VAR _x2 = IF ( ISBLANK ( _d2 ), "sem base comparável no ano anterior", _d2 )
VAR _c2 = "#9FC9C1"
VAR _s2 = [_Spark Lead Time Médio]
VAR _v3 = [Pontualidade %]
VAR _d3 = [Txt Pontualidade Meta]
VAR _x3 = IF ( ISBLANK ( _d3 ), "sem base comparável no ano anterior", _d3 )
VAR _c3 = [Cor Pontualidade]
VAR _s3 = [_Spark Pontualidade %]
VAR _v4 = [Atraso Médio]
VAR _x4 = "só entregas atrasadas"
VAR _c4 = [Cor Pontualidade]
VAR _s4 = [_Spark Atraso Médio]
VAR _v5 = [Concentração Top 5 %]
VAR _x5 = "fornecedores por valor"
VAR _c5 = "#18B89F"
RETURN
"<style>.g{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:14px;font-family:Segoe UI,sans-serif;padding:2px}.k{position:relative;background:linear-gradient(160deg,rgba(255,255,255,.08),rgba(255,255,255,.02));border:1px solid rgba(24,184,159,.28);border-radius:14px;padding:12px 14px 4px 18px;overflow:hidden;animation:up .6s ease both;box-shadow:0 8px 24px rgba(0,0,0,.25)}.k:before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c);box-shadow:0 0 12px var(--c)}.t{font-size:12px;color:#9FC9C1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.2px}.v{font-size:25px;font-weight:600;color:#FFFFFF;margin-top:2px;white-space:nowrap}.d{font-size:11px;color:var(--c);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.k svg{width:100%;height:30px;margin-top:2px;display:block}.k polyline{fill:none;stroke:var(--c);stroke-width:2;stroke-linejoin:round;stroke-dasharray:400;stroke-dashoffset:400;animation:dr 1.6s ease forwards .3s;vector-effect:non-scaling-stroke}.k:nth-child(2){animation-delay:.08s}.k:nth-child(3){animation-delay:.16s}.k:nth-child(4){animation-delay:.24s}.k:nth-child(5){animation-delay:.32s}.k:nth-child(6){animation-delay:.4s}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}@keyframes dr{to{stroke-dashoffset:0}}@media (prefers-reduced-motion:reduce){.k,.k polyline{animation:none;stroke-dashoffset:0;opacity:1}}</style><div class='g' style='--n:6'>"
    & "<div class='k' style='--c:" & _c0 & "'><div class='t'>Compras recebidas</div><div class='v'>" & IF ( ISBLANK ( _v0 ), "–", IF ( ABS ( _v0 ) >= 1000000, "R$ " & FORMAT ( _v0 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v0 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x0 & "</div>" & IF ( ISBLANK ( _s0 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s0 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c1 & "'><div class='t'>Recebimentos</div><div class='v'>" & IF ( ISBLANK ( _v1 ), "–", IF ( _v1 >= 1000000, FORMAT ( _v1 / 1000000, "#,0.00", "pt-BR" ) & " mi", IF ( _v1 >= 10000, FORMAT ( _v1 / 1000, "#,0.0", "pt-BR" ) & " mil", FORMAT ( _v1, "#,0", "pt-BR" ) ) ) ) & "</div><div class='d'>" & _x1 & "</div>" & IF ( ISBLANK ( _s1 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s1 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c2 & "'><div class='t'>Lead time médio</div><div class='v'>" & IF ( ISBLANK ( _v2 ), "–", FORMAT ( _v2, "#,0.0", "pt-BR" ) & " dias" ) & "</div><div class='d'>" & _x2 & "</div>" & IF ( ISBLANK ( _s2 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s2 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c3 & "'><div class='t'>Pontualidade (OTD)</div><div class='v'>" & IF ( ISBLANK ( _v3 ), "–", FORMAT ( _v3, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x3 & "</div>" & IF ( ISBLANK ( _s3 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s3 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c4 & "'><div class='t'>Atraso médio quando atrasa</div><div class='v'>" & IF ( ISBLANK ( _v4 ), "–", FORMAT ( _v4, "#,0.0", "pt-BR" ) & " dias" ) & "</div><div class='d'>" & _x4 & "</div>" & IF ( ISBLANK ( _s4 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s4 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c5 & "'><div class='t'>Concentração top 5</div><div class='v'>" & IF ( ISBLANK ( _v5 ), "–", FORMAT ( _v5, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x5 & "</div>" & "" & "</div>"
    & "</div>"
```

### _Spark Estoque Final (R$)

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Estoque Final (R$)] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Estoque Final (un)

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Estoque Final (un)] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Cobertura (dias)

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Cobertura (dias)] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Perdas (R$)

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Perdas (R$)] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### HTML KPIs Estoque

Cards HTML (HTML Content) com valor, comparação, cor semântica e sparkline SVG animada.

```dax
VAR _v0 = [Estoque Final (R$)]
VAR _d0 = [Txt Cobertura]
VAR _x0 = IF ( ISBLANK ( _d0 ), "sem base comparável no ano anterior", _d0 )
VAR _c0 = [Cor Cobertura]
VAR _s0 = [_Spark Estoque Final (R$)]
VAR _v1 = [Estoque Final (un)]
VAR _x1 = "saldo no fim do período"
VAR _c1 = [Cor Cobertura]
VAR _s1 = [_Spark Estoque Final (un)]
VAR _v2 = [Cobertura (dias)]
VAR _d2 = [Txt Cobertura Dias]
VAR _x2 = IF ( ISBLANK ( _d2 ), "sem base comparável no ano anterior", _d2 )
VAR _c2 = [Cor Cobertura]
VAR _s2 = [_Spark Cobertura (dias)]
VAR _v3 = [Giro Anualizado]
VAR _d3 = [Txt Giro]
VAR _x3 = IF ( ISBLANK ( _d3 ), "sem base comparável no ano anterior", _d3 )
VAR _c3 = [Cor Cobertura]
VAR _v4 = [Perdas (R$)]
VAR _d4 = [Txt Perdas]
VAR _x4 = IF ( ISBLANK ( _d4 ), "sem base comparável no ano anterior", _d4 )
VAR _c4 = [Cor Perdas]
VAR _s4 = [_Spark Perdas (R$)]
VAR _v5 = [Valor em Risco Validade (R$)]
VAR _d5 = [Txt Validade]
VAR _x5 = IF ( ISBLANK ( _d5 ), "sem base comparável no ano anterior", _d5 )
VAR _c5 = [Cor Validade]
RETURN
"<style>.g{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:14px;font-family:Segoe UI,sans-serif;padding:2px}.k{position:relative;background:linear-gradient(160deg,rgba(255,255,255,.08),rgba(255,255,255,.02));border:1px solid rgba(24,184,159,.28);border-radius:14px;padding:12px 14px 4px 18px;overflow:hidden;animation:up .6s ease both;box-shadow:0 8px 24px rgba(0,0,0,.25)}.k:before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c);box-shadow:0 0 12px var(--c)}.t{font-size:12px;color:#9FC9C1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.2px}.v{font-size:25px;font-weight:600;color:#FFFFFF;margin-top:2px;white-space:nowrap}.d{font-size:11px;color:var(--c);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.k svg{width:100%;height:30px;margin-top:2px;display:block}.k polyline{fill:none;stroke:var(--c);stroke-width:2;stroke-linejoin:round;stroke-dasharray:400;stroke-dashoffset:400;animation:dr 1.6s ease forwards .3s;vector-effect:non-scaling-stroke}.k:nth-child(2){animation-delay:.08s}.k:nth-child(3){animation-delay:.16s}.k:nth-child(4){animation-delay:.24s}.k:nth-child(5){animation-delay:.32s}.k:nth-child(6){animation-delay:.4s}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}@keyframes dr{to{stroke-dashoffset:0}}@media (prefers-reduced-motion:reduce){.k,.k polyline{animation:none;stroke-dashoffset:0;opacity:1}}</style><div class='g' style='--n:6'>"
    & "<div class='k' style='--c:" & _c0 & "'><div class='t'>Estoque final (custo)</div><div class='v'>" & IF ( ISBLANK ( _v0 ), "–", IF ( ABS ( _v0 ) >= 1000000, "R$ " & FORMAT ( _v0 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v0 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x0 & "</div>" & IF ( ISBLANK ( _s0 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s0 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c1 & "'><div class='t'>Estoque final (unidades)</div><div class='v'>" & IF ( ISBLANK ( _v1 ), "–", IF ( _v1 >= 1000000, FORMAT ( _v1 / 1000000, "#,0.00", "pt-BR" ) & " mi", IF ( _v1 >= 10000, FORMAT ( _v1 / 1000, "#,0.0", "pt-BR" ) & " mil", FORMAT ( _v1, "#,0", "pt-BR" ) ) ) ) & "</div><div class='d'>" & _x1 & "</div>" & IF ( ISBLANK ( _s1 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s1 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c2 & "'><div class='t'>Cobertura estimada</div><div class='v'>" & IF ( ISBLANK ( _v2 ), "–", FORMAT ( _v2, "#,0", "pt-BR" ) & " dias" ) & "</div><div class='d'>" & _x2 & "</div>" & IF ( ISBLANK ( _s2 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s2 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c3 & "'><div class='t'>Giro anualizado</div><div class='v'>" & IF ( ISBLANK ( _v3 ), "–", FORMAT ( _v3, "0.00", "pt-BR" ) & "x" ) & "</div><div class='d'>" & _x3 & "</div>" & "" & "</div>"
    & "<div class='k' style='--c:" & _c4 & "'><div class='t'>Perdas (custo)</div><div class='v'>" & IF ( ISBLANK ( _v4 ), "–", IF ( ABS ( _v4 ) >= 1000000, "R$ " & FORMAT ( _v4 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v4 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x4 & "</div>" & IF ( ISBLANK ( _s4 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s4 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c5 & "'><div class='t'>Risco de validade</div><div class='v'>" & IF ( ISBLANK ( _v5 ), "–", IF ( ABS ( _v5 ) >= 1000000, "R$ " & FORMAT ( _v5 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v5 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x5 & "</div>" & "" & "</div>"
    & "</div>"
```

### _Spark Despesas

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Despesas] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Margem Operacional Simplificada %

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Margem Operacional Simplificada %] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### _Spark Atingimento Lucro Bruto %

Pontos da sparkline (viewBox 100×30) dos últimos 12 meses.

```dax
VAR _fim = MIN ( CALCULATE ( MAX ( dCalendario[Data] ) ), [_Data Base] )
VAR _ini = EDATE ( EOMONTH ( _fim, -1 ) + 1, -11 )
VAR _t = CALCULATETABLE (
    ADDCOLUMNS ( SUMMARIZE ( FILTER ( ALL ( dCalendario ), dCalendario[Data] >= _ini && dCalendario[Data] <= _fim ), dCalendario[AnoMes Num] ), "@v", [Atingimento Lucro Bruto %] ),
    REMOVEFILTERS ( dCalendario ) )
VAR _f = FILTER ( _t, NOT ISBLANK ( [@v] ) )
VAR _n = COUNTROWS ( _f )
VAR _mn = MINX ( _f, [@v] )
VAR _mx = MAXX ( _f, [@v] )
VAR _r = ADDCOLUMNS ( _f, "@i", RANKX ( _f, dCalendario[AnoMes Num],, ASC ) )
RETURN IF ( _n >= 2,
    CONCATENATEX ( _r,
        FORMAT ( ( [@i] - 1 ) / ( _n - 1 ) * 100, "0.0", "en-US" ) & "," & FORMAT ( 27 - DIVIDE ( [@v] - _mn, _mx - _mn, 0.5 ) * 22, "0.0", "en-US" ),
        " ", dCalendario[AnoMes Num], ASC ) )
```

### HTML KPIs Financeiro

Cards HTML (HTML Content) com valor, comparação, cor semântica e sparkline SVG animada.

```dax
VAR _v0 = [Receita Líquida]
VAR _d0 = [Receita YoY %]
VAR _x0 = IF ( ISBLANK ( _d0 ), "sem base comparável no ano anterior", IF ( _d0 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d0 ), "0.0%", "pt-BR" ) & " vs ano anterior" )
VAR _c0 = IF ( ISBLANK ( _d0 ), "#9FC9C1", IF ( _d0 * 1 >= 0, "#18B89F", IF ( _d0 * 1 >= -0.03, "#F2C46D", "#EF9277" ) ) )
VAR _s0 = [_Spark Receita Líquida]
VAR _v1 = [Lucro Bruto]
VAR _d1 = [Lucro Bruto YoY %]
VAR _x1 = IF ( ISBLANK ( _d1 ), "sem base comparável no ano anterior", IF ( _d1 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d1 ), "0.0%", "pt-BR" ) & " vs ano anterior" )
VAR _c1 = IF ( ISBLANK ( _d1 ), "#9FC9C1", IF ( _d1 * 1 >= 0, "#18B89F", IF ( _d1 * 1 >= -0.03, "#F2C46D", "#EF9277" ) ) )
VAR _s1 = [_Spark Lucro Bruto]
VAR _v2 = [Despesas]
VAR _x2 = "pessoal, aluguel, operação, marketing"
VAR _c2 = [Txt Neutro]
VAR _s2 = [_Spark Despesas]
VAR _v3 = [Resultado Operacional Simplificado]
VAR _d3 = [Resultado Op Simplificado YoY %]
VAR _x3 = IF ( ISBLANK ( _d3 ), "sem base comparável no ano anterior", IF ( _d3 >= 0, "▲ +", "▼ −" ) & FORMAT ( ABS ( _d3 ), "0.0%", "pt-BR" ) & " vs ano anterior" )
VAR _c3 = IF ( ISBLANK ( _d3 ), "#9FC9C1", IF ( _d3 * 1 >= 0, "#18B89F", IF ( _d3 * 1 >= -0.03, "#F2C46D", "#EF9277" ) ) )
VAR _s3 = [_Spark Resultado Operacional Simplificado]
VAR _v4 = [Margem Operacional Simplificada %]
VAR _d4 = [Txt Margem Op]
VAR _x4 = IF ( ISBLANK ( _d4 ), "sem base comparável no ano anterior", _d4 )
VAR _c4 = [Cor Margem Op]
VAR _s4 = [_Spark Margem Operacional Simplificada %]
VAR _v5 = [Atingimento Lucro Bruto %]
VAR _x5 = "lucro bruto / meta"
VAR _c5 = [Cor Atingimento]
VAR _s5 = [_Spark Atingimento Lucro Bruto %]
RETURN
"<style>.g{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:14px;font-family:Segoe UI,sans-serif;padding:2px}.k{position:relative;background:linear-gradient(160deg,rgba(255,255,255,.08),rgba(255,255,255,.02));border:1px solid rgba(24,184,159,.28);border-radius:14px;padding:12px 14px 4px 18px;overflow:hidden;animation:up .6s ease both;box-shadow:0 8px 24px rgba(0,0,0,.25)}.k:before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c);box-shadow:0 0 12px var(--c)}.t{font-size:12px;color:#9FC9C1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.2px}.v{font-size:25px;font-weight:600;color:#FFFFFF;margin-top:2px;white-space:nowrap}.d{font-size:11px;color:var(--c);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.k svg{width:100%;height:30px;margin-top:2px;display:block}.k polyline{fill:none;stroke:var(--c);stroke-width:2;stroke-linejoin:round;stroke-dasharray:400;stroke-dashoffset:400;animation:dr 1.6s ease forwards .3s;vector-effect:non-scaling-stroke}.k:nth-child(2){animation-delay:.08s}.k:nth-child(3){animation-delay:.16s}.k:nth-child(4){animation-delay:.24s}.k:nth-child(5){animation-delay:.32s}.k:nth-child(6){animation-delay:.4s}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}@keyframes dr{to{stroke-dashoffset:0}}@media (prefers-reduced-motion:reduce){.k,.k polyline{animation:none;stroke-dashoffset:0;opacity:1}}</style><div class='g' style='--n:6'>"
    & "<div class='k' style='--c:" & _c0 & "'><div class='t'>Receita líquida</div><div class='v'>" & IF ( ISBLANK ( _v0 ), "–", IF ( ABS ( _v0 ) >= 1000000, "R$ " & FORMAT ( _v0 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v0 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x0 & "</div>" & IF ( ISBLANK ( _s0 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s0 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c1 & "'><div class='t'>Lucro bruto</div><div class='v'>" & IF ( ISBLANK ( _v1 ), "–", IF ( ABS ( _v1 ) >= 1000000, "R$ " & FORMAT ( _v1 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v1 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x1 & "</div>" & IF ( ISBLANK ( _s1 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s1 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c2 & "'><div class='t'>Despesas modeladas</div><div class='v'>" & IF ( ISBLANK ( _v2 ), "–", IF ( ABS ( _v2 ) >= 1000000, "R$ " & FORMAT ( _v2 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v2 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x2 & "</div>" & IF ( ISBLANK ( _s2 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s2 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c3 & "'><div class='t'>Resultado op. simplificado</div><div class='v'>" & IF ( ISBLANK ( _v3 ), "–", IF ( ABS ( _v3 ) >= 1000000, "R$ " & FORMAT ( _v3 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v3 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x3 & "</div>" & IF ( ISBLANK ( _s3 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s3 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c4 & "'><div class='t'>Margem op. simplificada</div><div class='v'>" & IF ( ISBLANK ( _v4 ), "–", FORMAT ( _v4, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x4 & "</div>" & IF ( ISBLANK ( _s4 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s4 & "'/></svg>" ) & "</div>"
    & "<div class='k' style='--c:" & _c5 & "'><div class='t'>Atingimento meta de lucro</div><div class='v'>" & IF ( ISBLANK ( _v5 ), "–", FORMAT ( _v5, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x5 & "</div>" & IF ( ISBLANK ( _s5 ), "", "<svg viewBox='0 0 100 30' preserveAspectRatio='none'><polyline points='" & _s5 & "'/></svg>" ) & "</div>"
    & "</div>"
```

### HTML KPIs Forecast

Cards HTML (HTML Content) com valor, comparação, cor semântica e sparkline SVG animada.

```dax
VAR _v0 = [Receita Prevista Cenário]
VAR _d0 = [Txt Forecast Intervalo]
VAR _x0 = IF ( ISBLANK ( _d0 ), "sem base comparável no ano anterior", _d0 )
VAR _c0 = "#9FC9C1"
VAR _v1 = [Lucro Bruto Previsto Cenário]
VAR _x1 = "premissa: CMV% últimos 12m × fator"
VAR _c1 = "#18B89F"
VAR _v2 = [Crescimento Previsto vs LY %]
VAR _x2 = "mesmos meses do ano anterior"
VAR _c2 = "#18B89F"
VAR _v3 = [WAPE Backtest %]
VAR _d3 = [Txt WAPE]
VAR _x3 = IF ( ISBLANK ( _d3 ), "sem base comparável no ano anterior", _d3 )
VAR _c3 = [Cor WAPE]
VAR _v4 = [Viés Backtest %]
VAR _x4 = "+ = superestima"
VAR _c4 = [Txt Neutro]
VAR _v5 = [Cenário Ativo]
VAR _x5 = "Conservador · Base · Otimista"
VAR _c5 = "#18B89F"
RETURN
"<style>.g{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:14px;font-family:Segoe UI,sans-serif;padding:2px}.k{position:relative;background:linear-gradient(160deg,rgba(255,255,255,.08),rgba(255,255,255,.02));border:1px solid rgba(24,184,159,.28);border-radius:14px;padding:12px 14px 4px 18px;overflow:hidden;animation:up .6s ease both;box-shadow:0 8px 24px rgba(0,0,0,.25)}.k:before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--c);box-shadow:0 0 12px var(--c)}.t{font-size:12px;color:#9FC9C1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;letter-spacing:.2px}.v{font-size:25px;font-weight:600;color:#FFFFFF;margin-top:2px;white-space:nowrap}.d{font-size:11px;color:var(--c);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.k svg{width:100%;height:30px;margin-top:2px;display:block}.k polyline{fill:none;stroke:var(--c);stroke-width:2;stroke-linejoin:round;stroke-dasharray:400;stroke-dashoffset:400;animation:dr 1.6s ease forwards .3s;vector-effect:non-scaling-stroke}.k:nth-child(2){animation-delay:.08s}.k:nth-child(3){animation-delay:.16s}.k:nth-child(4){animation-delay:.24s}.k:nth-child(5){animation-delay:.32s}.k:nth-child(6){animation-delay:.4s}@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}@keyframes dr{to{stroke-dashoffset:0}}@media (prefers-reduced-motion:reduce){.k,.k polyline{animation:none;stroke-dashoffset:0;opacity:1}}</style><div class='g' style='--n:6'>"
    & "<div class='k' style='--c:" & _c0 & "'><div class='t'>Receita prevista · 6 meses</div><div class='v'>" & IF ( ISBLANK ( _v0 ), "–", IF ( ABS ( _v0 ) >= 1000000, "R$ " & FORMAT ( _v0 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v0 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x0 & "</div>" & "" & "</div>"
    & "<div class='k' style='--c:" & _c1 & "'><div class='t'>Lucro bruto previsto</div><div class='v'>" & IF ( ISBLANK ( _v1 ), "–", IF ( ABS ( _v1 ) >= 1000000, "R$ " & FORMAT ( _v1 / 1000000, "#,0.00", "pt-BR" ) & " mi", "R$ " & FORMAT ( _v1 / 1000, "#,0.0", "pt-BR" ) & " mil" ) ) & "</div><div class='d'>" & _x1 & "</div>" & "" & "</div>"
    & "<div class='k' style='--c:" & _c2 & "'><div class='t'>Crescimento vs LY</div><div class='v'>" & IF ( ISBLANK ( _v2 ), "–", FORMAT ( _v2, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x2 & "</div>" & "" & "</div>"
    & "<div class='k' style='--c:" & _c3 & "'><div class='t'>WAPE do backtest</div><div class='v'>" & IF ( ISBLANK ( _v3 ), "–", FORMAT ( _v3, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x3 & "</div>" & "" & "</div>"
    & "<div class='k' style='--c:" & _c4 & "'><div class='t'>Viés do backtest</div><div class='v'>" & IF ( ISBLANK ( _v4 ), "–", FORMAT ( _v4, "0.0%", "pt-BR" ) ) & "</div><div class='d'>" & _x4 & "</div>" & "" & "</div>"
    & "<div class='k' style='--c:" & _c5 & "'><div class='t'>Cenário ativo</div><div class='v'>" & IF ( ISBLANK ( _v5 ), "–", _v5 ) & "</div><div class='d'>" & _x5 & "</div>" & "" & "</div>"
    & "</div>"
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
