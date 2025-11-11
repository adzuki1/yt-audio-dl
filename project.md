Venv:

    1. mover para o diretório do projeto
    cd /path/
    
    2. criar o ambiente virtual
    python3 -m venv venv

    3. ativar o ambiente virtual
    source venv/bin/activate 
    
    4. ao final do projeto, desativar venv
    deactivate


Instalação das Dependências:

    sudo apt-get install ffmpeg
    
    pip install -r requirements.txt


Código:

    1. ler e armazenar os dados do arquivo xlsx - ok

    2. download dos vídeos através da queue - ok

    3. criar pastas e adicionar arquivos - ok

    4. cortar o audio no intervalo almejado


Log:
    download dos arquivos em fila vêm corrompidos - ok


Trim audio:

intervalo