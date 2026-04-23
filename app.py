import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Henrry's Garage | Premium System", layout="wide")

# Conexión a Google Sheets (Asegúrate de configurar los Secrets en Streamlit Cloud)
conn = st.connection("gsheets", type=GSheetsConnection)

class ModernInvoice(FPDF):
    def draw_header(self, data):
        # Tonos extraídos del logo
        azul_oscuro = (30, 60, 90) 
        naranja = (220, 130, 50)  

        # Encabezado sólido azul
        self.set_fill_color(*azul_oscuro)
        self.rect(0, 0, 210, 55, 'F')
        
        # --- INSERTAR LOGO ---
        try:
            # Ubicación: x=12, y=8 | Ancho: 35mm
            self.image("logo.png", 12, 8, 35) 
            self.set_xy(52, 18) 
        except:
            # Si el archivo no está en GitHub, el texto se alinea a la izquierda
            self.set_xy(15, 18)
        
        # Nombre de la empresa en blanco
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, str(data['emisor_nombre']).upper(), ln=True)
        
        # Detalle estético naranja
        self.set_draw_color(*naranja)
        self.set_line_width(1.2)
        self.line(self.get_x(), 30, 130, 30)

        # Contacto debajo del título
        self.set_y(35)
        self.set_x(52 if self.get_x() > 20 else 15)
        self.set_font("Helvetica", "", 10)
        info = f"{data['emisor_dir']}  |  {data['emisor_tel']}  |  {data['emisor_email']}"
        self.cell(0, 5, info, ln=True)

def generate_pdf(data):
    pdf = ModernInvoice(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.draw_header(data)
    
    azul_oscuro = (30, 60, 90)
    naranja = (220, 130, 50)
    
    pdf.set_y(65)
    # Bloque de información del cliente y factura
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(95, 5, "FACTURADO A:", ln=0)
    pdf.cell(95, 5, "DETALLES DE PAGO:", ln=1)
    
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(95, 8, data['cliente'], ln=0)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(95, 8, f"Factura Nro: {data['inv_num']}", ln=1)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(95, 5, f"Proyecto: {data['project_addr']}", ln=0)
    pdf.cell(95, 5, f"Fecha Emisión: {data['fecha_hoy']}", ln=1)
    pdf.cell(95, 5, f"Pagar a: {data['payable_to']}", ln=0)
    pdf.cell(95, 5, f"Vencimiento: {data['due_date']}", ln=1)
    
    pdf.ln(15)

    # --- TABLA DE SERVICIOS ---
    pdf.set_fill_color(*azul_oscuro)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 10, " DESCRIPCION", border=0, fill=True)
    pdf.cell(25, 10, "CANT.", border=0, fill=True, align="C")
    pdf.cell(30, 10, "PRECIO U.", border=0, fill=True, align="C")
    pdf.cell(35, 10, "TOTAL", border=0, fill=True, align="C", ln=1)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(245, 248, 252)
    pdf.cell(100, 15, f" {data['desc']}", border='B', fill=True)
    pdf.cell(25, 15, str(data['qty']), border='B', fill=True, align="C")
    pdf.cell(30, 15, f"${data['unit_p']}", border='B', fill=True, align="C")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(35, 15, f"${data['total_p']}", border='B', fill=True, align="C", ln=1)
    
    # --- TOTAL RESALTADO ---
    pdf.ln(10)
    pdf.set_x(130)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(*naranja)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(30, 12, " TOTAL", fill=True, align="C")
    pdf.cell(40, 12, f"${data['total_p']} ", fill=True, align="R", ln=1)

    # --- GARANTIA (Texto Original) [cite: 17] ---
    pdf.ln(20)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*azul_oscuro)
    pdf.cell(0, 5, "TERMINOS DE GARANTIA", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 100, 100)
    
    warranty = (
        "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***\n"
        "For installation on a new garage door, it has a 1-year warranty on factory defects "
        "and installation by HENRRY DOORS we are not responsible for damages or bad "
        "manipulation when opening or closing the garage door And 6 months in Opener. [cite: 17]"
    )
    pdf.multi_cell(180, 4, warranty)
    
    pdf.ln(15)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*azul_oscuro)
    pdf.cell(0, 10, "Thank You For Your Business [cite: 18]", align="C", ln=True)
    
    return pdf.output()

# --- INTERFAZ ---
st.markdown("""<style>
    .stButton>button { background-color: #dc8232; color: white; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; }
    </style>""", unsafe_allow_html=True)

st.title("🚀 Henrry's Garage Door - Invoice Pro")
tab1, tab2 = st.tabs(["Nueva Factura", "Registro en Google Sheets"])

with st.sidebar:
    st.image("logo.png", width=150) # Muestra el logo en la barra lateral
    st.header("Emisor")
    e_nom = st.text_input("Empresa", "Henrry's Garage Door Service") [cite: 1]
    e_dir = st.text_input("Direccion", "Magnolia Houston tx") [cite: 3]
    e_tel = st.text_input("Telefono", "(661)648-6043") [cite: 4]
    e_eml = st.text_input("Email", "alemanperez99@gmail.com") [cite: 5]

with tab1:
    with st.form("invoice_form"):
        c1, c2, c3 = st.columns(3)
        inv = c1.text_input("Invoice #", "005") [cite: 8]
        clie = c2.text_input("Cliente", "The Woodlands Living") [cite: 8]
        paga = c3.text_input("Pagar a", "Henrry Perez") [cite: 8]
        
        proj = st.text_input("Direccion Proyecto", "4919 Curiosity Ct") [cite: 9]
        serv = st.text_input("Servicio", "Rail Repair in Genie Opener") [cite: 11]
        
        c4, c5 = st.columns(2)
        qty = c4.number_input("Cantidad", min_value=1, value=1) [cite: 14]
        prc = c5.number_input("Precio Unitario ($)", min_value=0.0, value=75.0) [cite: 15]
        vence = st.date_input("Vencimiento") [cite: 9]
        
        btn = st.form_submit_button("GUARDAR Y GENERAR PDF")

    if btn:
        datos = {
            'emisor_nombre': e_nom, 'emisor_dir': e_dir, 'emisor_tel': e_tel, 'emisor_email': e_eml,
            'fecha_hoy': datetime.now().strftime("%d/%m/%Y"), 'cliente': clie, 'payable_to': paga,
            'inv_num': inv, 'project_addr': proj, 'due_date': vence.strftime("%d/%m/%Y"),
            'desc': serv, 'qty': qty, 'unit_p': f"{prc:,.2f}", 'total_p': f"{(qty * prc):,.2f}"
        }
        
        # Guardar en Google Sheets
        try:
            df_hist = conn.read(worksheet="Sheet1", ttl=0)
            df_new = pd.concat([df_hist, pd.DataFrame([datos])], ignore_index=True)
            conn.update(worksheet="Sheet1", data=df_new)
            st.success("Guardado en Google Sheets")
        except:
            st.error("Error al conectar con Google Sheets. Verifica los Secrets.")

        pdf_bytes = generate_pdf(datos)
        st.download_button("Descargar Factura", data=bytes(pdf_bytes), file_name=f"Factura_{inv}.pdf")

with tab2:
    st.subheader("Historial Completo")
    if st.button("Sincronizar Datos"):
        df = conn.read(worksheet="Sheet1", ttl=0)
        st.dataframe(df, use_container_width=True)
