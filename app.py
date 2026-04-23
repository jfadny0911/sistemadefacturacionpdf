import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from sqlalchemy import text

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Henrry's Garage | Multi-Address System", layout="wide")

# Conexión a Neon
conn = st.connection("postgresql", type="sql")

class ModernInvoice(FPDF):
    def draw_header(self, data):
        azul_oscuro = (30, 60, 90) 
        naranja = (220, 130, 50)  

        self.set_fill_color(*azul_oscuro)
        self.rect(0, 0, 210, 50, 'F')
        
        self.set_draw_color(*naranja)
        self.set_line_width(1.2)
        self.line(0, 28, 110, 28)

        try:
            self.image("logo.png", 12, 8, 33) 
            self.set_xy(52, 15) 
        except:
            self.set_xy(15, 15)
        
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "HENRRY'S GARAGE DOOR SERVICE", ln=True)
        
        # Dirección del Emisor (La que editas en el panel)
        self.set_y(32)
        if self.get_x() < 50: self.set_x(52)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 5, f"{data['emisor_info']}", ln=True)

def generate_pdf(data, items_df):
    pdf = ModernInvoice()
    pdf.add_page()
    pdf.draw_header(data)
    
    dark_blue = (30, 60, 90)
    
    pdf.set_y(60)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(95, 5, "BILL TO:", ln=0)
    pdf.cell(95, 5, "INVOICE DETAILS:", ln=1)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(95, 8, data['client_name'].upper(), ln=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(95, 8, f"Invoice #: {data['inv_num']}", ln=1)
    
    # Aquí se imprimen las direcciones (pueden ser varias líneas)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.set_x(10)
    pdf.multi_cell(95, 5, f"Project Address(es):\n{data['project_addr']}")
    
    pdf.set_y(73) # Ajuste para que no choque con las direcciones
    pdf.set_x(105)
    pdf.cell(95, 5, f"Date: {data['date']}", ln=1)
    pdf.set_x(105)
    pdf.cell(95, 5, f"Due Date: {data['due_date']}", ln=1)
    pdf.set_x(105)
    pdf.cell(95, 5, f"Payable to: {data['payable_to']}", ln=1)
    
    pdf.ln(10)
    # TABLA
    pdf.set_fill_color(*dark_blue)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(110, 10, " DESCRIPTION", fill=True)
    pdf.cell(20, 10, "QTY", fill=True, align="C")
    pdf.cell(30, 10, "PRICE", fill=True, align="C")
    pdf.cell(30, 10, "TOTAL", fill=True, align="C", ln=1)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    total_val = 0
    for _, row in items_df.iterrows():
        l_total = row['Quantity'] * row['Unit Price']
        total_val += l_total
        pdf.cell(110, 10, f" {row['Description']}", border='B')
        pdf.cell(20, 10, str(row['Quantity']), border='B', align="C")
        pdf.cell(30, 10, f"${row['Unit Price']:,.2f}", border='B', align="C")
        pdf.cell(30, 10, f"${l_total:,.2f}", border='B', align="C", ln=1)
    
    pdf.ln(5)
    pdf.set_x(140)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(220, 130, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 12, f" TOTAL: ${total_val:,.2f}", fill=True, align="C", ln=1)

    # Garantía
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*dark_blue)
    pdf.cell(0, 5, "WARRANTY TERMS", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 100, 100)
    warranty = "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***\n1-year warranty on factory defects/installation, 6 months in Opener."
    pdf.multi_cell(180, 4, warranty)
    
    return pdf.output()

# --- PANEL DE DIRECCIÓN DEL EMISOR (MAGNOLIA) ---
with st.sidebar:
    st.header("⚙️ Your Business Info")
    st.info("Edit your address here. It will appear at the top of the invoice.")
    # Dirección por defecto de Magnolia editable
    my_address = st.text_area("Your Address", "31411 Terri Ln, Magnolia, TX 77354\n(661) 648-6043 | alemanperez99@gmail.com")
    my_payable = st.text_input("Payable to", "Henrry Perez")

# --- FORMULARIO DE CLIENTE ---
st.title("🛠️ Henrry's Garage Invoice System")

col1, col2 = st.columns(2)
inv_no = col1.text_input("Invoice #")
c_name = col2.text_input("Client Name")

# Área para múltiples direcciones de proyecto
p_addresses = st.text_area("Project Addresses (You can add two or more here)", placeholder="Address 1\nAddress 2...")
due_date = st.date_input("Due Date")

# Tabla de productos
st.subheader("Services & Products")
items_df = st.data_editor(
    pd.DataFrame([{"Description": "", "Quantity": 1, "Unit Price": 0.0}]),
    num_rows="dynamic", use_container_width=True
)

if st.button("SAVE & GENERATE"):
    total_invoice = (items_df['Quantity'] * items_df['Unit Price']).sum()
    hoy = datetime.now().strftime("%m/%d/%Y")
    
    try:
        with conn.session as session:
            # Guardamos la factura con la dirección que usaste en ese momento
            res = session.execute(text("""
                INSERT INTO invoices (invoice_number, cliente, project_addr, total_amount, fecha_hoy)
                VALUES (:inv, :clie, :proj, :total, :hoy) RETURNING id
            """), {"inv": inv_no, "clie": c_name, "proj": p_addresses, "total": float(total_invoice), "hoy": hoy})
            invoice_id = res.fetchone()[0]
            
            for _, row in items_df.iterrows():
                session.execute(text("""
                    INSERT INTO invoice_items (invoice_id, description, quantity, unit_price)
                    VALUES (:iid, :desc, :qty, :prc)
                """), {"iid": invoice_id, "desc": row['Description'], "qty": int(row['Quantity']), "prc": float(row['Unit Price'])})
            session.commit()
            
        st.success("Invoice Saved!")
        
        # Datos para PDF
        pdf_info = {
            "emisor_info": my_address, "client_name": c_name, "inv_num": inv_no,
            "project_addr": p_addresses, "date": hoy, "due_date": due_date.strftime("%m/%d/%Y"),
            "payable_to": my_payable
        }
        pdf_bytes = generate_pdf(pdf_info, items_df)
        st.download_button("📥 Download PDF", data=bytes(pdf_bytes), file_name=f"Invoice_{inv_no}.pdf")
        
    except Exception as e:
        st.error(f"Error: {e}")
