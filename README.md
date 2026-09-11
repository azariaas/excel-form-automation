# Excel → Web Form Automation

Automação em Python que lê registros de uma planilha Excel e os envia
automaticamente para formulários web, marcando cada linha já processada
para evitar reenvios duplicados.

## Sobre

Muitos processos internos ainda dependem de alguém copiar dados de uma
planilha e colá-los manualmente em um formulário web, linha por linha —
um trabalho repetitivo e sujeito a erros. Este projeto automatiza esse
fluxo: para cada linha não processada de uma planilha, o robô abre o
formulário correspondente, preenche os campos e envia, sinalizando a
linha (cor de destaque) assim que o envio é confirmado.

## Problema

Preencher manualmente dezenas ou centenas de formulários web a partir de
uma base de dados é lento, repetitivo e propenso a erros (linhas
puladas, dados reenviados, digitação incorreta).

## Solução

O projeto lê uma planilha `.xlsx`, identifica as linhas ainda não
enviadas (com base em uma cor de destaque na célula), preenche um
formulário web configurável via Selenium e marca a linha como concluída
— tudo de forma automática e reexecutável com segurança (linhas já
marcadas são puladas).

Os alvos (URLs) e os seletores de campo do formulário são totalmente
configuráveis em `config.json`, então o mesmo robô pode ser reaproveitado
para qualquer formulário web, não apenas um caso específico.

## Tecnologias

- Python 3
- Selenium + webdriver-manager (automação de navegador)
- openpyxl (leitura/escrita de planilhas Excel, incluindo formatação de células)
- logging (rastreamento de execução)
- pytest (testes automatizados)

## Funcionamento

```
Planilha (.xlsx)
      ↓
Leitura das linhas não processadas
      ↓
Preenchimento do formulário web (Selenium)
      ↓
Confirmação de envio
      ↓
Marcação da linha como concluída na planilha
```

## Estrutura

```
excel-form-automation/
├── main.py                     # ponto de entrada
├── automation/
│   ├── config.py               # carregamento da configuração
│   ├── excel_handler.py        # leitura/escrita/marcação da planilha
│   └── form_filler.py          # preenchimento e envio do formulário
├── scripts/
│   └── generate_sample_data.py # gera uma planilha de exemplo fictícia
├── data/
│   ├── config.example.json     # configuração de exemplo (alvos fictícios)
│   └── input_example.xlsx      # planilha de exemplo com dados fictícios
├── tests/
│   └── test_excel_handler.py
├── requirements.txt
└── .gitignore
```

## Como executar

1. Clone o repositório e entre na pasta do projeto.
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copie o arquivo de configuração de exemplo e ajuste os alvos:
   ```bash
   cp data/config.example.json data/config.json
   ```
   Edite `data/config.json` com a URL do formulário real e os seletores
   CSS dos campos que deseja preencher.
4. (Opcional) Gere uma planilha de exemplo para testar:
   ```bash
   python scripts/generate_sample_data.py
   ```
5. Execute a automação:
   ```bash
   python main.py --config data/config.json
   ```
6. Verifique o resultado: as linhas processadas com sucesso ficam
   destacadas na planilha, e um resumo é impresso no console ao final.

## Exemplo

Planilha de entrada (`data/input_example.xlsx`, aba `LOC1`):

| full_name       | phone          | email                  | document_id  | notes            |
|-----------------|----------------|-------------------------|--------------|-------------------|
| Maria Fictícia  | (11) 90000-0001 | maria.ficticia@example.com | 000.000.000-00 | Preferência à tarde |

Após a execução, a linha é destacada em amarelo e o console mostra:

```
✅ Maria Fictícia
Concluído — 1 enviados, 0 pulados (já enviados), 0 erros.
```

## Aprendizados

Este projeto demonstra:

- Automação de navegador com Selenium (localização de elementos,
  preenchimento de formulários, tratamento de erros de UI)
- Manipulação de planilhas com openpyxl, incluindo leitura de
  formatação de células (cores de preenchimento)
- Separação entre configuração e lógica de negócio
- Tratamento de erros por linha, sem interromper o processamento total
- Estruturação de um script utilitário em módulos testáveis
- Escrita de testes automatizados para a lógica que não depende de
  navegador

## Melhorias futuras

- Suporte a execução em modo headless com opção de configuração
- Retry automático com backoff em caso de falha temporária de rede
- Exportação de um relatório de execução (CSV/JSON) além do log no console
- Paralelização do processamento entre planilhas/abas independentes
