import pandas as pd
import numpy as np

def transformar_lento(df: pd.DataFrame, associacoes: dict, 
                      nomes_empresas: dict, cnpjs_empresas: dict) -> pd.DataFrame:
    """Versão com .apply() - uma linha por vez"""

    def mapear_nome(deal_id):
        company_id = associacoes.get(str(deal_id))
        if company_id:
            return nomes_empresas.get(company_id)
        return None

    def mapear_cnpj(deal_id):
        company_id = associacoes.get(str(deal_id))
        if company_id:
            return cnpjs_empresas.get(company_id)
        return None

    df['nome_empresa_associado'] = df['id'].apply(mapear_nome)
    df['cnpj_empresa_associado'] = df['id'].apply(mapear_cnpj)

    return df


def transformar_rapido(df: pd.DataFrame, associacoes: dict,
                       nomes_empresas: dict, cnpjs_empresas: dict) -> pd.DataFrame:
    """Versão vetorizada - lote inteiro de uma vez"""

    # Passo 1: deal_id → company_id (um .map() só)
    company_ids = df['id'].astype(str).map(associacoes)

    # Passo 2: company_id → nome e cnpj (mais dois .map())
    df['nome_empresa_associado'] = company_ids.map(nomes_empresas)
    df['cnpj_empresa_associado'] = company_ids.map(cnpjs_empresas)

    return df


def identificar_modificados_lento(df: pd.DataFrame) -> pd.DataFrame:
    """Versão com loop - compara datas uma por uma"""
    modificados = []
    
    for _, row in df.iterrows():
        if row["data_hubspot"] != row["data_local"]:
            modificados.append(row["id"])
    
    return df[df["id"].isin(modificados)]


def identificar_modificados_rapido(df: pd.DataFrame) -> pd.DataFrame:
    """Versão vetorizada - compara as duas colunas de uma vez"""
    mascara = df["data_hubspot"] != df["data_local"]
    return df[mascara]