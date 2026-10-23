# -*- coding: utf-8 -*-
"""Especificações Vega-Lite (Deneb) da FarmaVitta v2. Campos chegam pelo 'dataset' com os displayName curtos definidos no visual."""
import json

CONFIG = {
    "autosize": {"type": "fit", "contains": "padding"},
    "view": {"stroke": "transparent"},
    "background": "transparent",
    "font": "Segoe UI",
    "padding": 4,
    "axis": {"labelColor": "#9FC9C1", "titleColor": "#9FC9C1", "gridColor": "rgba(255,255,255,0.07)", "domainColor": "rgba(255,255,255,0.15)",
             "tickColor": "rgba(255,255,255,0.15)", "labelFontSize": 10, "titleFontSize": 10, "titleFontWeight": "normal"},
    "legend": {"labelColor": "#E8F3F1", "titleColor": "#9FC9C1", "orient": "top", "labelFontSize": 10, "symbolSize": 80},
    "text": {"color": "#E8F3F1", "fontSize": 10},
    "locale": {"number": {"decimal": ",", "thousands": ".", "grouping": [3], "currency": ["R$ ", ""]}},
}
VL = "https://vega.github.io/schema/vega-lite/v5.json"
MI = "format(datum.value / 1000000, ',.1f') + ' mi'"

SPECS = {}

SPECS["exec_receita"] = {
    "$schema": VL, "data": {"name": "dataset"}, "width": "container", "height": "container",
    "encoding": {"x": {"field": "mes", "type": "ordinal", "sort": {"field": "ord", "op": "min", "order": "ascending"}, "axis": {"title": None, "labelAngle": -45, "labelOverlap": False}}},
    "layer": [
        {"mark": {"type": "bar", "cornerRadiusTopLeft": 4, "cornerRadiusTopRight": 4, "width": {"band": 0.68}},
         "encoding": {"y": {"field": "receita", "type": "quantitative", "axis": {"title": None, "labelExpr": MI, "tickCount": 5}},
                      "color": {"field": "cor", "type": "nominal", "scale": None},
                      "tooltip": [{"field": "mes", "title": "Mês"}, {"field": "receita", "title": "Receita líquida", "format": ",.0f"},
                                  {"field": "ly", "title": "Ano anterior", "format": ",.0f"}, {"field": "meta", "title": "Meta", "format": ",.0f"}]}},
        {"mark": {"type": "line", "strokeDash": [5, 4], "color": "#EF9277", "strokeWidth": 2}, "encoding": {"y": {"field": "meta", "type": "quantitative"}}},
        {"mark": {"type": "line", "color": "#DDF5EB", "strokeWidth": 2, "opacity": 0.8, "point": {"filled": True, "size": 26, "color": "#DDF5EB"}},
         "encoding": {"y": {"field": "ly", "type": "quantitative"}}},
    ]}

SPECS["com_heatmap"] = {
    "$schema": VL, "data": {"name": "dataset"}, "width": "container", "height": "container",
    "mark": {"type": "rect", "cornerRadius": 3, "stroke": "#071E23", "strokeWidth": 2},
    "encoding": {
        "x": {"field": "mes", "type": "ordinal", "sort": {"field": "ord", "op": "min", "order": "ascending"}, "axis": {"title": None, "labelAngle": 0, "labelOverlap": True}},
        "y": {"field": "dia", "type": "ordinal", "sort": {"field": "dord", "op": "min", "order": "ascending"}, "axis": {"title": None}},
        "color": {"field": "cupons", "type": "quantitative", "scale": {"range": ["#0E3138", "#125F61", "#18B89F", "#DDF5EB"]},
                  "legend": {"title": "Cupons", "orient": "right", "gradientLength": 160}},
        "tooltip": [{"field": "mes", "title": "Mês"}, {"field": "dia", "title": "Dia"}, {"field": "cupons", "title": "Cupons", "format": ",.0f"}]}}

SPECS["prod_pareto"] = {
    "$schema": VL, "data": {"name": "dataset"}, "width": "container", "height": "container",
    "transform": [
        {"window": [{"op": "sum", "field": "rec", "as": "acc"}, {"op": "row_number", "as": "rk"}], "sort": [{"field": "rec", "order": "descending"}], "frame": [None, 0]},
        {"joinaggregate": [{"op": "sum", "field": "rec", "as": "tot"}]},
        {"calculate": "datum.acc / datum.tot", "as": "pct"},
        {"calculate": "(datum.rk < 10 ? '0' : '') + datum.rk + '. ' + datum.sub", "as": "lbl"},
        {"calculate": "datum.pct - datum.rec / datum.tot < 0.8 ? 'A (até 80%)' : 'B/C'", "as": "classe"}],
    "layer": [
        {"mark": {"type": "bar", "cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3},
         "encoding": {"x": {"field": "lbl", "type": "ordinal", "sort": "ascending", "axis": {"title": None, "labelAngle": -40, "labelLimit": 100}},
                      "y": {"field": "rec", "type": "quantitative", "axis": {"title": None, "labelExpr": MI}},
                      "color": {"field": "classe", "type": "nominal", "scale": {"domain": ["A (até 80%)", "B/C"], "range": ["#18B89F", "#3D6E72"]}, "legend": {"title": None}},
                      "tooltip": [{"field": "sub", "title": "Subcategoria"}, {"field": "rec", "title": "Receita", "format": ",.0f"}, {"field": "pct", "title": "% acumulado", "format": ".1%"}]}},
        {"layer": [
            {"mark": {"type": "line", "color": "#EF9277", "strokeWidth": 2, "point": {"color": "#EF9277", "size": 22}},
             "encoding": {"x": {"field": "lbl", "type": "ordinal", "sort": "ascending"},
                          "y": {"field": "pct", "type": "quantitative", "scale": {"domain": [0, 1]}, "axis": {"title": None, "format": ".0%", "orient": "right", "grid": False}}}},
            {"mark": {"type": "rule", "color": "#F2C46D", "strokeDash": [3, 3]}, "encoding": {"y": {"datum": 0.8}}}]}],
    "resolve": {"scale": {"y": "independent"}}}

SPECS["compras_heat"] = {
    "$schema": VL, "data": {"name": "dataset"}, "width": "container", "height": "container",
    "encoding": {"x": {"field": "cat", "type": "nominal", "axis": {"title": None, "labelAngle": 0, "orient": "top"}},
                 "y": {"field": "loja", "type": "nominal", "axis": {"title": None}}},
    "layer": [
        {"mark": {"type": "rect", "cornerRadius": 4, "stroke": "#071E23", "strokeWidth": 3},
         "encoding": {"color": {"field": "pont", "type": "quantitative", "scale": {"range": ["#EF9277", "#F2C46D", "#18B89F"]}, "legend": None},
                      "tooltip": [{"field": "loja", "title": "Loja"}, {"field": "cat", "title": "Categoria"}, {"field": "pont", "title": "Pontualidade", "format": ".1%"},
                                  {"field": "rec", "title": "Recebimentos", "format": ",.0f"}]}},
        {"mark": {"type": "text", "fontSize": 12, "fontWeight": 600, "color": "#071E23"}, "encoding": {"text": {"field": "pont", "type": "quantitative", "format": ".0%"}}}]}

SPECS["estoque_dot"] = {
    "$schema": VL, "data": {"name": "dataset"}, "width": "container", "height": "container",
    "layer": [
        {"mark": {"type": "rule", "color": "rgba(255,255,255,0.12)", "strokeWidth": 6},
         "encoding": {"y": {"field": "cat", "type": "nominal", "axis": {"title": None}}, "x": {"aggregate": "min", "field": "cob"}, "x2": {"aggregate": "max", "field": "cob"}}},
        {"mark": {"type": "circle", "size": 120, "opacity": 0.95},
         "encoding": {"y": {"field": "cat", "type": "nominal"}, "x": {"field": "cob", "type": "quantitative", "axis": {"title": "dias de cobertura"}, "scale": {"zero": True}},
                      "color": {"field": "loja", "type": "nominal", "scale": {"range": ["#18B89F", "#DDF5EB", "#F2C46D", "#EF9277"]}, "legend": {"title": None}},
                      "tooltip": [{"field": "cat", "title": "Categoria"}, {"field": "loja", "title": "Loja"}, {"field": "cob", "title": "Cobertura (dias)", "format": ",.0f"}]}},
        {"mark": {"type": "rule", "color": "#EF9277", "strokeDash": [4, 3]}, "encoding": {"x": {"datum": 120}}},
        {"mark": {"type": "text", "color": "#EF9277", "align": "left", "dx": 4, "baseline": "top", "fontSize": 10}, "encoding": {"x": {"datum": 120}, "y": {"value": 2}, "text": {"value": "excesso > 120 dias"}}}]}

SPECS["fin_waterfall"] = {
    "$schema": VL, "data": {"name": "dataset"}, "width": "container", "height": "container",
    "transform": [
        {"filter": "datum.val != null"},
        {"calculate": "datum.ord == 10 ? 0 : datum.val", "as": "amt"},
        {"window": [{"op": "sum", "field": "amt", "as": "acc"}], "sort": [{"field": "ord"}], "frame": [None, 0]},
        {"calculate": "datum.ord == 10 ? 0 : datum.acc - datum.val", "as": "ini"},
        {"calculate": "datum.ord == 10 ? datum.val : datum.acc", "as": "fim"},
        {"calculate": "datum.ord == 3 ? 'Receita' : datum.ord == 10 ? 'Resultado' : 'Dedução'", "as": "tipo"},
        {"calculate": "format(abs(datum.val) / 1000000, ',.2f') + ' mi'", "as": "rot"}],
    "encoding": {"x": {"field": "linha", "type": "nominal", "sort": {"field": "ord", "op": "min", "order": "ascending"}, "axis": {"title": None, "labelAngle": 0, "labelLimit": 120}}},
    "layer": [
        {"mark": {"type": "bar", "cornerRadius": 4, "width": {"band": 0.62}},
         "encoding": {"y": {"field": "ini", "type": "quantitative", "axis": {"title": None, "labelExpr": MI}}, "y2": {"field": "fim"},
                      "color": {"field": "tipo", "type": "nominal", "scale": {"domain": ["Receita", "Dedução", "Resultado"], "range": ["#18B89F", "#EF9277", "#DDF5EB"]}, "legend": None},
                      "tooltip": [{"field": "linha", "title": "Linha"}, {"field": "val", "title": "Valor", "format": ",.0f"}]}},
        {"mark": {"type": "text", "dy": -8, "fontSize": 11, "fontWeight": 600, "color": "#E8F3F1"},
         "encoding": {"y": {"field": "fim", "type": "quantitative"}, "text": {"field": "rot"}}}]}

SPECS["fc_banda"] = {
    "$schema": VL, "data": {"name": "dataset"}, "width": "container", "height": "container",
    "encoding": {"x": {"field": "mes", "type": "ordinal", "sort": {"field": "ord", "op": "min", "order": "ascending"}, "axis": {"title": None, "labelAngle": 0, "labelOverlap": True}}},
    "layer": [
        {"mark": {"type": "area", "color": "#18B89F", "opacity": 0.18}, "encoding": {"y": {"field": "lo", "type": "quantitative"}, "y2": {"field": "hi"}}},
        {"mark": {"type": "line", "color": "#DDF5EB", "strokeWidth": 2.5, "point": {"filled": True, "size": 24, "color": "#DDF5EB"}},
         "encoding": {"y": {"field": "real", "type": "quantitative", "axis": {"title": None, "labelExpr": MI}, "scale": {"zero": False}}}},
        {"mark": {"type": "line", "color": "#18B89F", "strokeWidth": 3, "strokeDash": [6, 4], "point": {"filled": True, "size": 34, "color": "#18B89F"}},
         "encoding": {"y": {"field": "prev", "type": "quantitative"},
                      "tooltip": [{"field": "mes", "title": "Mês"}, {"field": "prev", "title": "Previsto", "format": ",.0f"},
                                  {"field": "lo", "title": "Limite inferior", "format": ",.0f"}, {"field": "hi", "title": "Limite superior", "format": ",.0f"}]}},
        {"mark": {"type": "point", "opacity": 0}, "encoding": {"y": {"field": "real", "type": "quantitative"},
                                                              "tooltip": [{"field": "mes", "title": "Mês"}, {"field": "real", "title": "Realizado", "format": ",.0f"}]}}]}

def spec_json(k): return json.dumps(SPECS[k], ensure_ascii=False, separators=(",", ":"))
def config_json(): return json.dumps(CONFIG, ensure_ascii=False, separators=(",", ":"))
