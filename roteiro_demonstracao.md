# Roteiro de Demonstração - MiniAWS
*Este é um arquivo de orientação privado para conduzir a sua apresentação.*

---

## 🚀 Preparação
1. Certifique-se de que o servidor Flask está rodando.
   * Se precisar reiniciar, basta dar um duplo clique no arquivo **[run.bat](file:///c:/Users/rodri/Desktop/miniAWS/run.bat)**.
2. Abra o navegador em: **[http://localhost:5000/](http://localhost:5000/)**

---

## 📋 Passo a Passo da Apresentação

### Passo 1: Visão Geral (Dashboard)
*   Mostre a tela do **Dashboard**.
*   Explique que este é um painel unificado para monitorar a infraestrutura local que simula recursos da AWS.
*   Destaque os contadores de métricas (Instâncias, Buckets, Arquivos e Lambda) que atualizam em tempo real.

### Passo 2: Criar Servidor Web (Simulação EC2)
*   Navegue até a aba **EC2 (Instâncias)** no menu lateral.
*   Clique em **Nova Instância**.
*   Digite um nome para a máquina virtual (ex: `maquina-web-01`) e clique em **Criar Instância**.
*   Mostre que a instância foi criada com o status **PARADA** (Stopped), refletindo o comportamento real da AWS onde recursos criados não sobem cobrando por padrão ou aguardam inicialização.

### Passo 3: Criar Repositório de Arquivos (Simulação S3)
*   Navegue até a aba **S3 (Armazenamento)**.
*   Clique em **Novo Bucket S3**.
*   Crie um bucket compatível (ex: `site-estatico-bucket`).
*   Selecione o bucket criado na lista lateral. A área de arquivos à direita será aberta vazia.

### Passo 4: Upload e Disparo Automático (Simulação AWS Lambda)
*   No bucket selecionado, clique em **Upload de Arquivo** e envie um arquivo HTML qualquer (você pode usar um HTML simples ou o código do seu site).
*   **A mágica do Lambda:** Explique que o upload de um arquivo gerou um evento do tipo `s3:ObjectCreated`.
*   Navegue até a aba **AWS Lambda** e mostre a execução recente: a função serverless `miniAWS-S3-AutoTrigger-Logger` foi disparada de forma 100% automatizada e sem servidor ativo para ler o arquivo e catalogar metadados.
*   Mostre também a aba **Cloud Logs** para provar que o evento foi registrado cronologicamente no ecossistema.

### Passo 5: Publicação de Site (Integração EC2 + S3)
*   Volte à aba **EC2 (Instâncias)**.
*   Na sua instância `maquina-web-01`, clique em **Publicar HTML**.
*   Selecione a aba **Importar do S3**.
*   Selecione o bucket `site-estatico-bucket` e o arquivo HTML que você acabou de subir. Clique em **Importar e Publicar**.
*   *Explicação:* Esse passo simula a integração real de uma máquina EC2 baixando código de um bucket S3 para servir um site.

### Passo 6: Execução e Teste de Resiliência
*   Ainda no **EC2**, clique em **Iniciar** ao lado de `maquina-web-01` (o status mudará para **EXECUTANDO** e o LED ficará verde).
*   Clique em **Acessar Site** (ou abra `http://localhost:5000/site/maquina-web-01`). Mostre o site rodando de dentro da máquina virtual simulada!
*   **Demonstração de Queda:** Volte ao painel e clique em **Parar** na instância.
*   Recarregue a aba do site. O sistema retornará um erro **503 Service Unavailable** avisando de forma muito visual que a máquina EC2 está desligada (Stopped).

---

## 💡 Relação com os Serviços Reais da AWS

Para responder possíveis perguntas durante a banca ou apresentação:

| Recurso no MiniAWS | Equivalente na AWS Real | Comportamento Simulado |
| :--- | :--- | :--- |
| **Instâncias locais** | Amazon EC2 | Pastas sob `/instances` que servem HTML quando ativadas |
| **Buckets locais** | Amazon S3 | Pastas sob `/storage` para upload/download de objetos |
| **Função Python automática** | AWS Lambda | Trigger interno no Flask disparado ao interceptar novos arquivos |
| **Tela de Logs** | Amazon CloudWatch Logs | Exibição unificada de logs salvos em `logs.json` |
