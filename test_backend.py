import os
import json
import shutil
import unittest
from datetime import datetime
from io import BytesIO

# Importa o app Flask a ser testado
from app import app, INSTANCES_JSON, LOGS_JSON, INSTANCES_DIR, STORAGE_DIR

class MiniAWSTestCase(unittest.TestCase):
    def setUp(self):
        # Configura o cliente de teste do Flask
        self.app = app.test_client()
        self.app.testing = True

        # Fazer backup dos arquivos e pastas existentes, se houver
        self.backup_files = {}
        for path in [INSTANCES_JSON, LOGS_JSON]:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.backup_files[path] = f.read()
            else:
                self.backup_files[path] = None

        self.backup_dirs = {}
        for d in [INSTANCES_DIR, STORAGE_DIR]:
            if os.path.exists(d):
                backup_name = d + "_backup_test"
                if os.path.exists(backup_name):
                    shutil.rmtree(backup_name)
                shutil.copytree(d, backup_name)
                self.backup_dirs[d] = backup_name
            else:
                self.backup_dirs[d] = None

        # Limpar os ambientes para um teste limpo
        if os.path.exists(INSTANCES_DIR):
            shutil.rmtree(INSTANCES_DIR)
        os.makedirs(INSTANCES_DIR, exist_ok=True)

        if os.path.exists(STORAGE_DIR):
            shutil.rmtree(STORAGE_DIR)
        os.makedirs(STORAGE_DIR, exist_ok=True)

        with open(INSTANCES_JSON, 'w', encoding='utf-8') as f:
            f.write(json.dumps({}))
        with open(LOGS_JSON, 'w', encoding='utf-8') as f:
            f.write(json.dumps([]))

    def tearDown(self):
        # Restaurar backups
        for path, content in self.backup_files.items():
            if content is not None:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
            elif os.path.exists(path):
                os.remove(path)

        for d, backup_name in self.backup_dirs.items():
            if os.path.exists(d):
                shutil.rmtree(d)
            if backup_name is not None and os.path.exists(backup_name):
                shutil.copytree(backup_name, d)
                shutil.rmtree(backup_name)

    def test_dashboard_initial(self):
        response = self.app.get('/api/dashboard')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['instances_count'], 0)
        self.assertEqual(data['buckets_count'], 0)
        self.assertEqual(data['files_count'], 0)
        self.assertEqual(data['lambda_count'], 0)

    def test_create_and_delete_instance(self):
        # Criação
        response = self.app.post('/api/instances', json={'name': 'test-vm-01'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'test-vm-01')
        self.assertEqual(data['status'], 'stopped')
        self.assertFalse(data['has_site'])
        self.assertTrue(os.path.exists(os.path.join(INSTANCES_DIR, 'test-vm-01')))

        # Verificação na lista
        response = self.app.get('/api/instances')
        self.assertEqual(response.status_code, 200)
        instances_list = json.loads(response.data)
        self.assertEqual(len(instances_list), 1)
        self.assertEqual(instances_list[0]['name'], 'test-vm-01')

        # Exclusão
        response = self.app.delete('/api/instances/test-vm-01')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(os.path.exists(os.path.join(INSTANCES_DIR, 'test-vm-01')))

        # Verificar se removeu da lista
        response = self.app.get('/api/instances')
        instances_list = json.loads(response.data)
        self.assertEqual(len(instances_list), 0)

    def test_instance_start_stop(self):
        # Criar
        self.app.post('/api/instances', json={'name': 'test-vm-02'})

        # Iniciar
        response = self.app.post('/api/instances/test-vm-02/start')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'running')

        # Parar
        response = self.app.post('/api/instances/test-vm-02/stop')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'stopped')

    def test_s3_buckets_and_files(self):
        # Criar bucket
        response = self.app.post('/api/buckets', json={'name': 'test-bucket'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'test-bucket')
        self.assertEqual(data['files_count'], 0)
        self.assertTrue(os.path.exists(os.path.join(STORAGE_DIR, 'test-bucket')))

        # Listar buckets
        response = self.app.get('/api/buckets')
        self.assertEqual(response.status_code, 200)
        buckets = json.loads(response.data)
        self.assertEqual(len(buckets), 1)
        self.assertEqual(buckets[0]['name'], 'test-bucket')

        # Upload de arquivo
        file_data = b"<html><body>Hello Test</body></html>"
        response = self.app.post(
            '/api/buckets/test-bucket/files',
            data={'file': (BytesIO(file_data), 'test.html')},
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 201)
        res_file = json.loads(response.data)
        self.assertEqual(res_file['name'], 'test.html')
        self.assertEqual(res_file['size'], len(file_data))

        # Listar arquivos no bucket
        response = self.app.get('/api/buckets/test-bucket/files')
        self.assertEqual(response.status_code, 200)
        files = json.loads(response.data)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['name'], 'test.html')

        # Verificar se disparou a Lambda (evento logado)
        response = self.app.get('/api/dashboard')
        data = json.loads(response.data)
        self.assertEqual(data['lambda_count'], 1)  # Lambda foi executada pelo upload

    def test_publish_site_and_serve(self):
        # 1. Criar EC2
        self.app.post('/api/instances', json={'name': 'web-instance'})

        # 2. Criar Bucket S3 e fazer upload do HTML
        self.app.post('/api/buckets', json={'name': 'assets-bucket'})
        file_content = b"<h1>My Simulated Website</h1>"
        self.app.post(
            '/api/buckets/assets-bucket/files',
            data={'file': (BytesIO(file_content), 'index.html')},
            content_type='multipart/form-data'
        )

        # 3. Publicar no EC2 importando do S3
        response = self.app.post('/api/instances/web-instance/publish', json={
            'bucket': 'assets-bucket',
            'filename': 'index.html'
        })
        self.assertEqual(response.status_code, 200)

        # 4. Servir o site - Caso 1: Instância Parada (deve dar erro 503)
        with self.app.get('/site/web-instance') as response:
            self.assertEqual(response.status_code, 503)
            self.assertIn(b"503 Service Unavailable", response.data)

        # 5. Iniciar Instância e Servir o site - Caso 2: Instância Rodando (deve dar 200 e retornar HTML)
        self.app.post('/api/instances/web-instance/start')
        with self.app.get('/site/web-instance') as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"My Simulated Website", response.data)

if __name__ == '__main__':
    unittest.main()
