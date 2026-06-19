import os
import json
import shutil
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, abort

app = Flask(__name__, static_folder='static', static_url_path='')

INSTANCES_DIR = 'instances'
STORAGE_DIR = 'storage'
INSTANCES_JSON = 'instances.json'
LOGS_JSON = 'logs.json'

# Inicializa as pastas básicas
os.makedirs(INSTANCES_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)

def load_json(filepath, default_value):
    if not os.path.exists(filepath):
        save_json(filepath, default_value)
        return default_value
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default_value

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def log_event(service, event_description):
    logs = load_json(LOGS_JSON, [])
    now = datetime.now()
    log_entry = {
        'id': len(logs) + 1,
        'date': now.strftime("%d/%m/%Y"),
        'time': now.strftime("%H:%M:%S"),
        'service': service,
        'event': event_description
    }
    logs.insert(0, log_entry)  # Insere no início para o mais recente ficar em cima
    save_json(LOGS_JSON, logs)
    return log_entry

# Rota para servir a interface do frontend
@app.route('/')
def index():
    return app.send_static_file('index.html')

# API Dashboard
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    instances = load_json(INSTANCES_JSON, {})
    
    # Contar buckets e arquivos no S3
    buckets = []
    if os.path.exists(STORAGE_DIR):
        buckets = [d for d in os.listdir(STORAGE_DIR) if os.path.isdir(os.path.join(STORAGE_DIR, d))]
    
    total_files = 0
    for b in buckets:
        bucket_path = os.path.join(STORAGE_DIR, b)
        if os.path.exists(bucket_path):
            files = [f for f in os.listdir(bucket_path) if os.path.isfile(os.path.join(bucket_path, f))]
            total_files += len(files)
            
    logs = load_json(LOGS_JSON, [])
    lambda_count = sum(1 for log in logs if log['service'] == 'Lambda')
    
    return jsonify({
        'instances_count': len(instances),
        'buckets_count': len(buckets),
        'files_count': total_files,
        'lambda_count': lambda_count
    })

# API Logs
@app.route('/api/logs', methods=['GET'])
def get_logs():
    logs = load_json(LOGS_JSON, [])
    return jsonify(logs)

# API EC2 (Instâncias)
@app.route('/api/instances', methods=['GET'])
def list_instances():
    instances = load_json(INSTANCES_JSON, {})
    # Retorna como lista para facilitar o frontend
    return jsonify(list(instances.values()))

@app.route('/api/instances', methods=['POST'])
def create_instance():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'O nome da instância é obrigatório.'}), 400
        
    # Validar nome (apenas caracteres seguros)
    name = "".join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
    if not name:
        return jsonify({'error': 'Nome de instância inválido.'}), 400
        
    instances = load_json(INSTANCES_JSON, {})
    if name in instances:
        return jsonify({'error': f'Instância "{name}" já existe.'}), 400
        
    # Criar pasta física
    instance_path = os.path.join(INSTANCES_DIR, name)
    os.makedirs(instance_path, exist_ok=True)
    
    # Adicionar metadados
    instances[name] = {
        'name': name,
        'status': 'stopped',
        'created_at': datetime.now().strftime("%d/%m/%Y %H:%M"),
        'has_site': False
    }
    save_json(INSTANCES_JSON, instances)
    
    log_event('EC2', f'Instância "{name}" criada com sucesso.')
    
    return jsonify(instances[name]), 201

@app.route('/api/instances/<name>', methods=['DELETE'])
def delete_instance(name):
    instances = load_json(INSTANCES_JSON, {})
    if name not in instances:
        return jsonify({'error': 'Instância não encontrada.'}), 404
        
    # Remover pasta física
    instance_path = os.path.join(INSTANCES_DIR, name)
    if os.path.exists(instance_path):
        shutil.rmtree(instance_path)
        
    del instances[name]
    save_json(INSTANCES_JSON, instances)
    
    log_event('EC2', f'Instância "{name}" excluída.')
    
    return jsonify({'message': f'Instância {name} excluída.'})

@app.route('/api/instances/<name>/start', methods=['POST'])
def start_instance(name):
    instances = load_json(INSTANCES_JSON, {})
    if name not in instances:
        return jsonify({'error': 'Instância não encontrada.'}), 404
        
    instances[name]['status'] = 'running'
    save_json(INSTANCES_JSON, instances)
    
    log_event('EC2', f'Instância "{name}" iniciada.')
    
    return jsonify(instances[name])

@app.route('/api/instances/<name>/stop', methods=['POST'])
def stop_instance(name):
    instances = load_json(INSTANCES_JSON, {})
    if name not in instances:
        return jsonify({'error': 'Instância não encontrada.'}), 404
        
    instances[name]['status'] = 'stopped'
    save_json(INSTANCES_JSON, instances)
    
    log_event('EC2', f'Instância "{name}" interrompida.')
    
    return jsonify(instances[name])

@app.route('/api/instances/<name>/publish', methods=['POST'])
def publish_to_instance(name):
    instances = load_json(INSTANCES_JSON, {})
    if name not in instances:
        return jsonify({'error': 'Instância não encontrada.'}), 404
        
    # Aceita ou upload direto do arquivo HTML, ou seleção de arquivo do S3
    if 'file' in request.files:
        file = request.files['file']
        if not file.filename.endswith('.html'):
            return jsonify({'error': 'Apenas arquivos HTML (.html) são permitidos para publicação.'}), 400
            
        instance_path = os.path.join(INSTANCES_DIR, name)
        os.makedirs(instance_path, exist_ok=True)
        file.save(os.path.join(instance_path, 'index.html'))
        
        instances[name]['has_site'] = True
        save_json(INSTANCES_JSON, instances)
        
        log_event('EC2', f'Site publicado via upload direto na instância "{name}".')
        return jsonify({'message': 'Site publicado com sucesso.'})
        
    else:
        # Tenta pegar JSON para publicação a partir do S3
        data = request.get_json() or {}
        bucket = data.get('bucket')
        filename = data.get('filename')
        
        if not bucket or not filename:
            return jsonify({'error': 'Nenhum arquivo enviado ou bucket/arquivo não especificados.'}), 400
            
        source_path = os.path.join(STORAGE_DIR, bucket, filename)
        if not os.path.exists(source_path):
            return jsonify({'error': 'Arquivo de origem no S3 não encontrado.'}), 404
            
        instance_path = os.path.join(INSTANCES_DIR, name)
        os.makedirs(instance_path, exist_ok=True)
        shutil.copy(source_path, os.path.join(instance_path, 'index.html'))
        
        instances[name]['has_site'] = True
        save_json(INSTANCES_JSON, instances)
        
        log_event('EC2', f'Site publicado na instância "{name}" a partir do S3 ({bucket}/{filename}).')
        return jsonify({'message': f'Site publicado com sucesso na instância {name}.'})

# API S3 (Buckets & Arquivos)
@app.route('/api/buckets', methods=['GET'])
def list_buckets():
    buckets = []
    if os.path.exists(STORAGE_DIR):
        for item in os.listdir(STORAGE_DIR):
            item_path = os.path.join(STORAGE_DIR, item)
            if os.path.isdir(item_path):
                # Conta a quantidade de arquivos no bucket
                files_count = len([f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))])
                buckets.append({
                    'name': item,
                    'files_count': files_count,
                    'created_at': datetime.fromtimestamp(os.path.getctime(item_path)).strftime("%d/%m/%Y %H:%M")
                })
    return jsonify(buckets)

@app.route('/api/buckets', methods=['POST'])
def create_bucket():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'O nome do bucket é obrigatório.'}), 400
        
    # Validar nome (S3 compatível simples: minúsculas, números, hifens)
    name = name.lower()
    name = "".join(c for c in name if c.isalnum() or c == '-').strip()
    if not name:
        return jsonify({'error': 'Nome do bucket inválido.'}), 400
        
    bucket_path = os.path.join(STORAGE_DIR, name)
    if os.path.exists(bucket_path):
        return jsonify({'error': f'Bucket "{name}" já existe.'}), 400
        
    os.makedirs(bucket_path, exist_ok=True)
    
    log_event('S3', f'Bucket "{name}" criado.')
    
    return jsonify({
        'name': name,
        'files_count': 0,
        'created_at': datetime.now().strftime("%d/%m/%Y %H:%M")
    }), 201

@app.route('/api/buckets/<name>', methods=['DELETE'])
def delete_bucket(name):
    bucket_path = os.path.join(STORAGE_DIR, name)
    if not os.path.exists(bucket_path) or not os.path.isdir(bucket_path):
        return jsonify({'error': 'Bucket não encontrado.'}), 404
        
    shutil.rmtree(bucket_path)
    log_event('S3', f'Bucket "{name}" excluído.')
    return jsonify({'message': f'Bucket {name} excluído.'})

@app.route('/api/buckets/<bucket_name>/files', methods=['GET'])
def list_bucket_files(bucket_name):
    bucket_path = os.path.join(STORAGE_DIR, bucket_name)
    if not os.path.exists(bucket_path) or not os.path.isdir(bucket_path):
        return jsonify({'error': 'Bucket não encontrado.'}), 404
        
    files = []
    for item in os.listdir(bucket_path):
        item_path = os.path.join(bucket_path, item)
        if os.path.isfile(item_path):
            stat = os.stat(item_path)
            files.append({
                'name': item,
                'size': stat.st_size,
                'uploaded_at': datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M:%S")
            })
    return jsonify(files)

@app.route('/api/buckets/<bucket_name>/files', methods=['POST'])
def upload_file(bucket_name):
    bucket_path = os.path.join(STORAGE_DIR, bucket_name)
    if not os.path.exists(bucket_path) or not os.path.isdir(bucket_path):
        return jsonify({'error': 'Bucket não encontrado.'}), 404
        
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
        
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'Nome de arquivo inválido.'}), 400
        
    # Salvar arquivo
    filename = file.filename
    file.save(os.path.join(bucket_path, filename))
    
    # Log do evento S3
    log_event('S3', f'Arquivo "{filename}" enviado para o bucket "{bucket_name}".')
    
    # --- SIMULAÇÃO AWS LAMBDA ---
    # O upload no S3 dispara automaticamente a execução da Lambda
    log_event('Lambda', f'Função executada automaticamente em resposta ao upload de "{filename}" no bucket "{bucket_name}".')
    
    return jsonify({
        'name': filename,
        'size': os.path.getsize(os.path.join(bucket_path, filename)),
        'uploaded_at': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }), 201

@app.route('/api/buckets/<bucket_name>/files/<filename>', methods=['GET'])
def download_file(bucket_name, filename):
    bucket_path = os.path.join(STORAGE_DIR, bucket_name)
    if not os.path.exists(os.path.join(bucket_path, filename)):
        abort(404)
    return send_from_directory(bucket_path, filename, as_attachment=True)

@app.route('/api/buckets/<bucket_name>/files/<filename>', methods=['DELETE'])
def delete_file(bucket_name, filename):
    file_path = os.path.join(STORAGE_DIR, bucket_name, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'Arquivo não encontrado.'}), 404
        
    os.remove(file_path)
    log_event('S3', f'Arquivo "{filename}" excluído do bucket "{bucket_name}".')
    return jsonify({'message': f'Arquivo {filename} excluído.'})

# Servindo o site simulado da instância EC2
@app.route('/site/<instance_name>')
def serve_instance_site(instance_name):
    instances = load_json(INSTANCES_JSON, {})
    if instance_name not in instances:
        return """
        <html>
            <head>
                <title>Erro 404 - MiniAWS</title>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; background-color: #1e1e24; color: #fff; text-align: center; padding-top: 100px; }
                    .container { max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.05); padding: 40px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
                    h1 { color: #ff5252; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Instância Não Encontrada</h1>
                    <p>A instância EC2 especificada <strong>""" + instance_name + """</strong> não existe no simulador MiniAWS.</p>
                </div>
            </body>
        </html>
        """, 404

    instance = instances[instance_name]
    
    if instance['status'] != 'running':
        return """
        <html>
            <head>
                <title>Erro 503 - Instância Interrompida</title>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; background-color: #1a1a1e; color: #a0a0ab; text-align: center; padding-top: 100px; }
                    .container { max-width: 600px; margin: 0 auto; background: rgba(239, 68, 68, 0.05); padding: 40px; border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.2); box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
                    h1 { color: #ef4444; margin-bottom: 10px; }
                    p { font-size: 1.1rem; line-height: 1.6; }
                    .badge { display: inline-block; padding: 6px 12px; background: rgba(239, 68, 68, 0.2); color: #fca5a5; border-radius: 20px; font-size: 0.85rem; font-weight: 600; margin-top: 15px; text-transform: uppercase; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>503 Service Unavailable</h1>
                    <p>Não é possível acessar o site porque a instância EC2 <strong>""" + instance_name + """</strong> está desligada (<strong>STOPPED</strong>).</p>
                    <div class="badge">Estado: Stopped</div>
                </div>
            </body>
        </html>
        """, 503

    index_html_path = os.path.join(INSTANCES_DIR, instance_name, 'index.html')
    if not os.path.exists(index_html_path):
        return """
        <html>
            <head>
                <title>Erro 404 - Sem Conteúdo</title>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; background-color: #1e1e24; color: #fff; text-align: center; padding-top: 100px; }
                    .container { max-width: 600px; margin: 0 auto; background: rgba(255,255,255,0.05); padding: 40px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }
                    h1 { color: #ffb300; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Nenhum site publicado</h1>
                    <p>A instância <strong>""" + instance_name + """</strong> está rodando, mas nenhum arquivo HTML (index.html) foi publicado nela ainda.</p>
                </div>
            </body>
        </html>
        """, 404

    # Serve o arquivo index.html da instância
    return send_from_directory(os.path.join(INSTANCES_DIR, instance_name), 'index.html')

if __name__ == '__main__':
    # Cria os arquivos json iniciais caso não existam
    load_json(INSTANCES_JSON, {})
    load_json(LOGS_JSON, [])
    
    print("Iniciando o servidor Flask MiniAWS na porta 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
