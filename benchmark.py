import os
import subprocess
import time
import re
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURAÇÕES GERAIS
# ==========================================
TAMANHOS_TESTE = {
    "1KB": 1024,
    "100KB": 1024 * 100,
    "1MB": 1024 * 1024,
    "10MB": 1024 * 1024 * 10,
    "100MB": 1024 * 1024 * 100,
    "500MB": 1024 * 1024 * 500,
    "1GB": 1024 * 1024 * 1024
}

EXECUTAVEL_CPU = "aes_serial.exe" 
EXECUTAVEL_GPU = "aes_hip.exe"    
tamanhos_nomes = list(TAMANHOS_TESTE.keys())

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================
def criar_arquivo(nome, tamanho_bytes):
    if os.path.exists(nome):
        os.remove(nome)
    subprocess.run(f"fsutil file createnew {nome} {tamanho_bytes}", shell=True, stdout=subprocess.DEVNULL)

def limpar_arquivos_gerados(nome_base):
    for extensao in ["", ".enc", ".dec"]:
        arquivo = nome_base + extensao
        if os.path.exists(arquivo):
            try:
                os.remove(arquivo)
            except:
                pass

def rodar_benchmark(executavel, modo, arquivo):
    # Chama o executável C++ passando a flag (-e ou -d)
    resultado = subprocess.run([f".\\{executavel}", modo, arquivo], capture_output=True, text=True)
    
    match_tempo = re.search(r"Tempo de Execucao.*?:\s+([0-9.]+)", resultado.stdout)
    match_tp = re.search(r"Throughput:\s+([0-9.]+|inf)", resultado.stdout)
    
    tempo = float(match_tempo.group(1)) if match_tempo else 0.000001 
    tp_str = match_tp.group(1) if match_tp else "0"
    throughput = 0.0 if tp_str == 'inf' else float(tp_str)
    
    return tempo, throughput

def executar_bateria_de_testes(modo, nome_operacao):
    tempos_cpu, tempos_gpu = [], []
    throughputs_cpu, throughputs_gpu = [], []
    speedups = []
    
    print("\n" + "=" * 90)
    print(f"{'MÉTRICAS DE ' + nome_operacao.upper() + ' (' + modo + ')':^90}")
    print("=" * 90)
    print(f"{'Tamanho':<8} | {'Tempo CPU (s)':<13} | {'Tempo GPU (s)':<13} | {'Throughput CPU':<15} | {'Throughput GPU':<15} | {'Speedup'}")
    print("-" * 90)

    arquivo_teste = "arquivo_bench.bin"

    for nome, tamanho in TAMANHOS_TESTE.items():
        criar_arquivo(arquivo_teste, tamanho)
        
        # Roda na CPU
        t_cpu, tp_cpu = rodar_benchmark(EXECUTAVEL_CPU, modo, arquivo_teste)
        tempos_cpu.append(t_cpu)
        throughputs_cpu.append(tp_cpu)
        
        # Roda na GPU
        t_gpu, tp_gpu = rodar_benchmark(EXECUTAVEL_GPU, modo, arquivo_teste)
        tempos_gpu.append(t_gpu)
        throughputs_gpu.append(tp_gpu)
        
        # Calcula Speedup
        speedup = 0.0 if t_gpu <= 0.000001 else t_cpu / t_gpu
        speedups.append(speedup)
        
        # Imprime a linha da tabela no terminal
        print(f"{nome:<8} | {t_cpu:<13.6f} | {t_gpu:<13.6f} | {tp_cpu:<11.2f} MB/s | {tp_gpu:<11.2f} MB/s | {speedup:.2f}x")
        
        # Apaga os arquivos criados para não lotar o HD
        limpar_arquivos_gerados(arquivo_teste)
        time.sleep(0.5)

    return throughputs_cpu, throughputs_gpu, speedups

# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================
print("Iniciando testes... Isso pode levar alguns minutos.")

# 1. Bateria de Criptografia (-e)
tp_cpu_enc, tp_gpu_enc, speedup_enc = executar_bateria_de_testes("-e", "Criptografia")

# 2. Bateria de Descriptografia (-d)
tp_cpu_dec, tp_gpu_dec, speedup_dec = executar_bateria_de_testes("-d", "Descriptografia")

# ==========================================
# PLOTAGEM DOS GRÁFICOS (MATPLOTLIB)
# ==========================================
fig, axs = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Análise de Desempenho AES-128: CPU vs GPU', fontsize=16, fontweight='bold', y=0.98)

# [0, 0] Throughput Criptografia
axs[0, 0].plot(tamanhos_nomes, tp_cpu_enc, marker='o', label='CPU Serial', linewidth=2)
axs[0, 0].plot(tamanhos_nomes, tp_gpu_enc, marker='s', label='GPU Paralela', linewidth=2)
axs[0, 0].set_title('Throughput: Criptografia')
axs[0, 0].set_ylabel('Throughput (MB/s)')
axs[0, 0].grid(True, linestyle='--', alpha=0.7)
axs[0, 0].legend()

# [0, 1] Speedup Criptografia
axs[0, 1].plot(tamanhos_nomes, speedup_enc, marker='^', color='green', linewidth=2, label='Speedup Cripto')
axs[0, 1].axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='Inflexão (1x)')
axs[0, 1].set_title('Aceleração (Speedup): Criptografia')
axs[0, 1].set_ylabel('Vezes mais rápido')
axs[0, 1].grid(True, linestyle='--', alpha=0.7)
axs[0, 1].legend()

# [1, 0] Throughput Descriptografia
axs[1, 0].plot(tamanhos_nomes, tp_cpu_dec, marker='o', label='CPU Serial', linewidth=2)
axs[1, 0].plot(tamanhos_nomes, tp_gpu_dec, marker='s', label='GPU Paralela', linewidth=2)
axs[1, 0].set_title('Throughput: Descriptografia')
axs[1, 0].set_xlabel('Tamanho do Arquivo')
axs[1, 0].set_ylabel('Throughput (MB/s)')
axs[1, 0].grid(True, linestyle='--', alpha=0.7)
axs[1, 0].legend()

# [1, 1] Speedup Descriptografia
axs[1, 1].plot(tamanhos_nomes, speedup_dec, marker='^', color='green', linewidth=2, label='Speedup Descripto')
axs[1, 1].axhline(y=1.0, color='red', linestyle='--', alpha=0.7, label='Inflexão (1x)')
axs[1, 1].set_title('Aceleração (Speedup): Descriptografia')
axs[1, 1].set_xlabel('Tamanho do Arquivo')
axs[1, 1].set_ylabel('Vezes mais rápido')
axs[1, 1].grid(True, linestyle='--', alpha=0.7)
axs[1, 1].legend()

plt.tight_layout()
plt.subplots_adjust(top=0.93)
plt.savefig("graficos_completos_tcc.png", dpi=300)

print("\nTodos os testes finalizados com sucesso! A imagem 'graficos_completos_tcc.png' foi salva.")
plt.show()