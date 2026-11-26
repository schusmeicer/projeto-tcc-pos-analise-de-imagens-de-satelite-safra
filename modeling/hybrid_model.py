import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import LinearRegression
from sklearn.utils.validation import check_is_fitted

class HybridDetrendingRegressor(BaseEstimator, RegressorMixin):
    """
    Modelo híbrido:
    1. Ajusta uma Regressão Linear Múltipla em TODAS as features (garantindo a base de extrapolação espacial e temporal).
    2. Calcula os resíduos (o que a reta errou).
    3. Treina o estimador base (Random Forest/XGBoost) para prever as não-linearidades nesses resíduos.
    """
    def __init__(self, base_estimator):
        self.base_estimator = base_estimator
        self.linear_model = LinearRegression()

    def fit(self, X, y):
        self.linear_model.fit(X, y)
        linear_pred = self.linear_model.predict(X)
        
        residuals = y - linear_pred
        self.base_estimator.fit(X, residuals)
        
        self.is_fitted_ = True
        return self

    def predict(self, X):
        check_is_fitted(self, 'is_fitted_')
        
        linear_pred = self.linear_model.predict(X)
        residual_pred = self.base_estimator.predict(X)
        
        return linear_pred + residual_pred
