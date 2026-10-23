# -*- coding: utf-8 -*-
"""Monta o projeto PBIP FarmaVitta e valida todos os JSON contra os esquemas oficiais (microsoft/json-schemas).
Uso: python3 build.py <pasta_saida> <logo.png> [pasta_json_schemas]
"""
import os, sys, json, glob, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelo, modelo_v2, relatorio, relatorio_v2

out, logo = sys.argv[1], sys.argv[2]
schemas = sys.argv[3] if len(sys.argv) > 3 else None
NAME = "FarmaVitta_v2"
if os.path.exists(out): shutil.rmtree(out)
os.makedirs(out)
sm = os.path.join(out, f"{NAME}.SemanticModel"); rp = os.path.join(out, f"{NAME}.Report")
modelo.write_semantic_model_root(sm)
n_med = modelo.write_model(sm)
pages, n_vis, n_bm = relatorio_v2.write_report_v2(rp, f"{NAME}.SemanticModel", logo)
json.dump({"$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
           "version": "1.0", "artifacts": [{"report": {"path": f"{NAME}.Report"}}], "settings": {"enableAutoRecovery": True}},
          open(os.path.join(out, f"{NAME}.pbip"), "w", encoding="utf-8"), indent=2)
open(os.path.join(out, ".gitignore"), "w").write("**/.pbi/localSettings.json\n**/.pbi/cache.abf\n")
print(f"Tabelas: {len(modelo.T)} · Relações: {len(modelo.REL)} · Medidas: {n_med} · Páginas: {len(pages)} · Visuais: {n_vis} · Bookmarks: {n_bm}")

# ---------------- validação de esquema
if schemas:
    from jsonschema import Draft7Validator
    from referencing import Registry, Resource
    base_url = "https://developer.microsoft.com/json-schemas/"
    res = []
    for f in glob.glob(os.path.join(schemas, "**", "*.json"), recursive=True):
        try: s = json.load(open(f, encoding="utf-8"))
        except Exception: continue
        url = base_url + os.path.relpath(f, schemas).replace(os.sep, "/")
        r = Resource.from_contents(s, default_specification=__import__("referencing.jsonschema", fromlist=["DRAFT7"]).DRAFT7)
        res.append((url, r))
        if isinstance(s, dict) and s.get("$id"): res.append((s["$id"], r))
    reg = Registry().with_resources(res)
    erros, n = 0, 0
    for f in glob.glob(os.path.join(rp, "**", "*.json"), recursive=True) + glob.glob(os.path.join(sm, "*.pbism")) + glob.glob(os.path.join(sm, ".pbi", "*.json")):
        doc = json.load(open(f, encoding="utf-8"))
        sch = doc.get("$schema")
        if not sch: continue
        n += 1
        schema = reg.contents(sch) if sch in [u for u, _ in res] else None
        if schema is None:
            print("SEM ESQUEMA LOCAL:", sch); continue
        v = Draft7Validator(schema, registry=reg)
        es = list(v.iter_errors(doc))
        for e in es[:3]:
            print("ERRO", os.path.relpath(f, out), "→", "/".join(map(str, e.absolute_path)), ":", e.message[:220])
        erros += len(es)
    print(f"Validação de esquema: {n} arquivos JSON, {erros} erros")
