import streamlit as st
import pandas as pd
import joblib
import plotly.express as px
import os
import sys
import numpy as np

carpeta_actual = os.path.dirname(os.path.abspath(__file__))
carpeta_raiz = os.path.dirname(carpeta_actual)
sys.path.append(carpeta_raiz)

from src.economics import calcular_ahorro_neto, calcular_campana_masiva
columnas_modelo = joblib.load('streamlit_app/columnas_modelo.pkl')

st.set_page_config(page_title="Predicción de Churn - Telco", layout="wide")

st.title("📊 Predicción de Fuga de Clientes (Churn)")
st.write("Dashboard interactivo para explorar el impacto económico del modelo de predicción de churn.")

modelo = joblib.load('streamlit_app/modelo_final.pkl')
datos_test = pd.read_csv('streamlit_app/datos_test.csv')

modo = st.sidebar.radio(
    "Elegí una vista:",
    ["Exploración de escenarios", "Predicción de cliente individual"]
)

if modo == "Exploración de escenarios":
    st.header("Exploración de Escenarios Económicos")
    
    st.subheader("Ajustá los supuestos")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tasa_exito = st.slider("Tasa de éxito de campaña (%)", 10, 60, 35) / 100
    with col2:
        costo_campana = st.slider("Costo de campaña ($)", 10, 150, 49)
    with col3:
        umbral = st.slider("Umbral de decisión", 0.01, 0.99, 0.15)
    
    ahorro_modelo = calcular_ahorro_neto(
        datos_test['probabilidad'], 
        datos_test['churn_real'], 
        datos_test['LTV'], 
        umbral, 
        tasa_exito, 
        costo_campana
    )
    
    ahorro_masiva = calcular_campana_masiva(
        datos_test['LTV'], 
        datos_test['churn_real'] == 1, 
        len(datos_test), 
        tasa_exito, 
        costo_campana
    )
    
    st.subheader("Resultado")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Ahorro Neto - Modelo", f"${ahorro_modelo:,.2f}")
    with col2:
        st.metric("Ahorro Neto - Campaña Masiva", f"${ahorro_masiva:,.2f}")

    st.subheader("Ahorro Neto vs. Umbral de Decisión")
    
    
    umbrales_grafico = np.arange(0.01, 1.0, 0.02)
    ahorros_grafico = [
        calcular_ahorro_neto(datos_test['probabilidad'], datos_test['churn_real'], datos_test['LTV'], u, tasa_exito, costo_campana)
        for u in umbrales_grafico
    ]
    
    tabla_grafico = pd.DataFrame({'Umbral': umbrales_grafico, 'Ahorro Neto': ahorros_grafico})
    
    fig = px.line(tabla_grafico, x='Umbral', y='Ahorro Neto', title='Ahorro Neto según Umbral (con los supuestos actuales)')
    fig.add_hline(y=ahorro_masiva, line_dash='dash', annotation_text='Campaña masiva a ciegas')
    fig.add_vline(x=umbral, line_dash='dot', annotation_text='Umbral seleccionado')
    
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.header("Predicción de Cliente Individual")
    st.write("Cargá los datos de un cliente para estimar su probabilidad de fuga.")

    col1, col2 = st.columns(2)

    with col1:
        gender = st.selectbox("Género", ["Male", "Female"])
        senior = st.selectbox("¿Adulto mayor?", ["No", "Yes"])  
        partner = st.selectbox("¿Tiene pareja?", ["No", "Yes"])
        dependents = st.selectbox("¿Tiene personas a cargo?", ["No", "Yes"])
        tenure = st.number_input("Meses de antigüedad", 0, 72, 12)
        phone_service = st.selectbox("¿Tiene servicio telefónico?", ["Yes", "No"])
        contract = st.selectbox("Tipo de contrato", ["Month-to-month", "One year", "Two year"])
        paperless = st.selectbox("¿Facturación sin papel?", ["Yes", "No"])

    with col2:
        internet = st.selectbox("Servicio de Internet", ["DSL", "Fiber optic", "No"])
        online_security = st.selectbox("Seguridad online", ["No", "Yes", "No internet service"])
        online_backup = st.selectbox("Backup online", ["No", "Yes", "No internet service"])
        device_protection = st.selectbox("Protección de dispositivo", ["No", "Yes", "No internet service"])
        tech_support = st.selectbox("Soporte técnico", ["No", "Yes", "No internet service"])
        streaming_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
        streaming_movies = st.selectbox("Streaming Movies", ["No", "Yes", "No internet service"])
        multiple_lines = st.selectbox("Múltiples líneas", ["No", "Yes", "No phone service"])
        payment_method = st.selectbox("Método de pago", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
        monthly_charges = st.number_input("Cargo mensual ($)", 0.0, 150.0, 65.0)

    boton_predecir = st.button("Predecir riesgo de fuga")
    
    if boton_predecir:
        total_charges = monthly_charges * tenure

        contract_map = {"Month-to-month": 0, "One year": 1, "Two year": 2}
        servicio_map = {"Yes": 1, "No": 0, "No internet service": 0, "No phone service": 0}

        total_servicios = sum([
            servicio_map[phone_service], servicio_map[online_security],
            servicio_map[online_backup], servicio_map[device_protection],
            servicio_map[tech_support], servicio_map[streaming_tv],
            servicio_map[streaming_movies]
        ])
        cargo_promedio_mensual = total_charges / tenure if tenure > 0 else 0

        cliente = pd.DataFrame([{
            'Gender': 1 if gender == "Male" else 0,
            'Senior Citizen': 1 if senior == "Yes" else 0,
            'Partner': 1 if partner == "Yes" else 0,
            'Dependents': 1 if dependents == "Yes" else 0,
            'Tenure Months': tenure,
            'Phone Service': servicio_map[phone_service],
            'Online Security': servicio_map[online_security],
            'Online Backup': servicio_map[online_backup],
            'Device Protection': servicio_map[device_protection],
            'Tech Support': servicio_map[tech_support],
            'Streaming TV': servicio_map[streaming_tv],
            'Streaming Movies': servicio_map[streaming_movies],
            'Contract': contract_map[contract],
            'Paperless Billing': 1 if paperless == "Yes" else 0,
            'Monthly Charges': monthly_charges,
            'Total Charges': total_charges,
            'Total Services': total_servicios,
            'Cargo_Promedio_Mensual': cargo_promedio_mensual,
            'Multiple Lines_No': 1 if multiple_lines == "No" else 0,
            'Multiple Lines_No phone service': 1 if multiple_lines == "No phone service" else 0,
            'Multiple Lines_Yes': 1 if multiple_lines == "Yes" else 0,
            'Internet Service_DSL': 1 if internet == "DSL" else 0,
            'Internet Service_Fiber optic': 1 if internet == "Fiber optic" else 0,
            'Internet Service_No': 1 if internet == "No" else 0,
            'Payment Method_Bank transfer (automatic)': 1 if payment_method == "Bank transfer (automatic)" else 0,
            'Payment Method_Credit card (automatic)': 1 if payment_method == "Credit card (automatic)" else 0,
            'Payment Method_Electronic check': 1 if payment_method == "Electronic check" else 0,
            'Payment Method_Mailed check': 1 if payment_method == "Mailed check" else 0,
        }])

        cliente = cliente[columnas_modelo]
        probabilidad = modelo.predict_proba(cliente)[0][1]

        st.subheader("Resultado")
        st.metric("Probabilidad de fuga", f"{probabilidad*100:.1f}%")

        if probabilidad >= 0.15:
            st.error("⚠️ Cliente en riesgo — se recomienda contactar con campaña de retención")
        else:
            st.success("✅ Cliente de bajo riesgo — no requiere acción inmediata")