# Projeto_Artifactory
Projeto destinado a baixar os arquivos dos repositórios do Artifactory

## Configuração

Para que o script funcione precisa informar a url do seu Artifactory, seu usuário e sua api_key
```python
    url_base = "http://artifactory.<URL>/artifactory"  # Substitua pela URL do seu Artifactory
    username = '<usuário>'  # Substitua pelo seu usuário
    api_key = '<key>'  # Substitua pela sua chave API
```


## Utilização

Executar o script sem nenhum parâmetro fara com que o script retorne uma lista com todos os repositórios do seu Artifactory
```shell
./busca_Artifactory.py
```

Executar com o parâmetro --repo <repositorio> fará com que o script baixe todos os arquivos desse repositório
```shell
./buscar_Artifactory.py --repo exemplo_repo
```

Executar com o parâmetro --repo e com o --extensoes <txt,conf> fará com que o script filtre e baixe apenas os arquivos com as extensões passadas via parâmetro
```shell
./busca_Artifactory.py --repo exemplo_repo --extensoes txt,conf
```
