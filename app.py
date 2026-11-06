from flask import (
    Flask, render_template, request, redirect, url_for,
    abort, flash, jsonify
)

app = Flask(__name__)
app.secret_key = "municipios-nordeste"

# ---------------------------------------------------------------- dataset
municipios = {
    "São Luís": {"id_ibge": 2111300, "estado": "Maranhão", "sigla_uf": "MA", "capital": True, "populacao_estimada": 1115932},
    "Imperatriz": {"id_ibge": 2105302, "estado": "Maranhão", "sigla_uf": "MA", "capital": False, "populacao_estimada": 259337},
    "São José de Ribamar": {"id_ibge": 2111201, "estado": "Maranhão", "sigla_uf": "MA", "capital": False, "populacao_estimada": 179028},
    "Teresina": {"id_ibge": 2211001, "estado": "Piauí", "sigla_uf": "PI", "capital": True, "populacao_estimada": 871033},
    "Parnaíba": {"id_ibge": 2207702, "estado": "Piauí", "sigla_uf": "PI", "capital": False, "populacao_estimada": 153482},
    "Picos": {"id_ibge": 2208007, "estado": "Piauí", "sigla_uf": "PI", "capital": False, "populacao_estimada": 78627},
    "Fortaleza": {"id_ibge": 2304400, "estado": "Ceará", "sigla_uf": "CE", "capital": True, "populacao_estimada": 2582360},
    "Caucaia": {"id_ibge": 2303709, "estado": "Ceará", "sigla_uf": "CE", "capital": False, "populacao_estimada": 365212},
    "Juazeiro do Norte": {"id_ibge": 2307304, "estado": "Ceará", "sigla_uf": "CE", "capital": False, "populacao_estimada": 276264},
    "Sobral": {"id_ibge": 2312908, "estado": "Ceará", "sigla_uf": "CE", "capital": False, "populacao_estimada": 212437},
    "Natal": {"id_ibge": 2408102, "estado": "Rio Grande do Norte", "sigla_uf": "RN", "capital": True, "populacao_estimada": 890243},
    "Mossoró": {"id_ibge": 2408003, "estado": "Rio Grande do Norte", "sigla_uf": "RN", "capital": False, "populacao_estimada": 300618},
    "Parnamirim": {"id_ibge": 2403251, "estado": "Rio Grande do Norte", "sigla_uf": "RN", "capital": False, "populacao_estimada": 272490},
    "João Pessoa": {"id_ibge": 2507507, "estado": "Paraíba", "sigla_uf": "PB", "capital": True, "populacao_estimada": 825796},
    "Campina Grande": {"id_ibge": 2504009, "estado": "Paraíba", "sigla_uf": "PB", "capital": False, "populacao_estimada": 411807},
    "Santa Rita": {"id_ibge": 2513703, "estado": "Paraíba", "sigla_uf": "PB", "capital": False, "populacao_estimada": 137349},
    "Recife": {"id_ibge": 2611606, "estado": "Pernambuco", "sigla_uf": "PE", "capital": True, "populacao_estimada": 1661017},
    "Jaboatão dos Guararapes": {"id_ibge": 2607901, "estado": "Pernambuco", "sigla_uf": "PE", "capital": False, "populacao_estimada": 706867},
    "Olinda": {"id_ibge": 2609600, "estado": "Pernambuco", "sigla_uf": "PE", "capital": False, "populacao_estimada": 393115},
    "Caruaru": {"id_ibge": 2604106, "estado": "Pernambuco", "sigla_uf": "PE", "capital": False, "populacao_estimada": 365278},
    "Petrolina": {"id_ibge": 2611101, "estado": "Pernambuco", "sigla_uf": "PE", "capital": False, "populacao_estimada": 354317},
    "Maceió": {"id_ibge": 2704302, "estado": "Alagoas", "sigla_uf": "AL", "capital": True, "populacao_estimada": 1031597},
    "Arapiraca": {"id_ibge": 2700300, "estado": "Alagoas", "sigla_uf": "AL", "capital": False, "populacao_estimada": 234147},
    "Aracaju": {"id_ibge": 2800308, "estado": "Sergipe", "sigla_uf": "SE", "capital": True, "populacao_estimada": 664908},
    "Nossa Senhora do Socorro": {"id_ibge": 2805109, "estado": "Sergipe", "sigla_uf": "SE", "capital": False, "populacao_estimada": 185829},
    "Salvador": {"id_ibge": 2927408, "estado": "Bahia", "sigla_uf": "BA", "capital": True, "populacao_estimada": 2559945},
    "Feira de Santana": {"id_ibge": 2910800, "estado": "Bahia", "sigla_uf": "BA", "capital": False, "populacao_estimada": 619609},
    "Vitória da Conquista": {"id_ibge": 2930766, "estado": "Bahia", "sigla_uf": "BA", "capital": False, "populacao_estimada": 341128},
    "Camaçari": {"id_ibge": 2905701, "estado": "Bahia", "sigla_uf": "BA", "capital": False, "populacao_estimada": 304302},
    "Juazeiro": {"id_ibge": 2918407, "estado": "Bahia", "sigla_uf": "BA", "capital": False, "populacao_estimada": 218324},
}

UFS = [
    ("MA", "Maranhão"), ("PI", "Piauí"), ("CE", "Ceará"),
    ("RN", "Rio Grande do Norte"), ("PB", "Paraíba"), ("PE", "Pernambuco"),
    ("AL", "Alagoas"), ("SE", "Sergipe"), ("BA", "Bahia"),
]
ESTADOS = dict(UFS)

# ---------------------------------------------------------------- helpers
@app.template_filter("milhar")
def milhar(valor):
    """Formata 2559945 -> '2.559.945'."""
    return f"{int(valor):,}".replace(",", ".")


def resumo():
    por_uf, populacao, capitais = {}, 0, 0
    for dados in municipios.values():
        por_uf[dados["sigla_uf"]] = por_uf.get(dados["sigla_uf"], 0) + 1
        populacao += dados["populacao_estimada"]
        if dados["capital"]:
            capitais += 1
    return {
        "total_municipios": len(municipios),
        "capitais": capitais,
        "populacao_total": populacao,
        "estados": len(por_uf),
        "por_uf": por_uf,
    }


def listar(uf=None, busca=None):
    itens = []
    for nome in sorted(municipios):
        dados = municipios[nome]
        if uf and dados["sigla_uf"] != uf:
            continue
        if busca and busca.lower() not in nome.lower():
            continue
        itens.append({"nome": nome, **dados})
    return itens


def validar(entrada):
    """Valida e normaliza os campos. Levanta ValueError com mensagem amigável."""
    nome = str(entrada.get("nome") or "").strip()
    if not nome:
        raise ValueError("Informe o nome do município.")

    try:
        id_ibge = int(entrada.get("id_ibge"))
    except (TypeError, ValueError):
        raise ValueError("Informe um código IBGE numérico.")

    sigla = str(entrada.get("sigla_uf") or "").upper().strip()
    if sigla not in ESTADOS:
        raise ValueError("Selecione uma UF do Nordeste válida.")

    try:
        populacao = int(entrada.get("populacao_estimada"))
    except (TypeError, ValueError):
        raise ValueError("Informe a população estimada.")

    return nome, {
        "id_ibge": id_ibge,
        "estado": ESTADOS[sigla],
        "sigla_uf": sigla,
        "capital": entrada.get("capital") in (True, "on", "true", "1", 1),
        "populacao_estimada": populacao,
    }


# ---------------------------------------------------------------- páginas
@app.get("/")
def index():
    uf = (request.args.get("uf") or "").upper()
    busca = request.args.get("q") or ""
    return render_template(
        "index.html",
        municipios=listar(uf, busca),
        resumo=resumo(),
        ufs=UFS,
        uf=uf,
        busca=busca,
    )


@app.post("/municipios")
def criar():
    try:
        nome, dados = validar(request.form)
    except ValueError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("index"))

    if nome in municipios:
        flash(f"O município '{nome}' já está cadastrado.", "erro")
        return redirect(url_for("index"))

    municipios[nome] = dados
    flash(f"'{nome}' cadastrado com sucesso.", "ok")
    return redirect(url_for("index"))


@app.get("/municipios/<nome>")
def detalhe(nome):
    dados = municipios.get(nome)
    if not dados:
        abort(404)
    return render_template("municipio.html", nome=nome, dados=dados)


@app.route("/municipios/<nome>/editar", methods=["GET", "POST"])
def editar(nome):
    if nome not in municipios:
        abort(404)

    if request.method == "GET":
        return render_template(
            "municipio_editar.html", nome=nome,
            registro={"nome": nome, **municipios[nome]}, ufs=UFS,
        )

    try:
        novo_nome, dados = validar(request.form)
    except ValueError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("editar", nome=nome))

    if novo_nome != nome and novo_nome in municipios:
        flash(f"O município '{novo_nome}' já está cadastrado.", "erro")
        return redirect(url_for("editar", nome=nome))

    del municipios[nome]
    municipios[novo_nome] = dados
    flash(f"'{novo_nome}' atualizado.", "ok")
    return redirect(url_for("index"))


@app.post("/municipios/<nome>/excluir")
def excluir(nome):
    if nome not in municipios:
        abort(404)
    del municipios[nome]
    flash(f"'{nome}' removido.", "ok")
    return redirect(url_for("index"))


# ---------------------------------------------------------------- API JSON
@app.get("/api/municipios")
def api_listar():
    uf = (request.args.get("uf") or "").upper() or None
    lista = listar(uf)
    return jsonify({"resumo": resumo(), "filtro": {"uf": uf}, "total": len(lista), "municipios": lista})


@app.post("/api/municipios")
def api_criar():
    try:
        nome, dados = validar(request.get_json(silent=True) or {})
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    if nome in municipios:
        return jsonify({"erro": f"O município '{nome}' já está cadastrado"}), 409

    municipios[nome] = dados
    return jsonify({"mensagem": "Município cadastrado", "municipio": {"nome": nome, **dados}}), 201


@app.route("/api/municipios/<nome>", methods=["GET", "PATCH", "DELETE"])
def api_item(nome):
    if nome not in municipios:
        return jsonify({"erro": "Município não encontrado", "nome": nome}), 404

    if request.method == "GET":
        return jsonify({"municipio": {"nome": nome, **municipios[nome]}})

    if request.method == "DELETE":
        del municipios[nome]
        return jsonify({"mensagem": f"Município '{nome}' removido"})

    # PATCH: mescla o que veio com o registro atual
    entrada = {**municipios[nome], "nome": nome, **(request.get_json(silent=True) or {})}
    try:
        novo_nome, dados = validar(entrada)
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    if novo_nome != nome and novo_nome in municipios:
        return jsonify({"erro": f"O município '{novo_nome}' já está cadastrado"}), 409

    del municipios[nome]
    municipios[novo_nome] = dados
    return jsonify({"mensagem": "Município atualizado", "municipio": {"nome": novo_nome, **dados}})


if __name__ == "__main__":
    app.run(debug=True)