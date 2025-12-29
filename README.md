📄 PyDF Toolkit - Windows PDF Automation
Uma suíte de ferramentas leve, local e automatizada para manipulação de PDFs, integrada diretamente ao Menu de Contexto do Windows.

🚀 Sobre o Projeto
O PyDF Toolkit foi desenvolvido para resolver a ineficiência de manipular documentos PDF no dia a dia corporativo. Ao invés de depender de softwares pesados (Adobe) ou ferramentas online inseguras (iLovePDF), este projeto oferece uma solução nativa, rápida e privada.

O grande diferencial é a integração via Shell (Batch Scripting). O utilizador executa scripts Python complexos simplesmente clicando com o botão direito no arquivo ("Enviar Para"), sem precisar abrir terminais ou interfaces complexas.

🛠️ Funcionalidades
1. Fatiar (Split)
Divide um arquivo PDF em páginas individuais instantaneamente.

Automação: Cria pastas organizadas automaticamente.

Organização: Nomenclatura sequencial (01, 02, 03...).

<div align="center"> <img src="dividir.png" width="30%" alt="Demonstração" /> <img src="dividir%202.png" width="30%" alt="Console" /> <img src="dividir%203.png" width="30%" alt="Resultado" /> <p><em>Fluxo: Seleção > Processamento > Resultado na Pasta</em></p> </div>

2. Fatiar Inteligente (Smart Split)
Utiliza Regex e Extração de Texto para ler o conteúdo de cada página antes de salvar. Essencial para contabilidade e separar comprovativos misturados.

Lógica: Se encontrar um valor monetário (ex: "1.500,00"), renomeia o arquivo com o valor. Se não, usa um contador padrão.

<div align="center"> <img src="dividir%20smart.png" width="30%" alt="Menu Contexto" /> <img src="dividir%20smart%202.png" width="30%" alt="Console Log" /> <img src="dividir%20smart%203.png" width="30%" alt="Arquivos Finais" /> <p><em>Observe como os arquivos já saem nomeados com os valores detectados.</em></p> </div>

3. Juntar (Merge)
Unifica todos os PDFs de uma pasta selecionada em um único arquivo Unificados.pdf numa questão de segundos.

<div align="center"> <img src="juntar.png" width="24%" alt="Seleção" /> <img src="juntar%202.png" width="24%" alt="Processo" /> <img src="juntar%203.png" width="24%" alt="Arquivo Final" /> <img src="juntar%20turbo.png" width="24%" alt="Modo Turbo" /> </div>

4. Renomeação Automática (OCR Logic V4)
O cérebro do projeto. Analisa o texto de boletos, comprovativos bancários (Banestes, BB, Nubank, etc.) e guias de impostos.

Detecta padrões: PIX, BOLETO, DARF, EXTRATO.

Flexibilidade: 20 opções de ordenação (Data, Favorecido, Valor, Tipo).

Inteligência: Distingue quem pagou de quem recebeu e ignora saldos para focar no valor da transação.

<div align="center"> <h3>O Menu Interativo</h3> <img src="renomeara.png" width="80%" alt="Menu de Opções" /> </div>



<div align="center"> <img src="renomear.png" width="45%" alt="Console Analisando" /> <img src="renomear%202.png" width="45%" alt="Arquivos Renomeados" /> <p><em>Esquerda: Console detectando dados | Direita: Arquivos organizados automaticamente</em></p> </div> <div align="center"> <img src="renomear%203.png" width="80%" alt="Detalhes" /> </div>

🏗️ Arquitetura e Tecnologias
O projeto utiliza uma arquitetura híbrida para garantir a melhor UX no Windows:

Core (Python): Scripts robustos usando pypdf para manipulação de bytes e re (Regex) para lógica de extração de dados.

Wrapper (Batch): Scripts .bat que servem de "ponte", configurando o ambiente (UTF-8) e chamando o interpretador Python correto.

Instalador (Automation): Script de auto-diagnóstico que verifica dependências (pip), cria wrappers e injeta atalhos no SendTo.

graph LR
    A[Usuário (Menu Contexto)] -->|Clica em Enviar Para| B(Wrapper .BAT)
    B -->|Configura UTF-8| C{Script Python}
    C -->|Importa| D[pypdf Lib]
    C -->|Processa| E[Arquivo PDF]
    C -->|Retorna| F[Log Colorido no Terminal]

📦 Instalação e Uso
O projeto conta com um Instalador CLI Interativo.

Clone o repositório.

Coloque-o na pasta raiz de sua preferência (Ex: C:\Scripts).

Execute o arquivo Instalador_PyDF.bat.

Escolha a opção [3] INSTALAR / REPARAR.

O script verificará se o Python está instalado, instalará a dependência pypdf automaticamente e criará os atalhos.

<div align="center"> <img src="instalador.png" width="70%" alt="Instalador CLI" /> </div>

Como usar no dia a dia:
Clique com o botão direito em qualquer PDF (ou pasta).

Vá em Enviar Para > 01 - DIVIDIR (PyDF) (ou outra opção).

O script rodará e fechará automaticamente após o sucesso.

<div align="center"> <img src="pasta.png" width="60%" alt="Menu de Contexto Windows" /> </div>

✅ Testes Automatizados
Qualidade de código é prioridade. O projeto inclui um sistema de auto-diagnóstico (teste_sistema.py) que:

Cria PDFs "Mock" (falsos) para teste.

Executa todas as funções do sistema em ambiente isolado.

Valida se os arquivos de saída foram criados corretamente.

Limpa o ambiente após o teste.

Para rodar os testes, execute o instalador e escolha a opção [4] TESTE DE SISTEMA.

📂 Estrutura do Projeto
/
├── dividir.py          # Lógica de Split
├── dividir_smart.py    # Lógica de Split com leitura de conteúdo
├── juntar.py           # Lógica de Merge
├── renomear.py         # Lógica de Renomeação
├── motor.py            # Motor de Extração de Texto (Regex + Layout Analysis)
├── biblioteca_logs.py  # Formatação de Logs Coloridos
├── teste_sistema.py    # Suíte de Testes Unitários/Integração
└── Instalador_PyDF.bat # Gerenciador de Instalação (CLI)

📜 Licença
Este projeto está sob a licença MIT - sinta-se livre para usar e modificar.

Desenvolvido por Pedro Tavares Estudante de Ciência da Computação & Desenvolvedor Full Cycle em formação.