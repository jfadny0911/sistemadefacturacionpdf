import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Henrry's Garage | Invoice System", layout="wide")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CLASE PARA EL PDF ---
class ModernInvoice(FPDF):
    def draw_header(self, data):
        # Colores del logo
        azul_oscuro = (30, 60, 90)  # Tono azul principal del logo
        naranja = (220, 130, 50)   # Tono naranja/marrón del logo

        # Rectángulo azul oscuro de fondo en la parte superior
        self.set_fill_color(*azul_oscuro)
        self.rect(0, 0, 210, 50, 'F')
        
        self.set_xy(15, 15)
        # Nombre de la empresa en blanco para resaltar
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, str(data['emisor_nombre']).upper(), ln=True)
        
        # Línea naranja decorativa debajo del nombre
        self.set_draw_color(*naranja)
        self.set_line_width(1)
        self.line(15, 28, 100, 28)

        # Información de contacto en la cabecera
        self.set_y(32)
        self.set_font("Helvetica", "", 10)
        info = f"{data['emisor_dir']}  |  {data['emisor_tel']}  |  {data['emisor_email']}"
        self.cell(0, 5, info, ln=True)

def generate_pdf(data):
    pdf = ModernInvoice(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.draw_header(data)
    pdf.set_y(60)
    
    # --- INFO DE FACTURA ---
    azul_oscuro = (30, 60, 90)
    pdf.set_text_color(50, 50, 50)
    
    # Columna Izquierda: Cliente
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*azul_oscuro)
    pdf.cell(95, 6, "FACTURADO A:", ln=0)
    # Columna Derecha: Detalles
    pdf.cell(95, 6, "DETALLES DE LA FACTURA:", ln=1)
    
    # Datos específicos del cliente
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(95, 8, data['cliente'], ln=0)
    # Número de factura con fondo de color sutil
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(95, 8, f"Factura Nro: {data['inv_num']}", ln=1)
    
    # Más detalles
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(95, 6, f"Proyecto: {data['project_addr']}", ln=0)
    pdf.cell(95, 6, f"Fecha de Emisión: {data['fecha_hoy']}", ln=1)
    pdf.cell(95, 6, f"Pagar a: {data['payable_to']}", ln=0)
    pdf.cell(95, 6, f"Vencimiento: {data['due_date']}", ln=1)
    
    pdf.ln(15)

    # --- TABLA DE PRODUCTOS / SERVICIOS ---
    naranja = (220, 130, 50)
    azul_claro_fondo = (240, 245, 250)
    
    # Encabezado de tabla
    pdf.set_fill_color(*azul_oscuro)
    pdf.set_draw_color(*azul_oscuro)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(255, 255, 255)  # Texto en blanco
    pdf.cell(100, 10, " DESCRIPCIÓN", border=1, fill=True)
    pdf.cell(25, 10, "CANT.", border=1, fill=True, align="C")
    pdf.cell(30, 10, "PRECIO U.", border=1, fill=True, align="C")
    pdf.cell(35, 10, "TOTAL", border=1, fill=True, align="C", ln=1)
    
    # Filas de productos con fondo alterno para mejor lectura
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(*azul_claro_fondo)
    pdf.cell(100, 15, f" {data['desc']}", border='B', fill=True)
    pdf.cell(25, 15, str(data['qty']), border='B', fill=True, align="C")
    pdf.cell(30, 15, f"${data['unit_p']}", border='B', fill=True, align="C")
    # Total de la línea en negrita
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(35, 15, f"${data['total_p']}", border='B', fill=True, align="C", ln=1)
    
    # --- TOTAL ---
    pdf.ln(10)
    pdf.set_x(130)
    pdf.set_font("Helvetica", "B", 14)
    # Fondo naranja para el total resaltado
    pdf.set_fill_color(*naranja)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(30, 12, " TOTAL", fill=True, align="C")
    pdf.cell(40, 12, f"${data['total_p']} ", fill=True, align="R", ln=1)

    # --- GARANTÍA ---
    pdf.ln(20)
    pdf.set_x(15)
    pdf.set_text_color(50, 50, 50)
    # Título de garantía en azul oscuro
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*azul_oscuro)
    pdf.cell(0, 5, "TÉRMINOS DE GARANTÍA", ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 100, 100)
    
    warranty_text = (
        "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***\n"
        "For installation on a new garage door, it has a 1-year warranty on factory defects "
        "and installation by HENRRY DOORS we are not responsible for damages or bad "
        "manipulation when opening or closing the garage door And 6 months in Opener."
    )
    pdf.multi_cell(180, 4, warranty_text)
    
    # Mensaje de despedida
    pdf.ln(15)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*azul_oscuro)
    pdf.cell(0, 10, "¡Gracias por su preferencia!", align="C", ln=True)
    
    return pdf.output()

# --- INTERFAZ STREAMLIT ---
# CSS personalizado para mejorar la apariencia de la interfaz
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTabs [data-baseweb="tab"] { color: #204060; font-weight: bold; }
    .stTabs [aria-selected="true"] { color: #dc8232; border-bottom-color: #dc8232; }
    .stButton>button { background-color: #dc8232; color: white; width: 100%; border-radius: 5px; font-weight: bold; }
    .stButton>button:hover { background-color: #e09050; color: white; border-color: #e09050; }
    div[data-testid="stForm"] { border-color: #204060; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Gestión de Facturación - Henrry's Garage Door Service")
tab1, tab2 = st.tabs(["Crear Factura", "Historial en la Nube"])

# Sección de configuración del emisor (Siempre aparece)
with st.sidebar:
    st.header("⚙️ Configuración")
    e_nombre = st.text_input("Nombre de la Empresa", "Henrry's Garage Door Service")
    e_dir = st.text_input("Dirección", "Magnolia Houston tx")
    e_tel = st.text_input("Teléfono", "(661)648-6043")
    e_mail = st.text_input("Email", "alemanperez99@gmail.com")

# Tab para crear una nueva factura
with tab1:
    st.subheader("📝 Generar Nueva Factura")
    with st.form("modern_form"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            num_inv = st.text_input("Número de Factura", "005")
            cliente = st.text_input("Nombre del Cliente", "The Woodlands Living")
            pagar_a = st.text_input("Pagar a", "Henrry Perez")
        with col_f2:
            proyecto = st.text_input("Dirección del Proyecto", "4919 Curiosity Ct")
            fecha_vence = st.date_input("Fecha de Vencimiento")
        
        st.divider()
        
        # Detalles del trabajo realizado
        servicio = st.text_input("Descripción del Trabajo", "Rail Repair in Genie Opener")
        col_q, col_p = st.columns(2)
        cantidad = col_q.number_input("Cantidad", min_value=1, value=1)
        precio_u = col_p.number_input("Precio Unitario ($)", min_value=0.0, value=75.0)
        
        # Botón para generar la factura y guardarla
        generar = st.form_submit_button("GENERAR FACTURA CON DISEÑO PREMIUM")

    if generar:
        # Preparación de datos para el PDF y Google Sheets
        total_calculado = cantidad * precio_u
        datos_completos = {
            'emisor_nombre': e_nombre,
            'emisor_dir': e_dir,
            'emisor_tel': e_tel,
            'emisor_email': e_mail,
            'fecha_hoy': datetime.now().strftime("%d/%m/%Y"),
            'cliente': cliente,
            'payable_to': pagar_a,
            'inv_num': num_inv,
            'project_addr': proyecto,
            'due_date': fecha_vence.strftime("%d/%m/%Y"),
            'desc': servicio,
            'qty': cantidad,
            'unit_p': f"{precio_u:,.2f}",
            'total_p': f"{total_calculado:,.2f}"
        }
        
        # 1. Intentar guardar en Google Sheets
        try:
            # Leer datos existentes para anexar los nuevos
            existing_data = conn.read(worksheet="Sheet1", ttl=0)
            # Asegurar que el dataframe sea compatible con los nuevos datos
            df_new_row = pd.DataFrame([datos_completos])
            updated_df = pd.concat([existing_data, df_new_row], ignore_index=True)
            # Actualizar la hoja de Google Sheets
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success("✅ Factura registrada exitosamente en Google Sheets")
        except Exception as error_sheets:
            st.warning(f"No se pudo registrar en Google Sheets. Verifica la conexión y permisos: {error_sheets}")

        # 2. Generar y ofrecer la descarga del PDF
        try:
            pdf_result = generate_pdf(datos_completos)
            st.success("✨ Factura premium generada con éxito.")
            st.download_button(
                label="📥 DESCARGAR FACTURA PDF",
                data=bytes(pdf_result),
                file_name=f"Factura_{num_inv}_{cliente.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as error_pdf:
            st.error(f"Ocurrió un error al generar el PDF: {error_pdf}")

# Tab para visualizar el historial guardado
with tab2:
    st.subheader("📋 Historial de Facturas Registradas en la Nube")
    # Botón para cargar o actualizar los datos desde Google Sheets
    load_btn = st.button("Actualizar / Cargar Registro desde Google Sheets")
    
    if load_btn:
        try:
            # Leer los datos actualizados
            history_df = conn.read(worksheet="Sheet1", ttl=0)
            # Mostrar la tabla de datos en la interfaz
            st.dataframe(history_df, use_container_width=True)
            st.info("Datos cargados correctamente desde Google Sheets.")
        except Exception as e_load:
            st.error(f"Error al cargar datos desde Google Sheets: {e_load}")
