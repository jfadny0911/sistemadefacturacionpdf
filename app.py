import streamlit as st
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Henrry's Garage | Invoice System", layout="centered")

class ModernInvoice(FPDF):
    def draw_header(self, data):
        # Rectángulo de color en el encabezado (Azul Medianoche)
        self.set_fill_color(30, 50, 100)
        self.rect(0, 0, 210, 40, 'F')
        
        self.set_xy(15, 12)
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, data['emisor_nombre'].upper(), ln=True)
        
        self.set_font("Helvetica", "", 10)
        info = f"{data['emisor_dir']}  |  {data['emisor_tel']}  |  {data['emisor_email']}"
        self.cell(0, 5, info, ln=True)

def generate_pdf(data):
    pdf = ModernInvoice(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.draw_header(data)
    
    # --- INFO DE FACTURA ---
    pdf.set_y(50)
    pdf.set_text_color(50, 50, 50)
    
    # Encabezados de sección
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(95, 5, "FACTURADO A:", ln=0)
    pdf.cell(95, 5, "DETALLES DE FACTURA:", ln=1)
    
    # Datos del cliente y factura
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(95, 7, data['cliente'], ln=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(95, 7, f"Factura Nro: {data['inv_num']}", ln=1)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 5, f"Proyecto: {data['project_addr']}", ln=0)
    pdf.cell(95, 5, f"Fecha Emision: {data['fecha_hoy']}", ln=1)
    pdf.cell(95, 5, f"Pagar a: {data['payable_to']}", ln=0)
    pdf.cell(95, 5, f"Vencimiento: {data['due_date']}", ln=1)
    
    pdf.ln(15)

    # --- TABLA DE PRODUCTOS ---
    pdf.set_fill_color(245, 245, 245)
    pdf.set_draw_color(220, 220, 220)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(100, 10, " DESCRIPCION", border='B', fill=True)
    pdf.cell(25, 10, "CANT.", border='B', fill=True, align="C")
    pdf.cell(30, 10, "PRECIO U.", border='B', fill=True, align="C")
    pdf.cell(35, 10, "TOTAL", border='B', fill=True, align="C", ln=1)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(100, 15, f" {data['desc']}", border='B')
    pdf.cell(25, 15, str(data['qty']), border='B', align="C")
    pdf.cell(30, 15, f"${data['unit_p']}", border='B', align="C")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(35, 15, f"${data['total_p']}", border='B', align="C", ln=1)
    
    # --- TOTAL ---
    pdf.ln(10)
    pdf.set_x(130)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(30, 50, 100)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(30, 12, " TOTAL", fill=True)
    pdf.cell(40, 12, f"${data['total_p']} ", fill=True, align="R", ln=1)

    # --- GARANTIA ---
    pdf.ln(20)
    pdf.set_x(15)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 5, "TERMINOS DE GARANTIA", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 100, 100)
    
    warranty_text = (
        "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***\n"
        "For installation on a new garage door, it has a 1-year warranty on factory defects "
        "and installation by HENRRY DOORS we are not responsible for damages or bad "
        "manipulation when opening or closing the garage door And 6 months in Opener."
    )
    pdf.multi_cell(180, 4, warranty_text)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 50, 100)
    pdf.cell(0, 10, "Gracias por su preferencia", align="C", ln=True)
    
    return pdf.output()

# --- INTERFAZ STREAMLIT ---
st.title("Generador de Facturas Premium")

with st.sidebar:
    st.header("Configuracion")
    e_nombre = st.text_input("Empresa", "Henrry's Garage Door Service")
    e_dir = st.text_input("Direccion", "Magnolia Houston tx")
    e_tel = st.text_input("Telefono", "(661)648-6043")
    e_mail = st.text_input("Email", "alemanperez99@gmail.com")

with st.form("modern_form"):
    c1, c2 = st.columns(2)
    with c1:
        num_inv = st.text_input("Numero de Factura", "005")
        cliente = st.text_input("Cliente", "The Woodlands Living")
        pagar_a = st.text_input("Pagar a", "Henrry Perez")
    with c2:
        proyecto = st.text_input("Direccion del Proyecto", "4919 Curiosity Ct")
        fecha_vence = st.date_input("Fecha de Vencimiento")
    
    st.divider()
    
    servicio = st.text_input("Descripcion del Trabajo", "Rail Repair in Genie Opener")
    col_q, col_p = st.columns(2)
    cantidad = col_q.number_input("Cantidad", min_value=1, value=1)
    precio_u = col_p.number_input("Precio Unitario ($)", min_value=0.0, value=75.0)
    
    generar = st.form_submit_button("GENERAR FACTURA")

if generar:
    datos = {
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
        'total_p': f"{(cantidad * precio_u):,.2f}"
    }
    
    try:
        pdf_res = generate_pdf(datos)
        st.success("Factura creada exitosamente")
        st.download_button(
            label="Descargar PDF",
            data=bytes(pdf_res),
            file_name=f"Factura_{num_inv}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error: {e}")
