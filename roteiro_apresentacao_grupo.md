# 🎬 Roteiro de Apresentação — Grupo 5
## Computação em Nuvem: AWS (Amazon Web Services)
### Disciplina: Sistemas Distribuídos | 3ª Nota — 20261

---

> **Divisão geral:**
> - 🔹 **Rodrigo Cesar** — 1ª Metade: Slides de abertura + Teoria de Nuvem, Virtualização e EC2 + Demo ao vivo do EC2 no MiniAWS
> - 🔸 **Pedro Lucas** — 2ª Metade: Teoria de S3 e Lambda + Demo ao vivo de S3, Lambda e integração completa + Conclusão

---

## ⏱️ Cronograma da Apresentação

| Marcação | Segmento | Responsável |
|:---|:---|:---|
| `00:00 – 01:00` | Abertura e apresentação do grupo | **Rodrigo** |
| `01:00 – 02:30` | O que é Computação em Nuvem e a AWS | **Rodrigo** |
| `02:30 – 04:30` | Virtualização: Xen, KVM e AWS Nitro System | **Rodrigo** |
| `04:30 – 05:30` | Amazon EC2 — teoria | **Rodrigo** |
| `05:30 – 06:00` | Apresentação do MiniAWS (arquitetura) | **Rodrigo** |
| `06:00 – 08:00` | 🖥️ **Demo ao vivo — EC2 no MiniAWS** | **Rodrigo** |
| `08:00 – 09:30` | Amazon S3 — teoria | **Pedro** |
| `09:30 – 11:00` | AWS Lambda — teoria | **Pedro** |
| `11:00 – 13:00` | 🖥️ **Demo ao vivo — S3 + Lambda Trigger + Cloud Logs** | **Pedro** |
| `13:00 – 15:30` | 🖥️ **Demo ao vivo — Deploy + Integração EC2+S3 + Resiliência** | **Pedro** |
| `15:30 – 17:00` | Tabela comparativa, aprendizados e encerramento | **Pedro** |

**Tempo total alvo: ~17 minutos**

---

## 🔹 PRIMEIRA METADE — Rodrigo Cesar
**Duração: 00:00 – 08:00**

---

### SLIDE 1 — Capa
**Sugestão visual:** Logo AWS, título da apresentação, nomes dos integrantes, logo do IFMA/DComp.

> **💬 Fala (Rodrigo):**
> "Olá, professor, olá a todos. Eu sou o Rodrigo Cesar e, junto com o Pedro Lucas, formamos o Grupo 5. O tema da nossa apresentação é **Computação em Nuvem**, com foco no ecossistema da **Amazon Web Services**. A proposta do nosso trabalho vai além da teoria: nós desenvolvemos, do zero, um simulador funcional chamado **MiniAWS** que reproduz na prática o comportamento dos serviços EC2, S3 e Lambda. Vou começar apresentando os fundamentos e a arquitetura de virtualização da AWS. Em seguida, faço a primeira demonstração ao vivo. Depois, o Pedro assume para apresentar o S3, o Lambda e fechar com a demonstração completa de integração entre os serviços."

⏱️ *Meta: terminar esse slide em ~01:00*

---

### SLIDE 2 — O que é Computação em Nuvem e a AWS?
**Sugestão visual:** Mapa global com regiões AWS, diagrama IaaS/PaaS/SaaS em camadas.

> **💬 Fala (Rodrigo):**
> "Computação em nuvem, em essência, é o modelo de fornecer recursos de TI — servidores, armazenamento, banco de dados, rede — pela internet, com pagamento **apenas pelo que é consumido**. Isso elimina a necessidade de manter infraestrutura física local e se encaixa diretamente no conceito de **sistemas distribuídos**: recursos espalhados geograficamente operando como um ecossistema coeso.
>
> A AWS é a maior plataforma de nuvem do mundo. Ela organiza sua infraestrutura em **Regiões** — zonas geográficas como São Paulo, Virginia, Tóquio — e cada Região contém múltiplas **Zonas de Disponibilidade**, que são datacenters fisicamente isolados, mas interconectados por fibra de altíssima velocidade. Essa arquitetura é o que garante a **alta disponibilidade e tolerância a falhas** que estudamos na disciplina."

⏱️ *Meta: terminar esse slide em ~02:30*

---

### SLIDES 3 e 4 — Virtualização: Xen, KVM e AWS Nitro System
**Sugestão visual:** Diagrama comparativo entre Xen (com Dom0) e Nitro (com cartões ASIC). Seta de evolução temporal.

> **💬 Fala (Rodrigo):**
> "A base tecnológica de toda nuvem é a **virtualização**: a capacidade de abstrair hardware físico em múltiplas máquinas virtuais isoladas. A AWS passou por três gerações nessa evolução.
>
> **1ª Geração — Hypervisor Xen:** A AWS começou com o Xen, um hypervisor de **Tipo 1**, que roda diretamente no hardware físico. No modelo do Xen, existe o **Domínio 0** — um sistema operacional privilegiado responsável por gerenciar toda a entrada e saída de rede e disco — e os **Domínios de Usuário**, onde as instâncias dos clientes rodam. O problema: o Dom0 consumia uma fatia real da CPU física do servidor, que poderia estar sendo vendida ao cliente.
>
> **2ª Geração — KVM:** Visando eficiência, a AWS migrou para o **KVM** (Kernel-based Virtual Machine), que transforma o próprio kernel do Linux em um hypervisor Tipo 1, com melhor integração ao hardware e acesso direto às extensões de virtualização dos processadores modernos.
>
> **3ª Geração — AWS Nitro System:** Aqui está a verdadeira revolução. O Nitro descarrega **todas as funções de gerenciamento** para **cartões de hardware dedicados** — chips ASIC específicos para rede VPC, armazenamento EBS e segurança. Com isso, o hypervisor Nitro tornou-se tão enxuto que entrega virtualmente **100% da CPU e memória física** do servidor diretamente para a instância do cliente, sem overhead. Além da performance, o Nitro entrega isolamento físico de segurança, tornando impossível que um cliente acesse dados de outro mesmo em hardware compartilhado."

⏱️ *Meta: terminar esses slides em ~04:30*

---

### SLIDE 5 — Amazon EC2 (Teoria)
**Sugestão visual:** Ícone AWS EC2, tabela com famílias de instâncias (T, M, C, R) e seus casos de uso.

> **💬 Fala (Rodrigo):**
> "O primeiro serviço que vamos abordar é o **Amazon EC2** — Elastic Compute Cloud. Ele fornece servidores virtuais sob demanda, os quais chamamos de **instâncias**. Você escolhe o sistema operacional, a quantidade de CPU, memória e armazenamento, e a AWS provisiona em segundos.
>
> O EC2 organiza as instâncias em **famílias** otimizadas para diferentes cargas de trabalho: as famílias **T e M** são de uso geral, ideais para servidores web; a família **C** é otimizada para processamento computacional intensivo; e a família **R** é otimizada para memória, usada em bancos de dados em memória como Redis ou sistemas analíticos.
>
> No contexto de sistemas distribuídos, o EC2 é o **nó de computação**: o ponto ativo da rede que processa requisições. E é exatamente isso que vamos simular agora no nosso MiniAWS."

⏱️ *Meta: terminar esse slide em ~05:30*

---

### SLIDE 6 — Arquitetura do MiniAWS (Transição para a Demo)
**Sugestão visual:** Diagrama simples: [Navegador] → [Flask/Python] → [/instances + /storage + logs.json]

> **💬 Fala (Rodrigo):**
> "Para tornar esses conceitos tangíveis, nós desenvolvemos o **MiniAWS**: um simulador local funcional que replica o comportamento dos serviços AWS. O backend foi feito em **Python com Flask**, expondo rotas REST que imitam as APIs reais da AWS. O frontend é uma **SPA** — Single Page Application — desenvolvida com HTML5 e CSS dinâmico. A persistência é feita localmente no sistema de arquivos: máquinas EC2 criam subpastas físicas em `/instances`, buckets S3 criam subpastas em `/storage`, e todos os eventos são auditados num arquivo `logs.json`.
>
> Vou abrir o simulador agora."

⏱️ *Meta: terminar esse slide em ~06:00*

---

### 🖥️ DEMONSTRAÇÃO PARTE 1 — EC2 no MiniAWS
**Responsável: Rodrigo | Tempo: 06:00 – 08:00**

> ⚠️ **Antes de começar:** Abra `http://localhost:5000` no navegador em tela cheia. O Dashboard deve mostrar todos os contadores zerados.

**Passos a executar na tela:**

1. Mostre o **Dashboard** por 10 segundos, apontando os contadores (Instâncias EC2: 0, Buckets S3: 0, Arquivos: 0, Gatilhos Lambda: 0) e os logs recentes abaixo.
2. Clique na aba **"EC2 (Instâncias)"** no menu lateral.
3. Clique em **"Nova Instância"**.
4. No modal, preencha o nome: `servidor-web-grupo5` e clique em **"Criar Instância"**.
5. Mostre a instância criada com o badge vermelho **"Parado"**.
6. Clique em **"Iniciar"** — observe o badge mudar para verde **"Executando"**.
7. Clique no link **"Acessar Site"** — mostre a tela de aviso *"Nenhum site publicado"* (a máquina está ligada mas vazia).

> **💬 Fala (Rodrigo):**
> "Aqui está o nosso console. O Dashboard mostra a infraestrutura zerada. Vou acessar o EC2 e criar uma instância chamada `servidor-web-grupo5`. Percebam: ela nasce no estado **Parado** — comportamento idêntico ao EC2 real, onde a máquina é criada mas não consome CPU até ser ligada. Clicando em 'Iniciar', o nó de computação entra em modo **Executando**. Se eu acessar a URL desse servidor agora, o simulador me informa que a máquina está ativa, mas ainda não há conteúdo publicado nela — precisamos abastecer o armazenamento S3 primeiro.
>
> É exatamente aí que o Pedro entra. Vou passar a palavra a ele para apresentar o S3 e o Lambda."

---

## 🔸 SEGUNDA METADE — Pedro Lucas
**Duração: 08:00 – 17:00**

> ⚠️ **Pedro:** Ao assumir a apresentação, a tela do MiniAWS já está aberta. Mantenha o compartilhamento de tela ativo. Você vai usá-la novamente a partir do minuto 11:00.

---

### SLIDE 7 — Amazon S3 — Simple Storage Service (Teoria)
**Sugestão visual:** Diagrama mostrando Bucket > Objeto (Key + Value + Metadata). Ícone de replicação multi-AZ com setas entre 3 datacenters.

> **💬 Fala (Pedro):**
> "Obrigado, Rodrigo. Dando continuidade, vou apresentar o segundo serviço: o **Amazon S3**. Diferente do EC2, que fornece armazenamento em bloco acoplado à instância, o S3 é um serviço de **armazenamento de objetos**: você não gerencia sistemas de arquivos nem diretórios — você simplesmente envia objetos para um contêiner chamado **Bucket**.
>
> Cada objeto é composto por: o arquivo em si, uma **chave única** que funciona como endereço dentro do bucket, e **metadados** como tipo de conteúdo, tamanho e data de criação.
>
> O ponto mais impressionante do S3 em sistemas distribuídos é sua **durabilidade projetada de 99,999999999%** — os famosos *onze noves*. Isso é alcançado porque o S3 replica automaticamente cada objeto em no mínimo **três Zonas de Disponibilidade** fisicamente separadas dentro de uma região, sem que você precise configurar nada. Em termos práticos, isso significa que o S3 foi projetado para nunca perder um arquivo. Seus usos vão desde repositório de backups e imagens até hospedagem de sites estáticos completos."

⏱️ *Meta: terminar esse slide em ~09:30*

---

### SLIDE 8 — AWS Lambda — Computação Serverless (Teoria)
**Sugestão visual:** Fluxograma: [Evento S3 Upload] → [Trigger] → [Função Lambda executa] → [Log gerado]. Comparação: Servidor tradicional (sempre ligado) vs Lambda (executa só quando chamado).

> **💬 Fala (Pedro):**
> "O terceiro pilar é o **AWS Lambda**, o serviço de computação sem servidor da AWS. O termo *serverless* não significa que servidores não existem — eles existem, mas você nunca os vê ou gerencia. Você escreve apenas a função com a lógica que deseja executar, define **qual evento a disparará**, e a AWS cuida de tudo o mais.
>
> O Lambda opera sob o modelo **FaaS — Function as a Service**. A função fica completamente inativa, sem consumir recurso algum, até que um evento aconteça. Esse evento pode ser um upload de arquivo no S3, uma requisição HTTP, uma mensagem numa fila, ou até um agendamento por timer. Quando o gatilho dispara, o Lambda sobe um contêiner isolado, executa a função e o destrói. A cobrança é feita **por milissegundo de execução real**.
>
> Esse modelo é fundamental para arquiteturas **orientadas a eventos** em sistemas distribuídos: serviços que se comunicam de forma assíncrona e desacoplada, sem que um precise saber da existência do outro. É o conceito de *loose coupling* na prática. Vou mostrar isso acontecendo ao vivo agora."

⏱️ *Meta: terminar esse slide em ~11:00*

---

### 🖥️ DEMONSTRAÇÃO PARTE 2 — S3 + Lambda Trigger + Cloud Logs
**Responsável: Pedro | Tempo: 11:00 – 13:00**

> ⚠️ **Antes de começar:** Certifique-se de que a aba do MiniAWS está visível. A instância `servidor-web-grupo5` deve aparecer no EC2 com status "Executando" (criada pelo Rodrigo).

**Passos a executar na tela:**

1. Clique na aba **"S3 (Armazenamento)"** no menu lateral.
2. Clique em **"Novo Bucket S3"**.
3. No modal, preencha o nome: `bucket-estatico-grupo5` e clique em **"Criar Bucket"**.
4. O bucket criado será automaticamente selecionado na barra lateral esquerda, mostrando a área de arquivos vazia à direita.
5. Clique em **"Upload de Arquivo"**.
6. Selecione o arquivo HTML preparado para a demonstração e confirme o upload.
7. Mostre o arquivo listado na tabela com nome, tamanho e data/hora do upload.
8. Clique na aba **"AWS Lambda"** no menu lateral.
9. Mostre a tabela de execuções com a entrada da função `miniAWS-S3-AutoTrigger-Logger` com status **"Sucesso"** e o timestamp exato.
10. Clique na aba **"Cloud Logs"** no menu lateral.
11. Mostre as duas entradas cronológicas: primeiro o log do S3 (upload), depois o log do Lambda (execução automática).

> **💬 Fala (Pedro):**
> "Acesso a aba S3 e crio o bucket `bucket-estatico-grupo5`. O bucket aparece vazio, pronto para receber objetos. Faço o upload de um arquivo HTML — simula o código-fonte de um site estático que um desenvolvedor enviaria para a nuvem.
>
> Agora a parte mais importante: vou direto para a aba **AWS Lambda**. Sem que eu precisasse fazer absolutamente nada, a função `miniAWS-S3-AutoTrigger-Logger` foi **executada automaticamente** no exato momento do upload. Isso é arquitetura orientada a eventos: o S3 gerou um evento `ObjectCreated`, e o Lambda o capturou e processou sem nenhum servidor ativo.
>
> E na aba **Cloud Logs** — que simula o CloudWatch da AWS — vemos o rastro cronológico completo: o evento S3 de upload, seguido imediatamente pela execução da Lambda. Isso é o que chamamos de **auditoria de eventos distribuídos**."

---

### 🖥️ DEMONSTRAÇÃO PARTE 3 — Deploy EC2+S3 + Resiliência (Erro 503)
**Responsável: Pedro | Tempo: 13:00 – 15:30**

**Passos a executar na tela:**

1. Clique na aba **"EC2 (Instâncias)"** no menu lateral.
2. Na linha da instância `servidor-web-grupo5`, clique no botão **"Publicar HTML"** (ícone de nuvem com seta para cima).
3. No modal que abrir, clique na aba **"Importar do S3"**.
4. No dropdown "Selecione um bucket", escolha `bucket-estatico-grupo5`.
5. No dropdown "Selecione o arquivo HTML", escolha o arquivo que acabou de ser enviado.
6. Clique em **"Importar e Publicar"**.
7. Na tabela do EC2, a coluna "Site Hospedado" agora exibirá o link **"Acessar Site"**. Clique nele — uma nova aba abre com o site renderizado.
8. Volte à aba do MiniAWS. Clique em **"Parar"** na instância `servidor-web-grupo5` — o badge muda para vermelho "Parado".
9. Volte à aba do site e recarregue a página (F5).
10. Mostre a tela de erro **"503 Service Unavailable"** com a mensagem customizada sobre a instância desligada.

> **💬 Fala (Pedro):**
> "Agora a cereja do bolo: a **integração entre EC2 e S3**. Volto ao EC2 e clico em 'Publicar HTML' na nossa instância. Escolho a opção 'Importar do S3', seleciono o bucket e o arquivo HTML que acabamos de subir. O simulador então copia o objeto do S3 para o diretório da instância EC2 — exatamente como uma máquina real baixaria código de um repositório na nuvem antes de servir.
>
> Clicando em 'Acessar Site', o nosso servidor está **servindo a página na web**. O site está no ar.
>
> Mas o que acontece quando um nó de computação falha? Vou simular isso: clico em 'Parar'. A máquina vai para o estado desligado. Ao recarregar o site — **503 Service Unavailable**. O sistema retornou imediatamente o erro correto, avisando que o nó está fora do ar. Isso ilustra um comportamento crítico de sistemas distribuídos: **detectar e comunicar falhas de forma clara**. Em produção real, um load balancer rotearia o tráfego para outra instância. Aqui, mostramos que o nosso simulador respeita esse ciclo de vida."

---

### SLIDE 9 — Tabela Comparativa e Encerramento
**Sugestão visual:** Tabela abaixo em destaque + frase de encerramento.

| Serviço AWS Real | Simulação no MiniAWS | Conceito de Sistemas Distribuídos |
|:---|:---|:---|
| **Amazon EC2** | Pasta `/instances/<nome>` + rota HTTP `/site/<nome>` | Nó de computação, ciclo de vida e isolamento |
| **Amazon S3** | Pasta `/storage/<bucket>/` + objetos no filesystem | Armazenamento distribuído desacoplado |
| **AWS Lambda** | Trigger Python interno no Flask pós-upload | Arquitetura orientada a eventos, FaaS |
| **Amazon CloudWatch** | Arquivo `logs.json` + tela Cloud Logs | Auditoria e observabilidade de eventos |

> **💬 Fala (Pedro):**
> "Para fechar, esta tabela resume o mapeamento conceitual do nosso projeto. Cada abstração da AWS foi traduzida para uma estrutura local que preserva a **mesma lógica arquitetural**: isolamento de nós com o EC2, armazenamento de objetos desacoplado com o S3, execução reativa sem servidor com o Lambda, e auditoria centralizada com o Cloud Logs.
>
> O desenvolvimento do MiniAWS nos deu uma visão concreta de como um sistema distribuído real gerencia **estado, eventos, integração e falhas** em larga escala. Agradecemos ao professor e à banca pela atenção. Em nome do Grupo 5 — Rodrigo Cesar e Pedro Lucas — ficamos à disposição para perguntas. Muito obrigado!"

---

## 🧰 Checklist de Preparação (Antes de Gravar)

- [ ] Executar `run.bat` e confirmar servidor rodando em `http://localhost:5000`
- [ ] Limpar dados anteriores: apagar pastas dentro de `/instances` e `/storage`, e esvaziar `instances.json` e `logs.json` (substituir pelo conteúdo `{}` e `[]` respectivamente)
- [ ] Preparar arquivo HTML de demonstração (pode ser qualquer página simples com o nome do grupo)
- [ ] Abrir o navegador em tela cheia em `http://localhost:5000`
- [ ] Testar o fluxo completo uma vez antes de gravar para garantir fluidez

## ❓ Possíveis Perguntas da Banca e Respostas Sugeridas

| Pergunta | Resposta Sugerida |
|:---|:---|
| *"Como o Lambda é disparado no simulador?"* | "No backend Flask, a rota de upload do S3 chama diretamente a função `log_event('Lambda', ...)` após salvar o arquivo. Simula o mecanismo de event-trigger que o S3 real envia ao Lambda via SNS/SQS." |
| *"Por que usaram Flask e não Django?"* | "Flask é minimalista e permite construir APIs REST com total controle e sem overhead de ORM ou templates, ideal para um simulador educacional." |
| *"O Nitro é um hypervisor Tipo 1 ou Tipo 2?"* | "O Hypervisor Nitro é classificado como Tipo 1 (bare-metal), pois roda diretamente no hardware. A inovação foi terceirizar o plano de gerenciamento para ASICs dedicados, tornando-o o mais enxuto possível." |
| *"O que é paravirtualização?"* | "É uma técnica onde o sistema operacional convidado é modificado para saber que está rodando em uma VM, fazendo chamadas diretas ao hypervisor (hypercalls) em vez de emular hardware, o que traz ganho de desempenho." |
