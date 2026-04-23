import streamlit as st
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Henrry's Garage Invoice System", layout="wide")

def generate_pdf(data):
    # Inicializar PDF en formato A4
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_margins(10, 10, 10)
    
    # --- ENCABEZADO (Estilo basado en imagen) ---
    # Línea azul superior
    pdf.set_draw_color(30, 50, 150)
    pdf.set_line_width(1.5)
    pdf.line(10, 15, 200, 15)
    
    pdf.ln(12)
    # Nombre de la empresa
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(30, 50, 150)
    pdf.cell(0, 10, data['emisor_nombre'], ln=True)
    
    # Datos de contacto (Valores predeterminados corregidos)
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, data['emisor_dir'], ln=True)
    pdf.cell(0, 5, data['emisor_tel'], ln=True)
    pdf.cell(0, 5, data['emisor_email'], ln=True)
    
    # Título INVOICE y Fecha (Posicionados a la derecha)
    pdf.set_y(25)
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 10, "INVOICE", align="R", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, data['fecha_hoy'], align="R", ln=True)
    
    pdf.ln(15)

    # --- TABLAS DE DATOS (Invoice for / Payable to / Invoice #) ---
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 8, "Invoice for", border=1, fill=True)
    pdf.cell(60, 8, "Payable to", border=1, fill=True)
    pdf.cell(70, 8, "invoice #", border=1, fill=True, ln=True)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 10, data['cliente'], border=1)
    pdf.cell(60, 10, data['payable_to'], border=1)
    pdf.cell(70, 10, data['inv_num'], border=1, ln=True)
    
    pdf.ln(5)
    
    # Tabla de Proyecto y Fecha de Vencimiento
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 8, "Project", border=1, fill=True)
    pdf.cell(95, 8, "Due date", border=1, fill=True, ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 10, data['project_addr'], border=1)
    pdf.cell(95, 10, data['due_date'], border=1, ln=True)
    
    pdf.ln(10)

    # --- DETALLE DE PRODUCTOS / SERVICIOS ---
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 8, "DESCRIPTION", border=1, fill=True)
    pdf.cell(20, 8, "Qty", border=1, fill=True, align="C")
    pdf.cell(35, 8, "UNIT PRICE", border=1, fill=True, align="C")
    pdf.cell(35, 8, "TOTAL PRICE", border=1, fill=True, ln=True, align="C")
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 10, data['desc'], border=1)
    pdf.cell(20, 10, str(data['qty']), border=1, align="C")
    pdf.cell(35, 10, f"${data['unit_p']}", border=1, align="C")
    pdf.cell(35, 10, f"${data['total_p']}", border=1, align="C", ln=True)
    
    # Fila de Total
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(155, 10, "Total", align="R")
    pdf.cell(35, 10, f"${data['total_p']}", border=1, align="C", ln=True)

    # --- SECCIÓN DE GARANTÍA (Corregida para evitar FPDFException) ---
    pdf.ln(15)
    pdf.set_x(10) # Asegura el inicio en el margen izquierdo
    pdf.set_font("Arial", "B", 8)
    pdf.multi_cell(0, 5, "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***", ln=True)
    
    pdf.set_font("Arial", "", 8)
    warranty_text = (
        "For installation on a new garage door, it has a 1-year warranty on factory defects "
        "and installation by HENRRY DOORS we are not responsible for damages or bad "
        "manipulation when opening or closing the garage door And 6 months in Opener."
    )
    # multi_cell con w=0 usa todo el ancho disponible automáticamente
    pdf.multi_cell(0, 4, warranty_text, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 11)
    pdf.cell(0, 10, "Thank You For Your Business", align="C", ln=True)
    
    # Retornar el PDF como bytes (compatible con fpdf2)
    return pdf.output()

# --- INTERFAZ DE USUARIO CON STREAMLIT ---
st.title("📄 Generador de Facturas - Henrry's Garage")

# Sidebar para datos fijos pero editables (Dirección, Teléfono, etc.)
st.sidebar.header("Datos del Negocio")
e_nombre = st.sidebar.text_input("Nombre", "Henrry's Garage Door Service")
e_dir = st.sidebar.text_input("Dirección", "Magnolia Houston tx")
e_tel = st.sidebar.text_input("Teléfono", "(661)648-6043")
e_mail = st.sidebar.text_input("Email", "alemanperez99@gmail.com")

# Formulario principal de la factura
with st.form("invoice_form"):
    col1, col2, col3 = st.columns(3)
    num_inv = col1.text_input("Invoice #", "5")
    cliente = col2.text_input("Invoice For", "The Woodlands Living")
    pagar_a = col3.text_input("Payable to", "Henrry Perez")
    
    col4, col5 = st.columns(2)
    proyecto = col4.text_input("Project Address", "4919 Curiosity Ct")
    fecha_vence = col5.date_input("Due Date")
    
    st.divider()
    
    # Detalle del trabajo
    servicio = st.text_input("Description", "Rail Repair in Genie Opener")
    c_qty, c_price = st.columns(2)
    cantidad = c_qty.number_input("Qty", min_value=1, value=1)
    precio_u = c_price.number_input("Unit Price ($)", min_value=0.0, value=75.0)
    
    boton_generar = st.form_submit_button("Crear Factura")

if boton_generar:
    # Procesamiento de datos
    datos_finales = {
        'emisor_nombre': e_nombre,
        'emisor_dir': e_dir,
        'emisor_tel': e_tel,
        'emisor_email': e_mail,
        'fecha_hoy': datetime.now().strftime("%m/%d/%Y"),
        'cliente': cliente,
        'payable_to': pagar_a,
        'inv_num': num_inv,
        'project_addr': proyecto,
        'due_date': fecha_vence.strftime("%m/%d/%Y"),
        'desc': servicio,
        'qty': cantidad,
        'unit_p': f"{precio_u:.2f}",
        'total_p': f"{(cantidad * precio_u):.2f}"
    }
    
    try:
        pdf_output = generate_pdf(datos_finales)
        st.success("✅ ¡PDF generado con éxito!")
        st.download_button(
            label="📥 Descargar Factura PDF",
            data=bytes(pdf_output),
            file_name=f"Invoice_{num_inv}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error al generar el PDF: {e}")
