from sklearn.model_selection import cross_validate

def evaluar_modelo(modelo, X_train, y_train, skf, metricas):
    resultados=cross_validate(modelo, X_train, y_train, cv=skf, scoring=metricas)
    
    print('Resultados promedio:')
    for metrica in metricas:
        print(f'{metrica}: {resultados[f"test_{metrica}"].mean():.4f}')
    
    return resultados