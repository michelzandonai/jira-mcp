# Tarefa: Implementar Registro de Horas em Lote (`batch_log_work`)

## 1. Descrição da Funcionalidade

O objetivo desta funcionalidade é permitir que o usuário registre horas de trabalho em múltiplas tarefas de um **único projeto** com um só comando. O agente deve ser capaz de parsear uma frase complexa, extrair as diferentes entradas de trabalho (identificando as tasks pelo nome), e processá-las em lote.

É **crítico** que a ferramenta valide se a descrição de uma task corresponde a uma única issue. Em caso de múltiplas correspondências (ambiguidade), a ferramenta deve reportar um erro para aquele item específico e continuar com os outros.

**Exemplo de Comando do Usuário:**
> "No projeto 'Frontend', preciso registrar o seguinte: 2h na tarefa 'corrigir login', 30m na 'ajustar botão principal', e 1h na 'melhorar performance da lista'."

## 2. Plano de Desenvolvimento (Lista de Tarefas)

- [ ] **1. Criar função auxiliar reutilizável em `utils.py`:**
  - [ ] Criar a função `log_work_for_issue(jira_client, issue_key, time_spent, work_start_date, work_description)` que conterá a lógica pura de registrar trabalho para uma issue já conhecida.

- [ ] **2. Criar o arquivo da ferramenta:**
  - [ ] Criar o arquivo `src/tools/batch_log_work.py`.

- [ ] **3. Definir a função `batch_log_work`:**
  - [ ] A função receberá `project_identifier` (str) e `work_logs` (List[Dict]).

- [ ] **4. Implementar a lógica de processamento em lote:**
  - [ ] Iniciar um cliente Jira e uma lista `report`.
  - [ ] Validar o `project_key` uma única vez.
  - [ ] Iniciar um loop `for` para iterar sobre cada `log` na lista `work_logs`.

- [ ] **5. Implementar a busca e validação (dentro do loop):**
  - [ ] Usar `utils.find_issue_by_summary` para encontrar a `issue_key` a partir do `issue_identifier`.
  - [ ] Tratar erros de ambiguidade ou falha na busca.

- [ ] **6. Chamar a função auxiliar (dentro do loop):**
  - [ ] Chamar `utils.log_work_for_issue` com os dados validados.
  - [ ] Adicionar o resultado (sucesso ou falha) da função auxiliar ao `report`.

- [ ] **7. Finalizar e Integrar:**
  - [ ] Retornar o `report` consolidado.
  - [ ] Integrar a nova ferramenta ao `JiraAgent`.
  - [ ] Atualizar as `instruction` do agente para que ele entenda o novo formato (um projeto, várias tasks). 