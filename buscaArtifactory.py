import os
import requests
from tqdm import tqdm
import argparse
import time
import sys

# Aumentar o limite de recursão
sys.setrecursionlimit(3000)  # O padrão é geralmente 1000, aumente conforme necessário

# Cria uma sessão para reutilizar as conexões TCP
sessao = requests.Session()

def listar_repositorios_e_salvar(url_base, username, api_key):
    url = f"{url_base}/api/repositories"
    headers = {'Content-Type': 'application/json'}
    response = requests.get(url, auth=(username, api_key), headers=headers, timeout=10)

    if response.status_code == 200:
        try:
            repositorios = [repo['key'] for repo in response.json()]
            with open("lista_de_repositorios.txt", 'w') as arquivo:
                for repo in repositorios:
                    arquivo.write(repo + '\n')
            print("Lista de repositórios salva em lista_de_repositorios.txt")
        except ValueError:
            print("Resposta inválida (não é JSON ou está vazio):", response.text)
    else:
        print('Falha na requisição:', response.status_code, response.text)

def listar_arquivos_recursivamente(url_base, repo, path, username, api_key, extensoes=None, profundidade_atual=0, max_profundidade=100000):
    if profundidade_atual > max_profundidade:
        print("Profundidade máxima alcançada:", path)
        return []

    url_completa = f"{url_base}/api/storage/{repo}/{path.lstrip('/')}"
    headers = {'Content-Type': 'application/json'}
    arquivos = []

    with sessao.get(url_completa, auth=(username, api_key), headers=headers, timeout=10) as response:
        if response.status_code == 200:
            dados = response.json()
            if 'children' in dados:
                for item in dados['children']:
                    caminho_completo = os.path.join(path, item['uri'].lstrip('/'))
                    if item['folder']:
                        arquivos += listar_arquivos_recursivamente(url_base, repo, caminho_completo, username, api_key, extensoes, profundidade_atual + 1, max_profundidade)
                    elif not extensoes or any(caminho_completo.endswith(ext) for ext in extensoes):
                        arquivos.append(caminho_completo)
        else:
            print('Falha na requisição:', response.status_code, response.text)
    return arquivos

def baixar_arquivos_do_repositorio(url_base, repo, lista_arquivos, username, api_key, diretorio_base, delay=1):
    diretorio_repositorio = os.path.join(diretorio_base, repo)
    if not os.path.exists(diretorio_repositorio):
        os.makedirs(diretorio_repositorio)

    with tqdm(total=len(lista_arquivos), desc="Baixando arquivos", unit="file") as pbar:
        for arquivo in lista_arquivos:
            nome_arquivo = os.path.basename(arquivo)
            url_arquivo = f"{url_base}/{repo}/{arquivo.lstrip('/')}"
            path_destino = os.path.join(diretorio_repositorio, nome_arquivo)
            
            try:
                with sessao.get(url_arquivo, auth=(username, api_key), stream=True, timeout=10) as response:
                    if response.status_code == 200:
                        with open(path_destino, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                    else:
                        print(f"Falha ao baixar {arquivo}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Erro ao tentar baixar {arquivo}: {e}")
            
            pbar.update(1)
            time.sleep(delay)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script para interagir com o Artifactory.')
    parser.add_argument('--repo', type=str, help='Nome do repositório para listar ou baixar arquivos.')
    parser.add_argument('--extensoes', nargs='+', help='Lista de extensões de arquivo para filtrar (ex: --extensoes .txt .jpg)')
    args = parser.parse_args()

    url_base = "http://artifactory.santanderbr.corp/artifactory"  # Substitua pela URL do seu Artifactory
    username = 't798552'  # Substitua pelo seu usuário
    api_key = 'AKCpBrv6sB4SSRh1gT2E5UeyvNoi9j3kcdZpoRjk3aj5BLGBwLMiLxu4vR5reWzP7dxzf69v5'  # Substitua pela sua chave API

    if args.repo:
        # Listar e baixar arquivos do repositório especificado de forma recursiva
        arquivos = listar_arquivos_recursivamente(url_base, args.repo, '', username, api_key, args.extensoes or [])
        baixar_arquivos_do_repositorio(url_base, args.repo, arquivos, username, api_key, os.getcwd(), delay=30)
    else:
        # Listar todos os repositórios e salvar em um arquivo
        listar_repositorios_e_salvar(url_base, username, api_key)

