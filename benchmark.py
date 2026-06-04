import time
import numpy as np
import pandas as pd
from hubspot_pipeline.loader import carregar_deals
from hubspot_pipeline.transformer import (
    transformar_lento, 
    transformar_rapido,
    identificar_modificados_lento,
    identificar_modificados_rapido
)

N = 60_000  # volume de deals

# Gerar IDs falsos
deal_ids = [str(i) for i in range(N)]
company_ids_lista = [str(i % 1000) for i in range(N)]

# Montar os dicionários
associacoes    = dict(zip(deal_ids, company_ids_lista))
nomes_empresas = {str(i): f"Empresa {i}" for i in range(1000)}
cnpjs_empresas = {str(i): f"{i:014d}" for i in range(1000)}

# DataFrame simulado
df = pd.DataFrame({"id": deal_ids})

# DataFrame com datas simuladas
datas_base = pd.date_range("2024-01-01", periods=N, freq="h")
datas_modificadas = datas_base.to_series()
indices_modificados = np.random.choice(N, size=int(N * 0.3), replace=False)
datas_modificadas.iloc[indices_modificados] += pd.Timedelta(hours=1)

df_datas = pd.DataFrame({
    "id": deal_ids,
    "data_hubspot": datas_base,
    "data_local": datas_modificadas.values
})

# ── Benchmark 1: mapeamento de empresas ──
print("--- Mapeamento de empresas ---")

inicio_lento = time.time()
transformar_lento(df.copy(), associacoes, nomes_empresas, cnpjs_empresas)
fim_lento = time.time()

inicio_rapido = time.time()
transformar_rapido(df.copy(), associacoes, nomes_empresas, cnpjs_empresas)
fim_rapido = time.time()

tempo_lento  = fim_lento  - inicio_lento
tempo_rapido = fim_rapido - inicio_rapido

print(f"Lento:  {tempo_lento:.2f}s")
print(f"Rápido: {tempo_rapido:.2f}s")
print(f"Ganho:  {tempo_lento / tempo_rapido:.1f}x mais rápido")

# ── Benchmark 2: identificar modificados ──
print("\n--- Identificar modificados ---")

inicio_loop = time.time()
identificar_modificados_lento(df_datas.copy())
fim_loop = time.time()

inicio_vetor = time.time()
identificar_modificados_rapido(df_datas.copy())
fim_vetor = time.time()

tempo_loop  = fim_loop  - inicio_loop
tempo_vetor = fim_vetor - inicio_vetor

print(f"Loop:       {tempo_loop:.4f}s")
print(f"Vetorizado: {tempo_vetor:.4f}s")
print(f"Ganho:      {tempo_loop / tempo_vetor:.1f}x mais rápido")