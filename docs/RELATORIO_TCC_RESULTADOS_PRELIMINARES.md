# Previsão do Rendimento da Soja no Mato Grosso via Satélites e Machine Learning

**[Nome Completo do Aluno]**¹; **[Nome Completo do Orientador]**²
¹ Titulação. Nome da Empresa ou Instituição. E-mail: aluno@email.com
² Titulação. Nome da Empresa ou Instituição. E-mail: orientador@email.com

### Resumo
Este trabalho apresenta a avaliação de um modelo preditivo baseado em Random Forest Regressor para estimar a produtividade da soja (kg/ha) no estado do Mato Grosso. Utilizando dados do IBGE e séries temporais do Google Earth Engine, o modelo foi submetido a rigorosos métodos de validação, incluindo validação cruzada espacial e temporal, análise de resíduos, e testes de suposições estatísticas (Índice de Moran, Heterocedasticidade e Multicolinearidade). Os resultados demonstraram baixos erros (WMAPE de 5.27% em dados inéditos espacialmente), alta capacidade de generalização e aderência à ecofisiologia da cultura comprovada via valores SHAP, garantindo a confiabilidade agronômica do algoritmo para prever o rendimento agrícola face a variações climáticas.

**Palavras-chave:** Sensoriamento Remoto; Produtividade Agrícola; Random Forest; Validação Espacial; Agrometeorologia.

---

### Introdução
A previsão assertiva das safras agrícolas é de extrema importância para o planejamento econômico e logístico, especialmente no estado do Mato Grosso, o maior produtor de soja do Brasil. Dado que as safras estão sujeitas a grande variabilidade regional (tipos de solo, manejo) e choques temporais (secas severas, El Niño), os métodos tradicionais de modelagem e as validações convencionais podem falhar ou gerar falso otimismo.

Este projeto tem como objetivo desenvolver e validar um modelo preditivo, especificamente o algoritmo Random Forest Regressor, capaz de estimar o rendimento da soja de maneira generalizável. O estudo integra informações de produção do IBGE com séries temporais extraídas via Google Earth Engine, contemplando índices de vegetação (NDVI, EVI), temperatura de superfície (LST) e variáveis climáticas (TerraClimate).

O intuito deste relatório aos orientadores é fornecer as evidências metodológicas de que o modelo desenvolvido não apenas apresenta alta precisão preditiva, mas também cumpre rigorosamente as premissas estatísticas necessárias (ausência de vieses sistêmicos espaciais/temporais) e comprova seu poder de generalização no tempo e no espaço.

---

### Metodologia ou Material e Métodos
O modelo preditivo de Random Forest foi alimentado com variáveis agrometeorológicas orbitais divididas em duas janelas fenológicas cruciais: J1 (Crescimento Vegetativo) e J2 (Floração e Enchimento de Grãos). Para garantir a confiabilidade matemática e agronômica e impedir o *overfitting*, foram aplicadas as seguintes metodologias de avaliação e testes estatísticos:

1. **Validação Cruzada Espacial (Leave-Municipality-Out)**: A base de dados foi particionada via *GroupKFold* (5-folds). Safras inteiras de um mesmo município foram mantidas no grupo de teste, impedindo o modelo de "decorar" atributos puramente geográficos, testando sua capacidade real de mapear a resposta da cultura ao clima.
2. **Validação Cruzada Temporal (Walk-Forward e Out-of-Time)**: Utilizou-se técnica de janela expansiva, em que o modelo foi treinado com o histórico progressivo para prever valores do ano seguinte. Foi realizada também a previsão cega nas safras de 2022 e 2023, treinando exclusivamente o período de 2008 a 2021.
3. **Testes de Suposições Espaciais e Residuais**:
   - *Autocorrelação Espacial*: Aplicação do Índice de Moran Global sobre a magnitude e sinal dos resíduos usando matriz de vizinhos ($k=4$), para verificar possíveis falhas ("vazamento espacial") na captura de efeitos geográficos pelo satélite.
   - *Teste de Heterocedasticidade*: Teste formal por meio da Correlação de Spearman entre as estimativas e a magnitude do erro residual.
   - *Teste de Multicolinearidade*: Medição do *Variance Inflation Factor* (VIF) no pacote `statsmodels`.
4. **Interpretabilidade e Explicabilidade (XAI)**: A extração das métricas marginais aditivas foi conduzida utilizando o *SHAP TreeExplainer*, permitindo destrinchar o impacto individual de cada variável e comprovar se as decisões matemáticas respeitam a ecofisiologia da soja.

---

### Resultados Preliminares
Os testes realizados confirmaram que o modelo suporta estresse em novas instâncias, evidenciando robustez agronômica. 

Na **Validação Cruzada Espacial**, o erro percentual (WMAPE) estabilizou-se na excelente faixa de **5.27%**. Esse valor em instâncias espacialmente virgens prova que as variáveis multiespectrais escolhidas são autossuficientes em parametrizar a biologia da planta em diferentes coordenadas. 
Na análise **Out-of-Time (Temporal e de Amplitude)**, a previsão obteve um WMAPE de 6.00% com Erro Absoluto Médio (MAE) de 216 kg/ha. O gráfico de resíduos formou um "ruído branco" em torno de zero, não demonstrando tendência de subestimação em anos de quebra ou superestimação em anos de recorde produtivo.

Em relação ao comportamento estrito dos erros:
- **Autocorrelação Espacial**: O Índice de Moran Global rejeitou a hipótese de autocorrelação espacial dos erros. A distribuição foi considerada aleatória (Ruído Branco Espacial), provando empiricamente que as camadas de sensoriamento remoto (NDVI, LST) internalizaram de forma adequada o efeito da localização, eliminando a necessidade de componentes de *Krigagem* associados.
- **Heterocedasticidade**: O teste computou P-Valor de **0.0908**, superior a $\alpha = 0.05$. Com variância do erro constante e confirmada, o grau de incerteza da plataforma será equivalente para pequenos produtores prejudicados pela seca e para municípios em patamares hiper-produtivos.
- **Multicolinearidade e SHAP**: Detectou-se VIF elevado para o vigor multiespectral correlacionado (NDVI x EVI). Mesmo o modelo Random Forest não perdendo acurácia preditiva com isso, a explicabilidade necessitou de tratamento. A aplicação do método **SHAP** contornou esse problema e provou alta consistência agronômica. Os valores globais SHAP identificaram que, com exceção da variável sintética cronológica "ano" (vital para amortecer o *trend* de tecnologias em sementes), o clima medido na **Janela 2 (Enchimento e Floração)** domina as decisões da árvore de decisão. Sinais computados pelo satélite que expressam déficit hídrico (`def_j2`) e altas ondas de calor (`tmean_j2`) causaram severas penalidades (contribuição negativa) à estimativa da safra de soja do pixel correspondente, de acordo exato com as publicações de agrometeorologia.

---

### Conclusão(ões) ou Considerações Finais
As métricas e testes implementados validam fortemente as metodologias em construção e garantem que o Random Forest Regressor treinado suporta o rigor acadêmico demandado para este trabalho. A adoção de validações geo-espaciais e testes estatísticos complexos evitou com sucesso armadilhas comuns em modelagem ambiental, como falsas confianças associadas a *overfitting*. A extração do conhecimento agrometeorológico transparente via SHAP encerra preocupações de opacidade matemática ("caixa-preta"), recomendando o avanço natural da pesquisa à formatação dos seus produtos finais de publicação e visualização.

---

### Referências

ABATZOGLOU, J. T. et al. TerraClimate, a high-resolution global dataset of monthly climate and climatic water balance from 1958-2015. *Scientific Data*, 5(1), 1-12, 2018.

BREIMAN, L. Random Forests. *Machine Learning*, v. 45, n. 1, p. 5-32, 2001.

GORELICK, N. et al. Google Earth Engine: Planetary-scale geospatial analysis for everyone. *Remote Sensing of Environment*, v. 202, p. 18-27, 2017.

IBGE. Sistema IBGE de Recuperação Automática (SIDRA) – Pesquisa da Produção Agrícola Municipal (PAM). Rio de Janeiro, 2023.

LUNDBERG, S. M.; LEE, S. A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, v. 30, 2017.

MEYER, H.; PEBESMA, E. Machine learning-based global maps of ecological variables and the challenge of assessing them. *Nature Communications*, v. 13, n. 1, p. 2208, 2022.

PEDREGOSA, F. et al. Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, p. 2825-2830, 2011.

PEREIRA, R. H. M. et al. geobr: pacote R e Python para baixar conjuntos de dados espaciais oficiais do Brasil. *IPEA*, 2019.

REY, S. J.; ANSELIN, L. PySAL: A Python Library of Spatial Analytical Methods. *The Review of Regional Studies*, v. 37, n. 1, p. 5-27, 2007.
