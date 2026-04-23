import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from sqlalchemy import text

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Henrry's Garage | SQL System", layout="wide")

# Database Connection (Ensure 'url' is set in Streamlit Secrets)
# Secret format: [connections.postgresql] -> url = "postgresql://..."
conn = st.connection("postgresql", type="sql")

# Create Table if it doesn't exist
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
        dark_blue = (30, 60, 90) 
        orange = (220, 130, 50)  
        
        # Header Background
        self.set_fill_color(*dark_blue)
        self.rect(0, 0, 210, 50, 'F')
        
        # Decorative Line (Behind Logo)
        self.set_draw_color(*orange)
        self.set_line_width(1.2)
        self.line(0, 28, 110, 28)
        
        # Logo Integration
        try:
            self.image("logo.png", 12, 8, 33) 
            self.set_xy(50, 15) 
        except:
            self.set_xy(15, 15)
            
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "HENRRY'S GARAGE DOOR SERVICE", ln=True)
        
        self.set_y(32)
        if self.get_x() < 50: self.set_x(50)
        self.set_font("Helvetica", "", 10)
        info = f"{data['emisor_dir']}  |  {data['emisor_tel']}  |  {data['emisor_email']}"
        self.cell(0, 5, info, ln=True)

def generate_pdf(data):
    pdf = ModernInvoice(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.draw_header(data)
    
    pdf.set_y(60)
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(95, 5, "BILL TO:", ln=0)
    pdf.cell(95, 5, "INVOICE DETAILS:", ln=1)
    
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(95, 8, data['cliente'], ln=0)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(95, 8, f"Invoice #: {data['inv_num']}", ln=1)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 5, f"Project: {data['project_addr']}", ln=0)
    pdf.cell(95, 5, f"Date: {data['fecha_hoy']}", ln=1)
    pdf.cell(95, 5, f"Payable to: Henrry Perez", ln=0)
    pdf.cell(95, 5, f"Due Date: {data['due_date']}", ln=1)
    
    pdf.ln(15)
    
    # Table Header
    pdf.set_fill_color(30, 60, 90)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(100, 10, " DESCRIPTION", fill=True)
    pdf.cell(20, 10, "QTY", fill=True, align="C")
    pdf.cell(35, 10, "UNIT PRICE", fill=True, align="C")
    pdf.cell(35, 10, "TOTAL", fill=True, align="C", ln=1)
    
    # Table Content
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(100, 15, f" {data['desc']}", border='B')
    pdf.cell(20, 15, str(data['qty']), border='B', align="C")
    pdf.cell(35, 15, f"${data['unit_p']}", border='B', align="C")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(35, 15, f"${data['total_p']}", border='B', align="C", ln=1)
    
    # Total Box
    pdf.ln(10)
    pdf.set_x(130)
    pdf.set_fill_color(220, 130, 50) # Orange
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(70, 12, f" TOTAL: ${data['total_p']}", fill=True, align="C", ln=1)

    return pdf.output()

# --- STREAMLIT UI ---
st.title("🛠️ Henrry's Garage | Neon SQL System")
tab1, tab2 = st.tabs(["New Invoice", "Database History"])

with st.sidebar:
    try:
        st.image("logo.png", width=200)
    except:
        st.info("Upload logo.png to GitHub.")
    st.header("Business Settings")
    e_dir = st.text_input("Address", "Magnolia Houston tx")
    e_tel = st.text_input("Phone", "(661)648-6043")
    e_eml = st.text_input("Email", "alemanperez99@gmail.com")

with tab1:
    with st.form("invoice_form"):
        c1, c2 = st.columns(2)
        inv = c1.text_input("Invoice #", "005")
        clie = c2.text_input("Client Name")
        proj = st.text_input("Project Address")
        serv = st.text_input("Work Description")
        c3, c4 = st.columns(2)
        qty = c3.number_input("Quantity", min_value=1, value=1)
        prc = c4.number_input("Unit Price ($)", min_value=0.0)
        due = st.date_input("Due Date")
        submit = st.form_submit_button("SAVE & GENERATE PDF")

    if submit:
        total = qty * prc
        fecha_hoy = datetime.now().strftime("%m/%d/%Y")
        
        # Save to Neon
        try:
            with conn.session as session:
                query = text("""
                    INSERT INTO invoices (inv_num, cliente, project_addr, description, qty, unit_p, total_p, fecha_hoy, due_date)
                    VALUES (:inv, :clie, :proj, :serv, :qty, :prc, :total, :hoy, :due)
                """)
                session.execute(query, {"inv":inv, "clie":clie, "proj":proj, "serv":serv, "qty":qty, "prc":prc, "total":total, "hoy":fecha_hoy, "due":str(due)})
                session.commit()
            st.success("✅ Successfully saved to Neon Database")
            
            # PDF Data
            pdf_data = {
                "emisor_dir": e_dir, "emisor_tel": e_tel, "emisor_email": e_eml,
                "cliente": clie, "inv_num": inv, "project_addr": proj, 
                "fecha_hoy": fecha_hoy, "due_date": str(due), 
                "desc": serv, "qty": qty, "unit_p": f"{prc:,.2f}", "total_p": f"{total:,.2f}"
            }
            pdf_bytes = generate_pdf(pdf_data)
            st.download_button("📥 Download Invoice PDF", data=bytes(pdf_bytes), file_name=f"Invoice_{inv}.pdf")
        except Exception as e:
            st.error(f"Error saving to database: {e}")

with tab2:
    if st.button("Refresh Data from Neon"):
        df = conn.query("SELECT * FROM invoices ORDER BY id DESC;", ttl=0)
        st.dataframe(df, use_container_width=True)
