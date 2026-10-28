# OrganizadorDeArquivos
Um programa para Windows, feito em Python, que arruma pastas bagunçadas separando os arquivos em subpastas por tipo ou por data.

Fiz esse projeto como solução pessoal e utilizei para trabalho acadêmico, não sou programador profissional então o código é simples e está todo em um único arquivo.

# O que ele faz
Organiza os arquivos por tipo (PDFs, imagens, vídeos, músicas, documentos, compactados, instaladores e outros) ou por data (dia, mês ou ano).
Mostra uma prévia do que vai acontecer antes de mover qualquer arquivo, e você pode desmarcar o que não quiser mover.
Quando já existe um arquivo com o mesmo nome no destino, abre uma tela de conflito para você escolher entre ignorar, substituir ou renomear. Nas imagens, aparece uma miniatura para ajudar na decisão.
Os arquivos substituídos vão para a lixeira, e não são apagados de vez.
Pode incluir os arquivos das subpastas.
Pode separar os arquivos pesados (maiores que 300 MB) em pastas próprias.
Pode separar os documentos em Word, Excel, PowerPoint e arquivos de texto.
Permite desfazer a última organização.
Permite limpar as pastas vazias.

# O que você precisa antes
Windows: Desenvolvi e testei no Windows 11, o programa usa uma biblioteca que só funciona no Windows, então não serve para Mac ou Linux.

Python 3: Usei a versão 3.14.7, baixada em https://www.python.org/downloads/ e, na instalação, marque a opção "Add python.exe to PATH". Sem isso, os comandos abaixo não funcionam no cmd.

O Tkinter (a parte das janelas) já vem junto com o Python, então não precisa instalar.

# Dependências

O programa usa três bibliotecas que não vêm com o Python:

Pillow (versão que usei: 12.3.0): mostra as miniaturas das imagens e desenha o ícone da janela.

pywinstyles (versão que usei: 1.8): deixa a barra de título escura, combinando com o visual do programa.

Send2Trash (versão que usei: 2.1.0): manda os arquivos substituídos para a lixeira.

# Como instalar

Abra o cmd e rode:

pip install pillow pywinstyles send2trash

(Isso instala as três de uma vez, na versão mais recente de cada uma)

# Como rodar

Baixe o arquivo organizador.py.

No cmd, entre na pasta onde o arquivo está. Por exemplo, se ele estiver em Downloads:
   cd %USERPROFILE%\Downloads
   
Rode o programa:
   python organizador.py
   
# Se algo não funcionar

ModuleNotFoundError (por exemplo, "No module named PIL"): falta instalar alguma biblioteca. Rode de novo o comando de instalação.

A janela abre, mas a barra de título não fica escura: a pywinstyles não conseguiu aplicar o tema. É só visual, e o programa continua funcionando normalmente.

O Python não é reconhecido no cmd: reinstale o Python marcando a opção "Add python.exe to PATH".

Erro falando de tkinter: reinstale o Python e deixe marcada a opção "tcl/tk and IDLE".

# Avisos importantes!

O desfazer só vale para a última organização e enquanto o programa estiver aberto. Se você fechar o programa, ele esquece o que foi feito.

Antes de organizar uma pasta importante, confira a prévia com calma.

Cuidado ao selecionar a opção incluir subpastas, se por exemplo existir um programa com dependências em pastas separadas, eles serão incluidos na organização e possivelmente deixar o programa inultilizavel
