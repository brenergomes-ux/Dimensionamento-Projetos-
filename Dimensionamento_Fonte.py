import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Dimensionamento de Fonte LED - Gelopar",
    page_icon="💡",
    layout="wide"
)

st.title("💡 Dimensionador de Fonte para Conjuntos LED (12V)")
st.caption("Ferramenta de cálculo de potência e corrente para projetos de iluminação LED.")

st.sidebar.header("⚙️ Configurações Gerais")
margem_seguranca = st.sidebar.slider("Margem de Segurança (%)", min_value=10, max_value=50, value=20, step=5)
tensao_sistema = st.sidebar.number_input("Tensão do Sistema (V)", value=12.0, step=1.0)

st.subheader("1. Seleção e Quantidade dos Conjuntos")

col1, col2, col3 = st.columns(3)


with col1:
    st.markdown("### 🔹 Conjunto 1")
    #st.caption("Barras 600mm SERIE 240 LEDS (CCV168 -3077465)")
    qtd_conj1 = st.number_input("Qtd. de Barras (C1):", min_value=0, value=2, step=1)
    pot_conj1_unit = st.number_input("Potência Unitária (W):", value=17.0, step=0.5, key="c1_p")
    pot_total_c1 = qtd_conj1 * pot_conj1_unit
    st.info(f"**Subtotal C1:** {pot_total_c1:.2f} W")

with col2:
    st.markdown("### 🔹 Conjunto 2")
    #st.caption("KIT LED/TB CRISTAL 88L6500K (011870.03)")
    qtd_conj2 = st.number_input("Qtd. de Barras (C2):", min_value=0, value=2, step=1)
    pot_conj2_unit = st.number_input("Potência Unitária (W):", value=9.4, step=0.1, key="c2_p")
    pot_total_c2 = qtd_conj2 * pot_conj2_unit
    st.info(f"**Subtotal C2:** {pot_total_c2:.2f} W")

with col3:
    st.markdown("### 🔹 Conjunto 3")
    #st.caption("LED Neon Light White 10000K (9W/m)")
    pot_m_neon = st.number_input("Potência por metro (W/m):", value=9.0, step=0.5)
    
    st.write("**Trechos de fita:**")
    comp1 = st.number_input("Trecho A (m):", value=1.474, step=0.01, format="%.3f")
    qtd_comp1 = st.number_input("Qtd. Trecho A:", value=2, min_value=1)
    
    comp2 = st.number_input("Trecho B (m):", value=0.495, step=0.01, format="%.3f")
    qtd_comp2 = st.number_input("Qtd. Trecho B:", value=2, min_value=1)
    
    metragem_total_neon = (comp1 * qtd_comp1) + (comp2 * qtd_comp2)
    pot_total_c3 = metragem_total_neon * pot_m_neon
    
    st.caption(f"Metragem total: {metragem_total_neon:.3f} m")
    st.info(f"**Subtotal C3:** {pot_total_c3:.2f} W")

st.markdown("---")

# Cálculos Gerais
potencia_nominal_total = pot_total_c1 + pot_total_c2 + pot_total_c3
fator_margem = 1 + (margem_seguranca / 100)
potencia_com_margem = potencia_nominal_total * fator_margem
corrente_necessaria = potencia_com_margem / tensao_sistema

# Sugestão comercial de fonte
fontes_comerciais = [36, 60, 100, 120, 150, 200, 240, 300, 360, 500]
potencia_sugerida = next((f for f in fontes_comerciais if f >= potencia_com_margem), round(potencia_com_margem * 1.15))
corrente_sugerida = potencia_sugerida / tensao_sistema

st.subheader("2. Resultado do Dimensionamento")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Potência Nominal", f"{potencia_nominal_total:.2f} W")
m2.metric(f"Potência (+{margem_seguranca}%)", f"{potencia_com_margem:.2f} W")
m3.metric("Corrente Requerida", f"{corrente_necessaria:.2f} A")
m4.metric("Fonte Comercial Indicada", f"{potencia_sugerida} W / {corrente_sugerida:.1f} A")

st.markdown("---")
st.subheader("3. Especificação para Compra / Projeto")

st.success(
    f"""
    **ESPECIFICAÇÃO RECOMENDADA DA FONTE:**
    * **Tensão:** {tensao_sistema:.0f}V DC
    * **Capacidade de Potência Mínima:** {potencia_sugerida} Watts
    * **Capacidade de Corrente Mínima:** {corrente_sugerida:.1f} Amperes
    * **Tipo:** Fonte Chaveada {tensao_sistema:.0f}V DC em gabinete colmeia ou selado IP67/IP68.
    """
)
st.markdown("---")
st.subheader("4. Cálculo da Bitola dos Condutores (Queda de Tensão)")

col_b1, col_b2 = st.columns(2)

with col_b1:
    distancia = st.number_input("Distância da fonte até o ponto de distribuição (metros):", value=2.0, step=0.5)
    queda_max_pct = st.slider("Queda de Tensão Máxima Permitida (%)", min_value=1.0, max_value=5.0, value=3.0, step=0.5)

delta_v = tensao_sistema * (queda_max_pct / 100)
# Condutividade do cobre = 56 m/(ohm * mm²)
secao_calculada = (2 * distancia * corrente_necessaria) / (56 * delta_v)

bitolas_comerciais = [0.5, 0.75, 1.0, 1.5, 2.5, 4.0, 6.0, 10.0]
bitola_sugerida = next((b for b in bitolas_comerciais if b >= secao_calculada), max(bitolas_comerciais))

with col_b2:
    st.write("### Resultado da Fiação do Tronco Principal:")
    st.metric("Seção Mínima Calculada", f"{secao_calculada:.2f} mm²")
    st.metric("Bitola Comercial Indicada", f"{bitola_sugerida:.2f} mm²")

if bitola_sugerida < 1.5:
    st.warning("⚠️ Para alimentação principal da fonte recomenda-se no mínimo cabos de 1,5 mm² devido à resistência mecânica.")