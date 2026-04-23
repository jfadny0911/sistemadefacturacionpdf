import streamlit as st
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Henrry's Garage Invoice System", layout="wide")

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # --- ENCABEZADO (Basado en la imagen y texto proporcionado) ---
    # Línea decorativa azul superior (estilo logo)
    pdf.set_draw_color(30, 50, 150)
    pdf.set_line_width(2)
    pdf.line(10, 15, 200, 15)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(30, 50, 150) # Color azul del logo
    pdf.cell(0, 10, data['emisor_nombre'], ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, data['emisor_dir'], ln=True)
    pdf.cell(0, 5, data['emisor_tel'], ln=True)
    pdf.cell(0, 5, data['emisor_email'], ln=True)
    
    # Título INVOICE y Fecha
    pdf.set_y(25)
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 10, "INVOICE", align="R", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, data['fecha_hoy'], align="R", ln=True)
    
    pdf.ln(15)

    # --- TABLAS DE DATOS PRINCIPALES ---
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 10)
    # Encabezados de tabla superior
    pdf.cell(60, 8, "Invoice for", border=1, fill=True)
    pdf.cell(60, 8, "Payable to", border=1, fill=True)
    pdf.cell(70, 8, "invoice #", border=1, fill=True, ln=True)
    
    # Datos de tabla superior
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 10, data['cliente'], border=1)
    pdf.cell(60, 10, data['payable_to'], border=1)
    pdf.cell(70, 10, data['inv_num'], border=1, ln=True)
    
    pdf.ln(5)
    
    # Proyecto y Vencimiento
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 8, "Project", border=1, fill=True)
    pdf.cell(95, 8, "Due date", border=1, fill=True, ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 10, data['project_addr'], border=1)
    pdf.cell(95, 10, data['due_date'], border=1, ln=True)
    
    pdf.ln(10)

    # --- DETALLE DE TRABAJO ---
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 8, "DESCRIPTION", border=1, fill=True)
    pdf.cell(20, 8, "Qty", border=1, fill=True)
    pdf.cell(35, 8, "UNIT PRICE", border=1, fill=True)
    pdf.cell(35, 8, "TOTAL PRICE", border=1, fill=True, ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 10, data['desc'], border=1)
    pdf.cell(20, 10, str(data['qty']), border=1, align="C")
    pdf.cell(35, 10, f"${data['unit_p']}", border=1, align="C")
    pdf.cell(35, 10, f"${data['total_p']}", border=1, align="C", ln=True)
    
    # Total Final
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(155, 10, "Total", align="R")
    pdf.set_fill_color(255, 255, 255)
    pdf.cell(35, 10, f"${data['total_p']}", border=1, align="C", ln=True)

    # --- SECCIÓN DE GARANTÍA (Texto exacto del original) ---
    pdf.ln(15)
    pdf.set_font("Arial", "B", 8)
    pdf.multi_cell(0, 5, "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***")
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 4, "For installation on a new garage door, it has a 1-year warranty on factory defects and installation by HENRRY DOORS we are not responsible for damages or bad manipulation when opening or closing the garage door And 6 months in Opener.")
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 11)
    pdf.cell(0, 10, "Thank You For Your Business", align="C")
    
    return pdf.output()

# --- INTERFAZ DE USUARIO ---
st.title("🛠️ Sistema de Facturación - Henrry's Garage")

# Sidebar para datos del emisor (Siempre aparecen, pero son editables)
st.sidebar.header("Configuración del Emisor")
emisor_nombre = st.sidebar.text_input("Nombre de Empresa", "Henrry's Garage Door Service") # [cite: 1]
emisor_dir = st.sidebar.text_input("Dirección", "Magnolia Houston tx") # 
emisor_tel = st.sidebar.text_input("Teléfono", "(661)648-6043") # 
emisor_email = st.sidebar.text_input("Email", "alemanperez99@gmail.com") # [cite: 5]

# Cuerpo principal
with st.form("main_form"):
    c1, c2, c3 = st.columns(3)
    inv_num = c1.text_input("Invoice #", "5") # [cite: 8]
    client_name = c2.text_input("Invoice For", "The Woodlands Living") # [cite: 8]
    payable_to = c3.text_input("Payable to", "Henrry Perez") # [cite: 8]
    
    c4, c5 = st.columns(2)
    project_addr = c4.text_input("Project Address", "4919 Curiosity Ct") # [cite: 9]
    due_date = c5.date_input("Due Date") # [cite: 9]
    
    st.divider()
    
    # Detalle del servicio
    desc = st.text_input("Service Description", "Rail Repair in Genie Opener") # [cite: 11]
    col_q, col_p = st.columns(2)
    qty = col_q.number_input("Quantity", min_value=1, value=1) # [cite: 14]
    price = col_p.number_input("Unit Price ($)", min_value=0.0, value=75.0) # [cite: 15]
    
    submit_btn = st.form_submit_button("Generar Factura PDF")

if submit_btn:
    # Preparar datos para el PDF
    invoice_data = {
        'emisor_nombre': emisor_nombre,
        'emisor_dir': emisor_dir,
        'emisor_tel': emisor_tel,
        'emisor_email': emisor_email,
        'fecha_hoy': datetime.now().strftime("%m/%d/%Y"),
        'cliente': client_name,
        'payable_to': payable_to,
        'inv_num': inv_num,
        'project_addr': project_addr,
        'due_date': due_date.strftime("%m/%d/%Y"),
        'desc': desc,
        'qty': qty,
        'unit_p': f"{price:.2f}",
        'total_p': f"{(qty * price):.2f}"
    }
    
    pdf_bytes = generate_pdf(invoice_data)
    
    st.success("Factura generada exitosamente.")
    st.download_button(
        label="📥 Descargar Factura PDF",
        data=pdf_bytes,
        file_name=f"Invoice_{inv_num}.pdf",
        mime="application/pdf"
    )
