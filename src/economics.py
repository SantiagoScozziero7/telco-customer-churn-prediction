def calcular_ahorro_neto(probabilidades, y_real, LTV, umbral, tasa_exito, costo_campana):
    predicciones = (probabilidades >= umbral).astype(int)
    
    es_vp = (predicciones == 1) & (y_real == 1)
    es_fp = (predicciones == 1) & (y_real == 0)
    
    LTV_de_los_vp = LTV[es_vp]
    beneficio_vp = (LTV_de_los_vp * tasa_exito - costo_campana).sum()
    costo_fp = es_fp.sum() * costo_campana
    
    ahorro_neto = beneficio_vp - costo_fp
    
    return ahorro_neto