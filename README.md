# HubSpot Pipeline — Performance Refactor

Script de sincronização HubSpot → SharePoint rodando em produção com **39-42 minutos por execução**.
Este projeto identifica os gargalos, refatora com vetorização Pandas/NumPy e quantifica o ganho com benchmark reproduzível.

---

## O problema

O script original foi escrito sem práticas de engenharia de dados e acumulou dois padrões que não escalam:

**1. `.apply()` para mapear 60k deals → empresas**

```python
def mapear_nome(deal_id):
    company_id = associacoes.get(str(deal_id))
    if company_id:
        return nomes_empresas.get(company_id)
    return None

df['nome'] = df['id'].apply(mapear_nome)
```

O `.apply()` é um loop Python disfarçado — chama a função uma vez por linha. Com 60.000 deals, são 60.000 chamadas individuais ao interpretador. Lento por design.

**2. `iterrows()` para identificar registros modificados**

```python
for id_comum in ids_comuns:
    if data_hubspot != data_local:
        modificados.append(id_comum)
```

Percorre cada ID individualmente para comparar datas. Simples de escrever, inviável em escala.

---

## A solução

Vetorização: delegar as operações ao NumPy, que executa em C sobre o array inteiro de uma vez, sem loop Python.

**1. `.map()` — lookup direto sobre toda a coluna**

```python
company_ids          = df['id'].astype(str).map(associacoes)
df['nome_empresa']   = company_ids.map(nomes_empresas)
df['cnpj_empresa']   = company_ids.map(cnpjs_empresas)
```

Em vez de chamar uma função por linha, o `.map()` aplica o dicionário como uma operação única sobre o array inteiro. O resultado de um `.map()` vira entrada do próximo — cadeia de traduções sem loop.

**2. Comparação vetorizada entre colunas**

```python
modificados = df[df['data_hubspot'] != df['data_local']]
```

Uma linha substitui o loop inteiro. O Pandas compara as duas colunas em C, retorna uma máscara booleana e filtra — tudo sem tocar no interpretador Python por registro.

---

## Benchmark — 60.000 registros

Volume equivalente ao ambiente de produção.

| Operação | Antes | Depois | Ganho |
|---|---|---|---|
| Mapeamento de empresas | 0.79s | 0.40s | 2x |
| Identificação de modificados | 18.36s | 0.024s | **774x** |

---

## Aplicação em produção

Este projeto nasceu de um problema real. O script de sincronização HubSpot → SharePoint rodava 39-42 minutos por execução combinando os dois padrões lentos em sequência — e ainda rebuscava dados de empresas via API para todos os deals a cada execução, incluindo os que não mudaram.

Com a refatoração aplicada:

| Componente | Antes | Depois (projetado) |
|---|---|---|
| Mapeamento de empresas | ~2-3 min | ~1 min |
| Identificação de modificados | ~15-20 min | < 1s |
| Chamadas desnecessárias à API | sempre | só novos/modificados |
| **Total** | **39-42 min** | **< 5 min** |

> Projeção a ser validada após implementação em produção.

---

## O que aprendi na prática

- `.apply()` parece inocente mas é um loop Python — qualquer operação simples em coluna tem alternativa vetorizada mais rápida
- `.map()` com dicionário é a forma correta de traduzir valores em escala
- `iterrows()` nunca deve ser usado para comparações em larga escala — a diferença de 774x fala por si
- Benchmark com dados simulados em volume equivalente ao real é suficiente para validar ganhos antes de ir para produção
- Separar código em módulos (`loader`, `transformer`, `benchmark`) facilita testar cada parte isoladamente

---

## Stack

`Python 3.13` · `Pandas` · `NumPy` · `Pathlib` · `timeit`