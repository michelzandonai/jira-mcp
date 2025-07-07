# Tarefa: Implementar Criação de Issues em Lote (`batch_create_issues`)

## 1. Descrição da Funcionalidade

O objetivo desta funcionalidade é permitir ao usuário criar múltiplas issues no Jira de uma só vez com um único comando. O agente deverá ser capaz de extrair os dados de cada issue a ser criada, processá-las em lote e fornecer um relatório sobre a operação.

A funcionalidade **deve suportar o registro de horas no momento da criação** da issue, reutilizando a lógica da funcionalidade de registro em lote.

**Exemplo de Comando do Usuário:**
> "Crie duas tarefas no projeto 'Mobile': a primeira é 'Desenvolver tela de login', descrição 'Implementar UI', com 2h de trabalho hoje. A segunda é 'Criar componente de botão', descrição 'Botão reutilizável'."

## 2. Plano de Desenvolvimento (Lista de Tarefas)

- [ ] **1. Criar o arquivo da ferramenta:**
  - [ ] Criar o arquivo `src/tools/batch_create_issues.py`.

- [ ] **2. Definir a função `batch_create_issues`:**
  - [ ] A função receberá `issues_to_create` (List[Dict]).

- [ ] **3. Implementar a lógica de processamento em lote:**
  - [ ] Iniciar um cliente Jira e uma lista `report`.
  - [ ] Iniciar um loop `for` para iterar sobre cada `issue_data` na lista.

- [ ] **4. Implementar a busca e validação (dentro do loop):**
  - [ ] Validar campos obrigatórios.
  - [ ] Usar `utils.find_project_by_identifier` para encontrar o projeto.

- [ ] **5. Implementar a criação e o registro de tempo (orquestração):**
  - [ ] **Passo 1:** Chamar `jira_client.create_issue` para criar a issue.
  - [ ] Se a criação falhar, registrar o erro e pular para o próximo item.
  - [ ] **Passo 2 (Reutilização):** Se a criação for bem-sucedida e `time_spent` for fornecido, chamar a função auxiliar `utils.log_work_for_issue` para registrar o tempo na issue recém-criada.
  - [ ] Adicionar uma mensagem de sucesso (com o resultado de ambos os passos) ou falha ao `report`.

- [ ] **6. Finalizar e Integrar:**
  - [ ] Retornar o `report` consolidado.
  - [ ] Integrar a nova ferramenta ao `JiraAgent`.

- [ ] **7. Atualizar as `instruction` do agente para que ele saiba como usar a ferramenta.** 