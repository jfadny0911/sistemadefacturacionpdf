import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from sqlalchemy import text

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Henrry's Garage | Pro System", layout="wide")

# Conexión a Neon (Asegúrate de tener la URL en Secrets)
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
        self.set_y(32)
        self.set_x(52 if self.get_x() > 20 else 15)
        self.set_font("Helvetica", "", 10)
        info = f"{data['emisor_dir']}  |  {data['emisor_tel']}  |  {data['emisor_email']}"
        self.cell(0, 5, info, ln=True)

def generate_pdf(data, items_df):
    pdf = ModernInvoice()
    pdf.add_page()
    pdf.draw_header(data)
    
    pdf.set_y(60)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(95, 5, "BILL TO:", ln=0)
    pdf.cell(95, 5, "INVOICE DETAILS:", ln=1)
    
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(95, 8, data['client_name'], ln=0)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(95, 8, f"Invoice #: {data['inv_num']}", ln=1)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 5, f"Project: {data['project_addr']}", ln=0)
    pdf.cell(95, 5, f"Date: {data['date']}", ln=1)
    
    pdf.ln(10)
    # --- TABLA DE ITEMS ---
    pdf.set_fill_color(30, 60, 90)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(110, 10, " DESCRIPTION", fill=True)
    pdf.cell(20, 10, "QTY", fill=True, align="C")
    pdf.cell(30, 10, "PRICE", fill=True, align="C")
    pdf.cell(30, 10, "TOTAL", fill=True, align="C", ln=1)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    grand_total = 0
    for _, row in items_df.iterrows():
        line_total = row['Quantity'] * row['Unit Price']
        grand_total += line_total
        pdf.cell(110, 10, f" {row['Description']}", border='B')
        pdf.cell(20, 10, str(row['Quantity']), border='B', align="C")
        pdf.cell(30, 10, f"${row['Unit Price']:,.2f}", border='B', align="C")
        pdf.cell(30, 10, f"${line_total:,.2f}", border='B', align="C", ln=1)
    
    pdf.ln(5)
    pdf.set_x(140)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(220, 130, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 12, f" TOTAL: ${grand_total:,.2f}", fill=True, align="C")
    return pdf.output()

# --- INTERFAZ ---
st.title("🛠️ Henrry's Garage | Neon Multi-Item System")

with st.sidebar:
    st.header("Business Info")
    e_dir = st.text_input("Address", "Magnolia Houston tx")
    e_tel = st.text_input("Phone", "(661)648-6043")
    e_eml = st.text_input("Email", "alemanperez99@gmail.com")

# 1. Datos de la Factura
c1, c2 = st.columns(2)
inv_no = c1.text_input("Invoice #")
c_name = c2.text_input("Client Name")
p_addr = st.text_input("Project Address")

# 2. Tabla dinámica de productos
st.subheader("Invoice Items")
items_df = st.data_editor(
    pd.DataFrame([{"Description": "", "Quantity": 1, "Unit Price": 0.0}]),
    num_rows="dynamic",
    use_container_width=True
)

if st.button("SAVE & GENERATE PDF"):
    total_invoice = (items_df['Quantity'] * items_df['Unit Price']).sum()
    hoy = datetime.now().strftime("%m/%d/%Y")
    
    try:
        with conn.session as session:
            # Insertar Factura
            res = session.execute(text("""
                INSERT INTO invoices (invoice_number, cliente, project_addr, total_amount, fecha_hoy)
                VALUES (:inv, :clie, :proj, :total, :hoy) RETURNING id
            """), {"inv": inv_no, "clie": c_name, "proj": p_addr, "total": total_invoice, "hoy": hoy})
            invoice_id = res.fetchone()[0]
            
            # Insertar Items
            for _, row in items_df.iterrows():
                session.execute(text("""
                    INSERT INTO invoice_items (invoice_id, description, quantity, unit_price)
                    VALUES (:iid, :desc, :qty, :prc)
                """), {"iid": invoice_id, "desc": row['Description'], "qty": row['Quantity'], "prc": row['Unit Price']})
            session.commit()
            
        st.success(f"Factura {inv_no} guardada en Neon!")
        
        # Generar PDF
        pdf_data = {
            "emisor_dir": e_dir, "emisor_tel": e_tel, "emisor_email": e_eml,
            "client_name": c_name, "inv_num": inv_no, "project_addr": p_addr, "date": hoy
        }
        pdf_bytes = generate_pdf(pdf_data, items_df)
        st.download_button("📥 Download PDF", data=bytes(pdf_bytes), file_name=f"Invoice_{inv_no}.pdf")
        
    except Exception as e:
        st.error(f"Error: {e}")
