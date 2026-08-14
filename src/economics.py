def calcular_ahorro_neto(probabilidades, y_real, LTV, umbral, tasa_exito, costo_campana):
    predicciones = (probabilidades >= umbral).astype(int)
    
    es_vp = (predicciones == 1) & (y_real == 1)
    es_fp = (predicciones == 1) & (y_real == 0)
    
    LTV_de_los_vp = LTV[es_vp]
    beneficio_vp = (LTV_de_los_vp * tasa_exito - costo_campana).sum()
    costo_fp = es_fp.sum() * costo_campana
    
    ahorro_neto = beneficio_vp - costo_fp
    
    return ahorro_neto

def calcular_campana_masiva(LTV, son_churn_real, total_clientes, tasa_exito, costo_campana):
    LTV_de_los_que_se_van = LTV[son_churn_real]
    beneficio_retenidos = (LTV_de_los_que_se_van * tasa_exito - costo_campana).sum()
    costo_resto = (total_clientes - son_churn_real.sum()) * costo_campana
    return beneficio_retenidos - costo_resto