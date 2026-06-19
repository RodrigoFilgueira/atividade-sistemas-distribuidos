// Lógica Frontend do MiniAWS

let currentTab = 'dashboard';
let activeBucketName = null;
let activeEC2ForPublish = null;
let publishModalMode = 'direct';
let allLogs = [];

// Elementos do DOM
const currentTabTitle = document.getElementById('current-tab-title');
const currentTabSubtitle = document.getElementById('current-tab-subtitle');

// Inicialização da Página
document.addEventListener('DOMContentLoaded', () => {
    setupTabNavigation();
    loadData();
    
    // Atualiza o Dashboard a cada 10 segundos em segundo plano
    setInterval(() => {
        if (currentTab === 'dashboard') {
            fetchDashboard();
        }
    }, 10000);
});

// Configuração do Menu de Navegação (SPA)
function setupTabNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = item.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
}

function switchTab(tabId) {
    currentTab = tabId;
    
    // Atualiza classes ativas no menu lateral
    document.querySelectorAll('.nav-item').forEach(item => {
        if (item.getAttribute('data-tab') === tabId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Mostra/Esconde as telas correspondentes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        if (pane.id === `tab-${tabId}`) {
            pane.classList.add('active');
        } else {
            pane.classList.remove('active');
        }
    });

    // Atualiza cabeçalho
    updateHeader(tabId);
    
    // Carrega dados específicos da aba
    loadData();
}

function updateHeader(tabId) {
    const headers = {
        'dashboard': {
            title: 'Dashboard',
            subtitle: 'Visão geral da sua infraestrutura simulada.'
        },
        'ec2': {
            title: 'Instâncias EC2',
            subtitle: 'Gerencie servidores virtuais locais para hospedar suas aplicações.'
        },
        's3': {
            title: 'S3 Object Storage',
            subtitle: 'Buckets locais e armazenamento de objetos estáticos.'
        },
        'lambda': {
            title: 'AWS Lambda (Eventos)',
            subtitle: 'Monitore execuções orientadas a eventos automáticos em arquivos.'
        },
        'logs': {
            title: 'Cloud Logs',
            subtitle: 'Histórico detalhado de auditoria de todos os serviços.'
        }
    };

    if (headers[tabId]) {
        currentTabTitle.textContent = headers[tabId].title;
        currentTabSubtitle.textContent = headers[tabId].subtitle;
    }
}

// Carregar dados com base na aba ativa
function loadData() {
    fetchDashboard();
    
    if (currentTab === 'ec2') {
        fetchInstances();
    } else if (currentTab === 's3') {
        fetchBuckets();
    } else if (currentTab === 'lambda') {
        fetchLambdaLogs();
    } else if (currentTab === 'logs') {
        fetchCloudLogs();
    }
}

// --- API: DASHBOARD ---
async function fetchDashboard() {
    try {
        const response = await fetch('/api/dashboard');
        const data = await response.json();
        
        document.getElementById('count-ec2').textContent = data.instances_count;
        document.getElementById('count-s3').textContent = data.buckets_count;
        document.getElementById('count-files').textContent = data.files_count;
        document.getElementById('count-lambda').textContent = data.lambda_count;

        // Buscar logs recentes para a timeline do painel principal
        const logsResponse = await fetch('/api/logs');
        const logs = await logsResponse.json();
        renderMiniLogs(logs.slice(0, 5)); // Apenas os 5 mais recentes
    } catch (error) {
        console.error('Erro ao buscar dados do Dashboard:', error);
    }
}

function renderMiniLogs(logs) {
    const container = document.getElementById('mini-logs-container');
    if (logs.length === 0) {
        container.innerHTML = '<p class="empty-state">Nenhum evento registrado ainda.</p>';
        return;
    }

    container.innerHTML = logs.map(log => {
        let serviceClass = `log-${log.service.toLowerCase()}`;
        let iconClass = 'fa-solid ';
        if (log.service === 'EC2') iconClass += 'fa-server text-success';
        else if (log.service === 'S3') iconClass += 'fa-box-open text-orange';
        else if (log.service === 'Lambda') iconClass += 'fa-bolt text-warning';

        return `
            <div class="mini-log-item ${serviceClass}">
                <i class="${iconClass}"></i>
                <div class="mini-log-desc" title="${log.event}">${log.event}</div>
                <div class="mini-log-meta">${log.time}</div>
            </div>
        `;
    }).join('');
}

// --- API: EC2 (INSTÂNCIAS) ---
async function fetchInstances() {
    try {
        const response = await fetch('/api/instances');
        const instances = await response.json();
        
        const listContainer = document.getElementById('ec2-instances-list');
        if (instances.length === 0) {
            listContainer.innerHTML = '<tr><td colspan="5" class="table-empty">Nenhuma instância criada. Crie uma acima!</td></tr>';
            return;
        }

        listContainer.innerHTML = instances.map(inst => {
            const statusClass = inst.status === 'running' ? 'running' : 'stopped';
            const statusLabel = inst.status === 'running' ? 'Executando' : 'Parado';
            
            // Site URL link
            const url = `/site/${inst.name}`;
            const linkDisabled = inst.status !== 'running' || !inst.has_site;
            const linkClass = linkDisabled ? 'site-url disabled' : 'site-url';
            
            // Botões específicos de estado
            const toggleButton = inst.status === 'running' 
                ? `<button class="btn btn-sm btn-outline text-danger" onclick="stopInstance('${inst.name}')"><i class="fa-solid fa-stop"></i> Parar</button>`
                : `<button class="btn btn-sm btn-outline text-success" onclick="startInstance('${inst.name}')"><i class="fa-solid fa-play"></i> Iniciar</button>`;

            return `
                <tr>
                    <td><strong>${inst.name}</strong></td>
                    <td>
                        <span class="status-badge ${statusClass}">
                            <span class="status-dot"></span>
                            ${statusLabel}
                        </span>
                    </td>
                    <td>${inst.created_at}</td>
                    <td>
                        ${inst.has_site 
                            ? `<a href="${url}" target="_blank" class="${linkClass}"><i class="fa-solid fa-globe"></i> Acessar Site</a>`
                            : `<span class="text-muted">Sem site publicado</span>`}
                    </td>
                    <td>
                        <div class="actions-cell">
                            ${toggleButton}
                            <button class="btn btn-sm btn-outline" onclick="openPublishModal('${inst.name}')"><i class="fa-solid fa-cloud-arrow-up"></i> Publicar HTML</button>
                            <button class="btn btn-sm btn-secondary text-danger" onclick="deleteInstance('${inst.name}')"><i class="fa-solid fa-trash-can"></i></button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Erro ao buscar instâncias EC2:', error);
    }
}

async function handleCreateEC2(event) {
    event.preventDefault();
    const input = document.getElementById('ec2-name');
    const name = input.value.trim();
    
    try {
        const response = await fetch('/api/instances', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        
        const data = await response.json();
        if (response.ok) {
            closeModal('modal-create-ec2');
            input.value = '';
            fetchInstances();
            fetchDashboard();
        } else {
            alert(data.error || 'Erro ao criar instância.');
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

async function startInstance(name) {
    try {
        const response = await fetch(`/api/instances/${name}/start`, { method: 'POST' });
        if (response.ok) {
            fetchInstances();
            fetchDashboard();
        }
    } catch (error) {
        console.error('Erro ao ligar instância:', error);
    }
}

async function stopInstance(name) {
    try {
        const response = await fetch(`/api/instances/${name}/stop`, { method: 'POST' });
        if (response.ok) {
            fetchInstances();
            fetchDashboard();
        }
    } catch (error) {
        console.error('Erro ao desligar instância:', error);
    }
}

async function deleteInstance(name) {
    if (!confirm(`Tem certeza que deseja excluir a instância EC2 "${name}"? Todos os arquivos hospedados serão apagados.`)) return;
    
    try {
        const response = await fetch(`/api/instances/${name}`, { method: 'DELETE' });
        if (response.ok) {
            fetchInstances();
            fetchDashboard();
        }
    } catch (error) {
        console.error('Erro ao excluir instância:', error);
    }
}

// --- API: S3 (STORAGE) ---
async function fetchBuckets() {
    try {
        const response = await fetch('/api/buckets');
        const buckets = await response.json();
        
        const container = document.getElementById('s3-buckets-list');
        if (buckets.length === 0) {
            container.innerHTML = '<div class="bucket-card empty">Nenhum bucket criado.</div>';
            document.getElementById('s3-files-panel').style.display = 'none';
            activeBucketName = null;
            return;
        }

        container.innerHTML = buckets.map(bucket => {
            const isActive = bucket.name === activeBucketName ? 'active' : '';
            return `
                <div class="bucket-card ${isActive}" onclick="selectBucket('${bucket.name}')">
                    <div class="bucket-info">
                        <i class="fa-solid fa-bucket"></i>
                        <div class="bucket-meta">
                            <h4>${bucket.name}</h4>
                            <p>${bucket.files_count} arquivos | Criado em ${bucket.created_at.split(' ')[0]}</p>
                        </div>
                    </div>
                    <button class="btn-delete-bucket" onclick="event.stopPropagation(); deleteBucket('${bucket.name}')" title="Excluir Bucket">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            `;
        }).join('');

        // Se tiver buckets e nenhum ativo, seleciona o primeiro
        if (buckets.length > 0 && !activeBucketName) {
            selectBucket(buckets[0].name);
        } else if (activeBucketName) {
            // Recarrega arquivos do bucket selecionado
            fetchBucketFiles(activeBucketName);
        }
    } catch (error) {
        console.error('Erro ao buscar buckets S3:', error);
    }
}

async function handleCreateS3(event) {
    event.preventDefault();
    const input = document.getElementById('s3-name');
    const name = input.value.trim();
    
    try {
        const response = await fetch('/api/buckets', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        
        const data = await response.json();
        if (response.ok) {
            closeModal('modal-create-s3');
            input.value = '';
            activeBucketName = data.name; // Seleciona o novo bucket criado
            fetchBuckets();
            fetchDashboard();
        } else {
            alert(data.error || 'Erro ao criar bucket.');
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

async function deleteBucket(name) {
    if (!confirm(`Tem certeza que deseja excluir o bucket S3 "${name}"? Todos os arquivos contidos nele serão excluídos permanentemente.`)) return;
    
    try {
        const response = await fetch(`/api/buckets/${name}`, { method: 'DELETE' });
        if (response.ok) {
            if (activeBucketName === name) activeBucketName = null;
            fetchBuckets();
            fetchDashboard();
        }
    } catch (error) {
        console.error('Erro ao excluir bucket:', error);
    }
}

function selectBucket(bucketName) {
    activeBucketName = bucketName;
    document.getElementById('current-bucket-name').textContent = bucketName;
    document.getElementById('s3-files-panel').style.display = 'block';
    
    // Atualiza a classe active nos cards de buckets do HTML
    document.querySelectorAll('.bucket-card').forEach(card => {
        if (card.querySelector('h4').textContent === bucketName) {
            card.classList.add('active');
        } else {
            card.classList.remove('active');
        }
    });

    fetchBucketFiles(bucketName);
}

async function fetchBucketFiles(bucketName) {
    try {
        const response = await fetch(`/api/buckets/${bucketName}/files`);
        const files = await response.json();
        
        const listContainer = document.getElementById('s3-files-list');
        if (files.length === 0) {
            listContainer.innerHTML = '<tr><td colspan="4" class="table-empty">Nenhum arquivo enviado para este bucket. Faça o upload acima!</td></tr>';
            return;
        }

        listContainer.innerHTML = files.map(file => {
            const kbSize = (file.size / 1024).toFixed(2);
            return `
                <tr>
                    <td><strong>${file.name}</strong></td>
                    <td>${kbSize} KB</td>
                    <td>${file.uploaded_at}</td>
                    <td>
                        <div class="actions-cell">
                            <a href="/api/buckets/${bucketName}/files/${file.name}" class="btn btn-sm btn-outline text-success" title="Download"><i class="fa-solid fa-download"></i></a>
                            <button class="btn btn-sm btn-secondary text-danger" onclick="deleteBucketFile('${bucketName}', '${file.name}')" title="Excluir"><i class="fa-solid fa-trash-can"></i></button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Erro ao buscar arquivos:', error);
    }
}

async function handleUploadS3(event) {
    event.preventDefault();
    if (!activeBucketName) return;

    const fileInput = document.getElementById('s3-file-input');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`/api/buckets/${activeBucketName}/files`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            closeModal('modal-upload-file');
            fileInput.value = '';
            fetchBucketFiles(activeBucketName);
            fetchBuckets(); // atualiza contadores dos cartões de buckets
            fetchDashboard();
        } else {
            const data = await response.json();
            alert(data.error || 'Erro ao realizar upload.');
        }
    } catch (error) {
        console.error('Erro no upload:', error);
    }
}

async function deleteBucketFile(bucketName, filename) {
    if (!confirm(`Excluir o arquivo "${filename}" do bucket "${bucketName}"?`)) return;
    
    try {
        const response = await fetch(`/api/buckets/${bucketName}/files/${filename}`, { method: 'DELETE' });
        if (response.ok) {
            fetchBucketFiles(bucketName);
            fetchBuckets();
            fetchDashboard();
        }
    } catch (error) {
        console.error('Erro ao excluir arquivo:', error);
    }
}

// --- API: AWS LAMBDA ---
async function fetchLambdaLogs() {
    try {
        const response = await fetch('/api/logs');
        const logs = await response.json();
        
        // Filtra apenas eventos do AWS Lambda
        const lambdaLogs = logs.filter(log => log.service === 'Lambda');
        
        const listContainer = document.getElementById('lambda-executions-list');
        if (lambdaLogs.length === 0) {
            listContainer.innerHTML = '<tr><td colspan="3" class="table-empty">Nenhum evento registrado ainda. Envie arquivos no S3 para rodar a Lambda!</td></tr>';
            return;
        }

        listContainer.innerHTML = lambdaLogs.map(log => `
            <tr>
                <td><strong>${log.date} ${log.time}</strong></td>
                <td><span class="status-badge running"><span class="status-dot"></span> Sucesso</span></td>
                <td><code>${log.event}</code></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Erro ao buscar logs da Lambda:', error);
    }
}

// --- API: CLOUD LOGS ---
async function fetchCloudLogs() {
    try {
        const response = await fetch('/api/logs');
        allLogs = await response.json();
        renderLogs(allLogs);
    } catch (error) {
        console.error('Erro ao buscar logs gerais:', error);
    }
}

function renderLogs(logs) {
    const listContainer = document.getElementById('cloud-logs-list');
    if (logs.length === 0) {
        listContainer.innerHTML = '<tr><td colspan="4" class="table-empty">Nenhum evento registrado.</td></tr>';
        return;
    }

    listContainer.innerHTML = logs.map(log => {
        let badgeClass = `log-service-badge ${log.service.toLowerCase()}`;
        return `
            <tr>
                <td>${log.date}</td>
                <td>${log.time}</td>
                <td><span class="${badgeClass}">${log.service}</span></td>
                <td>${log.event}</td>
            </tr>
        `;
    }).join('');
}

function filterLogs(service) {
    // Altera classe active nos botões
    const buttons = document.querySelectorAll('#tab-logs .filter-controls button');
    buttons.forEach(btn => {
        if (btn.textContent.trim().toLowerCase() === service.toLowerCase() || (service === 'all' && btn.textContent.trim() === 'Todos')) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    if (service === 'all') {
        renderLogs(allLogs);
    } else {
        const filtered = allLogs.filter(log => log.service.toLowerCase() === service.toLowerCase());
        renderLogs(filtered);
    }
}

// --- PUBLICAÇÃO DE SITE (MODAIS MULTI-ABA) ---
function openPublishModal(instanceName) {
    activeEC2ForPublish = instanceName;
    document.getElementById('publish-target-ec2').textContent = instanceName;
    openModal('modal-publish-site');
    switchModalPublishTab('direct');
}

function switchModalPublishTab(mode) {
    publishModalMode = mode;
    const directForm = document.getElementById('form-publish-direct');
    const s3Form = document.getElementById('form-publish-s3');
    const tabs = document.querySelectorAll('.modal-tabs .modal-tab-btn');
    
    if (mode === 'direct') {
        directForm.style.display = 'block';
        s3Form.style.display = 'none';
        tabs[0].classList.add('active');
        tabs[1].classList.remove('active');
    } else {
        directForm.style.display = 'none';
        s3Form.style.display = 'block';
        tabs[0].classList.remove('active');
        tabs[1].classList.add('active');
        loadBucketsForPublishDropdown();
    }
}

async function loadBucketsForPublishDropdown() {
    try {
        const response = await fetch('/api/buckets');
        const buckets = await response.json();
        const select = document.getElementById('publish-s3-bucket');
        
        select.innerHTML = '<option value="">Selecione um bucket...</option>' + 
            buckets.map(b => `<option value="${b.name}">${b.name}</option>`).join('');
            
        document.getElementById('publish-s3-file').innerHTML = '<option value="">Selecione primeiro o bucket...</option>';
    } catch (error) {
        console.error(error);
    }
}

async function loadFilesForPublishDropdown(bucketName) {
    if (!bucketName) {
        document.getElementById('publish-s3-file').innerHTML = '<option value="">Selecione primeiro o bucket...</option>';
        return;
    }
    
    try {
        const response = await fetch(`/api/buckets/${bucketName}/files`);
        const files = await response.json();
        const select = document.getElementById('publish-s3-file');
        
        // Filtra apenas arquivos HTML para o deploy de site
        const htmlFiles = files.filter(f => f.name.endsWith('.html'));
        
        if (htmlFiles.length === 0) {
            select.innerHTML = '<option value="">Nenhum arquivo HTML (.html) encontrado.</option>';
            return;
        }

        select.innerHTML = '<option value="">Selecione o arquivo HTML...</option>' + 
            htmlFiles.map(f => `<option value="${f.name}">${f.name}</option>`).join('');
    } catch (error) {
        console.error(error);
    }
}

async function handlePublishDirect(event) {
    event.preventDefault();
    if (!activeEC2ForPublish) return;

    const fileInput = document.getElementById('publish-direct-file');
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`/api/instances/${activeEC2ForPublish}/publish`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            closeModal('modal-publish-site');
            fileInput.value = '';
            fetchInstances();
            fetchDashboard();
        } else {
            const data = await response.json();
            alert(data.error || 'Erro ao publicar site.');
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

async function handlePublishS3(event) {
    event.preventDefault();
    if (!activeEC2ForPublish) return;

    const bucket = document.getElementById('publish-s3-bucket').value;
    const filename = document.getElementById('publish-s3-file').value;

    if (!bucket || !filename) {
        alert('Selecione o bucket e o arquivo.');
        return;
    }

    try {
        const response = await fetch(`/api/instances/${activeEC2ForPublish}/publish`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bucket, filename })
        });
        
        if (response.ok) {
            closeModal('modal-publish-site');
            fetchInstances();
            fetchDashboard();
        } else {
            const data = await response.json();
            alert(data.error || 'Erro ao publicar do S3.');
        }
    } catch (error) {
        console.error('Erro:', error);
    }
}

// --- UTILITÁRIOS DE MODAL ---
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}
