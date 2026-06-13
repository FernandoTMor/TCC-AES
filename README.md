# TCC-AES
Repositório designado para o meu tcc cujo oo tema é: Paralelização do Algoritmo AES em CPU e GPU Utilizando HIP sobre ROCm


## Requisitos

### Hardware

- Processador compatível com arquitetura x86_64;
- Mínimo de 8 GB de memória RAM;
- GPU AMD compatível com HIP para execução da versão paralela.

### Software

- Windows 11 (64 bits);
- AMD Software: Adrenalin Edition atualizado;
- HIP SDK para Windows;
- Python 3.10 ou superior;
- Compilador C++ compatível com o HIP SDK.

### Bibliotecas Python

Instale as dependências com:

```powershell
pip install matplotlib
```

### Verificação do Ambiente

```powershell
python --version
hipcc --version
```

## Compilação

### Versão Serial (CPU)

```powershell
g++ -O3 aes_serial.cpp -o aes_serial.exe
```

### Versão Paralela (GPU)

```powershell
hipcc -O3 aes_hip.cpp -o aes_hip.exe
```

## Execução dos Benchmarks

Certifique-se de que os arquivos abaixo estejam no mesmo diretório:

- aes_serial.exe
- aes_hip.exe
- benchmark.py

Execute:

```powershell
python benchmark.py
```

O script irá:

1. Gerar arquivos de teste entre 1 KB e 1 GB;
2. Executar criptografia e descriptografia nas versões CPU e GPU;
3. Calcular tempo de execução, throughput e speedup;
4. Gerar o gráfico:

```text
graficos_completos_tcc.png
```

