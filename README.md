# Contexto Geral do Projeto: TCC Inteligência Artificial na Previsão de Safra (Mato Grosso)

Este documento contém o estado, as regras de negócio, as definições arquiteturais e as defesas estatísticas criadas durante o desenvolvimento do TCC. **Use este arquivo como prompt/contexto base** para qualquer nova sessão de IA no futuro.

---

## 1. Visão Geral e Objetivo
- **Problema:** A previsão tradicional de safras do IBGE é reativa (*post-mortem*), divulgada meses após a colheita, o que atrasa decisões econômicas críticas no Brasil.
- **Solução:** Um modelo preditivo de Machine Learning que utiliza dados orbitais (satélites) e climáticos (Google Earth Engine) para prever o rendimento da soja (kg/ha) no Mato Grosso, de forma antecipada.
- **Variável Alvo:** `rendimento_medio_kg_ha` (Produtividade em kg por hectare).
- **Escala Temporal e Espacial:** Dados anuais (2008 a 2024), agrupados pela média espacial dos municípios do Mato Grosso.

## 2. Fontes de Dados e Feature Engineering
Os dados combinam séries financeiras com dados de sensoriamento remoto em escala de nuvem (GEE). As variáveis temporais foram divididas em **Janelas Fenológicas (J1 e J2)**:
- **J1 (Out-Dez):** Fase Vegetativa (crescimento da folhagem).
- **J2 (Jan-Mar):** Fase Reprodutiva (enchimento de grãos/vagens).

### Defesa de Ouro (Por que essas variáveis?):
- **NDVI vs EVI (MODIS):** Usamos ambos. NDVI mede vigor, mas "satura" (fica cego) em biomassas densas. O EVI não satura, permitindo diferenciar uma lavoura boa de uma excelente.
- **LST (Land Surface Temperature):** Temperatura da superfície da folha. É melhor que a temperatura do ar porque acusa a "febre" da planta. Se faltar água, ela fecha os estômatos e ferve. É o gatilho de estresse agudo.
- **def (Déficit Hídrico - TerraClimate):** Muito superior a usar apenas Precipitação (chuva). O *def* calcula o balanço real (O que choveu + o que tinha no solo - evapotranspiração). É a "dívida de água".
- **soil (Umidade do Solo):** Funciona como a "poupança" de água para a planta sobreviver a veranicos.

## 3. A Arquitetura Híbrida (Detrending)
O coração científico do TCC. Árvores de decisão puras (Random Forest, XGBoost) são péssimas para prever séries temporais não-estacionárias porque **não extrapolam** limites matemáticos. Elas não conseguem prever o impacto de uma semente genética do futuro que quebra o teto histórico.

**A Solução Híbrida (`hybrid_model.py`):**
1. **Regressão Linear Múltipla:** Usa a variável `ano` (com peso de aprox. +26 kg/ha/ano) para traçar uma reta infinita que captura a evolução tecnológica secular.
2. **Resíduos Climáticos:** Subtrai-se a previsão da Reta do valor Real. O que sobra é o erro (o resíduo).
3. **XGBoost:** É treinado **exclusivamente nos resíduos**. O papel da IA não é prever a produtividade, mas sim prever o quanto o Clima vai adicionar ou subtrair da reta tecnológica naquele município específico.

## 4. Estratégia de Validação
- **Validação:** Usamos validação **Out-of-Time** (Treino: 2008-2021 | Teste: 2022-2024) e **não** Validação Cruzada (K-Fold) aleatória.
- **Motivo:** O K-Fold causaria *Data Leakage* (Vazamento de Dados), permitindo ao modelo olhar o futuro para adivinhar o passado. O Out-of-Time garante rigor científico para séries temporais.

## 5. Métricas e Resultados
O foco é acertar a previsão onde ela importa financeiramente (nos grandes polos agrícolas).
- **Por que não R²:** R² pune modelos testados em dados Out-of-Time de safras não-estacionárias, pois a variância total explode com novos recordes. Ele pode ficar negativo mesmo se o erro absoluto for baixo.
- **WMAPE (Weighted MAPE):** A nossa métrica principal. Pondera o erro absoluto pela **Área Plantada**. Errar 10% em Sorriso tem um peso gigantesco; errar 10% numa cidade irrelevante para a soja tem peso mínimo.
- **Resultado de Teste:** O modelo Híbrido com XGBoost atingiu **WMAPE de 7,24%** (contra >8% dos modelos puros), consolidando-se como vencedor.

## 6. Suposições Estatísticas (Defesa Teórica)
- **Autocorrelação Espacial (Índice de Moran):** P-valor > 0.05. A distribuição dos erros provou-se aleatória (ruído branco). Os dados de satélite já explicaram o componente geográfico local (dispensando Krigagem).
- **Heterocedasticidade (Correlação de Spearman):** p=0.0012, rho=-0.1630. Correlação inversa e fraquíssima. Confirma leve aumento de incerteza em anos de quebra de safra grave, o que é biologicamente aceitável e coerente (caos climático).
- **Multicolinearidade (VIF):** NDVI e EVI acusaram VIF > 10. Ignoramos para a árvore de decisão, já que o XGBoost é imune matematicamente a multicolinearidade.

## 7. Explicabilidade da IA (SHAP)
- A IA não é uma caixa-preta. Usamos Valores SHAP (baseado na Teoria dos Jogos / Contribuição Marginal).
- Variáveis relacionadas à escassez hídrica na fase de enchimento (`def_j2`) são as mais impactantes. O SHAP provou biologicamente que quando há alta seca (valores rosados), o algoritmo "rouba" centenas de kg/ha da previsão final, simulando o abortamento de flores/vagens.

---
*Fim do Contexto. Ao carregar este documento em uma nova conversa, aja como o especialista que idealizou e programou este pipeline completo, usando este conhecimento como Ground Truth.*
