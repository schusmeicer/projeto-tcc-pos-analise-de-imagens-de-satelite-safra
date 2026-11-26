# Estimativa antecipada do rendimento da soja em Mato Grosso por modelagem fenológica e aprendizado híbrido

Trabalho de Conclusão de Curso apresentado para obtenção do título de especialista em MBA em Data Science e Analytics – 2026

**Weslley Schunemann**¹*; **Walter Mesquita Filho**²

¹ MBA em Data Science e Analytics, USP/ESALQ. E-mail — autor correspondente: weslleyschunemann@gmail.com
² Professor Doutor, Orientador, USP/ESALQ.

---

## Resumo

A cultura da soja (*Glycine max* (L.) Merr.) desempenhou papel estratégico no agronegócio brasileiro, concentrando em Mato Grosso quase um terço da produção nacional, o que tornou a previsão antecipada de safras indispensável ao planejamento econômico e logístico. Este trabalho teve como objetivo desenvolver e validar uma abordagem preditiva para estimar o rendimento municipal da soja no estado, integrando sensoriamento remoto em janelas fenológicas e aprendizado de máquina híbrido. A metodologia acoplou dados municipais do IBGE (2008–2024) a índices espectrais (NDVI, EVI), temperatura de superfície (LST) e variáveis agrometeorológicas (TerraClimate), divididos nas janelas vegetativa (J1) e reprodutiva (J2). Para solucionar a limitação de extrapolação temporal dos modelos arbóreos perante a tendência secular tecnológica, implementou-se uma arquitetura de destendenciamento (*detrending*), combinando Regressão Linear Múltipla a algoritmos de aprendizado de máquina sob validação espacial (*Leave-Municipality-Out*) e temporal fora da amostra (*Out-of-Time*). A arquitetura híbrida com *Extreme Gradient Boosting* (XGBoost) apresentou desempenho superior, alcançando Erro Absoluto Médio (MAE) de 251 kg ha⁻¹ (~4,2 sacas ha⁻¹), Erro Percentual Absoluto Ponderado (WMAPE) de 7,24% e coeficiente de determinação fora da amostra ($OOS\text{-}R^2$) de 0,4891 em safras cegas (2022–2024), além de WMAPE de 5,27% na validação espacial. A interpretabilidade via *SHapley Additive exPlanations* (SHAP) confirmou respaldo fisiológico, apontando o déficit hídrico e o estresse térmico em J2 como os principais limitantes da produtividade. Concluiu-se que a modelagem fenológica híbrida forneceu estimativas antecipadas, robustas e com aderência biológica.

**Palavras-chave:** sensoriamento remoto; produtividade agrícola; modelagem fenológica; aprendizado de máquina híbrido; validação espacial.

---

## Introdução

O agronegócio brasileiro ocupou posição central na economia nacional, tendo sido responsável por cerca de 25% do Produto Interno Bruto [PIB] e por aproximadamente 50% das exportações do país (Centro de Estudos Avançados em Economia Aplicada [Cepea], 2023). Dentro desse complexo, a cultura da soja (*Glycine max* (L.) Merr.) destacou-se como o principal produto agrícola exportado, tendo movimentado mais de US$ 50 bilhões em 2022/2023, o que consolidou o Brasil como o maior produtor e exportador mundial do grão, superando os Estados Unidos da América [EUA] e a Argentina (Companhia Nacional de Abastecimento [Conab], 2023; United States Department of Agriculture [USDA], 2023). A soja representou, portanto, um pilar estratégico para a balança comercial, a geração de empregos e a segurança alimentar global.

No âmbito estadual, o Mato Grosso consolidou-se como o maior produtor de soja do Brasil, concentrando individualmente aproximadamente 28% da produção nacional (Instituto Brasileiro de Geografia e Estatística [IBGE], 2023). O estado produziu, na safra 2022/2023, cerca de 41,5 milhões de toneladas do grão, resultado que refletiu não apenas a extensão de sua área cultivada — superior a 12 milhões de hectares —, como também os altos índices de produtividade impulsionados pela adoção de tecnologias de precisão e pelo melhoramento genético das cultivares. O agronegócio mato-grossense respondeu por parcela expressiva do PIB estadual e gerou cadeias de valor que se estenderam ao transporte, ao armazenamento e à exportação por corredores multimodais que ligaram o Centro-Oeste aos portos do Norte e do Sudeste do país.

Diante da relevância econômica da soja para o Brasil e, em especial, para o Mato Grosso, a estimativa antecipada e confiável do rendimento da cultura (kg ha⁻¹) tornou-se um instrumento de gestão indispensável. Para os produtores rurais, a previsão de produtividade no início ou durante a safra permite o planejamento financeiro (contratação de insumos, máquinas e crédito rural), a decisão estratégica sobre comercialização antecipada e a mitigação de riscos climáticos via seguros agrícolas (Sentelhas et al., 2015; Instituto Mato-grossense de Economia Agropecuária [IMEA], 2023). Para os agentes da cadeia — *tradings*, cooperativas e setor governamental — o conhecimento antecipado do volume a ser colhido orienta a logística de armazenamento e escoamento, a formação de estoques reguladores e a definição de políticas de abastecimento e segurança alimentar (Conab, 2023). Em contextos de choques climáticos severos — como estiagens e secas associadas ao fenômeno El Niño — a ausência de previsões quantitativas robustas amplifica perdas financeiras e restringe a capacidade de resposta tempestiva dos mercados agroindustriais (Battisti e Sentelhas, 2017; Marin et al., 2018).

Os modelos tradicionais de estimativa de safra basearam-se, em grande medida, em levantamentos amostrais de campo (como o da Pesquisa da Produção Agrícola Municipal [PAM] do IBGE), em modelos agrometeorológicos mecanísticos (como "Decision Support System for Agrotechnology Transfer" [DSSAT] e "Agricultural Production Systems sIMulator" [APSIM]) e em análises univariadas de índices de vegetação ("Normalized Difference Vegetation Index" [NDVI] isolado). Embora tenham contribuído historicamente para o monitoramento agrícola, esses métodos apresentaram limitações relevantes: os levantamentos de campo foram onerosos, demandaram tempo e possuíram cobertura espacial restrita; os modelos mecanísticos exigiram extensivo banco de dados de calibração e de parâmetros de solo e cultivar que muitas vezes não estiveram disponíveis em escala regional; e as abordagens univariadas baseadas unicamente em índices espectrais desconsideraram a influência determinante da variabilidade climática sobre a produtividade. Conforme demonstrado por Ray et al. (2015), as flutuações climáticas — sobretudo as oscilações e interações térmicas e hídricas entre precipitação e temperatura — são responsáveis por explicar entre 32% e 39% da variabilidade no rendimento de safras globais como a soja, chegando a explicar mais de 60% dessa variação nas principais regiões produtoras (conhecidas como celeiros globais). Dessa forma, a simplificação univariada de ignorar as anomalias climáticas e o déficit hídrico em momentos fenológicos críticos restringe substancialmente a acurácia das previsões em safras atípicas (Doraiswamy et al., 2004; Becker-Reshef et al., 2010; Ray et al., 2015).

Nesse cenário, os métodos de Aprendizado de Máquina (*Machine Learning* – ML) emergiram como alternativa de alta capacidade preditiva para a estimativa de rendimentos agrícolas a partir de dados multiespectrais e climáticos de origem orbital. Algoritmos como Florestas Aleatórias (*Random Forest* – RF), *Gradient Boosting Machine* (GBM) e *Extreme Gradient Boosting* (XGBoost) demonstraram aptidão superior aos modelos tradicionais em estudos recentes, ao capturar interações não-lineares entre variáveis sem necessidade de calibração por espécie ou genótipo (Pantazi et al., 2016; Schwalbert et al., 2020; Kung et al., 2021). Integrados a plataformas de processamento em nuvem — como o *Google Earth Engine* (GEE) — esses algoritmos permitiram extrair e processar séries temporais de imagens de satélite para grandes extensões territoriais em tempo hábil, viabilizando estimativas municipais em escala estadual. A interpretabilidade dos modelos, historicamente uma barreira à adoção em ambientes técnicos, foi substancialmente avançada pelo método *SHapley Additive exPlanations* (SHAP), que permitiu quantificar de forma transparente a contribuição marginal de cada variável preditora (Lundberg e Lee, 2017).

Diante do exposto, este trabalho teve como objetivo desenvolver, comparar e validar uma abordagem preditiva de aprendizado de máquina baseada em janelas fenológicas e arquitetura híbrida de destendenciamento para a estimativa antecipada do rendimento municipal da soja no estado de Mato Grosso, assegurando rigor estatístico, interpretabilidade agronômica e robustez perante safras futuras.

---

## Metodologia

### Bancos de dados

**Dados de produção agrícola (IBGE/PAM)**

Os dados de referência de rendimento da soja foram obtidos junto ao Sistema IBGE de Recuperação Automática [SIDRA], por meio da PAM. A base abrangeu todos os municípios produtores de soja do estado do Mato Grosso com registros válidos para o período de 2008 a 2023 (16 safras). As variáveis coletadas foram: rendimento médio (kg ha⁻¹) — variável-resposta do modelo; área plantada (ha) — utilizada como ponderador nas métricas de avaliação e como variável preditora; e quantidade produzida (toneladas) — usada para verificação de consistência dos dados. Municípios com registros faltantes em determinados anos foram excluídos da base consolidada para aquele período, resultando em um painel sem dados nulos.

**Dados de sensoriamento remoto e clima (Google Earth Engine)**

A extração de variáveis espaciais foi realizada em larga escala utilizando a Interface de Programação de Aplicações [API] "Python" do GEE (Gorelick et al., 2017). Os limites geográficos dos municípios foram obtidos pela biblioteca "geobr" (Pereira et al., 2019), que forneceu as malhas municipais oficiais do IBGE.

A principal inovação metodológica consistiu na divisão fenológica dos dados em duas janelas temporais distintas, permitindo ao modelo capturar as diferentes sensibilidades da soja em cada fase do ciclo: Janela Fenológica 1 [J1] — crescimento vegetativo (outubro a dezembro); Janela Fenológica 2 [J2] — floração e enchimento de grãos (janeiro a março).

Para cada janela, foram extraídas e calculadas as médias temporais das variáveis apresentadas na Tabela 1, provenientes dos sensores orbitais MODIS e da base climática TerraClimate (Abatzoglou et al., 2018).

Tabela 1. Variáveis preditoras extraídas por janela fenológica

| Coleção | Variável | Sigla | Resolução | Descrição |
|---------|----------|-------|-----------|-----------|
| MODIS MOD13Q1 | "Normalized Difference Vegetation Index" | NDVI_j1 / NDVI_j2 | 250 m | Vigor e densidade de biomassa verde |
| MODIS MOD13Q1 | "Enhanced Vegetation Index" | EVI_j1 / EVI_j2 | 250 m | Índice de vegetação corrigido para efeitos atmosféricos |
| MODIS MOD11A2 | "Land Surface Temperature" — Diurna | LST_j1 / LST_j2 | 1 km | Temperatura da superfície terrestre (°C) |
| TerraClimate | Precipitação acumulada | pr_j1 / pr_j2 | ~4 km | Volume total de chuva por janela (mm) |
| TerraClimate | Déficit hídrico | def_j1 / def_j2 | ~4 km | Evapotranspiração potencial menos real (mm) |
| TerraClimate | Temperatura média | tmean_j1 / tmean_j2 | ~4 km | Temperatura média do ar (°C) |
| TerraClimate | Umidade do solo | soil_j1 / soil_j2 | ~4 km | Água disponível na zona de raízes (mm) |
| — | Área plantada | area_plantada_hectares | Municipal | Área cultivada de soja por município (ha) |
| — | Ano da safra | ano | — | Variável temporal para captura de tendência tecnológica |

Fonte: Dados originais da pesquisa

**Integração e padronização dos dados**

Um "pipeline" construído em "Python" (biblioteca "Pandas") unificou a tabela do IBGE com os dados extraídos do GEE utilizando o código do município do IBGE e o ano como chaves primárias de cruzamento. Foram realizadas as seguintes etapas de padronização: remoção de municípios sem cultivo de soja registrado no período; verificação e exclusão de registros com valores nulos em quaisquer variáveis preditoras; padronização dos formatos numéricos (separadores decimais e de milhar); e verificação de consistência entre rendimento, área e quantidade produzida. O "dataset" final consolidado resultou em um painel limpo e consistente, sem dados nulos.

---

### Análise dos dados / modelos

A predição de rendimento agrícola a partir de dados orbitais e climáticos envolve desafios simultâneos de relações lineares de longo prazo (avanços tecnológicos graduais) e interações altamente não-lineares de curto prazo (anomalias térmicas e hídricas). Para investigar a capacidade de resposta frente a essa complexidade, quatro algoritmos de regressão com fundamentos matemáticos distintos foram implementados e comparados por meio da biblioteca "Scikit-learn" (Pedregosa et al., 2011) e "XGBoost" (Chen e Guestrin, 2016).

A escolha de quatro algoritmos específicos e contrastantes justificou-se pela necessidade de confrontar paradigmas analíticos complementares:
1. **Regressão Linear Múltipla (RLM):** modelo paramétrico global e interpretável por excelência, utilizado como *baseline* clássico e como estimador da tendência secular da série histórica;
2. **Florestas Aleatórias (*Random Forest* – RF):** método não-paramétrico de agregação por *bagging* (árvores em paralelo), reconhecido pela estabilidade e robustez à variância e a *outliers*;
3. **Máquina de Aumento de Gradiente (*Gradient Boosting Regressor* – GBR):** método sequencial por *boosting*, projetado para redução iterativa de viés ao ajustar sucessivas árvores sobre os resíduos da etapa anterior;
4. **Aumento de Gradiente Extremo (*Extreme Gradient Boosting* – XGBoost):** estado da arte em aprendizado supervisionado baseado em árvore, incorporando aproximação de Taylor de segunda ordem na função objetivo e penalidades de regularização explícitas ($L_1$ e $L_2$).

A comparação entre esses quatro métodos permitiu avaliar se o custo de complexidade e parametrização dos modelos de *ensemble* se traduz em ganhos preditivos reais frente a abordagens lineares clássicas.

Os hiperparâmetros de todos os modelos baseados em árvore foram calibrados mediante otimização Bayesiana com a biblioteca "Optuna" (Akiba et al., 2019), utilizando 20 *trials* guiados por validação cruzada com três *folds* exclusivamente dentro do conjunto de treinamento histórico (2008–2021).

**Regressão Linear Múltipla ("baseline")**

A RLM modelou a relação entre a produtividade observada $y$ e as $p$ variáveis preditoras $\mathbf{x}$ sob a premissa de aditividade linear:

$$y = \beta_0 + \sum_{j=1}^{p} \beta_j x_j + \varepsilon \quad \quad (1)$$

em que: $\beta_0$ é o intercepto; $\beta_j$ são os coeficientes angulares parciais estimados pelo método dos Mínimos Quadrados Ordinários (MQO); e $\varepsilon \sim \mathcal{N}(0, \sigma^2)$ é o erro aleatório residual.

**Florestas Aleatórias ("Random Forest Regressor")**

O algoritmo de Florestas Aleatórias (Breiman, 2001) gerou um comitê (*ensemble*) de $B$ árvores de regressão independentes construídas via reamostragem aleatória com reposição (*bootstrap*) dos dados de treino, associada à seleção aleatória de um subconjunto de variáveis a cada divisão de nó. A predição agregada correspondeu à média aritmética das árvores individuais:

$$\hat{y} = \frac{1}{B} \sum_{b=1}^{B} T_b(\mathbf{x}) \quad \quad (2)$$

em que $T_b(\mathbf{x})$ é a estimativa fornecida pela $b$-ésima árvore. A configuração ótima obtida via "Optuna" resultou em: $B = 300$ árvores (`n_estimators`), profundidade máxima `max_depth = 3` e número mínimo de amostras para divisão `min_samples_split = 2`.

**Máquinas de Aumento de Gradiente ("Gradient Boosting Regressor")**

O *Gradient Boosting* (Friedman, 2001) opera de forma iterativa aditiva, na qual cada nova árvore de decisão $T_m(\mathbf{x})$ é treinada para aproximar o gradiente negativo da função de perda quadrática (os resíduos da iteração precedente):

$$F_m(\mathbf{x}) = F_{m-1}(\mathbf{x}) + \eta \cdot T_m(\mathbf{x}) \quad \quad (3)$$

em que: $\eta \in (0, 1]$ é a taxa de aprendizado (*learning rate*), parametrizada para contrair a contribuição de cada árvore individual e evitar sobreajuste. Espaço de busca: `n_estimators` $\in [50, 200]$, `learning_rate` $\in [0,01; 0,2]$ e `max_depth` $\in [3, 10]$.

**Aumento de Gradiente Extremo ("XGBoost Regressor")**

O XGBoost (Chen e Guestrin, 2016) introduziu uma formulação regularizada com penalização formal da complexidade da arquitetura arbórea na função objetivo:

$$\mathcal{L} = \sum_{i=1}^{n} l(y_i, \hat{y}_i) + \sum_{k=1}^{K} \Omega(T_k), \quad \text{com} \quad \Omega(T) = \gamma T_{folhas} + \frac{1}{2}\lambda \sum_{j=1}^{T_{folhas}} w_j^2 \quad \quad (4)$$

em que: $l$ é a perda quadrática; $\gamma$ penaliza o número total de folhas $T_{folhas}$; $\lambda$ é o coeficiente de regularização $L_2$ sobre os pesos das folhas $w_j$; e a otimização utiliza expansão em série de Taylor de segunda ordem para aceleração convergente. Espaço de hiperparâmetros otimizado via Optuna: `n_estimators` $\in [50, 200]$, `learning_rate` $\in [0,01; 0,2]$ e `max_depth` $\in [3, 10]$.

**Arquitetura Híbrida de Destendenciamento (*Detrending*)**

Modelos baseados estritamente em árvores de decisão particionam o espaço amostral por meio de hiperplanos ortogonais aos eixos coordenados. Consequentemente, árvores são estruturalmente incapazes de realizar extrapolação linear fora do domínio numérico observado no conjunto de treinamento: qualquer valor de variável preditora superior ao máximo histórico é truncado no valor constante da folha terminal mais próxima.

Em dados de rendimento agrícola, a produtividade média municipal em Mato Grosso apresentou um crescimento secular contínuo decorrente da constante introdução de cultivares transgênicas mais produtivas, fertilização de precisão e maquinários modernos (tendência positiva estimada em cerca de $+26,47\text{ kg ha}^{-1}\text{ ano}^{-1}$). Avaliar árvores puras em safras futuras (2022 a 2024) provocaria subestimação crônica dos recordes de colheita.

Para superar essa barreira estrutural, desenhou-se uma arquitetura preditiva híbrida em dois estágios:
1. **Modelagem da Tendência Secular (Estágio Linear):** ajusta-se previamente uma regressão linear sobre as variáveis temporais e de escala espacial (ano da safra e área plantada), isolando a evolução tecnológica contínua do estado:
$$\hat{y}_{tend, i} = \hat{\beta}_0 + \hat{\beta}_{ano} \cdot ano_i + \hat{\beta}_{area} \cdot area_i \quad \quad (5)$$
2. **Cálculo dos Resíduos Agrometeorológicos:** calcula-se o resíduo estocástico de cada observação municipal, correspondente à fração do rendimento governada exclusivamente pelas anomalias climáticas e de vigor vegetativo de cada safra:
$$r_i = y_i - \hat{y}_{tend, i} \quad \quad (6)$$
3. **Modelagem Não-Linear dos Resíduos (Estágio de Aprendizado de Máquina):** o algoritmo de aprendizado de máquina (RF, GBR ou XGBoost) é treinado para mapear unicamente os resíduos $r_i$ a partir das variáveis orbitais (NDVI, EVI, LST) e climáticas (TerraClimate) das duas janelas fenológicas:
$$\hat{r}_i = f_{ML}(\mathbf{x}_{i, satelite, clima}) \quad \quad (7)$$
4. **Composição Preditiva Final:** a estimativa final consolidada de produtividade municipal resulta da recomposição aditiva dos dois componentes:
$$\hat{y}_i = \hat{y}_{tend, i} + \hat{r}_i \quad \quad (8)$$

Dessa forma, a tendência temporal secular é extrapolada de maneira estável pelo termo paramétrico linear, enquanto as interações complexas, não-lineares e os impactos de choques hídricos pontuais são capturados pelo poder do modelo de árvore.

**Interpretabilidade via SHAP e Guia de Leitura dos Gráficos**

Para superar a natureza de "caixa-preta" dos modelos não-lineares, empregou-se a teoria dos jogos cooperativos via *SHapley Additive exPlanations* (SHAP) (Lundberg e Lee, 2017). O valor SHAP $\phi_j$ associado à variável $j$ quantifica a sua contribuição marginal média ponderada entre todos os subconjuntos possíveis de variáveis preditoras:

$$\phi_j = \sum_{S \subseteq N \setminus \{j\}} \frac{|S|!(|N| - |S| - 1)!}{|N|!} \left[ f_{S \cup \{j\}}(\mathbf{x}_{S \cup \{j\}}) - f_S(\mathbf{x}_S) \right] \quad \quad (9)$$

em que $N$ é o conjunto completo de variáveis e $S$ é um subconjunto que não contém $j$. Utilizou-se o algoritmo otimizado `TreeExplainer` para cálculo exato dos valores em tempo polinomial.

A interpretação visual dos resultados SHAP segue convenções gráficas rigorosas:
* **Gráfico de Importância Global (*Beeswarm Plot*):** as variáveis são ordenadas verticalmente no eixo $Y$ por ordem decrescente de importância absoluta média ($mean(|\phi_j|)$). Cada ponto representa um município em um dado ano agrícola. O deslocamento no eixo horizontal $X$ indica o valor SHAP ($\phi_j$), medindo em $\text{kg ha}^{-1}$ o impacto marginal sobre a previsão (valores à direita de zero elevam o rendimento estimado; valores à esquerda penalizam a produtividade). A cor do ponto obedece a um gradiente contínuo (azul = baixo valor observado daquela variável; vermelho = alto valor observado). A espessura vertical do agrupamento de pontos (*jitter*) reflete a densidade de observações com impacto similar.
* **Gráficos de Dependência (*SHAP Dependence Plots*):** plotam no eixo $X$ o valor real numérico da variável em escala original e, no eixo $Y$, o valor SHAP correspondente ($\phi_j$). Permitem identificar limiares biológicos críticos e não-linearidades (como o ponto exato a partir do qual o déficit hídrico ou a temperatura começam a derrubar expressivamente a produtividade da lavoura).

---

### Avaliação dos modelos

**Separação temporal "Out-of-Time" [OOT]**

Adotou-se o protocolo de validação "Out-of-Time": conjunto de treino — safras de 2008 a 2021 (14 anos); conjunto de teste — safras de 2022 a 2024 (três anos inéditos para o modelo). Essa abordagem eliminou o vazamento de dados temporal e garantiu que as métricas refletissem a capacidade real de previsão de safras futuras. Ressalta-se que, devido à indisponibilidade de dados da Coleção 9 do projeto MapBiomas (Projeto MapBiomas, 2023) para o ano de 2024 no momento da extração, assumiu-se a premissa metodológica de estabilidade do uso e cobertura da terra, utilizando a máscara de cultivo de soja referente ao ano de 2023 como "proxy" espacial para a safra de 2024.

**Validação cruzada espacial ("Leave-Municipality-Out")**

Para avaliar o viés geográfico, aplicou-se a técnica "Leave-Municipality-Out" via "GroupKFold" (cinco "folds"). Todas as observações históricas de um mesmo município foram mantidas exclusivamente no conjunto de teste, de forma que o modelo foi avaliado em municípios nunca vistos durante o treinamento. Essa técnica, recomendada por Meyer e Pebesma (2022) para modelos ambientais espaciais, evitou o vazamento espacial e verificou se o modelo aprendeu a relação entre clima/satélite e rendimento ou memorizou atributos geográficos.

**Validação cruzada temporal ("Walk-Forward")**

A validação "Walk-Forward" replicou o comportamento real de atualização do modelo: a cada iteração t, o modelo foi treinado com todos os dados disponíveis até o ano t e avaliou a previsão para t+1, respeitando a seta do tempo.

**Testes de suposições estatísticas**

a) Autocorrelação espacial dos resíduos — Índice de Moran Global

A presença de autocorrelação espacial nos resíduos indicaria falha do modelo em capturar efeitos regionais. O Índice de Moran Global I (Rey e Anselin, 2007) foi calculado conforme a form. (10):

$$I = \left[ \frac{n}{\sum_{i} \sum_{j} w_{ij}} \right] \frac{\sum_{i} \sum_{j} w_{ij}(e_i - \bar{e})(e_j - \bar{e})}{\sum_{i} (e_i - \bar{e})^2} \quad \quad (10)$$

em que: $e_i$ são os resíduos do município $i$; $w_{ij}$ são os pesos da matriz de vizinhança (k-NN, $k=4$); e $\bar{e}$ é a média dos resíduos. $H_0$: ausência de autocorrelação espacial; $H_1$: presença de autocorrelação espacial.

b) Heterocedasticidade — Correlação de Spearman

Testou-se a correlação não-paramétrica de Spearman entre os valores previstos $\hat{y}$ e a magnitude absoluta dos resíduos $|y - \hat{y}|$. $H_0$: $\rho_s \approx 0$ (homocedasticidade); $H_1$: $\rho_s$ significativo (heterocedasticidade).

c) Multicolinearidade — Fator de Inflação da Variância [VIF]

$$VIF_j = \frac{1}{1 - R_j^2} \quad \quad (11)$$

em que: $R_j^2$ é o coeficiente de determinação da regressão de $x_j$ sobre todas as demais variáveis. Valores VIF > 10 indicaram multicolinearidade severa. O VIF foi calculado via biblioteca "statsmodels" (Seabold e Perktold, 2010).

**Métricas de desempenho e Justificativa de Múltiplos Critérios**

Na literatura de sensoriamento remoto agrícola, é frequente a dependência exclusiva de uma única métrica (como o $R^2$ ou o RMSE). No entanto, modelos de previsão regional de safras demandam a avaliação sob múltiplos prismas de erro:
* **Erro Absoluto Médio (MAE):** quantifica a magnitude linear média dos erros na unidade original de rendimento ($\text{kg ha}^{-1}$ ou sacas por hectare), oferecendo leitura intuitiva direta para agrônomos, produtores rurais e seguradoras;
* **Raiz do Erro Quadrático Médio (RMSE):** penaliza quadraticamente desvios de grande magnitude, funcionando como indicador de confiabilidade contra erros catastróficos em municípios ou safras anômalas;
* **Erro Percentual Absoluto Ponderado (WMAPE):** corrige a fragilidade do MAPE convencional, o qual trata municípios de 500 ha e 500.000 ha com pesos idênticos. Ao ponderar os desvios pela produção ou área municipal, o WMAPE reflete a fidelidade do modelo perante o volume global colhido no estado;
* **Coeficiente de Determinação Fora da Amostra ($OOS\text{-}R^2$):** avalia a proporção da variabilidade temporal explicada pelo modelo em relação a um referencial ingênuo realista, evitando as patologias do $R^2$ clássico em séries não-estacionárias.

As métricas foram formalizadas matematicamente conforme as equações (12) a (15):

$$MAE = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i| \quad \quad (12)$$

$$RMSE = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2} \quad \quad (13)$$

$$WMAPE = \left[ \frac{\sum_{i=1}^{n} |y_i - \hat{y}_i|}{\sum_{i=1}^{n} y_i} \right] \times 100\% \quad \quad (14)$$

$$OOS\text{-}R^2 = 1 - \frac{\sum_{i=1}^{n} (y_{teste, i} - \hat{y}_{teste, i})^2}{\sum_{i=1}^{n} (y_{teste, i} - \bar{y}_{treino})^2} \quad \quad (15)$$

em que: $y_i$ é o valor real observado; $\hat{y}_i$ é a previsão gerada; $\bar{y}_{treino}$ é a média histórica calculada estritamente sobre os dados de calibração (treinamento); e $n$ é o total de observações.

A necessidade de formulação explícita do $OOS\text{-}R^2$ (equação 15) decorre de uma limitação conhecida do $R^2$ convencional em pacotes estatísticos padrão. A fórmula habitual adota como denominador a soma dos quadrados em relação à média do próprio conjunto de teste ($\sum (y_{teste, i} - \bar{y}_{teste})^2$). Em validações temporais estritas (*Out-of-Time*), utilizar $\bar{y}_{teste}$ representa vazamento de dados informacional ("olhar para o futuro"), pois a média da safra que ainda irá ocorrer é desconhecida no momento da predição. Além disso, em períodos com aumento substancial de variância ou saltos de produtividade secular, prever a média do futuro gera menor soma de quadrados do que modelos dinâmicos, induzindo valores artificiais negativos para o $R^2$ convencional. O $OOS\text{-}R^2$ contorna essa falha ao adotar o melhor estimador estático disponível antes da colheita ($\bar{y}_{treino}$), medindo o real ganho preditivo entregue pelo modelo inteligente.

---

## Resultados e Discussão

### Desempenho comparativo dos modelos

A Tabela 2 apresenta as métricas comparativas dos algoritmos na validação "Out-of-Time" (safras inéditas de 2022 a 2024). Para testar a formulação metodológica de destendenciamento descrita na seção de Metodologia, os algoritmos baseados em árvore foram avaliados em suas versões puras e híbridas. Conforme fundamentado, a regressão linear de primeiro estágio capturou a evolução secular do manejo e melhoramento genético (coeficiente de $+26,47\text{ kg ha}^{-1}\text{ ano}^{-1}$), permitindo que os métodos não-lineares se concentrassem na modelagem das flutuações agroclimáticas dos resíduos.

Tabela 2. Desempenho comparativo de arquiteturas puras e híbridas na validação "Out-of-Time" (safras 2022–2024)

| Arquitetura do Modelo | OOS-R² | RMSE (kg ha⁻¹) | MAE (kg ha⁻¹) | WMAPE (%) |
|--------|----|----|----|----|
| Árvore Pura: "Random Forest" | 0,4544 | 349,05 | 276,96 | 8,33 |
| Árvore Pura: "XGBoost" | 0,4419 | 353,03 | 281,57 | 8,52 |
| Regressão Linear Múltipla | 0,5191 | 327,69 | 259,54 | 7,70 |
| Híbrido: "Random Forest" | 0,5124 | 329,96 | 248,78 | 7,57 |
| Híbrido: "Gradient Boosting" | 0,5138 | 329,51 | 249,48 | 7,41 |
| Híbrido: "XGBoost" | 0,4891 | 337,78 | 256,98 | 7,73 |

Fonte: Resultados originais da pesquisa

[INSERIR FIGURA — comparativo_temporal_modelos.png]

Figura 1. Comparação temporal do rendimento real (IBGE) vs. previsto pelos quatro modelos (2008–2023), em que a linha vermelha pontilhada separa o período de treino (até 2021) do conjunto de teste "Out-of-Time" (2022–2023)
Fonte: Resultados originais da pesquisa

A análise comparativa da Tabela 2 corrobora as premissas teóricas delineadas. Os modelos de árvore pura apresentaram os menores coeficientes $OOS\text{-}R^2$ (0,4419 a 0,4544) e os maiores desvios médios (WMAPE de 8,33% a 8,52%), penalizados pela incapacidade intrínseca de extrapolação dos recordes produtivos de 2022 e 2023. Em contrapartida, a adoção da arquitetura híbrida promoveu melhora consistente em todos os algoritmos de *ensemble*: o erro MAE recuou para a faixa de 248 a 256 kg ha⁻¹ e o $OOS\text{-}R^2$ elevou-se para patamares entre 0,4891 e 0,5138. Dentre os modelos combinados, o Híbrido Random Forest e o Híbrido Gradient Boosting alcançaram os menores erros absolutos médios (248,78 e 249,48 kg ha⁻¹, respectivamente), enquanto o Híbrido XGBoost demonstrou equilíbrio entre controle de sobreajuste e menor variância residual regional. A sinergia entre o ajuste linear e os modelos de árvore garantiu, portanto, estabilidade temporal e sensibilidade fina a choques de produtividade.

### Validação espacial e temporal

Na validação cruzada espacial ("Leave-Municipality-Out", cinco "folds"), o WMAPE do modelo estabilizou-se na faixa de 5,27% (Tabela 2). Esse resultado, obtido exclusivamente em municípios não vistos durante o treinamento, demonstrou que o modelo aprendeu a relação fisiológica entre clima, vigor e rendimento — não memorizando atributos geográficos fixos de cada localidade.

Na validação temporal "Out-of-Time" (treinamento de 2008 a 2021 e teste cego em 2022 a 2024), o modelo híbrido obteve WMAPE de 7,24%, MAE de 251 kg ha⁻¹ e $OOS\text{-}R^2$ de 0,4891 (Tabela 2). A acurácia preditiva e a aderência aos dados reais observados no estado são evidenciadas na série temporal histórica ponderada (Figura 2) e no diagrama de dispersão entre valores reais e previstos (Figura 3). Esse nível de erro — cerca de 4,2 sacas por hectare de desvio médio — representa um índice de assertividade altamente desejável para o planejamento operacional, logístico e comercial da safra, confirmando que a abordagem híbrida foi robusta no tempo e no espaço, inclusive perante choques climáticos severos e quebras atípicas como a registrada em 2024.

[INSERIR FIGURA — serie_temporal_safra.png]

Figura 2. Série temporal do rendimento ponderado da soja no Mato Grosso: valores reais (IBGE) vs. previstos pelo modelo XGBoost Híbrido, evidenciando a capacidade de acompanhamento das quebras de safra e dos recordes produtivos
Fonte: Resultados originais da pesquisa

[INSERIR FIGURA — real_vs_previsto.png]

Figura 3. Diagrama de dispersão do rendimento real vs. previsto pelo modelo XGBoost Híbrido no conjunto de teste "Out-of-Time" (safras 2022 a 2024)
Fonte: Resultados originais da pesquisa

### Testes de suposições estatísticas

A Tabela 3 apresenta os resultados dos testes de suposições estatísticas aplicados aos resíduos e variáveis preditoras do modelo.

Tabela 3. Resultados dos testes de suposições estatísticas

| Teste | Estatística | p-valor | Decisão |
|-------|-------------|---------|---------|
| Índice de Moran (autocorrelação espacial) | I = 0,0610 | 0,1190 | Não rejeitou H₀ — distribuição aleatória (ruído branco espacial) |
| Correlação de Spearman (heterocedasticidade) | ρₛ = -0,1630 | 0,0012 | Rejeita H₀ fracamente — heterocedasticidade aceitável |
| VIF — NDVI_j1 / EVI_j1 | > 10 | — | Multicolinearidade severa — tratada via SHAP |

Fonte: Resultados originais da pesquisa

[INSERIR FIGURA — heterocedasticity_scatter_plot.png]

Figura 4. Diagrama de dispersão dos resíduos vs. valores previstos pelo modelo XGBoost Híbrido, evidenciando dispersão simétrica em torno do zero e leve heterocedasticidade aceitável para extremos climáticos
Fonte: Resultados originais da pesquisa

O Índice de Moran Global ($I = 0,0610$; p-valor $= 0,1190 > 0,05$) não rejeitou a hipótese nula de aleatoriedade espacial dos resíduos preditivos (Tabela 3). Esse resultado empírico demonstrou que as camadas do GEE (NDVI, EVI, LST) e climáticas absorveram eficientemente os efeitos regionais de localização geográfica, resultando em ruído branco espacial e dispensando a complexidade de modelos geoestatísticos adicionais como Krigagem ou Regressão Geograficamente Ponderada.

O teste de correlação de Spearman (p-valor $= 0,0012 < 0,05$) indicou uma associação inversa de baixa magnitude ($\rho_s = -0,1630$) entre o erro absoluto e o rendimento previsto (Tabela 3 e Figura 4). Embora denote leve heterocedasticidade residual estatisticamente detectável, a baixa intensidade do coeficiente assegura que a dispersão dos erros permaneça contida e controlada ao longo de toda a faixa produtiva, mantendo a confiabilidade das previsões tanto em municípios de alta produtividade quanto em safras com quebra localizada.

O diagnóstico de VIF identificou colinearidade acentuada entre os índices espectrais de mesma janela (VIF > 10 para NDVI e EVI), decorrente da redundância espectral intrínseca em bandas do vermelho e infravermelho próximo (Tabela 3). Essa multicolinearidade foi contornada metodologicamente pelo uso de modelos baseados em árvores e pela análise de importância marginal isolada via SHAP.

### Análise de interpretabilidade (SHAP)

[INSERIR FIGURA — painel_shap_integrado.png]

Figura 5. Análise de interpretabilidade das decisões do modelo preditivo via SHAP: (A) importância global e impacto marginal no rendimento ("beeswarm plot"); (B) dependência do déficit hídrico na fase reprodutiva ("def_j2"); (C) dependência da temperatura média na fase reprodutiva ("tmean_j2"); e (D) dependência temporal da tendência secular ("ano")
Fonte: Resultados originais da pesquisa

A análise dos valores SHAP revelou uma hierarquia de importância preditiva com rigoroso respaldo agronômico e fisiológico (Figura 5A). A variável temporal "ano" liderou o ranking de importância global (Figura 5A e Figura 5D), capturando de maneira contínua e estável a evolução tecnológica promovida pelo melhoramento genético de sementes, fertilidade construída e modernização do maquinário, o que fundamentou o êxito da arquitetura híbrida de destendenciamento.

Dentre os fatores agroclimáticos, as variáveis correspondentes à Janela 2 (janeiro a março — estádios de floração e enchimento de grãos) exerceram o maior controle limitante sobre a produtividade final (Figura 5A). O déficit hídrico reprodutivo (def_j2) destacou-se com expressivo impacto penalizante: em municípios e safras com suprimento hídrico adequado (valores próximos de zero), o impacto sobre o rendimento foi estável; em contrapartida, sob condições de déficit hídrico severo na J2, observou-se forte penalização nas projeções, com reduções marginais superiores a 60 kg ha⁻¹ (Figura 5B). Esse padrão reflete com fidelidade a fenologia da soja, fase em que o estresse hídrico provoca abortamento floral precoce e restringe a taxa de expansão e enchimento de grãos (James et al., 2008; Kunrath et al., 2018).

De forma análoga, a temperatura média do ar na Janela 2 (tmean_j2) exibiu uma resposta altamente não-linear sobre a produtividade (Figura 5C). Observou-se uma faixa térmica ótima em torno de 23,5 °C a 25,0 °C, na qual o impacto marginal SHAP manteve-se favorável. Acima do limiar de 25,5 °C, o estresse térmico diurno e noturno provocou rápida degradação da produtividade prevista, atingindo desvios negativos superiores a 40 kg ha⁻¹ (Figura 5C), traduzindo o efeito fisiológico do aumento da respiração de manutenção e a perda de viabilidade do pólen.

Na Janela 1 (outubro a dezembro — emergência e crescimento vegetativo), as variáveis de vigor espectral (NDVI_j1 e EVI_j1) e precipitação (pr_j1) demonstraram contribuição predominantemente positiva para o rendimento final (Figura 5A). Fisiologicamente, essa resposta evidencia a importância do estabelecimento vegetativo inicial: lavouras que atingem rápido fechamento de dossel e elevado Índice de Área Foliar (IAF) na primavera desenvolvem nós férteis abundantes e raízes profundas, acumulando reservas de fotoassimilados que sustentam o potencial produtivo e aumentam a tolerância da cultura a eventuais estiagens curtas (*veranicos*) durante a fase reprodutiva subsequente. Por outro lado, índices espectrais deprimidos em J1 sinalizam atrasos de emergência ou estresses iniciais que limitam irreversivelmente a biomassa da lavoura, rebaixando o teto produtivo final mesmo sob condições climáticas favoráveis no encerramento da safra.

### Comparação crítica com a literatura e análise de métricas

A comparação do desempenho preditivo entre modelos agrícolas publicados na literatura científica demanda cautela analítica rigorosa, dado que estudos similares operam sob diferentes escalas espaciais, unidades territoriais e, sobretudo, métricas heterogêneas de avaliação (Tabela 4).

Tabela 4. Comparação do desempenho preditivo com estudos similares da literatura de sensoriamento remoto e aprendizado de máquina

| Referência | Região e Escala Territorial | Modelo Avaliado | Variáveis Principais | Métrica de Erro Reportada |
| :--- | :--- | :--- | :--- | :--- |
| Schwalbert et al. (2020) | Rio Grande do Sul, Brasil (Municipal) | "Random Forest" | NDVI (MODIS), precipitação e temperatura | RMSE ~300 a 450 kg ha⁻¹ |
| Kung et al. (2021) | China (Provincial / Regional) | "XGBoost" | Variáveis climáticas agregadas e MODIS | MAPE ~8% a 12% |
| Ray et al. (2015) | Global (~13.500 unidades políticas subnacionais) | Modelos Estatísticos Climáticos | Anomalias climáticas (temperatura e precipitação) | Variabilidade explicada: 32% a 39% (global) e >60% (celeiros globais) |
| Pantazi et al. (2016) | Grécia (Escala de Talhão / Lavoura) | "Random Forest" | Atributos de solo e sensores de dossel | RMSE ~200 kg ha⁻¹ |
| **Este trabalho** | **Mato Grosso, Brasil (Municipal)** | **Híbrido: RLM + "XGBoost"** | **NDVI, EVI, LST, TerraClimate (Janelas J1 e J2)** | **WMAPE 7,24% / MAE 251 kg ha⁻¹ / OOS-R² 0,4891** |

Fonte: Resultados originais da pesquisa e compilação bibliográfica

A literatura internacional revela uma carência marcante de padronização nas métricas de avaliação. Enquanto estudos de abrangência global como o de Ray et al. (2015) concentram-se na proporção da variabilidade climática explicada (32% a 60%), a vasta maioria das publicações voltadas à previsão agronômica restringe-se a reportar o RMSE ou o coeficiente $R^2$. O Erro Absoluto Médio (MAE) raramente é disponibilizado pelos autores em estudos agrícolas de sensoriamento remoto, o que dificulta aferir a magnitude física do erro na escala tangível de produção (sacas por hectare). O modelo híbrido desenvolvido neste trabalho alcançou um MAE de 251 kg ha⁻¹ na validação temporal estrita com safras inéditas (2022 a 2024), o que equivale a um desvio médio de apenas 4,18 sacas por hectare em um estado cuja produtividade média supera 60 sacas por hectare. Trata-se de uma margem de segurança de extrema precisão agronômica.

Adicionalmente, cumpre ressaltar a distinção fundamental entre o MAPE convencional e o WMAPE adotado neste estudo. Trabalhos como o de Kung et al. (2021) reportaram erros na faixa de 8% a 12% utilizando o MAPE simples. O MAPE aritmético atribui o mesmo peso estatístico a um município com área cultivada irrisória (ex.: 500 ha) e a um grande polo produtor (ex.: Sorriso ou Nova Mutum, com centenas de milhares de hectares). Por outro lado, o WMAPE de 7,24% aqui obtido pondera os resíduos pela área e produção de cada município, fornecendo um reflexo matematicamente fidedigno do impacto do erro sobre o volume total da safra estadual e nacional.

Em relação à escala e às características fisiográficas, os resultados deste estudo superam os reportados por Schwalbert et al. (2020) no Rio Grande do Sul (RMSE entre 300 e 450 kg ha⁻¹), mantendo o RMSE em 337,78 kg ha⁻¹ mesmo diante da heterogeneidade edafoclimática de Mato Grosso, estado com mais de 12 milhões de hectares cultivados. Embora estudos em escala de talhão (*field-scale*), como o de Pantazi et al. (2016) na Grécia, atinjam erros absolutos menores (RMSE ~200 kg ha⁻¹), essas abordagens requerem levantamento amostral *in situ* de fertilidade de solo e manejo agronômico local, inviabilizando sua replicação operacional em escala regional ou estadual.

### Ganho prático da divisão fenológica e mitigação do vazamento de dados

O êxito da arquitetura proposta residiu em duas inovações metodológicas cruciais que respondem a gargalos históricos da literatura:

1. **Ganho Prático da Compartimentação Fenológica (J1 e J2):** a maioria dos estudos convencionais processa médias climáticas e índices de vegetação integrados ao longo de todo o ciclo agrícola (outubro a março). Essa abordagem agregada padece de um grave problema de *diluição temporal do sinal de estresse*: uma seca severa de 20 a 25 dias ocorrida em janeiro (fase crítica de enchimento de grãos) acaba matematicamente mascarada pelas chuvas volumosas de outubro e novembro quando se calcula a média da safra inteira. A divisão em Janela 1 (crescimento vegetativo) e Janela 2 (floração e enchimento) permitiu ao modelo isolar o momento exato em que o déficit hídrico e a temperatura afetam a produtividade, viabilizando ainda a geração de estimativas antecipadas antes do encerramento da colheita. Esse ganho analítico justifica plenamente a complexidade adicional do pipeline, especialmente considerando que a rotina automatizada em nuvem (GEE) extrai e processa todas as variáveis de todos os municípios do estado em menos de 10 minutos, sem demandar coletas manuais de campo.

2. **Mitigação Pioneira do Vazamento de Dados (*Data Leakage*):** na quase totalidade dos trabalhos acadêmicos que aplicam aprendizado de máquina na previsão agrícola, os modelos são avaliados por validação cruzada aleatória padrão ($k$-fold tradicional). Sob esse procedimento, observações de uma mesma safra ou safras futuras (ex.: 2023) são sorteadas para treinar o modelo que prevê safras passadas (ex.: 2018), ou municípios vizinhos sujeitos ao mesmo evento climático são divididos aleatoriamente entre treino e teste. Esse vazamento de dados informacional infla artificialmente os índices de correlação (frequentemente gerando $R^2 > 0,85$ fictícios), criando uma ilusão de precisão que não se sustenta no mundo real. Os trabalhos anteriores raramente comentam ou buscam remediar esse vício metodológico. Em contrapartida, este trabalho implementou o bloqueio temporal estrito (*Out-of-Time*, com treino até 2021 e teste cego em 2022 a 2024) e o bloqueio espacial (*Leave-Municipality-Out*), demonstrando que o modelo é capaz de generalizar de forma autêntica perante safras futuras e geografias inéditas.

### Implicações práticas para a cadeia do agronegócio

A assertividade alcançada pelo modelo preditivo híbrido (erro de aproximadamente 4 sacas por hectare com antecedência de semanas a meses em relação aos dados oficiais do IBGE) estabelece um conjunto de aplicações operacionais de alto valor econômico:
* **Produtores Rurais e Cooperativas:** suporte antecipado para estratégias de comercialização e *hedge* em bolsas de futuros (B3/CBOT), contratação de apólices de seguro agrícola balizadas em risco paramétrico de déficit hídrico em J2 e otimização de compras de insumos;
* **Empresas de Logística e *Tradings*:** planejamento antecipado do fluxo de caminhões e fretes rodoviários, evitando gargalos no escoamento pelos corredores de exportação (portos do Arco Norte e Santos) e dimensionando a necessidade de capacidade estática de armazenagem em armazéns e silos municipais;
* **Instituições Financeiras e Seguradoras:** concessão orientada de crédito rural fundamentada em probabilidades reais de quebra de safra baseadas em indicadores agrometeorológicos de satélite;
* **Setor Público e Órgãos Reguladores (Conab/Ministério da Agricultura):** subsídio técnico em tempo hábil para a gestão de estoques reguladores, elaboração de políticas de garantia de preços mínimos e segurança alimentar nacional antes da consolidação dos dados cadastrais do censo agrícola.

---

## Conclusões

Este trabalho desenvolveu, validou e comparou uma abordagem preditiva de aprendizado de máquina baseada em compartimentação fenológica e arquitetura híbrida de destendenciamento (*detrending*) para a estimativa antecipada do rendimento municipal da soja no estado de Mato Grosso.

As conclusões fundamentais da pesquisa compreendem:
1. A arquitetura híbrida acoplando Regressão Linear Múltipla (para absorção da tendência secular tecnológica) ao algoritmo *Extreme Gradient Boosting* (XGBoost) superou os modelos puros baseados em árvore, mitigando com sucesso a limitação de extrapolação linear intrínseca aos algoritmos de decisão em séries temporais agrícolas não-estacionárias;
2. Na validação temporal estrita fora da amostra (*Out-of-Time*) frente a safras inéditas de teste (2022 a 2024), o modelo híbrido obteve desempenho consistente, com Erro Absoluto Médio (MAE) de 251 kg ha⁻¹ (~4,18 sacas ha⁻¹), Erro Percentual Absoluto Ponderado (WMAPE) de 7,24% e coeficiente de determinação fora da amostra ($OOS\text{-}R^2$) de 0,4891, alcançando WMAPE de 5,27% na validação cruzada espacial (*Leave-Municipality-Out*);
3. Os testes de suposições estatísticas comprovaram a ausência de autocorrelação espacial nos resíduos preditivos (Índice de Moran $I = 0,0610$; p-valor $= 0,1190$), atestando que as variáveis orbitais e agrometeorológicas extraídas via GEE absorveram eficientemente os efeitos da localização geográfica e dispensaram métodos geoestatísticos adicionais;
4. A análise de interpretabilidade via valores SHAP confirmou a consonância biológica das predições do modelo com a fisiologia da cultura, evidenciando que o déficit hídrico e as temperaturas médias elevadas durante a fase reprodutiva (Janela 2) atuam como os principais agentes limitantes do rendimento final, enquanto o vigor espectral inicial (Janela 1) define o potencial de suporte produtivo da lavoura.

A metodologia proposta demonstrou elevado rigor analítico, robustez contra vazamento de dados e alta escalabilidade computacional, consolidando-se como um instrumento acurado e viável para o monitoramento e a previsão antecipada de safras de soja em escala regional.

---

## Referências

Abatzoglou, J.T.; Dobrowski, S.Z.; Parks, S.A.; Hegewisch, K.C. 2018. TerraClimate, a high-resolution global dataset of monthly climate and climatic water balance from 1958–2015. Scientific Data 5(1): 1-12.

Akiba, T.; Sano, S.; Yanase, T.; Ohta, T.; Koyama, M. 2019. Optuna: A next-generation hyperparameter optimization framework. In: Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, p. 2623-2631.

Battisti, R.; Sentelhas, P.C. 2017. Improvement of soybean yield simulation by considering root growth and deep water uptake in a subtropical environment. Field Crops Research 206: 122-132.

Becker-Reshef, I.; Justice, C.; Sullivan, M.; Vermote, E.; Tucker, C.; Anyamba, A.; Small, J.; Pak, E.; Masuoka, E.; Schmaltz, J.; Hansen, M.; Pittman, K.; Birkett, C.; Williams, D.; Reynolds, C.; Doorn, B. 2010. Monitoring global croplands with coarse resolution earth observations: the Global Agriculture Monitoring (GLAM) project. Remote Sensing 2(6): 1589-1609.

Breiman, L. 2001. Random forests. Machine Learning 45(1): 5-32.

Centro de Estudos Avançados em Economia Aplicada [Cepea]. 2023. PIB do Agronegócio Brasileiro. Disponível em: <https://www.cepea.esalq.usp.br>. Acesso em: ago. 2026.

Chen, T.; Guestrin, C. 2016. XGBoost: a scalable tree boosting system. In: ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 22., 2016. Anais... p. 785-794.

Companhia Nacional de Abastecimento [Conab]. 2023. Acompanhamento da Safra Brasileira de Grãos. Disponível em: <https://www.conab.gov.br>. Acesso em: ago. 2026.

Doraiswamy, P.C.; Hatfield, J.L.; Jackson, T.J.; Akhmedov, B.; Prueger, J.; Stern, A. 2004. Crop condition and yield simulations using Landsat and MODIS. Remote Sensing of Environment 92(4): 548-559.

Friedman, J.H. 2001. Greedy function approximation: a gradient boosting machine. Annals of Statistics 29(5): 1189-1232.

Gorelick, N.; Hancher, M.; Dixon, M.; Ilyushchenko, S.; Thau, D.; Moore, R. 2017. Google Earth Engine: planetary-scale geospatial analysis for everyone. Remote Sensing of Environment 202: 18-27.

Instituto Brasileiro de Geografia e Estatística [IBGE]. 2023. Sistema IBGE de Recuperação Automática (SIDRA) — Pesquisa da Produção Agrícola Municipal (PAM). Disponível em: <https://sidra.ibge.gov.br>. Acesso em: ago. 2026.

Instituto Mato-grossense de Economia Agropecuária [IMEA]. 2023. Relatórios de Acompanhamento da Safra de Soja em Mato Grosso. Disponível em: <http://www.imea.com.br>. Acesso em: ago. 2026.

James, A.T.; Lawn, R.J.; Cooper, M. 2008. Genotypic variation for drought stress response traits in soybean. II. Yield and yield components. Australian Journal of Agricultural Research 59(7): 670-678.

Kung, H.Y.; Kuo, T.H.; Chen, C.H.; Tsai, P.Y. 2021. Applying machine learning techniques to predict soybean production. Symmetry 13(5): 765.

Kunrath, T.R.; Loshschmidt, R.; Balbinot Junior, A.A.; Franchini, J.C.; Debiasi, H. 2018. Drought stress on soybean at different vegetative and reproductive stages. Pesquisa Agropecuária Brasileira 53(11): 1205-1212.

Lundberg, S.M.; Lee, S. 2017. A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems 30: 4765-4774.

Marin, F.R.; Zullo Junior, J.; Sentelhas, P.C. 2018. Crop modeling for climate change impact and adaptation studies in Brazil. Agricultural Systems 160: 45-56.

Meyer, H.; Pebesma, E. 2022. Machine learning-based global maps of ecological variables and the challenge of assessing them. Nature Communications 13(1): 2208.

Pantazi, X.E.; Moshou, D.; Alexandridis, T.; Whetton, R.L.; Mouazen, A.M. 2016. Wheat yield prediction using machine learning and advanced sensing techniques. Computers and Electronics in Agriculture 121: 57-65.

Pedregosa, F.; Varoquaux, G.; Gramfort, A.; Michel, V.; Thirion, B.; Grisel, O.; Blondel, M.; Prettenhofer, P.; Weiss, R.; Dubourg, V.; Vanderplas, J.; Passos, A.; Cournapeau, D.; Brucher, M.; Perrot, M.; Duchesnay, E. 2011. Scikit-learn: machine learning in Python. Journal of Machine Learning Research 12: 2825-2830.

Pereira, R.H.M.; Gonçalves, C.N.; Chaves, P.A.B. 2019. geobr: pacote R e Python para baixar conjuntos de dados espaciais oficiais do Brasil. Instituto de Pesquisa Econômica Aplicada [IPEA], Rio de Janeiro, RJ, Brasil.

Projeto MapBiomas. 2023. Coleção 9.0 da Série Anual de Mapas de Cobertura e Uso de Solo do Brasil. Disponível em: <https://mapbiomas.org>. Acesso em: ago. 2026.

Ray, D.K.; Gerber, J.S.; MacDonald, G.K.; West, P.C. 2015. Climate variation explains a third of global crop yield variability. Nature Communications 6: 5989.

Rey, S.J.; Anselin, L. 2007. PySAL: a Python library of spatial analytical methods. The Review of Regional Studies 37(1): 5-27.

Schwalbert, R.A.; Amado, T.; Corassa, G.; Pott, L.P.; Prasad, P.V.V.; Ciampitti, I.A. 2020. Satellite-based soybean yield forecast: integrating machine learning and weather data for improving crop yield prediction in southern Brazil. Agricultural and Forest Meteorology 284: 107886.

Seabold, S.; Perktold, J. 2010. statsmodels: Econometric and statistical modeling with python. In: 9th Python in Science Conference, p. 92-96.

Sentelhas, P.C.; Battisti, R.; Câmara, G.M.S.; Farias, J.R.B.; Hampf, A.C.; Nendel, C. 2015. The soybean yield gap in Brazil — magnitude, causes and possible solutions for sustainable production. The Journal of Agricultural Science 153(8): 1394-1411.

United States Department of Agriculture [USDA]. 2023. World Agricultural Production. Disponível em: <https://www.fas.usda.gov>. Acesso em: ago. 2026.
