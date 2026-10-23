import csv,random,datetime,calendar,zipfile,json,os,collections,math
from pathlib import Path
R=random.Random(20261022)
D=Path(__file__).parent
start=datetime.date(2024,10,1); end=datetime.date(2026,9,30)
def save(name,header,rows):
 with (D/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.writer(f,delimiter=';'); w.writerow(header); w.writerows(rows)

def money(v):return f'{v:.2f}' # decimal dot, semicolon delimiter
stores=[('L001','Campinas','SP','Campinas - Cambuí','2021-03-15',1.21),('L002','Jundiaí','SP','Jundiaí - Centro','2022-05-10',1.04),('L003','Sorocaba','SP','Sorocaba - Campolim','2023-02-01',1.12),('L004','Piracicaba','SP','Piracicaba - Centro','2024-06-12',0.91)]
save('dim_lojas.csv',['id_loja','cidade','uf','nome_loja','data_abertura','indice_demanda'],stores)
categories=[('Medicamentos',2100,[('Analgésicos e antitérmicos',.23),('Antialérgicos',.10),('Cardiovascular',.14),('Gastrointestinal',.13),('Dermatológicos',.09),('Antibióticos',.09),('Vitaminas e minerais',.10),('Outros medicamentos',.12)]),('Suplementos',850,[('Proteínas',.25),('Vitaminas',.30),('Creatina',.13),('Bem-estar',.32)]),('Higiene e Beleza',900,[('Cabelos',.28),('Cuidados com a pele',.26),('Higiene bucal',.24),('Higiene pessoal',.22)]),('Baby',550,[('Fraldas',.35),('Fórmulas infantis',.20),('Lenços umedecidos',.25),('Cuidados infantis',.20)]),('Perfumaria',600,[('Perfumes',.35),('Desodorantes',.30),('Body splash',.15),('Kits e presentes',.20)])]
assert sum(c[1] for c in categories)==5000
brands=['VittaCare','MedNova','BioEssence','ClariMed','NaturaVida','UniPharma','DermaPlus','Solara','Essentia','NeoHealth','BellaPura','FarmaLab','BabyJoy','VidaFit','PrimeCare','Puravie','NexMed','AltoBem']
prods=[]; catalog=[]
for cat,n,subs in categories:
 for j in range(n):
  sub=R.choices([x[0] for x in subs],[x[1] for x in subs])[0]
  brand=R.choice(brands)
  mult={'Medicamentos':(7,95),'Suplementos':(25,220),'Higiene e Beleza':(6,115),'Baby':(10,175),'Perfumaria':(15,320)}[cat]
  price=round(R.uniform(*mult),2)
  margin=R.uniform(.23,.44) if cat=='Medicamentos' else R.uniform(.32,.57)
  cost=round(price*(1-margin),2)
  generico=int(cat=='Medicamentos' and R.random()<.41)
  controlado=int(cat=='Medicamentos' and R.random()<.06)
  rx=int(cat=='Medicamentos' and R.random()<.52)
  code=f'P{len(prods)+1:05d}'
  name=f'{sub} {brand} {j+1:04d}'
  prods.append((code,name,cat,sub,brand,money(price),money(cost),generico,controlado,rx,'Ativo'))
  catalog.append((code,cat,sub,price,cost,brand))
save('dim_produtos.csv',['id_produto','nome_produto','categoria','subcategoria','marca','preco_lista_referencia','custo_unitario_referencia','eh_generico','eh_controlado','exige_receita','status'],prods)
customers=[]
for i in range(1,22001):
 join=start+datetime.timedelta(days=R.randrange((end-start).days+1))
 city=R.choices([s[1] for s in stores],[.30,.23,.26,.21])[0]
 segment=R.choices(['Fidelidade','Regular','Ocasional'],[.31,.49,.20])[0]
 customers.append((f'C{i:06d}',city,join.isoformat(),segment,R.choice(['18-29','30-44','45-59','60+'])))
save('dim_clientes.csv',['id_cliente','cidade_cadastro','data_cadastro','segmento_cadastro','faixa_etaria'],customers)
customer_by_month=collections.defaultdict(list)
for c in customers:
 k=c[2][:7];customer_by_month[k].append(c[0])
months=[]
for year in [2024,2025,2026]:
 for m in range(1,13):
  d=datetime.date(year,m,1)
  if start<=d<=end:months.append((year,m,f'{year}-{m:02d}',calendar.monthrange(year,m)[1]))
# assortment, store monthly targets: 4x 5000 all active at least once, but each store stocks ~4000
assort={s[0]:set(R.sample(range(5000),k=4050+R.randrange(300))) for s in stores}
# Store product initial stock; monthly demand built bottom-up from orders, inventory purchases always reconcile
stock={(s[0],catalog[idx][0]):R.randint(8,42) for s in stores for idx in assort[s[0]]}
initial_rows=[(l,p,q,'2024-09-30') for (l,p),q in sorted(stock.items())]
save('f_estoque_inicial.csv',['id_loja','id_produto','quantidade_inicial','data_base'],initial_rows)
orders=[];lines=[];stock_rows=[];cost_rows=[];goals=[];returns=[]
all_registered=[];orderid=0;lineid=0;returnid=0
sum_month=collections.defaultdict(lambda:[0.,0.,0])
# reusable customer population by start date, avoiding selection for future registrations
for year,m,ym,days in months:
 all_registered.extend(customer_by_month.get(ym,[]))
 base_month=13 if m==12 else 12 if m in (11,5) else 9 if m==2 else 10
 for store in stores:
  lid=store[0]; factor=store[-1]
  n_orders=int((1190+ (year-2024)*115)*factor*base_month/10 * R.uniform(.96,1.04))
  demand=collections.Counter();revenue=0;cmv=0;discounts=0
  available=tuple(assort[lid])
  for _ in range(n_orders):
   day=R.randint(1,days);dt=datetime.date(year,m,day)
   orderid+=1;oid=f'V{orderid:08d}'
   cid=R.choice(all_registered) if R.random()<.83 and all_registered else ''
   channel=R.choices(['Loja física','Site','Aplicativo','Delivery'],[.72,.10,.11,.07])[0]
   payment=R.choices(['Pix','Cartão crédito','Cartão débito','Dinheiro'],[.28,.39,.26,.07])[0]
   num=R.choices([1,2,3,4,5,6],[.36,.29,.18,.10,.05,.02])[0]
   skus=R.sample(available,num)
   total_gross=total_disc=total_net=total_cost=0.
   for idx in skus:
    p,cat,sub,price,cost,brand=catalog[idx]
    qty=R.choices([1,2,3,4],[.76,.18,.05,.01])[0]
    discpct=R.choices([0,.03,.06,.1,.15,.20],[.40,.15,.20,.15,.08,.02])[0]
    # reference list price multiplied by modest annual pricing inflation
    soldprice=round(price*(1+ .034*(year-2024)),2)
    unit_net=round(soldprice*(1-discpct),2)
    unit_cost=round(cost*(1+.027*(year-2024)),2)
    gross=round(qty*soldprice,2);net=round(qty*unit_net,2);costline=round(qty*unit_cost,2)
    lineid+=1
    lines.append((f'I{lineid:09d}',oid,lid,p,dt.isoformat(),qty,money(soldprice),money(discpct),money(gross-net),money(net),money(costline)))
    demand[p]+=qty;total_gross+=gross;total_disc+=gross-net;total_net+=net;total_cost+=costline
   orders.append((oid,dt.isoformat(),lid,cid,channel,payment,num,money(total_gross),money(total_disc),money(total_net),money(total_cost)))
   revenue+=total_net;cmv+=total_cost;discounts+=total_disc
  for idx in sorted(assort[lid]):
   pid=catalog[idx][0];opening=stock[(lid,pid)];sold=demand[pid]
   # replenishment only as needed and reasonable buffers, some overstocks for business insights
   reorder=max(5,int(sold*.85));target=reorder+R.randint(5,28)
   purchase=max(0,sold+target-opening) if (opening-sold<reorder) else 0
   # 2% expiry/damage events, recorded as adjustment
   loss=R.randint(1,3) if R.random()<.016 and opening+purchase-sold>5 else 0
   closing=opening+purchase-sold-loss
   assert closing>=0
   stock[(lid,pid)]=closing
   if sold or purchase or loss:
    stock_rows.append((ym,lid,pid,opening,purchase,sold,loss,closing,money(catalog[idx][4]*(1+.027*(year-2024)))))
  rent=round({'L001':22500,'L002':16500,'L003':20000,'L004':14200}[lid]*(1+.045*(year-2024)),2)
  payroll=round(n_orders*11.40+R.uniform(7000,13500),2)
  op=round(n_orders*4.2+R.uniform(2500,5000),2)
  digital=round(revenue*(.014+R.uniform(0,.009)),2)
  cost_rows.append((ym,lid,money(rent),money(payroll),money(op),money(digital),money(rent+payroll+op+digital)))
  goals.append((ym,lid,money(revenue*R.uniform(.97,1.14)),money((revenue-cmv)*R.uniform(.93,1.10))))
  sum_month[(ym,lid)]=[round(revenue,2),round(cmv,2),n_orders]
save('f_vendas.csv',['id_venda','data_venda','id_loja','id_cliente','canal','forma_pagamento','qtd_itens_distintos','valor_bruto','valor_desconto','valor_liquido','custo_mercadoria'],orders)
save('f_itens_venda.csv',['id_item','id_venda','id_loja','id_produto','data_venda','quantidade','preco_unitario_bruto','taxa_desconto','valor_desconto','valor_liquido','custo_total'],lines)
save('f_estoque_mensal.csv',['ano_mes','id_loja','id_produto','estoque_inicial','qtd_entradas','qtd_vendida','qtd_perdas','estoque_final','custo_unitario_referencia'],stock_rows)
save('f_despesas_mensais.csv',['ano_mes','id_loja','aluguel','pessoal','operacionais','marketing_canais','despesa_total'],cost_rows)
save('f_metas_mensais.csv',['ano_mes','id_loja','meta_receita','meta_lucro_bruto'],goals)
# suppliers and each product assigned a default supplier; purchases aggregated in stock
suppliers=[(f'F{i:03d}',f'Distribuidora Saúde {i:02d}',R.choice(['SP','MG','PR']),R.choice([15,21,28,30,45])) for i in range(1,61)]
save('dim_fornecedores.csv',['id_fornecedor','razao_social_ficticia','uf','prazo_medio_dias'],suppliers)
save('ponte_produto_fornecedor.csv',['id_produto','id_fornecedor'],[(p[0],suppliers[(i*11)%60][0]) for i,p in enumerate(catalog)])
cal=[];d=start
while d<=end:
 cal.append((d.isoformat(),d.year,d.month,d.strftime('%Y-%m'),(d.weekday()+1)%7,d.isoweekday(),(d.weekday()<5)*1));d+=datetime.timedelta(days=1)
save('dim_calendario.csv',['data','ano','mes','ano_mes','dia_semana_domingo_zero','dia_semana_iso','dia_util'],cal)
readme=f'''# FarmaVitta — Base sintética BI 24 meses\n\n**Dados totalmente fictícios; não representam operações, pessoas ou empresas reais.**\n\n## Recorte\n- Período: 2024-10-01 a 2026-09-30 (24 meses fechados).\n- Lojas: Campinas, Jundiaí, Sorocaba e Piracicaba (SP).\n- Produtos: exatamente 5.000 SKUs: medicamentos 2.100, suplementos 850, higiene e beleza 900, baby 550 e perfumaria 600.\n- Clientes sintéticos: {len(customers):,}.\n- Vendas: {len(orders):,}; itens de venda: {len(lines):,}.\n- Estoque: snapshot mensal por loja/produto com movimentação de entrada, saída, perdas e saldo inicial/final.\n\n## Regras de negócio / granularidade\n- `f_vendas`: 1 linha por venda/cupom. `valor_liquido = valor_bruto - valor_desconto`; `custo_mercadoria` é soma do custo dos itens.\n- `f_itens_venda`: 1 linha por SKU do cupom. **Não somar `f_vendas` e `f_itens_venda` no mesmo indicador**.\n- `f_estoque_mensal`: 1 linha por loja/SKU/mês para itens com movimento; `estoque_final = estoque_inicial + qtd_entradas - qtd_vendida - qtd_perdas`. Para snapshots de SKUs sem movimento, carregar o saldo do mês anterior ou usar `f_estoque_inicial`; não presumir ausência como saldo zero.\n- `f_despesas_mensais`: 1 linha por loja/mês. Margem bruta = receita líquida - CMV. Resultado operacional simplificado = margem bruta - despesas; **não é EBITDA contábil auditado**.\n- `f_metas_mensais`: 1 linha por loja/mês, metas construídas sinteticamente.\n- `dim_produtos`: preços e custos de referência são fictícios e não representam CMED, PMC ou preços regulados efetivos.\n- Campos `eh_controlado` e `exige_receita` são simulações de classificação e não constituem informação farmacológica.\n- Clientes possuem IDs artificiais; não há nomes, CPF, informação clínica nem dados pessoais reais.\n- `f_vendas.id_cliente` vazio = compra anônima. Evitar usar número de cupons como número de clientes.\n- CSV: UTF-8 com BOM, separador ponto e vírgula, números com ponto decimal e datas ISO 8601.\n- Moeda: BRL.\n\n## Modelo recomendado\n- `dim_calendario[data]` → `f_vendas[data_venda]` / `f_itens_venda[data_venda]`; usar `ano_mes` (padrão YYYY-MM) para snapshots e metas.\n- `dim_lojas[id_loja]` → todas as fatos aplicáveis.\n- `dim_produtos[id_produto]` → `f_itens_venda` / `f_estoque_mensal`.\n- `dim_clientes[id_cliente]` → `f_vendas[id_cliente]` (excluir ID em branco do lado da dimensão).\n- `f_vendas[id_venda]` → `f_itens_venda[id_venda]` (1:N, direção única); cuidado com caminhos ambíguos via data e loja.\n- `ponte_produto_fornecedor` liga produtos e fornecedores; preferir trazer fornecedor padrão à dimensão produto no Power Query se a relação for 1 fornecedor/SKU.\n\n## Indicadores\nReceita líquida, CMV, lucro bruto, margem bruta %, descontos %, ticket médio, itens por cupom, vendas por canal, crescimento YoY, clientes identificados, frequência, produtos/categorias, estoque final, cobertura estimada, ruptura potencial, perdas, despesas e resultado operacional simplificado.\n\n## Limitações de simulação\n- Estoque mensal agregado, não representa eventos individuais de recebimento, lote e vencimento.\n- Não há devoluções, impostos, tarifas específicas por transação ou detalhamento de receitas médicas.\n- Produtos são descrições comerciais sintéticas, não medicamentos registrados.\n- `quantidade_inicial` em 2024-09-30 garante reconciliação de movimentação.\n'''
(D/'LEIA-ME.md').write_text(readme,encoding='utf-8')
summary={'periodo':['2024-10-01','2026-09-30'],'lojas':4,'produtos':len(prods),'clientes':len(customers),'vendas':len(orders),'itens_venda':len(lines),'estoque_mensal_linhas':len(stock_rows),'receita_total':round(sum(float(x[9]) for x in orders),2),'cmv_total':round(sum(float(x[10]) for x in orders),2),'categorias':{c[0]:c[1] for c in categories},'arquivos':{p.name:p.stat().st_size for p in D.glob('*.csv')}}
(D/'RESUMO_BASE.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
# validations
assert len({p[0] for p in prods})==5000 and len(orders)==len({o[0] for o in orders})
assert all(o[7]==money(float(o[8])+float(o[9])) for o in orders)
assert all(s[7]==s[3]+s[4]-s[5]-s[6] for s in stock_rows)
assert sum(x[5] for x in stock_rows)==sum(int(x[5]) for x in lines)
with zipfile.ZipFile('/mnt/data/FarmaVitta_Base_Dados_24_Meses.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in sorted(D.iterdir()):
  if f.is_file():z.write(f,arcname='FarmaVitta/'+f.name)
print(json.dumps(summary,ensure_ascii=False,indent=2))
