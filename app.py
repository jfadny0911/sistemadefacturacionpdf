import streamlit as st
from fpdf import FPDF
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Generador Henrry's Garage", layout="centered")

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # --- ENCABEZADO (Basado en el documento original) ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Henrry's Garage Door Service", ln=True) [cite: 1]
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "31411 terri ln", ln=True) [cite: 2]
    pdf.cell(0, 5, "Magnolia Houston tx", ln=True) [cite: 3]
    pdf.cell(0, 5, "(661)648-6043", ln=True) [cite: 4]
    pdf.cell(0, 5, "alemanperez99@gmail.com", ln=True) [cite: 5]
    
    pdf.set_y(10)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INVOICE", align="R", ln=True) [cite: 6]
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, data['date'], align="R", ln=True) [cite: 7]
    
    pdf.ln(10)

    # --- TABLAS DE INFORMACIÓN ---
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 10)
    # Fila de encabezados
    pdf.cell(60, 8, "Invoice for", border=1, fill=True) [cite: 8]
    pdf.cell(60, 8, "Payable to", border=1, fill=True) [cite: 8]
    pdf.cell(70, 8, "invoice #", border=1, fill=True, ln=True) [cite: 8]
    
    # Fila de datos
    pdf.set_font("Arial", "", 10)
    pdf.cell(60, 8, data['client'], border=1)
    pdf.cell(60, 8, data['payable'], border=1)
    pdf.cell(70, 8, data['inv_num'], border=1, ln=True)
    
    pdf.ln(5)
    
    # Proyecto y Fecha de vencimiento
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 8, "Project", border=1, fill=True) [cite: 9]
    pdf.cell(95, 8, "Due date", border=1, fill=True, ln=True) [cite: 9]
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 8, data['project'], border=1)
    pdf.cell(95, 8, data['due_date'], border=1, ln=True)
    
    pdf.ln(10)

    # --- DETALLE DE SERVICIOS ---
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 8, "DESCRIPTION", border=1, fill=True) [cite: 10]
    pdf.cell(20, 8, "Qty", border=1, fill=True) [cite: 12]
    pdf.cell(35, 8, "UNIT PRICE", border=1, fill=True) [cite: 13]
    pdf.cell(35, 8, "TOTAL PRICE", border=1, fill=True, ln=True) [cite: 13]
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 8, data['desc'], border=1)
    pdf.cell(20, 8, str(data['qty']), border=1)
    pdf.cell(35, 8, f"${data['unit_p']}", border=1)
    pdf.cell(35, 8, f"${data['total_p']}", border=1, ln=True)
    
    # Total
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(155, 10, "Total", align="R") [cite: 19]
    pdf.cell(35, 10, f"${data['total_p']}", border=1, align="C", ln=True) [cite: 20]

    # --- GARANTÍA (Texto literal del original) ---
    pdf.ln(10)
    pdf.set_font("Arial", "B", 8)
    pdf.multi_cell(0, 5, "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***") [cite: 17]
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 4, "For installation on a new garage door, it has a 1-year warranty on factory defects and installation by HENRRY DOORS we are not responsible for damages or bad manipulation when opening or closing the garage door And 6 months in Opener.") [cite: 17]
    
    pdf.ln(5)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Thank You For Your Business", align="C") [cite: 18]
    
    return pdf.output(dest='S')

# --- INTERFAZ STREAMLIT ---
st.title("📄 Generador de Facturas Henrry's")

with st.form("invoice_form"):
    col1, col2 = st.columns(2)
    with col1:
        inv_num = st.text_input("Invoice #", "5")
        client = st.text_input("Invoice for", "The Woodlands Living")
    with col2:
        payable = st.text_input("Payable to", "Henrry Perez")
        date_str = st.date_input("Fecha Factura").strftime("%m/%d/%Y")
    
    project = st.text_input("Project (Address)", "4919 Curiosity Ct")
    due_date = st.date_input("Due Date").strftime("%m/%d/%Y")
    
    st.divider()
    
    desc = st.text_area("Descripción del Servicio", "Rail Repair in Genie Opener")
    c1, c2 = st.columns(2)
    qty = c1.number_input("Cantidad", min_value=1, value=1)
    price = c2.number_input("Precio Unitario ($)", min_value=0.0, value=75.0)
    
    submit = st.form_submit_button("Crear PDF")

if submit:
    total = qty * price
    invoice_data = {
        'inv_num': inv_num, 'client': client, 'payable': payable,
        'date': date_str, 'project': project, 'due_date': due_date,
        'desc': desc, 'qty': qty, 'unit_p': price, 'total_p': total
    }
    
    pdf_out = generate_pdf(invoice_data)
    st.success("¡Factura lista!")
    st.download_button(label="Descargar Factura PDF", data=bytes(pdf_out), file_name=f"Invoice_{inv_num}.pdf", mime="application/pdf")
