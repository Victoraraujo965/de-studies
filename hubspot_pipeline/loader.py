from pathlib import Path
import pandas as pd

COLUNAS_OBRIGATORIAS = ["id", "dealname", "pipeline", "dealstage", "acao"]

def carregar_deals(caminho: str) -> pd.DataFrame:
    """Função para load do arquivo, com 3 validações"""

    arquivo = Path(caminho)

    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    try:
        open(arquivo, "rb").close()
    except PermissionError:
        raise PermissionError(f"Arquivo em uso, feche antes de continuar: {caminho}")

    df = pd.read_excel(caminho)

    if len(df) == 0:
        raise ValueError("Arquivo vazio, nenhum registro encontrado")
    
    return df