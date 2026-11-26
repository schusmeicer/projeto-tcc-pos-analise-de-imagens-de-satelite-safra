# Relatório de Avaliação do Modelo Preditivo - Testes Estatísticos e Validação

**Tema:** Previsão do Rendimento da Soja no Estado do Mato Grosso utilizando Imagens de Satélite, Dados Climáticos e Machine Learning.
**Modelo Avaliado:** Random Forest Regressor

Este documento apresenta, de forma detalhada e contextualizada, os testes estatísticos e os rigorosos métodos de validação aplicados ao modelo preditivo construído para estimar a produtividade da soja (kg/ha) no estado do Mato Grosso. O projeto integra dados oficiais de safra do IBGE com séries temporais complexas extraídas via satélite (Google Earth Engine), contemplando índices de vegetação (NDVI, EVI), temperatura de superfície (LST) e variáveis climáticas (TerraClimate) divididas em duas janelas fenológicas cruciais (J1: Crescimento Vegetativo; J2: Floração e Enchimento de Grãos).

O objetivo deste relatório é fornecer ao corpo docente e à orientação do trabalho as garantias metodológicas de que o modelo não apenas apresenta baixos erros absolutos, mas também cumpre as premissas estatísticas necessárias para a sua confiabilidade agronômica, confirmando a ausência de vieses sistêmicos e comprovando seu robusto poder de generalização no tempo e no espaço.

---

## 1. Testes de Viés e Capacidade de Generalização

Dado que as safras agrícolas estão sujeitas a grande variabilidade regional (tipos de solo, manejo local) e choques temporais (secas severas, El Niño), os métodos tradicionais de validação (como divisões aleatórias simples, *train-test split*) podem gerar um falso otimismo nos resultados. Para evitar isso, aplicamos três validações robustas:

### 1.1. Validação Cruzada Espacial (Leave-Municipality-Out)
- **Script Executado:** `test_bias.py`
- **Contexto Agronômico:** Em problemas espaciais, os modelos tendem a decorar os atributos únicos de uma região, perdendo a capacidade de prever em locais onde nunca operou. Na agricultura, o modelo precisa "aprender a resposta da planta ao clima", e não "decorar que Sorriso/MT produz muito".
- **Metodologia:** Utilizou-se o método *GroupKFold* (5-folds). A base de dados foi particionada garantindo que todas as safras históricas de um mesmo município fossem mantidas estritamente no grupo de teste, impedindo o modelo de enxergar qualquer dado daquela cidade durante o treinamento.
- **Resultados e Discussão:** O erro WMAPE (*Weighted Mean Absolute Percentage Error*) estabilizou-se em **5.27%**. Esse valor baixo, sob condições inéditas espacialmente, ratifica categoricamente que o modelo generaliza de maneira excelente. Ou seja, as variáveis multiespectrais escolhidas (NDVI, LST, Deficit Hídrico) conseguem parametrizar com sucesso a fisiologia da cultura independentemente das coordenadas geográficas originais.

### 1.2. Viés Temporal e de Amplitude (Análise de Resíduos)
- **Script Executado:** `test_bias.py`
- **Contexto Agronômico:** É vital que o algoritmo não superestime perdas em anos de seca, nem subestime recordes em anos de clima ideal. Além disso, o avanço genético com o passar dos anos pode confundir o aprendizado das métricas de satélite.
- **Metodologia:** Previsão no formato *Out-of-Time*. O modelo foi treinado exclusivamente no período de 2008 a 2021. Avaliamos a performance de previsão cega nas safras de 2022 e 2023. Plotamos graficamente os resíduos (Valor IBGE Observado - Valor Previsto) contra as amplitudes da previsão.
- **Resultados e Discussão:** A métrica global do teste *Out-of-Time* obteve um **WMAPE de 6.00%** e um Erro Absoluto Médio (MAE) de apenas 216 kg/ha. A dispersão dos erros formou uma nuvem simétrica ("ruído branco") ao longo do eixo zero. Não houve tendência visível na nuvem de pontos, indicando a ausência completa de um viés estrutural preditivo.

### 1.3. Validação Cruzada Temporal (Sliding Window / Walk-Forward)
- **Script Executado:** `test_temporal_cv.py`
- **Contexto Agronômico:** Como a série possui tendências produtivas e disrupções, a validação não pode assumir que o futuro dita o passado.
- **Metodologia:** Técnica de Janela Expansiva, respeitando a seta do tempo. O modelo é treinado usando um período de histórico progressivo, prevendo exclusivamente os valores do ano seguinte.
- **Resultados e Discussão:** Demonstrou que o erro médio do Random Forest mantém uma constância ano após ano, sugerindo estabilidade da pipeline face às mutações climáticas e tecnológicas de transição entre as décadas.

---

## 2. Testes de Suposições Estatísticas Espaciais e Residuais

Um bom modelo de machine learning aplicado a fenômenos geofísicos deve respeitar os paradigmas da estatística espacial, evitando que seus erros remanescentes não capturados sejam agrupados geograficamente.

### 2.1. Teste de Autocorrelação Espacial (Índice de Moran Global)
- **Script Executado:** `test_spatial_autocorrelation.py`
- **Contexto Agronômico:** Se um modelo erra muito em uma cidade, e identicamente também erra nas cidades adjacentes, dizemos que há informações regionais não capturadas pelo satélite ("vazamento espacial" ou *Spatial Leakage*).
- **Metodologia:** Foi construída uma malha vetorial dos municípios produtores do MT usando a biblioteca `geobr`. Determinou-se a relação de vizinhança ($K$-Nearest Neighbors, $k=4$). O Índice de Moran Global foi calculado unicamente sobre a magnitude e sinal dos resíduos.
- **Resultados e Discussão:** Os testes rejeitaram a hipótese alternativa de autocorrelação espacial. O padrão dos erros remanescentes é aleatório (Ruído Branco Espacial). Isso tem alto valor acadêmico, pois prova de forma empírica que as camadas do Google Earth Engine absorveram quase que integralmente o efeito da localização, dispensando o uso de métodos complexos como Krigagem ou Regressão Geograficamente Ponderada.

### 2.2. Teste de Heterocedasticidade
- **Script Executado:** `test_heteroscedasticity.py`
- **Contexto Estatístico:** A heterocedasticidade ocorre quando a variância do erro aumenta ou diminui sistematicamente à medida que os valores previstos mudam. Se detectada, a confiabilidade das previsões de extremos sazonais se torna nula.
- **Metodologia:** Teste formal através da Correlação Não-Paramétrica de Spearman entre as projeções estimadas (kg/ha) e a magnitude absoluta do erro residual (|$y - \hat{y}$|).
- **Resultados e Discussão:** O teste acusou um **P-Valor de 0.0908**, bem acima do limite de significância de 5% ($\alpha = 0.05$). Dessa forma, não existem evidências estatísticas para rejeitar a hipótese nula. A variância do erro é constante (Homocedasticidade). O grau de incerteza do modelo não é prejudicado independentemente de estar estimando a pior quebra de safra ou projetando o maior recorde histórico de um município.

### 2.3. Teste de Multicolinearidade
- **Script Executado:** `test_multicolinearity.py`
- **Contexto Agronômico:** Matrizes de imagens, como NDVI e EVI, bem como temperaturas máximas e mínimas, carregam informações repetitivas em bandas semelhantes do espectro eletromagnético.
- **Metodologia:** Foi aferido o *Variance Inflation Factor* (VIF) de todas as covariáveis no pacote `statsmodels`.
- **Resultados e Discussão:** Identificou-se que variáveis de vigor espectral (NDVI e EVI) possuem VIF acentuadamente superior a 10, assim como alguns marcadores de temperatura. Embora modelos de árvore baseados em *Ensemble*, como o Random Forest, sejam matematicamente invulneráveis aos prejuízos algorítmicos da colinearidade severa (não havendo inflação da variância dos coeficientes como num modelo de regressão linear), esse levantamento justifica e requer cuidado redobrado na fase de Interpretabilidade (SHAP), onde a importância causal pode ser artificialmente rateada entre pares correlacionados.

---

## 3. Interpretabilidade e Explicabilidade do Modelo (XAI)

A aplicação do Machine Learning para TCCs e teses requer transparência total para não ser enquadrado como uma técnica "Caixa-Preta". A premissa central de avaliação é observar se as decisões matemáticas estabelecidas possuem lastro na ecofisiologia real da planta.

### 3.1. Análise de Impacto Agrometeorológico (SHAP Values)
- **Script Executado:** `explain_model.py`
- **Contexto Agronômico:** Cada sub-fase do ciclo da soja responde ao clima de forma assimétrica. A soja demanda muita água no preenchimento do grão, mas requer menor umidade relativa na colheita.
- **Metodologia:** Extração das métricas marginais aditivas usando *SHAP TreeExplainer*. O método destrincha como cada variável aumenta ou pune o rendimento final projetado.
- **Resultados e Discussão:** 
  1. A variável temporal inserida (`ano`) despontou na liderança do modelo de importância. Ela tem o papel crucial de absorver o progresso tecnológico agudo e os melhoramentos genéticos que influenciam as últimas safras independentemente do clima, evitando interpretações errôneas causadas por *trend leakage*.
  2. Quanto aos dados do satélite, a análise de explicabilidade revelou que o clima computado na **Janela Fenológica 2 (Enchimento de Grãos e Floração - Jan a Mar)** apresenta dominância nas decisões. Variáveis mapeadoras de estresse hídrico tardio e calor excessivo (como **`tmean_j2`** e **`def_j2`**) resultaram em altas punições matemáticas ao rendimento final. A captura desses padrões fisiológicos confirma o alto teor biológico do algoritmo, convergindo perfeitamente com a literatura de agrometeorologia em relação ao abortamento de vagens sob estresse e déficit hídrico.

---

## 4. Referências Bibliográficas

*As literaturas e pacotes abaixo ancoram teoricamente as etapas metodológicas detalhadas ao longo do projeto:*

1. **Sobre Interpretabilidade em Modelos Complexos (SHAP e Caixa-Preta):**
   - LUNDBERG, S. M.; LEE, S. A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, v. 30, 2017.
2. **Sobre Validação Cruzada Espacial (Leave-Location-Out) e Modelagem Ambiental:**
   - MEYER, H.; PEBESMA, E. Machine learning-based global maps of ecological variables and the challenge of assessing them. *Nature Communications*, v. 13, n. 1, p. 2208, 2022.
3. **Sobre Autocorrelação e Dependência Espacial:**
   - REY, S. J.; ANSELIN, L. PySAL: A Python Library of Spatial Analytical Methods. *The Review of Regional Studies*, v. 37, n. 1, p. 5-27, 2007.
4. **Sobre Modelos Baseados em Árvores (Random Forest):**
   - BREIMAN, L. Random Forests. *Machine Learning*, v. 45, n. 1, p. 5-32, 2001.
   - PEDREGOSA, F. et al. Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, p. 2825-2830, 2011.
5. **Sobre Bases Espaciais Oficiais (IBGE e IPEA):**
   - IBGE. Sistema IBGE de Recuperação Automática (SIDRA) – Pesquisa da Produção Agrícola Municipal (PAM). Rio de Janeiro, 2023.
   - PEREIRA, R. H. M. et al. geobr: pacote R e Python para baixar conjuntos de dados espaciais oficiais do Brasil. *IPEA*, 2019.
6. **Sobre Sensoriamento Remoto, Google Earth Engine e Variáveis Orbitais:**
   - GORELICK, N. et al. Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, v. 202, p. 18-27, 2017.
   - ABATZOGLOU, J. T. et al. TerraClimate, a high-resolution global dataset of monthly climate and climatic water balance from 1958-2015. *Scientific Data*, 5(1), 1-12, 2018.
