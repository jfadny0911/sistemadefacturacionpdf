import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Henrry's Garage | Invoice System", layout="wide")

# Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

class ModernInvoice(FPDF):
    def draw_header(self, data):
        # Colors from the logo
        dark_blue = (30, 60, 90) 
        orange = (220, 130, 50)  

        # 1. Solid blue background
        self.set_fill_color(*dark_blue)
        self.rect(0, 0, 210, 50, 'F')
        
        # 2. Decorative orange line (drawn behind the logo)
        self.set_draw_color(*orange)
        self.set_line_width(1.2)
        self.line(0, 28, 110, 28)

        # 3. Insert LOGO
        try:
            self.image("logo.png", 12, 8, 33) 
            self.set_xy(50, 15) 
        except:
            self.set_xy(15, 15)
        
        # 4. Company Name
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, str(data['emisor_nombre']).upper(), ln=True)
        
        # 5. Contact Information
        self.set_y(32)
        if self.get_x() < 50:
            self.set_x(50)
        self.set_font("Helvetica", "", 10)
        info = f"{data['emisor_dir']}  |  {data['emisor_tel']}  |  {data['emisor_email']}"
        self.cell(0, 5, info, ln=True)

def generate_pdf(data):
    pdf = ModernInvoice(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.draw_header(data)
    
    dark_blue = (30, 60, 90)
    orange = (220, 130, 50)
    
    pdf.set_y(60)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(120, 120, 120)
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
    pdf.cell(95, 5, f"Payable to: {data['payable_to']}", ln=0)
    pdf.cell(95, 5, f"Due Date: {data['due_date']}", ln=1)
    
    pdf.ln(15)

    # --- TABLE HEADER ---
    pdf.set_fill_color(*dark_blue)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 10, " DESCRIPTION", border=0, fill=True)
    pdf.cell(20, 10, "QTY", border=0, fill=True, align="C")
    pdf.cell(35, 10, "UNIT PRICE", border=0, fill=True, align="C")
    pdf.cell(35, 10, "TOTAL", border=0, fill=True, align="C", ln=1)
    
    # --- TABLE CONTENT ---
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.set_fill_color(245, 248, 252)
    pdf.cell(100, 15, f" {data['desc']}", border='B', fill=True)
    pdf.cell(20, 15, str(data['qty']), border='B', fill=True, align="C")
    pdf.cell(35, 15, f"${data['unit_p']}", border='B', fill=True, align="C")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(35, 15, f"${data['total_p']}", border='B', fill=True, align="C", ln=1)
    
    # --- TOTAL ---
    pdf.ln(10)
    pdf.set_x(130)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(*orange)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(30, 12, " TOTAL", fill=True, align="C")
    pdf.cell(40, 12, f"${data['total_p']} ", fill=True, align="R", ln=1)

    # --- WARRANTY ---
    pdf.ln(20)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*dark_blue)
    pdf.cell(0, 5, "WARRANTY TERMS", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 100, 100)
    
    warranty = (
        "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***\n"
        "For installation on a new garage door, it has a 1-year warranty on factory defects "
        "and installation by HENRRY DOORS we are not responsible for damages or bad "
        "manipulation when opening or closing the garage door And 6 months in Opener."
    )
    pdf.multi_cell(180, 4, warranty)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*dark_blue)
    pdf.cell(0, 10, "Thank You For Your Business", align="C", ln=True)
    
    return pdf.output()

# --- STREAMLIT INTERFACE ---
st.title("🛠️ Henrry's Garage - Invoice System")

tab1, tab2 = st.tabs(["Create Invoice", "Cloud History"])

with st.sidebar:
    try:
        st.image("logo.png", width=200)
    except:
        st.info("Upload logo.png to GitHub.")
    st.header("Business Details")
    e_nom = st.text_input("Company", "Henrry's Garage Door Service")
    e_dir = st.text_input("Address", "Magnolia Houston tx")
    e_tel = st.text_input("Phone", "(661)648-6043")
    e_eml = st.text_input("Email", "alemanperez99@gmail.com")

with tab1:
    with st.form("main_form"):
        c1, c2, c3 = st.columns(3)
        inv = c1.text_input("Invoice #", "005")
        clie = c2.text_input("Client Name", "The Woodlands Living")
        paga = c3.text_input("Payable to", "Henrry Perez")
        
        proj = st.text_input("Project Address", "4919 Curiosity Ct")
        serv = st.text_input("Description of Work", "Rail Repair in Genie Opener")
        
        c4, c5 = st.columns(2)
        qty = c4.number_input("Quantity", min_value=1, value=1)
        prc = c5.number_input("Unit Price ($)", min_value=0.0, value=75.0)
        due = st.date_input("Due Date")
        
        btn = st.form_submit_button("SAVE & GENERATE PDF")

    if btn:
        total_v = qty * prc
        datos = {
            'emisor_nombre': e_nom, 'emisor_dir': e_dir, 'emisor_tel': e_tel, 'emisor_email': e_eml,
            'fecha_hoy': datetime.now().strftime("%m/%d/%Y"), 'cliente': clie, 'payable_to': paga,
            'inv_num': inv, 'project_addr': proj, 'due_date': due.strftime("%m/%d/%Y"),
            'desc': serv, 'qty': qty, 'unit_p': f"{prc:,.2f}", 'total_p': f"{total_v:,.2f}"
        }
        
        try:
            df_h = conn.read(worksheet="Sheet1", ttl=0)
            df_n = pd.concat([df_h, pd.DataFrame([datos])], ignore_index=True)
            conn.update(worksheet="Sheet1", data=df_n)
            st.success("✅ Saved to Google Sheets")
        except Exception as e:
            st.error(f"Sheets Error: {e}")

        pdf_b = generate_pdf(datos)
        st.download_button("📥 Download Invoice PDF", data=bytes(pdf_b), file_name=f"Invoice_{inv}.pdf")

with tab2:
    if st.button("Refresh History"):
        try:
            df = conn.read(worksheet="Sheet1", ttl=0)
            st.dataframe(df, use_container_width=True)
        except:
            st.error("Error loading data. Check Google Sheets connection.")
