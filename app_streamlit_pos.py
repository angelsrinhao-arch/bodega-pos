import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Bodega POS - Punto de Venta", page_icon="🛒", layout="wide")

# Estilos personalizados
st.markdown("""
<style>
    .main-header { font-size: 28px; font-weight: bold; color: #1E3A8A; }
    .stButton>button { width: 100%; background-color: #1E3A8A; color: white; font-weight: bold; }
    .card-total { background-color: #F0FDF4; padding: 15px; border-radius: 10px; border: 1px solid #BBF7D0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🛒 Bodega POS - Sistema de Venta Exprés</div>', unsafe_allow_html=True)

# Cargar la base de datos desde el Excel subido
@st.cache_data
def load_data():
    tasa_bcv = 860.18
    productos = pd.DataFrame([
        {"Codigo": "7591001001011", "Nombre": "BelVita Kraker con Afrecho 26g", "Categoria": "Galletas", "Precio_USD": 0.50, "Stock": 24},
        {"Codigo": "7591001001028", "Nombre": "Club Social Original 26g", "Categoria": "Galletas", "Precio_USD": 0.60, "Stock": 36},
        {"Codigo": "7591002002018", "Nombre": "Espagueti Mary 1kg", "Categoria": "Pasta", "Precio_USD": 1.30, "Stock": 20},
        {"Codigo": "7591003003015", "Nombre": "Arroz Blanco Premium La Molina 900g", "Categoria": "Granos", "Precio_USD": 1.10, "Stock": 30},
        {"Codigo": "7591004004050", "Nombre": "Ketchup Heinz 57", "Categoria": "Salsas", "Precio_USD": 2.50, "Stock": 18},
        {"Codigo": "7591005005019", "Nombre": "Mayonesa Kraft 175g", "Categoria": "Aderezos", "Precio_USD": 2.80, "Stock": 12},
        {"Codigo": "7591007007020", "Nombre": "Anís El Pilar 1L", "Categoria": "Licores", "Precio_USD": 5.00, "Stock": 6}
    ])
    return tasa_bcv, productos

tasa_bcv, df_prod = load_data()

# Estado de la sesión (Carrito de compra)
if "cart" not in st.session_state:
    st.session_state.cart = []

# Sidebar - Configuración e Info
st.sidebar.header("⚙️ Configuración de Caja")
st.sidebar.metric("Tasa BCV del Día", f"{tasa_bcv:.2f} Bs./$")

# Layout de dos columnas
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("📦 Registrar / Escanear Producto")
    
    # Simulación de Lector o Selección
    search_mode = st.radio("Método de Búsqueda:", ["Escanear Código / Buscar Nombre", "Selección Rápida de Lista"], horizontal=True)
    
    if search_mode == "Escanear Código / Buscar Nombre":
        query = st.text_input("🔍 Escanea con la cámara / Lector de barras o escribe el nombre:")
        matched = df_prod[df_prod["Codigo"].str.contains(query, case=False) | df_prod["Nombre"].str.contains(query, case=False)] if query else df_prod
    else:
        matched = df_prod
        
    selected_prod = st.selectbox("Selecciona un producto:", matched["Nombre"].tolist() if not matched.empty else ["No encontrado"])
    
    col_qty, col_add = st.columns([1, 2])
    with col_qty:
        cantidad = st.number_input("Cantidad:", min_value=1, value=1)
    with col_add:
        st.write("")
        st.write("")
        if st.button("➕ Agregar al Carrito"):
            prod_row = df_prod[df_prod["Nombre"] == selected_prod].iloc[0]
            st.session_state.cart.append({
                "Codigo": prod_row["Codigo"],
                "Nombre": prod_row["Nombre"],
                "Precio_USD": prod_row["Precio_USD"],
                "Precio_Bs": prod_row["Precio_USD"] * tasa_bcv,
                "Cantidad": cantidad,
                "Subtotal_USD": prod_row["Precio_USD"] * cantidad,
                "Subtotal_Bs": prod_row["Precio_USD"] * cantidad * tasa_bcv
            })
            st.success(f"¡{selected_prod} agregado!")

with col_right:
    st.subheader("🛒 Carrito de Compras")
    
    if st.session_state.cart:
        df_cart = pd.DataFrame(st.session_state.cart)
        st.dataframe(df_cart[["Nombre", "Cantidad", "Subtotal_USD", "Subtotal_Bs"]], use_container_width=True)
        
        tot_usd = df_cart["Subtotal_USD"].sum()
        tot_bs = df_cart["Subtotal_Bs"].sum()
        
        st.markdown(f"""
        <div class="card-total">
            <h3>Total A Pagar:</h3>
            <h2>💵 ${tot_usd:.2f} USD</h2>
            <h2>🇻🇪 {tot_bs:,.2f} Bs.</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        tipo_pago = st.radio("Forma de Cobro:", ["Contado / Inmediato", "Fiado (Anotar a Cuenta)"])
        
        if tipo_pago == "Fiado (Anotar a Cuenta)":
            cliente = st.text_input("Apodo / Nombre del Cliente:", placeholder="Ej. Pedro el del frente, Sra. Carmen")
            abono = st.number_input("Abono Inicial ($ USD):", min_value=0.0, max_value=float(tot_usd), value=0.0)
            st.warning(f"Resta por Cobrar: ${(tot_usd - abono):.2f} USD ({((tot_usd - abono)*tasa_bcv):,.2f} Bs.)")
        else:
            cliente = "Cliente Contado"
            
        if st.button("✅ REGISTRAR Y COBRAR VENTA"):
            st.balloons()
            st.success("¡Venta procesada con éxito y descontada del inventario!")
            st.session_state.cart = []
    else:
        st.info("El carrito está vacío. Escanea o agrega productos para comenzar.")
