from app.tools.agendamentos import MAX_RESULTADOS, TOOL, ConsultarAgendamentosInput
from app.tools.registry import execute

NOME = "consultar_agendamentos"


def test_lista_sem_filtros(conn, add):
    add()
    add(participante="Beatriz")
    r = execute(conn, NOME, {})
    assert r["ok"] is True
    assert r["dados"]["total"] == 2


def test_filtra_por_participante(conn, add):
    add(participante="Carlos Souza")
    add(participante="Beatriz Lima")
    r = execute(conn, NOME, {"participante": "carlos"})
    nomes = [a["participante"] for a in r["dados"]["agendamentos"]]
    assert nomes == ["Carlos Souza"]


def test_filtra_por_intervalo_de_datas(conn, add):
    add(inicio="2026-11-02T10:00", fim="2026-11-02T11:00")
    add(inicio="2026-11-03T23:30", fim="2026-11-04T00:30")
    add(inicio="2026-11-04T09:00", fim="2026-11-04T10:00")
    r = execute(conn, NOME, {"data_inicio": "2026-11-03", "data_fim": "2026-11-03"})
    assert [a["inicio"] for a in r["dados"]["agendamentos"]] == ["2026-11-03T23:30"]


def test_nao_retorna_cancelados(conn, add):
    add(status="cancelado")
    r = execute(conn, NOME, {})
    assert r["dados"]["total"] == 0


def test_data_invalida_e_rejeitada(conn):
    r = execute(conn, NOME, {"data_inicio": "amanhã"})
    assert r["ok"] is False
    assert r["erro"] == "parametros_invalidos"


def test_intervalo_invertido_e_rejeitado(conn):
    r = execute(conn, NOME, {"data_inicio": "2026-11-05", "data_fim": "2026-11-01"})
    assert r["ok"] is False
    assert r["erro"] == "parametros_invalidos"


def test_parametro_desconhecido_e_rejeitado(conn):
    r = execute(conn, NOME, {"sql": "DROP TABLE agendamentos"})
    assert r["ok"] is False
    assert r["erro"] == "parametros_invalidos"
    conn.execute("SELECT COUNT(*) FROM agendamentos")  # a tabela continua existindo


def test_injecao_de_sql_e_tratada_como_texto(conn, add):
    add()
    r = execute(conn, NOME, {"participante": "'; DROP TABLE agendamentos; --"})
    assert r["ok"] is True
    assert r["dados"]["total"] == 0
    assert conn.execute("SELECT COUNT(*) FROM agendamentos").fetchone()[0] == 1


def test_ferramenta_desconhecida(conn):
    r = execute(conn, "apagar_tudo", {})
    assert r == {"ok": False, "erro": "ferramenta_desconhecida"}


def test_resultado_truncado(conn, add):
    for i in range(MAX_RESULTADOS + 5):
        add(inicio=f"2026-11-03T10:{i:02d}", fim=f"2026-11-03T11:{i:02d}")
    r = execute(conn, NOME, {})
    assert r["dados"]["total"] == MAX_RESULTADOS
    assert r["dados"]["truncado"] is True


def test_esquema_do_modelo_bate_com_a_validacao():
    # Evita que o que o modelo "enxerga" divirja do que o servidor aceita.
    assert set(TOOL.parameters["properties"]) == set(ConsultarAgendamentosInput.model_fields)