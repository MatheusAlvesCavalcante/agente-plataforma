# Decisões de arquitetura

1. **Monólito modular.** Um único backend com fronteiras internas claras. Mais simples de
   aprender e manter do que microsserviços, e permite separar depois se for preciso.
2. **Catálogo de ferramentas no código.** Versionado no Git e testável. Configuração no banco
   fica para depois e nunca substitui um executor aprovado.
3. **Adaptador de IA isolado (`app/llm/`).** O orquestrador não sabe qual provedor está por trás.
   As mensagens carregam um campo opaco (`provider_data`) porque os modelos Gemini 3 exigem que
   dados internos do raciocínio (*thought signatures*) voltem junto com as chamadas de ferramenta.
4. **Sem chamada automática de funções do SDK.** Toda execução passa pelo nosso registro, que
   valida e, nas próximas fases, autoriza e audita.
5. **SQLite no protótipo**, com migração para PostgreSQL planejada para a fase de produção.
6. **Princípio central:** o modelo propõe, o servidor decide. A identidade do usuário vem sempre
   do servidor, nunca de parâmetros fornecidos pelo modelo.