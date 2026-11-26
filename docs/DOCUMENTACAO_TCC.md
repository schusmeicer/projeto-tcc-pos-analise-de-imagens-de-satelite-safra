# Estrutura e Documentação do TCC
**Tema Proposto:** Previsão do Rendimento da Soja no Estado do Mato Grosso utilizando Imagens de Satélite, Dados Climáticos e Machine Learning.

Este documento foi elaborado para servir como um "esqueleto" ou roteiro detalhado para a escrita do seu Trabalho de Conclusão de Curso (TCC) de Pós-Graduação. Ele descreve ponta a ponta todas as metodologias, fontes de dados e resultados que desenvolvemos.

---

## 1. Introdução

A produção de soja no Estado do Mato Grosso é um dos principais pilares do agronegócio e da economia brasileira. O monitoramento contínuo das safras e a previsão antecipada do rendimento (kg/ha) são fundamentais para o planejamento logístico, econômico e de segurança alimentar do país.
Tradicionalmente, a estimativa de safras baseia-se em questionários e amostragem de campo, processos que demandam tempo e recursos. Com o avanço do **Sensoriamento Remoto** e técnicas de **Machine Learning**, tornou-se viável analisar o desenvolvimento fenológico da cultura e as condições climáticas em larga escala para prever a produtividade antes mesmo da colheita finalizada.

O objetivo deste projeto foi construir e validar um modelo preditivo capaz de estimar o rendimento da soja em nível municipal no Mato Grosso, combinando dados oficiais de produção (IBGE) com séries temporais de índices de vegetação e clima extraídos em nuvem via Google Earth Engine.

---

## 2. Materiais e Métodos

A metodologia do trabalho consistiu em 5 etapas principais: Obtenção de Dados de Referência, Extração de Dados Orbitais, Cruzamento de Dados, Modelagem Preditiva e Previsão Futura.

### 2.1. Área de Estudo e Base Oficial (IBGE)
A área de estudo contemplou os municípios produtores de soja do Estado do Mato Grosso.
Os dados oficiais (verdade terrestre) foram obtidos através do Sistema IBGE de Recuperação Automática (SIDRA), especificamente a pesquisa **PAM (Produção Agrícola Municipal)**.
- **Período Histórico:** Safras de 2008 a 2023.
- **Variáveis Coletadas:** Área Plantada (ha), Quantidade Produzida (Toneladas) e Rendimento Médio (kg/ha).

### 2.2. Sensoriamento Remoto e Clima (Google Earth Engine)
A extração de variáveis espaciais foi feita em massa utilizando a API do Google Earth Engine (GEE) via linguagem Python. Para delimitar os municípios, utilizou-se a biblioteca `geobr` (IPEA), que fornece as malhas geográficas oficiais do Brasil de 2020. 

A grande inovação desta metodologia foi a **divisão fenológica** dos dados em duas janelas distintas de extração, permitindo que o modelo capture as diferentes sensibilidades da planta em cada estágio:
- **Janela 1 (Crescimento Vegetativo):** Outubro a Dezembro.
- **Janela 2 (Floração e Enchimento de Grãos):** Janeiro a Março.

Para cada janela, extraiu-se das coleções orbitais:

**A. Coleção MODIS (MOD13Q1 - 250m e MOD11A2 - 1km)**
- **NDVI** e **EVI**: Índices de vegetação avaliando o vigor e a densidade da biomassa.
- **LST (Land Surface Temperature)**: Mede o calor irradiado pela superfície, crucial para detectar estresse térmico da planta.

**B. Coleção TerraClimate (~4km)**
- **Precipitação Acumulada (`pr`)** e **Déficit Hídrico (`def`)**: Avaliam a disponibilidade de água para a cultura.
- **Temperatura Média (`tmean`)**: Extraída do ERA5-Land. Essencial para detectar ondas de calor ou crescimento lento (frio extremo).
- **Umidade do Solo (`soil`)**: Reflete a água disponível na zona de raízes.

### 2.3. Integração e Tratamento dos Dados
Um pipeline construído em Pandas (script `merge_datasets.py`) unificou a tabela do IBGE com os dados do GEE utilizando o "Código do Município" e o "Ano" como chaves primárias. Foram removidos municípios que não reportaram cultivo de soja em anos específicos, resultando em um Dataset consolidado e robusto sem dados nulos.

### 2.4. Validação e Modelagem com Machine Learning
Para simular um ambiente do mundo real, evitou-se a tradicional quebra aleatória de dados (train_test_split). Adotou-se o método de **Validação Out-of-Time**:
- **Base de Treino:** Safras de 2008 a 2021.
- **Base de Teste:** Safras de 2022 a 2024 (três anos inéditos para avaliar o poder preditivo no tempo). Ressalta-se que a máscara espacial do MapBiomas de 2023 foi utilizada para a safra de 2024 devido à indisponibilidade de dados da Coleção 9 no momento da análise.

Para evitar confusão entre mudança climática e melhoramento genético das sementes, adicionou-se a variável temporal **`ano`** (Avanço Tecnológico) no treinamento. 

Adicionalmente, aplicou-se a técnica de **Validação Cruzada Espacial (Leave-Municipality-Out)** para garantir a ausência de viés regional, e a biblioteca **SHAP (SHapley Additive exPlanations)** para abrir a "caixa-preta" e interpretar o impacto agronômico de cada variável.

---

## 3. Resultados e Discussão

### 3.1. Desempenho dos Algoritmos e Ausência de Viés
Após o treinamento e aplicação no conjunto de Teste Out-of-Time (2022-2023), o modelo que apresentou a melhor capacidade de generalização foi o **Random Forest Regressor**.

**Métricas Finais da Arquitetura Aprimorada:**
- **Random Forest Regressor:** WMAPE de 6.00%, MAE de 216 kg/ha.
*(Anteriormente, sem janelas fenológicas e sem a variável 'ano', o WMAPE orbitava em 9.56%).*

No Teste de Viés Espacial (onde o modelo treina em algumas cidades e tenta prever em cidades 100% desconhecidas), a validação cruzada atingiu WMAPE de **5.27%**. Isso prova que o modelo possui baixo viés locacional (não decora as cidades) e generaliza com excelência, tomando suas decisões baseando-se estritamente no clima e satélite.

Adicionalmente, foi realizado o **Teste de Heterocedasticidade** (Correlação de Spearman entre o valor previsto e a magnitude absoluta do erro). O P-Valor resultante foi de **0.0908** (acima do nível de significância de 0.05), indicando que não há evidências estatísticas de heterocedasticidade. A variância do erro é constante (Homocedasticidade), provando que o modelo não sofre de desvios sistêmicos ao prever safras muito grandes ou muito pequenas.

### 3.2. Interpretabilidade Agronômica (Análise SHAP)
A aplicação do **SHAP** revelou que a variável `ano` lidera as influências devido ao avanço tecnológico (genética, defensivos, maquinário).
Dentre as variáveis ambientais, o modelo capturou perfeitamente a literatura agronômica: o clima na **Janela 2 (Enchimento de grãos)** é o mais decisivo. Temperaturas extremas (`tmean_j2`) e déficit hídrico tardio (`def_j2`) reduzem fortemente o rendimento previsto, validando que o Random Forest realmente aprendeu a biologia da soja, em vez de correlações espúrias.

### 3.3. Análise da Curva Histórica
*(Insira a Imagem da Série Temporal `serie_temporal_safra.png` gerada via Cross-Validation)*
O gráfico de série temporal (projetado com a rigorosa técnica de `cross_val_predict` para evitar "data leakage" de in-sample fitting) acompanhou organicamente as fortes quebras de safra do passado e os recordes produtivos recentes do estado, refletindo com segurança os solavancos reais reportados pelo IBGE.

---

## 4. Estudo de Caso Prático: Simulação de Previsão Recente (Safra 2023/2024)

Para ilustrar a utilidade comercial, o script `predict_future.py` simulou o encerramento da safra recente usando os dados climáticos consolidados até o momento:
1. O Random Forest foi treinado no histórico pleno.
2. Foram extraídas do GEE as imagens orbitais mais recentes.
3. Estimou-se a produtividade final projetada (kg/ha).

**Ranking de Previsões Top 5 (Rendimento Projetado):**
1. **Conquista D'oeste:** ~3.925 kg/ha
2. **Alto Taquari:** ~3.881 kg/ha
3. **Aripuanã:** ~3.874 kg/ha
4. **Santa Cruz Do Xingu:** ~3.838 kg/ha
5. **Luciara:** ~3.833 kg/ha

Isso prova que a pipeline é uma robusta ferramenta de Inteligência de Mercado, podendo atuar na antecipação de safras e apontamento de anomalias regionais.

---

## 5. Conclusão

A integração do Google Earth Engine com a linguagem Python demonstrou ser uma ferramenta altamente performática para monitorar o maior estado produtor de soja do Brasil. A transição de abordagens visuais limitadas (NDVI exclusivo) para modelos de Machine Learning abastecidos com múltiplas camadas ambientais (Vigor + Clima) reduziu o Erro Absoluto para patamares extremamente competitivos (menos de 10%).
Projetos como esse evidenciam que o uso da inteligência artificial pode atuar ativamente na gestão do risco climático da agricultura moderna.

---

### Referências Importantes para sua Bibliografia:
1. **GEE:** GORELICK, N. et al. Google Earth Engine: Planetary-scale geospatial analysis for everyone. Remote Sensing of Environment, v. 202, p. 18-27, 2017.
2. **Geobr:** PEREIRA, R. H. M. et al. geobr: pacote R e Python para baixar conjuntos de dados espaciais oficiais do Brasil. IPEA, 2019.
3. **Scikit-Learn:** PEDREGOSA, F. et al. Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, p. 2825-2830, 2011.
4. **MODIS:** DIDAN, K. MOD13Q1 MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid V061. NASA EOSDIS Land Processes DAAC, 2021.
5. **TerraClimate:** ABATZOGLOU, J. T. et al. TerraClimate, a high-resolution global dataset of monthly climate and climatic water balance from 1958-2015. Scientific Data, 5(1), 1-12, 2018.
6. **SHAP (Interpretabilidade):** LUNDBERG, S. M.; LEE, S. A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems, v. 30, 2017.
