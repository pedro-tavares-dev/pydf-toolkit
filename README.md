PyDF Toolkit - Windows PDF Automation

Uma suíte de ferramentas leve, local e automatizada para manipulação de PDFs, integrada diretamente ao Menu de Contexto do Windows.

Sobre o Projeto

O PyDF Toolkit foi desenvolvido para resolver a ineficiência de manipular documentos PDF no dia a dia corporativo. Ao invés de depender de softwares pesados (Adobe) ou ferramentas online inseguras (iLovePDF), este projeto oferece uma solução nativa, rápida e privada.

O diferencial é a integração via Shell (Batch Scripting), permitindo que o usuário execute scripts Python complexos simplesmente clicando com o botão direito no arquivo ("Enviar Para").

Funcionalidades

1. Fatiar (Split)

Divide um arquivo PDF em páginas individuais instantaneamente.

Criação automática de pastas organizadas.

Nomenclatura sequencial.

2. Fatiar Inteligente (Smart Split)

Utiliza Regex e Extração de Texto para ler o conteúdo de cada página antes de salvar.

Ideal para separar comprovantes ou notas fiscais.

Lógica: Se encontrar um valor monetário (ex: "1.500,00"), renomeia o arquivo com o valor. Se não, usa um contador padrão.

3. Juntar (Merge)

Unifica todos os PDFs de uma pasta em um único arquivo Unificados.pdf.

4. Renomeação Automática (OCR Logic)

Analisa o texto de boletos ou comprovantes PIX para identificar o tipo de documento e renomeá-lo automaticamente.

Detecta padrões: PIX, BOLETO, DARF.

Arquitetura e Tecnologias

O projeto utiliza uma arquitetura híbrida para garantir a melhor UX no Windows:

Core (Python): Scripts robustos usando pypdf para manipulação de bytes e re (Regex) para lógica de extração de dados.

Wrapper (Batch): Scripts .bat que servem de "ponte", configurando o ambiente (UTF-8), chamando o interpretador Python correto e gerenciando pausas de execução.

Instalador (Automation): Um script de auto-diagnóstico que verifica dependências (pip install), cria os wrappers e injeta os atalhos na pasta SendTo do Windows.

graph LR
    A[Usuário (Menu Contexto)] -->|Clica em Enviar Para| B(Wrapper .BAT)
    B -->|Configura UTF-8| C{Script Python}
    C -->|Importa| D[pypdf Lib]
    C -->|Processa| E[Arquivo PDF]
    C -->|Retorna| F[Log Colorido no Terminal]


Instalação e Uso

O projeto conta com um Instalador CLI Interativo.

Clone o repositório.

Coloque-o na sua pasta mãe do Disco local principal. Ex:C:\Scripts

Execute o arquivo Instalador_PyDF.bat.

Escolha a opção [3] INSTALAR / REPARAR.

O script verificará se o Python está instalado.

Instalará a dependência pypdf automaticamente.

Criará os atalhos no menu de contexto.

Como usar:

Clique com o botão direito em qualquer PDF (ou pasta).

Vá em Enviar Para > 01 - DIVIDIR (PyDF) (ou outra opção).

O script rodará e fechará automaticamente após o sucesso.

Testes Automatizados

Qualidade de código é prioridade. O projeto inclui um sistema de auto-diagnóstico (teste_sistema.py) que:

Cria PDFs "Mock" (falsos) para teste.

Executa todas as funções do sistema em ambiente isolado.

Valida se os arquivos de saída foram criados corretamente.

Limpa o ambiente após o teste.

Para rodar os testes, execute o instalador e escolha a opção [4] TESTE DE SISTEMA.

Estrutura do Projeto

/
├── dividir.py          # Lógica de Split
├── dividir_smart.py    # Lógica de Split com leitura de conteúdo
├── juntar.py           # Lógica de Merge
├── renomear.py         # Lógica de Renomeação
├── motor.py            # Motor de Extração de Texto (Regex)
├── biblioteca_logs.py  # Formatação de Logs Coloridos
├── teste_sistema.py    # Suíte de Testes Unitários/Integração
└── Instalador_PyDF.bat # Gerenciador de Instalação (CLI)


Licença

Este projeto está sob a licença MIT - sinta-se livre para usar e modificar.

Desenvolvido por Pedro Tavares
Estudante de Ciência da Computação & Desenvolvedor Full Cycle em formação.
