# Agente Plataforma

> Plataforma conversacional modular e orientada a ferramentas.
> A IA interpreta e propõe; o backend valida, autoriza, executa e audita.

**Status:** protótipo de aprendizado em desenvolvimento. **Não está pronto para produção.**

## A ideia

Em muitos chatbots, a IA "faz as coisas" diretamente. Aqui, ela apenas **propõe chamadas
estruturadas de ferramentas**, e quem decide é o código:

- O modelo de IA nunca é uma autoridade de segurança.
- Cada ferramenta tem definição clara, parâmetros validados e um executor aprovado no código.
- O que é dito ao usuário se baseia no **resultado real** da execução, não na palavra do modelo.
- Inteligência conversacional, regras de negócio, permissões e dados ficam em camadas separadas.

## Como funciona

```
Usuário → Chat (terminal) → Orquestrador ⇄ Modelo de IA (via adaptador)
                                 │
                                 ├─ Registro de ferramentas (definição + executor)
                                 ├─ Validação de parâmetros (Pydantic)
                                 ├─ Autorização (usuários, papéis, permissões)
                                 ├─ Auditoria
                                 └─ Banco de dados (SQLite)
```

Fluxo de uma pergunta: o usuário escreve → o modelo pede uma ferramenta com parâmetros
estruturados → o servidor valida e executa → o resultado volta ao modelo → o modelo redige a resposta.

## O que já funciona

- Chat no terminal com histórico de conversa
- Adaptador de IA isolado (hoje Gemini; trocar de provedor significa escrever um novo adaptador)
- Chamada de ferramentas (*function calling*) com parâmetros estruturados
- Ferramenta `consultar_agendamentos`: validação de entrada, SQL parametrizado e limite de resultados
- Laço de orquestração com limite de passos e desfazimento do histórico em caso de falha
- Testes automatizados que não usam rede (com um "modelo de mentira")

## Roadmap

- [x] **Fase 1:** fundamentos (chat no terminal, integração com o modelo)
- [x] **Fase 2:** primeira ferramenta (consulta, validação, function calling)
- [ ] **Fase 3:** identidade e permissões (usuários, papéis, autorização no servidor) — em andamento
- [ ] **Fase 4:** operações de escrita com confirmação e proteção contra duplicidade
- [ ] **Fase 5:** orquestração de várias etapas e contexto
- [ ] **Fase 6:** extensibilidade (catálogo de ferramentas, versionamento)
- [ ] **Fase 7:** produção (observabilidade, carga, backups)

## Começando

Requisitos: Python 3.12+ e uma chave de API do Gemini ([Google AI Studio](https://aistudio.google.com/app/apikey)).

```powershell
git clone https://github.com/MatheusAlvesCavalcante/agente-plataforma.git
cd agente-plataforma
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edite o `.env` com sua chave (`LLM_API_KEY`) e o nome do modelo (`LLM_MODEL`). Depois:

```powershell
python -m scripts.seed
python -m app.cli
```

Experimente perguntar:

- `Quais reuniões eu tenho amanhã?`
- `Tenho algo com o Carlos?`
- `Cancela a reunião com a Beatriz` (ainda não existe essa ferramenta; o assistente deve dizer que não consegue)

## Testes

```powershell
python -m pytest -v
```

Os testes não chamam a API de IA nem consomem cota.

## Estrutura

```
app/
├── orchestrator/   # laço central: modelo ⇄ ferramentas
├── llm/            # adaptadores de provedores de IA
├── tools/          # definição, validação e execução das ferramentas
├── db/             # conexão e esquema do SQLite
├── auth/           # identidade e permissões (em construção)
├── audit/          # trilha de auditoria (em construção)
└── cli.py          # chat no terminal
scripts/            # utilitários (ex.: popular o banco)
tests/              # testes automatizados
docs/               # decisões de arquitetura
```

## Segurança

- **Nunca** versione o arquivo `.env`: ele guarda a chave de API e está no `.gitignore`.
- O `scripts/seed.py` cria dados fictícios, e as etapas de autenticação usam senhas fracas **apenas para
  desenvolvimento local**. Jamais use essas credenciais fora do seu computador.
- Na camada gratuita de provedores de IA, o que você envia pode ser usado pelo provedor.
  Use apenas dados fictícios.
- Este projeto é um protótipo de aprendizado: ainda não passou por revisão de segurança.

## Licença

[MIT](LICENSE)