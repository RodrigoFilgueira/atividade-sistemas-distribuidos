# MiniAWS - Simulador de Serviços AWS 🚀

Este projeto é um simulador local simplificado de serviços da AWS (Amazon Web Services), projetado para fins didáticos na disciplina de **Sistemas Distribuídos**. Ele simula a integração de quatro componentes centrais da nuvem da AWS:
1. **Amazon EC2:** Criação, inicialização, parada e publicação de sites estáticos em servidores virtuais.
2. **Amazon S3:** Armazenamento de arquivos estáticos estruturados em Buckets.
3. **AWS Lambda:** Execução sem servidor orientada a eventos (disparada automaticamente no upload de arquivos para o S3 para analisar metadados).
4. **Amazon CloudWatch Logs:** Monitoramento unificado e cronológico de eventos e atividades do ecossistema.

---

## 🛠️ Pré-requisitos
Para executar o simulador, você precisa ter instalado no seu computador:
*   **Python 3.x** instalado e configurado nas variáveis de ambiente (`PATH`).

---

## 🚀 Como Executar o Simulador

### Método 1: Dois cliques (Apenas Windows)
1. Dê um duplo clique no arquivo **`run.bat`** localizado na raiz do projeto.
2. O script instalará as dependências necessárias automaticamente (Flask) e iniciará o servidor.
3. O painel estará disponível no seu navegador em: **[http://localhost:5000](http://localhost:5000)**.

### Método 2: Linha de Comando (Qualquer OS)
1. Abra o terminal ou prompt de comando na raiz do projeto.
2. Instale a biblioteca necessária (Flask):
   ```bash
   pip install -r requirements.txt
   ```
3. Execute o servidor:
   ```bash
   python app.py
   ```
4. Abra o navegador no endereço: **[http://localhost:5000](http://localhost:5000)**.

---

## 📋 Roteiro de Teste Passo a Passo

Siga estes passos simples para testar a integração dos serviços de nuvem de ponta a ponta:

### Passo 1: Criar um Servidor (Simulando EC2)
1. No menu lateral do dashboard, vá para a aba **EC2**.
2. Clique em **Nova Instância**.
3. Diga um nome para o seu servidor (ex: `maquina-web-01`) e clique em **Criar Instância**.
4. Observe que ela é criada com o status **PARADA** (Stopped), aguardando ativação.

### Passo 2: Criar o Armazenamento (Simulando S3)
1. No menu lateral, acesse a aba **S3**.
2. Clique em **Novo Bucket S3**.
3. Dê um nome único para o bucket (ex: `site-estatico-bucket`) e clique em **Criar**.
4. Selecione o bucket criado na lista lateral (a área de arquivos à direita será exibida vazia).

### Passo 3: Upload e Disparo Automático (Simulando AWS Lambda & CloudWatch)
1. Dentro do seu bucket selecionado, clique no botão **Upload de Arquivo**.
2. Selecione o arquivo de teste **`index_teste.html`** (localizado na raiz deste projeto) e conclua o upload.
3. **A reação do Lambda:** O upload de um arquivo para o S3 gera automaticamente um gatilho do tipo `s3:ObjectCreated`.
4. Vá para a aba **AWS Lambda** no menu lateral e veja que a função `miniAWS-S3-AutoTrigger-Logger` foi disparada automaticamente sem intervenção humana para analisar e coletar os metadados do arquivo.
5. Vá para a aba **Cloud Logs** e comprove que o registro temporal e ordenado do evento foi registrado no ecossistema de monitoramento.

### Passo 4: Publicar o Site (Integração EC2 + S3)
1. Volte à aba **EC2**.
2. Na linha correspondente à sua instância (`maquina-web-01`), clique no botão **Publicar HTML**.
3. Selecione a aba **Importar do S3**.
4. Selecione o bucket (`site-estatico-bucket`), escolha o arquivo (`index_teste.html`) e clique em **Importar e Publicar**.
   * *O simulador copiará o arquivo do S3 para a pasta virtual do seu servidor EC2, simulando um deploy real de código.*

### Passo 5: Teste de Acesso e Resiliência
1. Na lista de instâncias do **EC2**, clique em **Iniciar** ao lado de `maquina-web-01`. O status mudará para **EXECUTANDO** (Running) e o LED de status ficará verde.
2. Clique em **Acessar Site** (ou abra `http://localhost:5000/site/maquina-web-01` diretamente no seu navegador). O site importado do S3 rodará com sucesso!
3. **Simulando Queda de Serviço:** Volte ao painel do MiniAWS e clique em **Parar** na instância.
4. Recarregue a aba do seu site (`http://localhost:5000/site/maquina-web-01`). Você verá uma página de erro **503 Service Unavailable** com design visual, confirmando que a sua máquina virtual EC2 está fora do ar.

---

## 📁 Estrutura de Arquivos da Entrega

O projeto foi limpo de arquivos de desenvolvimento, mantendo apenas o necessário:
*   `app.py`: Backend Flask que implementa a API do simulador.
*   `static/`: Pasta contendo a interface web em HTML, CSS e JS.
*   `index_teste.html`: Arquivo de exemplo rico visualmente e dinâmico, usado para carregar no S3 e testar a publicação.
*   `instances/` e `storage/`: Pastas temporárias onde o simulador cria as instâncias e buckets fisicamente (devem ser enviadas vazias).
*   `instances.json` e `logs.json`: Arquivos de banco de dados locais inicializados limpos para que seu teste comece do zero.
*   `requirements.txt` e `run.bat`: Arquivos de dependências e script de execução.
*   `README.md`: Este guia explicativo.
