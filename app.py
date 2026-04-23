import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from sqlalchemy import create_all, text

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Henrry's Garage | SQL System", layout="wide")

# Conexión a Neon PostgreSQL usando el Secrets
conn = st.connection("postgresql", type="sql")

# Crear la tabla si no existe
with conn.session as session:
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            inv_num TEXT,
            cliente TEXT,
            project_addr TEXT,
            description TEXT,
            qty INT,
            unit_p FLOAT,
            total_p FLOAT,
            fecha_hoy TEXT,
            due_date TEXT
        );
    """))
    session.commit()

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
            self.set_xy(50, 15) 
        except:
            self.set_xy(15, 15)
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "HENRRY'S GARAGE DOOR SERVICE", ln=True)
        self.set_y(32)
        if self.get_x() < 50: self.set_x(50)
        self.set_font("Helvetica", "", 10)
        info = f"{data['emisor_dir']}  |  {data['emisor_tel']}  |  {data['emisor_email']}"
        self.cell(0, 5, info, ln=True)

def generate_pdf(data):
    pdf = ModernInvoice()
    pdf.add_page()
    pdf.draw_header(data)
    # ... (El resto de la lógica del PDF se mantiene igual que la versión en inglés)
    pdf.set_y(60)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(95, 5, "BILL TO:", ln=0)
    pdf.cell(95, 5, "INVOICE DETAILS:", ln=1)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(95, 8, data['cliente'], ln=0)
    pdf.cell(95, 8, f"Invoice #: {data['inv_num']}", ln=1)
    
    # Tabla de productos
    pdf.ln(15)
    pdf.set_fill_color(30, 60, 90)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 10, " DESCRIPTION", fill=True)
    pdf.cell(20, 10, "QTY", fill=True, align="C")
    pdf.cell(35, 10, "UNIT PRICE", fill=True, align="C")
    pdf.cell(35, 10, "TOTAL", fill=True, align="C", ln=1)
    
    pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 15, data['desc'], border='B')
    pdf.cell(20, 15, str(data['qty']), border='B', align="C")
    pdf.cell(35, 15, f"${data['unit_p']}", border='B', align="C")
    pdf.cell(35, 15, f"${data['total_p']}", border='B', align="C", ln=1)

    return pdf.output()

# --- INTERFAZ ---
st.title("🚀 Henrry's Garage | SQL System (Neon)")
tab1, tab2 = st.tabs(["New Invoice", "Database History"])

with tab1:
    with st.form("sql_form"):
        inv = st.text_input("Invoice #", "005")
        clie = st.text_input("Client Name")
        proj = st.text_input("Project Address")
        serv = st.text_input("Work Description")
        qty = st.number_input("Quantity", min_value=1, value=1)
        prc = st.number_input("Unit Price", min_value=0.0)
        due = st.date_input("Due Date")
        submit = st.form_submit_button("SAVE TO NEON & GENERATE")

    if submit:
        total = qty * prc
        fecha_hoy = datetime.now().strftime("%m/%d/%Y")
        
        # Guardar en Neon
        with conn.session as session:
            query = text("""
                INSERT INTO invoices (inv_num, cliente, project_addr, description, qty, unit_p, total_p, fecha_hoy, due_date)
                VALUES (:inv, :clie, :proj, :serv, :qty, :prc, :total, :hoy, :due)
            """)
            session.execute(query, {"inv":inv, "clie":clie, "proj":proj, "serv":serv, "qty":qty, "prc":prc, "total":total, "hoy":fecha_hoy, "due":str(due)})
            session.commit()
        
        st.success("✅ Saved in Neon Database")
        
        # Generar PDF (usamos datos de emisor por defecto)
        emisor = {"emisor_dir": "Magnolia Houston tx", "emisor_tel": "(661)648-6043", "emisor_email": "alemanperez99@gmail.com"}
        pdf_data = {**emisor, "cliente": clie, "inv_num": inv, "project_addr": proj, "fecha_hoy": fecha_hoy, "due_date": str(due), "desc": serv, "qty": qty, "unit_p": prc, "total_p": total, "payable_to": "Henrry Perez"}
        
        pdf_bytes = generate_pdf(pdf_data)
        st.download_button("📥 Download PDF", data=bytes(pdf_bytes), file_name=f"Invoice_{inv}.pdf")

with tab2:
    if st.button("Load from Neon"):
        df = conn.query("SELECT * FROM invoices ORDER BY id DESC;", ttl=0)
        st.dataframe(df)
