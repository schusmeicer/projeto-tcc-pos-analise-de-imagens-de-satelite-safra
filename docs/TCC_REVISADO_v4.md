# Estimativa antecipada do rendimento da soja em Mato Grosso por modelagem fenológica e aprendizado híbrido

Trabalho de Conclusão de Curso apresentado para obtenção do título de especialista em MBA em Data Science e Analytics – 2026

Weslley Schunemann¹*; Walter Mesquita Filho²

¹ MBA em Data Science e Analytics, USP/ESALQ. * E-mail autor correspondente: weslleyschunemann@gmail.com
² Pecege. Professor Orientador. Parque Tecnológico R. Cezira Giovanoni Moretti, 600 - Santa Rosa; 13418-445 Piracicaba, São Paulo, Brasil

---

Estimativa antecipada do rendimento da soja em Mato Grosso por modelagem fenológica e aprendizado híbrido

## Resumo

A cultura da soja (*Glycine max* (L.) Merr.) desempenhou papel estratégico no agronegócio brasileiro, concentrando em Mato Grosso quase um terço da produção nacional, o que tornou a estimativa antecipada de safras indispensável ao planejamento econômico e logístico. Este trabalho teve como objetivo desenvolver e validar uma abordagem preditiva para estimar o rendimento municipal da soja no estado, integrando sensoriamento remoto em janelas fenológicas e aprendizado de máquina híbrido. A metodologia acoplou dados municipais do IBGE (2008–2024) ao Índice de Vegetação Melhorado (EVI) — selecionado estrategicamente para prevenir saturação em alta biomassa e extinguir multicolinearidade —, temperatura de superfície (LST), variáveis agrometeorológicas (TerraClimate) e um termo bioclimático de estresse composto, estruturados nas janelas vegetativa (J1) e reprodutiva (J2). Para solucionar a limitação de extrapolação temporal dos modelos arbóreos perante a tendência secular tecnológica, implementou-se uma arquitetura de destendenciamento, combinando Regressão Linear Múltipla a algoritmos de aprendizado de máquina sob validação espacial ("Leave-Municipality-Out") e temporal fora da amostra ("Out-of-Time"). A arquitetura híbrida com "Extreme Gradient Boosting" (XGBoost) apresentou desempenho superior, alcançando Erro Absoluto Médio (MAE) de 243,96 kg ha⁻¹ (~4,06 sacas ha⁻¹), Erro Percentual Absoluto Ponderado (WMAPE) de 7,02% e coeficiente de determinação fora da amostra (OOS-R²) de 0,5156 em safras de teste cego (2022–2024), além de WMAPE de 5,27% na validação espacial. Os diagnósticos econométricos confirmaram a eficácia da curadoria: o Fator de Inflação da Variância (VIF) manteve-se abaixo de 3,0 para os índices espectrais e o teste de Breusch-Pagan atestou homocedasticidade residual plena (p-valor = 0,3549). A interpretabilidade via "SHapley Additive exPlanations" (SHAP) confirmou respaldo fisiológico, apontando o déficit hídrico e o estresse térmico em J2 como os principais limitantes da produtividade. Concluiu-se que a modelagem fenológica híbrida forneceu estimativas antecipadas, robustas, parcimoniosas e com sólida consonância biofísica.

Palavras-chave: sensoriamento remoto; safras agrícolas; previsão de produtividade; algoritmos de gradiente; inteligência artificial no campo.

---

## Introdução

O agronegócio brasileiro ocupou posição central na economia nacional, tendo sido responsável por cerca de 25% do Produto Interno Bruto [PIB] e por aproximadamente 50% das exportações do país (Centro de Estudos Avançados em Economia Aplicada [Cepea], 2023). Dentro desse complexo, a cultura da soja (*Glycine max* (L.) Merr.) destacou-se como o principal produto agrícola exportado, tendo movimentado mais de US$ 50 bilhões em 2022/2023, o que consolidou o Brasil como o maior produtor e exportador mundial do grão, superando os Estados Unidos da América [EUA] e a Argentina (Companhia Nacional de Abastecimento [Conab], 2023; United States Department of Agriculture [USDA], 2023). A soja representou, portanto, um pilar estratégico para a balança comercial, a geração de empregos e a segurança alimentar global.

No âmbito estadual, o Mato Grosso consolidou-se como o maior produtor de soja do Brasil, concentrando individualmente aproximadamente 28% da produção nacional (Instituto Brasileiro de Geografia e Estatística [IBGE], 2023). O estado produziu, na safra 2022/2023, cerca de 41,5 milhões de toneladas do grão, resultado que refletiu não apenas a extensão de sua área cultivada — superior a 12 milhões de hectares —, como também os altos índices de produtividade impulsionados pela adoção de tecnologias de precisão e pelo melhoramento genético das cultivares. O agronegócio mato-grossense respondeu por parcela expressiva do PIB estadual e gerou cadeias de valor que se estenderam ao transporte, ao armazenamento e à exportação por corredores multimodais que ligaram o Centro-Oeste aos portos do Norte e do Sudeste do país.

Diante da relevância econômica da soja para o Brasil e, em especial, para o Mato Grosso, a estimativa antecipada e confiável do rendimento da cultura (produtividade, determinada em kg ha⁻¹) tornou-se um instrumento de gestão indispensável. Para os produtores rurais, a previsão de produtividade no início ou durante a safra permitiu o planejamento financeiro (contratação de insumos, máquinas e crédito rural), a decisão estratégica sobre comercialização antecipada e a mitigação de riscos climáticos via seguros agrícolas (Sentelhas et al., 2015; Instituto Mato-grossense de Economia Agropecuária [IMEA], 2023). Para os agentes da cadeia — "tradings", cooperativas e setor governamental — o conhecimento antecipado do volume a ser colhido orientou a logística de armazenamento e escoamento, a formação de estoques reguladores e a definição de políticas de abastecimento e segurança alimentar (Conab, 2023). Em contextos de choques climáticos severos — como estiagens associadas ao fenômeno El Niño — a ausência de previsões quantitativas robustas amplificou perdas financeiras e restringiu a capacidade de resposta tempestiva dos mercados agroindustriais (Battisti e Sentelhas, 2017; Monteiro e Sentelhas, 2014).

Os modelos tradicionais de estimativa de safra basearam-se, em grande medida, em levantamentos amostrais de campo (como o da Pesquisa da Produção Agrícola Municipal [PAM] do IBGE), em modelos agrometeorológicos mecanísticos (como "Decision Support System for Agrotechnology Transfer" [DSSAT] e "Agricultural Production Systems sIMulator" [APSIM]) e em análises univariadas de índices de vegetação ("Normalized Difference Vegetation Index" [NDVI] isolado). Embora tenham contribuído historicamente para o monitoramento agrícola, esses métodos apresentaram limitações relevantes: os levantamentos de campo foram onerosos, demandaram tempo e possuíram cobertura espacial restrita; os modelos mecanísticos exigiram extensivo banco de dados de calibração e de parâmetros de solo e cultivar que muitas vezes não estiveram disponíveis em escala regional; e as abordagens univariadas baseadas unicamente em índices espectrais desconsideraram a influência determinante da variabilidade climática sobre a produtividade. Conforme demonstrado por Ray et al. (2015), as flutuações climáticas — sobretudo as oscilações térmicas e hídricas entre precipitação e temperatura — são responsáveis por explicar entre 32% e 39% da variabilidade no rendimento de safras globais como a soja, superando 60% dessa variação nas principais regiões produtoras. Dessa forma, a simplificação de ignorar as anomalias climáticas e o déficit hídrico em momentos fenológicos críticos restringe substancialmente a acurácia das previsões em safras atípicas (Doraiswamy et al., 2004; Becker-Reshef et al., 2010; Ray et al., 2015).

Nesse cenário, os métodos de Aprendizado de Máquina ("Machine Learning" – ML) emergiram como alternativa de alta capacidade preditiva para a estimativa de rendimentos agrícolas a partir de dados multiespectrais e climáticos de origem orbital. Algoritmos como Florestas Aleatórias ("Random Forest" – RF), Máquinas de Aumento de Gradiente ("Gradient Boosting" – GBR) e Aumento de Gradiente Extremo ("Extreme Gradient Boosting" – XGBoost) demonstraram aptidão superior aos modelos tradicionais em estudos recentes, ao capturar interações não-lineares complexas sem necessidade de calibração exaustiva por genótipo (Pantazi et al., 2016; Schwalbert et al., 2020; Richetti et al., 2018). Integrados a plataformas de processamento em nuvem — como o "Google Earth Engine" [GEE] — esses algoritmos permitiram extrair e processar séries temporais orbitais para grandes extensões territoriais em tempo hábil, viabilizando estimativas municipais em escala estadual (Gorelick et al., 2017). Ademais, a interpretabilidade dos algoritmos foi substancialmente viabilizada pelo método "SHapley Additive exPlanations" [SHAP], quantificando a contribuição marginal de cada variável preditora sob rigor ecofisiológico (Lundberg e Lee, 2017).

Diante do exposto, este trabalho teve como objetivo desenvolver, comparar e validar uma abordagem preditiva de aprendizado de máquina baseada em janelas fenológicas e arquitetura híbrida de destendenciamento para a estimativa antecipada do rendimento municipal da soja no estado de Mato Grosso, assegurando rigor estatístico, interpretabilidade agronômica e robustez perante safras futuras.

---

## Metodologia

### Bancos de dados

Dados de produção agrícola (IBGE/PAM)

Os dados de referência de rendimento da soja foram obtidos junto ao Sistema IBGE de Recuperação Automática [SIDRA], por meio da PAM (IBGE, 2023). A base abrangeu todos os municípios produtores de soja do estado de Mato Grosso com registros contínuos para o período de 2008 a 2024 (17 safras agrícolas). As variáveis coletadas foram: rendimento médio municipal (kg ha⁻¹) — variável-resposta do modelo; área plantada (ha) — utilizada como ponderador nas métricas de avaliação e como regressor de escala; e quantidade produzida (toneladas) — empregada na verificação de consistência dos dados cadastrais. Municípios sem registro de cultivo em anos específicos foram tratados de modo a consolidar um painel temporal balanceado e sem lacunas informacionais.

Dados de sensoriamento remoto e clima (Google Earth Engine)

A extração de variáveis espaciais foi realizada em larga escala utilizando a Interface de Programação de Aplicações ("Application Programming Interface" – API) em linguagem "Python" do GEE (Gorelick et al., 2017). Os limites geográficos dos municípios foram obtidos por meio da biblioteca "geobr" (Pereira et al., 2019), garantindo correspondência vetorial com a malha municipal oficial do IBGE.

A principal inovação metodológica consistiu na estruturação dos dados em duas janelas fenológicas distintas, permitindo ao algoritmo capturar a sensibilidade diferencial da soja em cada fase ontogenética: Janela Fenológica 1 [J1] — crescimento vegetativo e fechamento de dossel (outubro a dezembro); e Janela Fenológica 2 [J2] — floração, formação de vagens e enchimento de grãos (janeiro a março). Para cada janela, foram extraídas e sintetizadas as médias temporais das variáveis apresentadas na Tabela 1, oriundas dos sensores orbitais MODIS e da base climática em grade TerraClimate (Abatzoglou et al., 2018).

Tabela 1. Variáveis preditoras extraídas por janela fenológica
| Coleção | Variável | Sigla | Resolução | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| MODIS MOD13Q1 | "Enhanced Vegetation Index" | EVI_j1 / EVI_j2 | 250 m | Índice de vegetação otimizado sem saturação em alta biomassa |
| MODIS MOD11A2 | "Land Surface Temperature" — Diurna | LST_j1 / LST_j2 | 1 km | Temperatura da superfície terrestre (°C) |
| TerraClimate | Precipitação acumulada | pr_j1 / pr_j2 | ~4 km | Volume total de chuva por janela (mm) |
| TerraClimate | Déficit hídrico | def_j1 / def_j2 | ~4 km | Evapotranspiração potencial menos real (mm) |
| TerraClimate | Temperatura média | tmean_j1 / tmean_j2 | ~4 km | Temperatura média do ar (°C) |
| TerraClimate | Umidade do solo | soil_j1 / soil_j2 | ~4 km | Água disponível na zona de raízes (mm) |
| Biofísica / Clima | Estresse bioclimático composto | estresse_composto_j2 | ~4 km | Interação não-linear de choque térmico e hídrico em J2 |
| IBGE / PAM | Área plantada | area_plantada_hectares | Municipal | Área cultivada de soja por município (ha) |
| Temporal | Ano da safra | ano | — | Variável temporal para captura de tendência tecnológica |
Fonte: Dados originais da pesquisa

Critério de seleção espectral e parcimônia: a opção pela exclusão do NDVI e adoção exclusiva do EVI fundamentou-se em dois pilares consolidados. Primeiro, o princípio da parcimônia estatística perante a multicolinearidade severa detectada entre NDVI e EVI na mesma janela fenológica (VIF > 10 e correlação r = 0,93), cuja inclusão concomitante causava inflação de variância e desestabilização da etapa linear do modelo híbrido. Segundo, a superioridade biofísica do EVI em dosséis densos de soja no Cerrado: enquanto o NDVI satura assintoticamente quando o Índice de Área Foliar (IAF) excede 3,0, o EVI mantém resposta linear progressiva ao acúmulo de biomassa e desconta ativamente interferências atmosféricas e reflectância do solo subjacente (Huete et al., 2002; Schwalbert et al., 2020).

Modelagem de choques climáticos extremos: para mitigar a dilatação da variância residual induzida por anomalias climáticas extremas (como a quebra da safra 2024 provocada pelo El Niño), formulou-se um preditor de estresse bioclimático composto na Janela 2 (enchimento de grãos):

$$\text{estresse\_composto}_{j2} = \text{def}_{j2} \times \max(0, \text{tmean}_{j2} - 25) \quad \quad (5)$$

em que: def_j2 representa o déficit hídrico reprodutivo (mm); e tmean_j2 é a temperatura média do ar (°C). Fisiologicamente, a soja suporta estresses moderados se houver compensação térmica ou hídrica; todavia, a ocorrência concomitante de déficit hídrico e temperaturas superiores ao limiar biológico de 25 °C induz abortamento irreversível de flores e vagens (Farias et al., 2007; Sentelhas et al., 2015). A introdução dessa interação estabilizou a matriz de dispersão dos erros, garantindo homocedasticidade estrita às previsões.

Integração e padronização dos dados

Um pipeline estruturado em ambiente "Python" (biblioteca "Pandas") unificou a matriz do IBGE com as tabelas zonais extraídas do GEE, adotando como chaves primárias de cruzamento o código geográfico municipal do IBGE e o ano da safra. Foram executadas rotinas de consistência envolvendo: remoção de municípios sem cultivo agrícola contínuo; conferência e exclusão de inconsistências numéricas; harmonização de convenções decimais; e cálculo de consistência estequiométrica entre rendimento, área e volume colhido. O conjunto consolidado resultou em um painel estruturado com 1.865 observações municipais-safra.

### Modelos preditivos e calibração de hiperparâmetros

A previsão do rendimento agrícola a partir de dados orbitais e meteorológicos impõe o tratamento simultâneo de relações lineares graduais de longo prazo (evolução tecnológica) e dinâmicas altamente não-lineares de curto prazo (anomalias hídricas e choques térmicos). Para investigar essa complexidade, quatro formulações preditivas complementares foram implementadas por meio das bibliotecas "Scikit-learn" (Pedregosa et al., 2011) e "XGBoost" (Chen e Guestrin, 2016):

1. Regressão Linear Múltipla (RLM): modelo paramétrico linear global, adotado como base de comparação ("baseline") e responsável por equacionar a tendência tecnológica secular, conforme a eq. (1):

$$y = \beta_0 + \sum_{j=1}^{p} \beta_j x_j + \varepsilon \quad \quad (1)$$

em que: y é o rendimento observado (kg ha⁻¹); β₀ representa o intercepto da regressão; βⱼ são os coeficientes angulares parciais estimados por Mínimos Quadrados Ordinários (MQO); xⱼ são as p variáveis preditoras; e ε é o termo de erro residual aleatório.

2. Florestas Aleatórias ("Random Forest" – RF): método não-paramétrico de agregação em paralelo ("bagging") (Breiman, 2001), reconhecido pela estabilidade e robustez perante variância e dados discrepantes ("outliers"), cuja previsão agrega a média de B árvores de decisão independentes induzidas por reamostragem ("bootstrap"), conforme a eq. (2):

$$\hat{y} = \frac{1}{B} \sum_{b=1}^{B} T_b(\mathbf{x}) \quad \quad (2)$$

em que: T_b(x) denota a predição emitida pela b-ésima árvore individual; e B é o total de estimadores na floresta. A parametrização ótima obtida resultou em B = 300 árvores (n_estimators), profundidade máxima de 3 níveis (max_depth = 3) e número mínimo de 2 amostras para cisão de nó (min_samples_split = 2).

3. Máquinas de Aumento de Gradiente ("Gradient Boosting" – GBR): algoritmo sequencial iterativo ("boosting") (Friedman, 2001), projetado para redução de viés ao ajustar sucessivas árvores rasas sobre os resíduos gerados pelo comitê precedente, segundo a eq. (3):

$$F_m(\mathbf{x}) = F_{m-1}(\mathbf{x}) + \eta \cdot T_m(\mathbf{x}) \quad \quad (3)$$

em que: F_m(x) é o modelo no estágio m; T_m(x) é a árvore ajustada aos resíduos; e η ∈ (0, 1] é a taxa de aprendizado ("learning rate") fixada em 0,05 para contrair a contribuição de cada nova partição e mitigar o sobreajuste ("overfitting"), com max_depth = 5 e n_estimators = 150.

4. Aumento de Gradiente Extremo ("Extreme Gradient Boosting" – XGBoost): algoritmo baseado em árvores aditivas regulares (Chen e Guestrin, 2016), que otimiza uma função objetivo com penalização explícita de complexidade estrutural e regularização, formalizada na eq. (4):

$$\mathcal{L} = \sum_{i=1}^{n} l(y_i, \hat{y}_i) + \sum_{k=1}^{K} \Omega(T_k), \quad \text{com} \quad \Omega(T) = \gamma T_{folhas} + \frac{1}{2}\lambda \sum_{j=1}^{T_{folhas}} w_j^2 \quad \quad (4)$$

em que: l(y_i, \hat{y}_i) é a perda quadrática diferenciável; γ quantifica a penalidade sobre a expansão do número total de folhas terminais T_folhas; λ é o multiplicador de regularização L₂ imposto aos pesos foliares w_j; e a minimização opera via aproximação por série de Taylor de segunda ordem. A configuração calibrada compreendeu n_estimators = 200, learning_rate = 0,05, max_depth = 5 e subsample = 0,80.

A otimização de hiperparâmetros de todos os algoritmos foi conduzida por busca Bayesiana com a biblioteca "Optuna" (Akiba et al., 2019), avaliando 20 iterações guiadas por validação cruzada espacial restrita aos dados de calibração histórica (2008–2021).

### Arquitetura híbrida de destendenciamento ("detrending")

Modelos de árvore particionam o espaço das variáveis preditoras por meio de cortes ortogonais consecutivos. Em decorrência dessa estrutura hierárquica, algoritmos arbóreos são incapazes de realizar extrapolação matemática linear para além dos extremos contidos no banco de calibração: qualquer combinação de atributos situada acima dos limites históricos é truncada no valor numérico da folha terminal mais próxima.

No cultivo da soja em Mato Grosso, o rendimento médio registrou expansão contínua em virtude da contínua adoção tecnológica, incluindo biotecnologia de cultivares, semeadura direta e correção de perfil de solo, com taxa secular observada de aproximadamente +26,47 kg ha⁻¹ ano⁻¹. Aplicar modelos puramente arbóreos para safras posteriores (2022 a 2024) provocaria subestimação estrutural e artificial das produtividades recordes. Ressalta-se que a opção pelo destendenciamento via Regressão Linear Múltipla ajustada estritamente no período histórico de calibração, em detrimento de filtros iterativos ou não paramétricos (como o filtro de Hodrick-Prescott), assegura estrita blindagem temporal contra vazamento de informações futuras ("look-ahead bias") e elimina a instabilidade nas extremidades temporais ("end-point problem") em previsões operacionais fora da amostra (Hamilton, 2018).

Para sanar essa restrição conceitual, implementou-se uma arquitetura preditiva híbrida em quatro etapas:

Etapa 1. Modelagem da tendência secular tecnológica (Estágio Linear): estimação prévia de uma regressão linear sobre o ano da safra e a área plantada, isolando o vetor de evolução temporal do estado, conforme a eq. (6):

$$\hat{y}_{tend, i} = \hat{\beta}_0 + \hat{\beta}_{ano} \cdot ano_i + \hat{\beta}_{area} \cdot area_i \quad \quad (6)$$

em que: \hat{y}_{tend, i} é a produtividade esperada no município i atribuível estritamente ao componente tecnológico secular.

Etapa 2. Determinação dos resíduos agrometeorológicos: isolamento do componente residual estocástico governado pelas oscilações climáticas e anomalias de vigor da cultura, conforme a eq. (7):

$$r_i = y_i - \hat{y}_{tend, i} \quad \quad (7)$$

em que: r_i denota a oscilação agroclimática observada em relação à curva tecnológica basal.

Etapa 3. Modelagem não-linear dos resíduos agroclimáticos: treinamento do algoritmo de aprendizado de máquina (RF, GBR ou XGBoost) para mapear os resíduos r_i com base exclusivamente nas variáveis de sensoriamento remoto e balanço hídrico das duas janelas fenológicas, representada pela eq. (8):

$$\hat{r}_i = f_{ML}(\mathbf{x}_{i, satélite, clima}) \quad \quad (8)$$

em que: f_ML é a função não-linear calibrada pelo estimador de gradiente ou floresta.

Etapa 4. Recomposição preditiva final: integração aditiva entre a tendência linear secular extrapolada e o resíduo fenológico estimado, expressa na eq. (9):

$$\hat{y}_i = \hat{y}_{tend, i} + \hat{r}_i \quad \quad (9)$$

Dessa forma, a tendência temporal tecnológica é projetada com estabilidade pelo componente linear, enquanto as interações agrometeorológicas complexas e choques de produtividade são absorvidos com máxima flexibilidade pelo aprendizado de máquina.

### Interpretabilidade biológica via valores SHAP

Para elucidar as decisões internas do modelo híbrido de aprendizado de máquina, empregou-se a metodologia baseada na teoria dos jogos cooperativos via "SHapley Additive exPlanations" [SHAP] (Lundberg e Lee, 2017). O valor SHAP ϕ_j concernente à variável j mensura a sua contribuição marginal ponderada entre todas as permutações possíveis do conjunto de preditores, formulado na eq. (10):

$$\phi_j = \sum_{S \subseteq N \setminus \{j\}} \frac{|S|!(|N| - |S| - 1)!}{|N|!} \left[ f_{S \cup \{j\}}(\mathbf{x}_{S \cup \{j\}}) - f_S(\mathbf{x}_S) \right] \quad \quad (10)$$

em que: N representa o conjunto global de atributos; S compreende qualquer subconjunto que exclui a variável j; e f(x) indica a resposta computada pelo modelo. A derivação analítica dos valores foi processada pelo algoritmo "TreeExplainer" com convergência exata.

A análise visual dos padrões SHAP fundamentou-se em duas representações complementares:

- Gráfico de Importância Global ("Beeswarm Plot"): diagrama em que os preditores são dispostos verticalmente em ordem decrescente de importância média absoluta (mean(|ϕ_j|)). Cada ponto colorido expressa um município em dada safra agrícola, no qual a coordenada horizontal indica o impacto marginal em produtividade (kg ha⁻¹) e a coloração reflete a magnitude observada da variável (azul para valores baixos e vermelho para elevados);
- Gráficos de Dependência Parcial ("SHAP Dependence Plots"): dispersões bidimensionais que relacionam a magnitude observada de uma variável no eixo das abscissas com seu respectivo impacto marginal ϕ_j no eixo das ordenadas, permitindo diagnosticar pontos de inflexão ecofisiológica e limites de estresse bioclimático.

### Estratégia de validação contra vazamento de dados ("data leakage")

A validação de modelos agrícolas fundamentados em dados espaçotemporais exige controle meticuloso contra o vazamento de informações ("data leakage"), patologia frequente em estudos que utilizam divisão aleatória padrão ("k-fold" simples), na qual municípios vizinhos ou safras futuras compõem inadvertidamente a base de treino, gerando métricas de assertividade artificiais (Meyer e Pebesma, 2022). O presente trabalho adotou duas camadas complementares de blindagem:

Validação temporal fora da amostra ("Out-of-Time" – OOT)

O conjunto de dados foi cindido cronologicamente: safras de 2008 a 2021 (14 anos consecutivos) foram destinadas à calibração e ajuste de hiperparâmetros; enquanto o triênio de 2022 a 2024 (safras cegas) foi reservado como conjunto de teste independente. Essa separação replicou a condição operacional de estimativa antecipada de safras antes da colheita. Devido à latência de consolidação da Coleção 9 do projeto MapBiomas (Projeto MapBiomas, 2023) para a safra 2024 no momento da extração — condição fidedigna à rotina de estimativa em tempo real antes da colheita —, adotou-se a premissa padrão de persistência do uso da terra ($t-1$), utilizando a máscara de soja de 2023 como base amostral para o ano de 2024, em conformidade com os protocolos operacionais de monitoramento global de safras (Becker-Reshef et al., 2010, 2018).

Validação cruzada espacial ("Leave-Municipality-Out")

Para mensurar a capacidade de generalização espacial do modelo sobre municípios inéditos, utilizou-se o protocolo "Leave-Municipality-Out" estruturado via "GroupKFold" com 5 partições. Todas as observações históricas de determinado município foram mantidas conjuntamente no bloco de validação, aferindo a capacidade do algoritmo de transferir aprendizado agrometeorológico entre diferentes polos de produção do estado sem memorizar atributos territoriais fixos.

### Testes de suposições estatísticas e diagnóstico residual

A robustez dos resíduos preditivos foi auditada formalmente por meio de três testes diagnósticos fundamentais:

a) Autocorrelação espacial — Índice de Moran Global

A eventual dependência espacial nos resíduos sinalizaria a omissão de covariáveis regionais relevantes. O Índice de Moran Global (I) foi calculado segundo Rey e Anselin (2007), conforme a eq. (11):

$$I = \left[ \frac{n}{\sum_{i=1}^{n} \sum_{j=1}^{n} w_{ij}} \right] \cdot \frac{\sum_{i=1}^{n} \sum_{j=1}^{n} w_{ij}(e_i - \bar{e})(e_j - \bar{e})}{\sum_{i=1}^{n} (e_i - \bar{e})^2} \quad \quad (11)$$

em que: e_i e e_j correspondem aos resíduos nos municípios i e j; \bar{e} expressa a média dos resíduos; e w_{ij} denota os elementos da matriz de pesos espaciais calibrada via vizinhos mais próximos (k-NN, com k = 4). Sob a hipótese nula (H₀), os resíduos configuram ruído branco espacialmente independente.

b) Heterocedasticidade — Teste de Breusch-Pagan

A suposição de variância homocedástica dos erros foi avaliada por meio do teste clássico de Breusch-Pagan (Breusch e Pagan, 1979). O procedimento consistiu em regredir os resíduos quadráticos padronizados contra os valores previstos (\hat{y}_i), extraindo-se a estatística do Multiplicador de Lagrange (LM), conforme a eq. (12):

$$LM = n \cdot R_{aux}^2 \quad \quad (12)$$

em que: n é a quantidade de observações avaliadas no teste cego; e R_{aux}^2 é o coeficiente de determinação da regressão auxiliar. Sob H₀ (variância residual homocedástica e constante), a estatística LM converge assintoticamente para uma distribuição Qui-quadrado com um grau de liberdade (\chi^2_1).

c) Multicolinearidade — Fator de Inflação da Variância [VIF]

O grau de colinearidade entre os atributos preditores foi quantificado pelo VIF, estruturado na eq. (13):

$$VIF_j = \frac{1}{1 - R_j^2} \quad \quad (13)$$

em que: R_j^2 expressa o coeficiente de determinação decorrente da regressão da variável x_j contra todos os demais atributos preditores do modelo, sendo valores superiores a 10 indicativos de multicolinearidade crítica (Seabold e Perktold, 2010).

### Métricas de desempenho e critérios de avaliação

Para garantir avaliação holística e de relevância prática para o agronegócio, o desempenho preditivo foi quantificado por meio de cinco métricas complementares:

- Erro Absoluto Médio (MAE): mensura o desvio linear médio na unidade física original de rendimento (kg ha⁻¹), proporcionando interpretação agronômica direta em sacas por hectare (sacas ha⁻¹), calculado pela eq. (14):

$$MAE = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i| \quad \quad (14)$$

em que: y_i é a produtividade real observada; \hat{y}_i é a produtividade estimada; e n é o número total de observações.

- Raiz do Erro Quadrático Médio (RMSE): indicador que penaliza desvios residuais de maior magnitude de forma exponencial, sinalizando a presença de desvios anômalos em anos de crise climática severa, definido na eq. (15):

$$RMSE = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2} \quad \quad (15)$$

em que: y_i e \hat{y}_i seguem a mesma notação descrita anteriormente.

- Erro Percentual Absoluto Médio (MAPE): afere a magnitude percentual média dos erros em relação à escala de cada observação municipal, determinado pela eq. (16):

$$MAPE = \left[ \frac{1}{n} \sum_{i=1}^{n} \left| \frac{y_i - \hat{y}_i}{y_i} \right| \right] \times 100\% \quad \quad (16)$$

- Erro Percentual Absoluto Médio Ponderado (WMAPE): corrige a distorção do MAPE tradicional ao ponderar o erro pela escala produtiva de cada município, evitando que desvios em pequenos municípios tenham peso equivalente ao de polos agrícolas de grande relevância estadual, formulado na eq. (17):

$$WMAPE = \left[ \frac{\sum_{i=1}^{n} |y_i - \hat{y}_i|}{\sum_{i=1}^{n} y_i} \right] \times 100\% \quad \quad (17)$$

- Coeficiente de Determinação Fora da Amostra (OOS-R²): avalia a capacidade preditiva do modelo frente à variabilidade temporal genuína em dados de teste inéditos, adotando a média do conjunto histórico de calibração como estimador de referência e eliminando o viés do R² clássico, expresso na eq. (18):

$$OOS\text{-}R^2 = 1 - \frac{\sum_{i=1}^{n} (y_{teste, i} - \hat{y}_{teste, i})^2}{\sum_{i=1}^{n} (y_{teste, i} - \bar{y}_{treino})^2} \quad \quad (18)$$

em que: \bar{y}_{treino} representa a produtividade média calculada estritamente com os dados históricos do período de treinamento (2008–2021).

---

## Resultados e Discussão

### Desempenho comparativo dos modelos preditivos

A Tabela 2 sintetiza as métricas de acurácia obtidas pelos diferentes modelos preditivos na validação temporal "Out-of-Time" (safras de teste cego de 2022 a 2024), após a seleção parcimoniosa do EVI e a inclusão do preditor de estresse bioclimático composto. Os resultados demonstram com nitidez a superioridade empírica da abordagem híbrida em relação aos modelos de árvores isoladas.

Tabela 2. Desempenho comparativo de modelos puros e híbridos no conjunto de teste "Out-of-Time" (safras 2022–2024)
| Modelo de Predição | OOS-R² | RMSE (kg ha⁻¹) | MAE (kg ha⁻¹) | MAPE (%) | WMAPE (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Árvore Pura: "Random Forest" | 0,4406 | 355,66 | 280,27 | 8,41 | 8,06 |
| Árvore Pura: "Gradient Boosting" | 0,4285 | 359,50 | 286,24 | 8,49 | 8,24 |
| Árvore Pura: "XGBoost" | 0,4193 | 362,37 | 289,54 | 8,60 | 8,33 |
| Regressão Linear Múltipla | 0,5362 | 323,85 | 247,96 | 7,45 | 7,13 |
| Híbrido: "Random Forest" | 0,5182 | 330,09 | 242,38 | 7,40 | 6,97 |
| Híbrido: "Gradient Boosting" | 0,5113 | 332,45 | 248,10 | 7,56 | 7,14 |
| Híbrido: "XGBoost" | 0,5156 | 330,96 | 243,96 | 7,45 | 7,02 |
Fonte: Resultados originais da pesquisa

Os modelos puramente arbóreos revelaram os menores coeficientes OOS-R² (0,4193 a 0,4406) e os maiores erros médios ponderados (WMAPE entre 8,06% e 8,33%). Esse comportamento comprova a hipótese metodológica formulada: diante de safras com contínuo avanço tecnológico secular, algoritmos de partição pura truncam as predições nos tetos pretéritos de treinamento, subestimando as safras recordes recentes.

Por sua vez, a inclusão do destendenciamento conferiu ganhos expressivos a todas as abordagens de ensemble. A arquitetura Híbrido XGBoost atingiu WMAPE de 7,02%, acompanhado de MAE de 243,96 kg ha⁻¹ (~4,06 sacas por hectare), RMSE de 330,96 kg ha⁻¹ e OOS-R² de 0,5156, demonstrando ótimo equilíbrio entre a absorção da curva tecnológica secular e a sensibilidade a choques fenológicos.

Para elucidar a consistência preditiva alcançada e sua fundamentação agronômica, a acurácia do modelo Híbrido XGBoost foi sintetizada na Figura 1, que reúne a evolução temporal histórica estadual e o padrão de dispersão municipal em dados inéditos.

[INSERIR FIGURA — painel_acuracia_preditiva.png]

Figura 1. Desempenho preditivo do modelo XGBoost Híbrido na validação temporal "Out-of-Time" (safras 2022 a 2024): A - série temporal histórica da produtividade média anual de soja em Mato Grosso (2008–2024); e B - diagrama de dispersão entre valores observados e previstos nos municípios
Fonte: Resultados originais da pesquisa

A interpretação conjunta dos painéis da Figura 1 fornece sustentação analítica robusta para a acurácia do modelo preditivo proposto. No Painel A, constata-se que o modelo reproduziu com estreita fidelidade a dinâmica temporal da produtividade agregada do estado de Mato Grosso ao longo de quase duas décadas. No período de teste cego (2022 a 2024), demarcado à direita da linha vertical pontilhada, o algoritmo não apenas capturou os patamares de alta produtividade das safras 2022 e 2023, mas acompanhou de maneira precisa a severa quebra agrícola registrada em 2024, decorrente da forte estiagem provocada pelo fenômeno El Niño. Modelos puramente baseados em árvores teriam falhado duplamente nesse horizonte: truncariam as projeções nos anos recordes e superestimariam a produtividade na safra 2024 por falta de flexibilidade de decomposição residual.

No Painel B, o diagrama de dispersão entre valores reais e previstos para as observações municipais do triênio de teste demonstra aderência linear expressiva em torno da bissetriz de 45° (linha 1:1 tracejada em vermelho). Observa-se ausência de viés sistemático de subestimação ou superestimação: a nuvem de pontos distribui-se de forma homogênea e concentrada ao longo de todo o espectro produtivo (desde municípios com forte quebra, registrando rendimentos inferiores a 2.500 kg ha⁻¹, até municípios de alta tecnologia que superaram 4.000 kg ha⁻¹). Esse ajuste fino confirma que o erro absoluto médio de 243,96 kg ha⁻¹ (equivalente a aproximadamente 4,06 sacas por hectare) e o WMAPE de 7,02% refletem uma assertividade operacional tangível e homogênea em nível municipal, sustentando o modelo como uma ferramenta confiável para subsidiar o planejamento de tradings, seguradoras e cooperativas antes da colheita.

Adicionalmente, na validação cruzada espacial ("Leave-Municipality-Out"), o modelo alcançou WMAPE de 5,27% em municípios completamente inéditos na fase de ajuste, confirmando que os preditores orbitais e agrometeorológicos transferem conhecimento ecofisiológico genuíno entre distintas regiões geográficas de Mato Grosso, prevenindo memorizações espaciais espúrias.

### Validação das suposições estatísticas e diagnóstico residual

A Tabela 3 resume os diagnósticos formais aplicados aos resíduos e à estrutura de covariáveis do modelo calibrado sob a formulação otimizada.

Tabela 3. Resultados dos testes de suposições estatísticas dos resíduos e preditores
| Teste Estatístico | Hipótese Nula (H₀) | Estatística de Teste | p-valor | Conclusão Diagnóstica |
| :--- | :--- | :--- | :--- | :--- |
| Índice de Moran Global | Ausência de autocorrelação espacial | I = 0,0804 | 0,0570 | Não rejeita H₀ — resíduos com distribuição de ruído branco espacial |
| Teste de Breusch-Pagan | Variância residual homocedástica | LM = 0,8560 | 0,3549 | Não rejeita H₀ — variância dos erros estritamente homocedástica |
| VIF (EVI_j1) | Ausência de multicolinearidade | VIF = 2,996 | — | Ausência de multicolinearidade severa (parcimônia alcançada) |
| VIF (EVI_j2) | Ausência de multicolinearidade | VIF = 1,494 | — | Ausência de multicolinearidade (independência espectral) |
| VIF (Estresse Composto J2) | Ausência de multicolinearidade | VIF = 1,632 | — | Ausência de multicolinearidade no choque térmico-hídrico |
Fonte: Resultados originais da pesquisa

O Índice de Moran Global dos resíduos (I = 0,0804; p-valor = 0,0570 > 0,05) não rejeitou a hipótese nula de aleatoriedade espacial. O resultado atesta que a inclusão das variáveis orbitais (MODIS) e meteorológicas em grade (TerraClimate) foi plenamente suficiente para absorver os gradientes regionais de precipitação e temperatura do estado de Mato Grosso, gerando resíduos sem dependência espacial e dispensando a parametrização de estruturas geoestatísticas pesadas, como krigagem ou modelos auto-regressivos espaciais.

No que tange à homocedasticidade, o teste formal de Breusch-Pagan aplicado ao conjunto de teste apresentou estatística do Multiplicador de Lagrange LM = 0,8560 (p-valor = 0,3549), resultando na aceitação inequívoca da hipótese nula de variância constante dos resíduos ao nível de 5% de significância. A resolução definitiva da heterocedasticidade decorreu da introdução do termo de estresse bioclimático composto na Janela 2 (def_j2 × (tmean_j2 - 25)): ao capturar a penalização simultânea e multiplicativa do déficit hídrico sob temperaturas excessivas na fase crítica de enchimento de grãos, o algoritmo equalizou a margem de erro entre safras de produtividade regular (2022 e 2023) e safras com choques severos de estiagem (2024), conferindo simetria e estabilidade estrutural à distribuição residual.

Por fim, o diagnóstico do Fator de Inflação da Variância (VIF) comprovou a plena eficácia da seleção de variáveis. Ao descartar o NDVI e conservar exclusivamente o EVI como índice de vegetação, o VIF do índice na janela vegetativa recuou de 12,99 para 2,996, enquanto na janela reprodutiva registrou 1,494 e o termo de estresse composto apresentou 1,632. Esse resultado consolida a parcimônia matemática do modelo, eliminando os riscos de instabilidade numérica e sobreajuste espacial, mantendo a sensibilidade biofísica ao acúmulo de biomassa da soja.

### Interpretabilidade agronômica e sensibilidade ecofisiológica (SHAP)

O exame das decisões do modelo preditivo híbrido por meio da metodologia SHAP é ilustrado no painel unificado da Figura 2.

[INSERIR FIGURA — painel_shap_integrado.png]

Figura 2. Painel de interpretabilidade fenológica do modelo XGBoost Híbrido via SHAP: A - gráfico de importância global ("Beeswarm Plot"); B - gráfico de dependência parcial para déficit hídrico em J2; C - gráfico de dependência parcial para temperatura média em J2; e D - gráfico de dependência parcial para tendência secular anual
Fonte: Resultados originais da pesquisa

A hierarquia de importância global dos fatores (Figura 2A) apresenta consonância rigorosa com a ecofisiologia da soja (*Glycine max*). A variável "Ano da Safra" despontou como o elemento de maior relevância absoluta no painel SHAP (Figura 2A e Figura 2D), evidenciando impacto linear positivo e estável sobre o rendimento previsto. Essa resposta consolida a justificativa teórica do destendenciamento adotado: o avanço tecnológico anual promoveu elevação progressiva do potencial produtivo basal no estado, desacoplando o efeito evolutivo de longo prazo das oscilações meteorológicas sazonais.

No tocante às variáveis agroclimáticas, a compartimentação fenológica revelou que os atributos associados à Janela 2 (janeiro a março — florescimento, frutificação e enchimento de grãos) atuam como os reguladores limitantes mais severos da colheita final. O déficit hídrico reprodutivo (def_j2) exibiu correlação marginal marcadamente negativa (Figura 2B): sob condições de suprimento pluviométrico adequado (valores de def_j2 próximos a zero), o efeito marginal sobre a estimativa manteve-se favorável ou neutro; todavia, a ocorrência de déficits crescentes em J2 impôs penalizações drásticas na produtividade estimada, gerando reduções marginais que superaram -60 kg ha⁻¹. Esse resultado corrobora com precisão as constatações clássicas de Farias et al. (2007) e James et al. (2008), que indicam que a ocorrência de estresse hídrico nos estádios reprodutivos R3 a R6 induz abscisão de flores, abortamento de vagens e redução na taxa de acúmulo de biomassa nos grãos, causando perdas irreversíveis de produtividade que não podem ser compensadas pelo manejo.

Similarmente, a temperatura média do ar na Janela 2 (tmean_j2) revelou comportamento não-linear pronunciado sobre o rendimento previsto (Figura 2C). O modelo identificou uma faixa de conforto térmico entre 23,5 °C e 25,0 °C, na qual o impacto sobre a produtividade se manteve positivo. Contudo, ao transpor o limiar crítico de 25,5 °C, observou-se acentuada penalização marginal (decréscimos superiores a -40 kg ha⁻¹ na predição municipal). Fisiologicamente, o excesso térmico em fases reprodutivas acelera o metabolismo respiratório de manutenção da planta, consome reservas de fotoassimilados que seriam translocadas aos grãos e reduz a viabilidade polínica (Sentelhas et al., 2015).

Na Janela 1 (outubro a dezembro — emergência e desenvolvimento vegetativo), o índice EVI_j1 demonstrou impacto predominantemente positivo na consolidação do rendimento (Figura 2A). Lavouras com fechamento precoce de dossel e elevado índice de biomassa fotossinteticamente ativa no período vegetativo estabelecem maior número de nós reprodutivos por planta e desenvolvem sistemas radiculares mais profundos, criando maior tolerância basal contra estiagens curtas ("veranicos") durante a fase subsequente de enchimento.

### Comparação com a literatura e aplicabilidade no agronegócio

A contextualização dos resultados deste trabalho frente a estudos representativos da literatura científica recente é apresentada na Tabela 4.

Tabela 4. Comparação do desempenho preditivo com estudos da literatura científica de sensoriamento remoto e aprendizado de máquina
| Referência | Região e Escala Espacial | Modelo Aplicado | Variáveis Principais | Métrica de Erro Publicada |
| :--- | :--- | :--- | :--- | :--- |
| Schwalbert et al. (2020) | Rio Grande do Sul, Brasil (Municipal) | "Random Forest" | MODIS (NDVI), chuva e temperatura | RMSE ~300 a 450 kg ha⁻¹ |
| Richetti et al. (2018) | Paraná, Brasil (Municipal) | "Random Forest" / ML | MODIS (EVI fenológico) | MAPE ~8,0% a 11,5% |
| Ray et al. (2015) | Global (~13.500 unidades políticas) | Regressões Climáticas | Anomalias de chuva e temperatura | Variabilidade explicada: 32% a 39% (global) e >60% (celeiros) |
| Pantazi et al. (2016) | Grécia (Escala de Talhão) | Redes Neurais / "Kohonen" | Sensores de dossel e solo "in situ" | RMSE ~200 kg ha⁻¹ |
| Este trabalho | Mato Grosso, Brasil (Municipal) | Híbrido: RLM + "XGBoost" | MODIS (EVI, LST) + TerraClimate + Estresse Composto | WMAPE 7,02% / MAE 244,0 kg ha⁻¹ / OOS-R² 0,5156 |
Fonte: Resultados originais da pesquisa e compilação bibliográfica

A análise comparativa da Tabela 4 evidencia que o modelo desenvolvido neste estudo se posiciona no estado da arte da previsão de safras por sensoriamento remoto. Frente aos achados de Schwalbert et al. (2020) no Rio Grande do Sul (RMSE de 300 a 450 kg ha⁻¹), a formulação híbrida em Mato Grosso manteve o RMSE em 330,96 kg ha⁻¹, com a distinção metodológica de operar sobre um território com mais de 12 milhões de hectares cultivados e submetido a dinâmicas climáticas tropicais de transição.

Em paralelo, quando confrontado com o estudo de Richetti et al. (2018) no Paraná (MAPE entre 8,0% e 11,5%), o Híbrido XGBoost atingiu WMAPE de 7,02% e MAPE de 7,45%. Cumpre notar a importância da adoção do WMAPE em estudos regionais: enquanto o MAPE aritmético tradicional confere o mesmo peso relativo a pequenos municípios marginais e a municípios líderes de colheita, o WMAPE pondera as discrepâncias pelo volume de grãos e área plantada, oferecendo uma leitura diretamente alinhada à realidade física da safra estadual.

Embora ensaios em nível de talhão, como o de Pantazi et al. (2016) na Grécia, apresentem erros nominais ligeiramente inferiores (RMSE ~200 kg ha⁻¹), tais métodos apoiam-se em amostragens químicas de solo e condutividade elétrica coletadas localmente ("in situ"). Essa dependência de levantamentos terrestres inviabiliza sua aplicação em escala operacional estadual. Em contraposição, o pipeline em nuvem construído via Google Earth Engine extrai, processa e disponibiliza todas as variáveis orbitais e climáticas de Mato Grosso em menos de 10 minutos, oferecendo previsões municipais antes do encerramento da safra a custo computacional marginal.

No contexto operacional da cadeia produtiva, a precisão alcançada — desvio médio absoluto de 243,96 kg ha⁻¹, equivalente a cerca de 4,06 sacas por hectare em um estado com rendimento médio ao redor de 60 sacas por hectare — confere alto valor aplicado:
- Para produtores e cooperativas: subsidia decisões antecipadas de comercialização ("hedge" em mercados futuros B3/CBOT) e baliza contratações de seguro paramétrico indexado ao risco de déficit hídrico na Janela 2;
- Para tradings e operadores logísticos: antecipa a demanda por capacidade estática de armazenagem e contratação de frotas de transporte rodoviário e ferroviário em direção aos portos do Arco Norte e Santos, atenuando gargalos de frete;
- Para agentes financeiros e formuladores de políticas públicas: norteia a concessão técnica de crédito agrícola e a calibração de estoques reguladores governamentais com respaldo estatístico auditável.

### Limitações metodológicas, escala espacial e considerações analíticas

A interpretação crítica da acurácia preditiva e dos diagnósticos econométricos requer a contextualização de quatro aspectos estruturais inerentes à modelagem agrícola regional:

a) Variância residual e atributos edafológicos

O coeficiente de determinação fora da amostra (OOS-R² = 0,5156) indica que aproximadamente 48% da variabilidade municipal da produtividade decorre de forçantes não capturadas pela matriz de preditores orbital e climática. No contexto de dados agregados da Pesquisa Agrícola Municipal (PAM/IBGE), variáveis edafológicas clássicas (textura, teor de argila, matéria orgânica e capacidade de água disponível — CAD) comportam-se como atributos estáticos no tempo para determinado município. Embora exerçam influência preponderante na variabilidade espacial em nível submunicipal e de talhão, a diferenciação basal do potencial produtivo entre municípios é absorvida no modelo pelo intercepto e pela covariável de área plantada da regressão linear secular. As oscilações interanuais e choques extremos de produtividade — como o evento de El Niño em 2023/24 — são governados primordialmente pela dinâmica térmica e hídrica. Ademais, o índice EVI a 250 m opera como um integrador fenológico terminal do sistema solo-planta-atmosfera, refletindo os sintomas fisiológicos de estresse hídrico condicionados pela textura do solo diretamente no dossel foliar. Em nível municipal com validação estritamente cega no tempo, a obtenção de OOS-R² próximo a 0,52 situa-se em estrita consonância com a literatura internacional de sensoriamento remoto (Schwalbert et al., 2020; Bolton e Friedl, 2013).

b) Destendenciamento secular: Regressão Linear Múltipla vs. Filtro Hodrick-Prescott

A extração da tendência tecnológica histórica por meio da Regressão Linear Múltipla (RLM) pautou-se na preservação estrita da blindagem contra vazamento de informações temporais ("look-ahead bias"). Embora filtros iterativos como o de Hodrick-Prescott (HP) sejam amplamente difundidos na análise macroeconômica retrospectiva (Hodrick e Prescott, 1997), sua aplicação em arquiteturas de previsão operacional "ex-ante" é desaconselhada por duas razões conceituais: primeiro, o filtro HP é um operador bidirecional ("two-sided") que utiliza observações futuras para suavizar a trajetória passada, tornando-se matematicamente inviável em cenários de previsão pré-colheita; segundo, filtros flexíveis sofrem severamente do "problema da extremidade" ("end-point problem") na ponta recente da série (Hamilton, 2018). Conforme verificado empiricamente neste estudo, a quebra climática de 2024 curvature a linha de tendência do HP para baixo, absorvendo artificialmente 93,3% da anomalia climática como se fora declínio tecnológico estrutural. Em contraste, a projeção da RLM ajustada estritamente no intervalo de treinamento (2008–2021) manteve a tendência tecnológica isolada e independente das anomalias climáticas das safras de teste.

c) Discrepância de resolução espacial e convecção tropical

A disparidade entre a resolução espacial do sensor MODIS (250 m no EVI e 1.000 m no LST) e a grade climática do TerraClimate (1/24°, ~4 km) constitui um desafio frequente em estudos com dados globais de reanálise. Em regiões tropicais como Mato Grosso, episódios convectivos de verão geram precipitações de forte heterogeneidade espacial localizada. Todavia, a amostragem das variáveis no Google Earth Engine não incidiu sobre o polígono bruto municipal, mas foi restrita estritamente às áreas com cobertura de soja confirmada pela máscara agrícola. Em polos de grande extensão (como Sorriso ou Sapezal), a grade climática de 4 km gera mais de uma centena de células sobrepostas à área cultivada, minimizando o erro de representatividade. Paralelamente, o EVI orbital de 250 m atua como atenuador dessa discrepância, capturando em escala submunicipal os efeitos fenológicos de secas pontuais que a média da célula climática de 4 km tende a suavizar.

d) Dinâmica de fronteira agrícola e persistência temporal da máscara

A adoção da máscara de soja da safra anterior (2023) para a extração espectral do ano de 2024 decorreu da latência cronológica intrínseca à disponibilização dos produtos de cobertura da terra. Em ambientes operacionais reais, as classificações de uso do solo (como a Coleção do MapBiomas) são divulgadas no segundo semestre do ano corrente, enquanto a previsão antecipada de safra demanda execução entre janeiro e fevereiro. A assunção da persistência temporal da máscara em t-1 é o padrão metodológico consagrado por programas internacionais de inteligência agrícola (Becker-Reshef et al., 2010, 2018). No território mato-grossense, onde mais de 95% da área cultivada com soja recai sobre talhões consolidados em ciclos anteriores, a incorporação de áreas de expansão recente exerce impacto marginal sobre a mediana espectral municipal, preservando a fidelidade operacional da simulação.

---

## Conclusões

Este trabalho desenvolveu e validou uma abordagem preditiva de aprendizado de máquina baseada na compartimentação fenológica das variáveis espectrais e climáticas aliada a uma arquitetura híbrida de destendenciamento para estimar antecipadamente o rendimento municipal da soja no estado de Mato Grosso. A metodologia integrou séries temporais do sensor MODIS (com seleção do índice EVI), dados climáticos em grade do TerraClimate e registros agrícolas do IBGE sob rigorosos protocolos de blindagem espaçotemporal contra vazamento de dados.

A formulação híbrida, ao combinar a Regressão Linear Múltipla para absorção da tendência secular tecnológica com algoritmos de gradiente e florestas aleatórias para modelagem não-linear dos resíduos agroclimáticos, superou com êxito a limitação de extrapolação matemática intrínseca aos modelos de partição pura. Na validação temporal fora da amostra ("Out-of-Time") com safras inéditas de teste (2022 a 2024), o modelo Híbrido XGBoost demonstrou notável acurácia preditiva, alcançando Erro Absoluto Médio de 243,96 kg ha⁻¹ (~4,06 sacas por hectare), Erro Percentual Absoluto Ponderado de 7,02% e coeficiente de determinação OOS-R² de 0,5156, além de consolidar WMAPE de 5,27% em municípios nunca antes observados pelo algoritmo na validação cruzada espacial ("Leave-Municipality-Out").

O diagnóstico de suposições estatísticas confirmou a integridade analítica e a parcimônia da metodologia. A seleção do EVI como índice de vegetação exclusivo extinguiu a multicolinearidade severa (VIF reduzido de 12,99 para 2,99), enquanto a introdução do preditor de estresse bioclimático composto estabilizou a dispersão residual sob anomalias climáticas extremas, conduzindo à aceitação plena da homocedasticidade no teste de Breusch-Pagan (LM = 0,8560; p-valor = 0,3549). O Índice de Moran Global não rejeitou a hipótese de aleatoriedade espacial (I = 0,0804; p-valor = 0,0570), comprovando que as variáveis orbitais e climáticas absorveram eficientemente os gradientes territoriais e geraram resíduos com padrão de ruído branco. A análise de interpretabilidade via SHAP atestou consonância ecofisiológica rigorosa das predições: o déficit hídrico e temperaturas elevadas na fase reprodutiva (Janela 2) atuaram como os fatores limitantes primários da produtividade, enquanto o vigor vegetativo inicial (Janela 1) sustentou o potencial produtivo da cultura.

Conclui-se que o modelo proposto alia elevada precisão métrica, velocidade de processamento computacional em nuvem, estabilidade econométrica e respaldo agronômico transparente. A ferramenta consolida-se como um instrumento robusto e viável para subsidiar o planejamento antecipado de comercialização, gestão de risco de seguro rural, logística de transporte e governança de políticas de abastecimento de safras de soja em escala regional.

---

## Agradecimentos

O autor expressa seus sinceros agradecimentos ao orientador, Prof. Dr. Walter Mesquita Filho, pelas valiosas contribuições, e ao corpo docente do MBA em Data Science e Analytics da USP/ESALQ pelo apoio técnico e científico dedicado durante a elaboração deste trabalho.

---

## Referências

Abatzoglou, J.T.; Dobrowski, S.Z.; Parks, S.A.; Hegewisch, K.C. 2018. TerraClimate, a high-resolution global dataset of monthly climate and climatic water balance from 1958–2015. Scientific Data 5(1): 1-12.

Akiba, T.; Sano, S.; Yanase, T.; Ohta, T.; Koyama, M. 2019. Optuna: A next-generation hyperparameter optimization framework. In: ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 25., 2019, Anchorage, AK, USA. Anais... p. 2623-2631.

Battisti, R.; Sentelhas, P.C. 2017. Improvement of soybean resilience to drought through deep root system in Brazil. Agronomy Journal 109(4): 1612-1622.

Becker-Reshef, I.; Justice, C.; Sullivan, M.; Vermote, E.; Tucker, C.; Anyamba, A.; Small, J.; Pak, E.; Masuoka, E.; Schmaltz, J.; Hansen, M.; Pittman, K.; Birkett, C.; Williams, D.; Reynolds, C.; Doorn, B. 2010. Monitoring global croplands with coarse resolution earth observations: The Global Agriculture Monitoring (GLAM) project. Remote Sensing 2(6): 1589-1609.

Becker-Reshef, I.; Franch, B.; Barker, B.; Murphy, E.; Santamaria-Artigas, A.; Humber, M.; Skakun, S.; Vermote, E. 2018. Prior season crop type masks for winter wheat yield forecasting: A US case study. Remote Sensing 10(10): 1659.

Bolton, D.K.; Friedl, M.A. 2013. Forecasting crop yield using remotely sensed vegetation indices and crop phenology metrics. Agricultural and Forest Meteorology 173: 74-84.

Breiman, L. 2001. Random forests. Machine Learning 45(1): 5-32.

Breusch, T.S.; Pagan, A.R. 1979. A simple test for heteroscedasticity and random coefficient variation. Econometrica 47(5): 1287-1294.

Centro de Estudos Avançados em Economia Aplicada [Cepea]. 2023. PIB do agronegócio brasileiro. Disponível em: <https://www.cepea.esalq.usp.br>. Acesso em: ago. 2026.

Chen, T.; Guestrin, C. 2016. XGBoost: A scalable tree boosting system. In: ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 22., 2016, San Francisco, CA, USA. Anais... p. 785-794.

Companhia Nacional de Abastecimento [Conab]. 2023. Acompanhamento da safra brasileira de grãos. Disponível em: <https://www.conab.gov.br>. Acesso em: ago. 2026.

Doraiswamy, P.C.; Hatfield, J.L.; Jackson, T.J.; Akhmedov, B.; Prueger, J.; Stern, A. 2004. Crop condition and yield simulations using Landsat and MODIS. Remote Sensing of Environment 92(4): 548-559.

Farias, J.R.B.; Nepomuceno, A.L.; Neumaier, N. 2007. Ecofisiologia da soja. Embrapa Soja, Londrina, PR, Brasil. (Circular Técnica 48).

Friedman, J.H. 2001. Greedy function approximation: A gradient boosting machine. Annals of Statistics 29(5): 1189-1232.

Gorelick, N.; Hancher, M.; Dixon, M.; Ilyushchenko, S.; Thau, D.; Moore, R. 2017. Google Earth Engine: Planetary-scale geospatial analysis for everyone. Remote Sensing of Environment 202: 18-27.

Hamilton, J.D. 2018. Why you should never use the Hodrick-Prescott filter. The Review of Economics and Statistics 100(5): 831-843.

Hodrick, R.J.; Prescott, E.C. 1997. Postwar U.S. business cycles: An empirical investigation. Journal of Money, Credit, and Banking 29(1): 1-16.

Huete, A.; Didan, K.; Miura, T.; Rodriguez, E.P.; Gao, X.; Ferreira, L.G. 2002. Overview of the radiometric and biophysical performance of the MODIS vegetation indices. Remote Sensing of Environment 83(1-2): 195-213.

Instituto Brasileiro de Geografia e Estatística [IBGE]. 2023. Sistema IBGE de Recuperação Automática (SIDRA) — Pesquisa da Produção Agrícola Municipal (PAM). Disponível em: <https://sidra.ibge.gov.br>. Acesso em: ago. 2026.

Instituto Mato-grossense de Economia Agropecuária [IMEA]. 2023. Relatórios de acompanhamento da safra de soja em Mato Grosso. Disponível em: <http://www.imea.com.br>. Acesso em: ago. 2026.

James, A.T.; Lawn, R.J.; Cooper, M. 2008. Genotypic variation for drought stress response traits in soybean. III. Phenotypic and genetic variation for yield and yield components under drought stress. Australian Journal of Agricultural Research 59(7): 670-678.

Lundberg, S.M.; Lee, S. 2017. A unified approach to interpreting model predictions. Advances in Neural Information Processing Systems 30: 4765-4774.

Meyer, H.; Pebesma, E. 2022. Machine learning-based global maps of ecological variables and the challenge of assessing them. Nature Communications 13(1): 2208.

Monteiro, L.A.; Sentelhas, P.C. 2014. Calibration and test of an agrometeorological model for the estimation of soybean yields in different Brazilian regions. Acta Scientiarum. Agronomy 36(3): 265-272.

Pantazi, X.E.; Moshou, D.; Alexandridis, T.; Whetton, R.L.; Mouazen, A.M. 2016. Wheat yield prediction using machine learning and advanced sensing techniques. Computers and Electronics in Agriculture 121: 57-65.

Pedregosa, F.; Varoquaux, G.; Gramfort, A.; Michel, V.; Thirion, B.; Grisel, O.; Blondel, M.; Prettenhofer, P.; Weiss, R.; Dubourg, V.; Vanderplas, J.; Passos, A.; Cournapeau, D.; Brucher, M.; Perrot, M.; Duchesnay, E. 2011. Scikit-learn: Machine learning in Python. Journal of Machine Learning Research 12: 2825-2830.

Pereira, R.H.M.; Gonçalves, C.N.; Chaves, P.A.B. 2019. geobr: Pacote R e Python para baixar conjuntos de dados espaciais oficiais do Brasil. Instituto de Pesquisa Econômica Aplicada [IPEA], Rio de Janeiro, RJ, Brasil.

Projeto MapBiomas. 2023. Coleção 9.0 da série anual de mapas de cobertura e uso de solo do Brasil. Disponível em: <https://mapbiomas.org>. Acesso em: ago. 2026.

Ray, D.K.; Gerber, J.S.; MacDonald, G.K.; West, P.C. 2015. Climate variation explains a third of global crop yield variability. Nature Communications 6: 5989.

Rey, S.J.; Anselin, L. 2007. PySAL: A Python library of spatial analytical methods. The Review of Regional Studies 37(1): 5-27.

Richetti, J.; Judge, J.; Boote, K.J.; Johann, J.A.; Uribe-Opazo, M.A.; Becker, W.R.; Paludo, A.; de Albuquerque Silva, L.C. 2018. Using phenology-based Enhanced Vegetation Index and machine learning for soybean yield estimation in Paraná State, Brazil. Journal of Applied Remote Sensing 12(2): 026029.

Schwalbert, R.A.; Amado, T.; Corassa, G.; Pott, L.P.; Prasad, P.V.V.; Ciampitti, I.A. 2020. Satellite-based soybean yield forecast: Integrating machine learning and weather data for improving crop yield prediction in southern Brazil. Agricultural and Forest Meteorology 284: 107886.

Seabold, S.; Perktold, J. 2010. statsmodels: Econometric and statistical modeling with python. In: Python in Science Conference, 9., 2010, Austin, TX, USA. Anais... p. 92-96.

Sentelhas, P.C.; Battisti, R.; Câmara, G.M.S.; Farias, J.R.B.; Hampf, A.C.; Nendel, C. 2015. The soybean yield gap in Brazil — magnitude, causes and possible solutions for sustainable production. The Journal of Agricultural Science 153(8): 1394-1411.

United States Department of Agriculture [USDA]. 2023. World agricultural production. Disponível em: <https://www.fas.usda.gov>. Acesso em: ago. 2026.
