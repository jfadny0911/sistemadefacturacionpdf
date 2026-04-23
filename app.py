import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from sqlalchemy import text

# --- CONFIGURACIÓN DE PÁGINA ---
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
        
        self.set_y(32)
        if self.get_x() < 50: self.set_x(52)
        self.set_font("Helvetica", "", 9)
        self.multi_cell(0, 4, f"{data['emisor_info']}")

def generate_pdf(data, items_df, addr_df):
    pdf = ModernInvoice()
    pdf.add_page()
    pdf.draw_header(data)
    
    dark_blue = (30, 60, 90)
    
    pdf.set_y(55)
    # BLOQUE IZQUIERDO: CLIENTE Y DIRECCIONES
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(95, 5, "BILL TO:", ln=1)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(95, 7, data['client_name'].upper(), ln=1)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(95, 5, "Project Addresses:", ln=1)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    # Listar direcciones en casillas/líneas separadas
    for addr in addr_df['Address']:
        if addr.strip():
            pdf.cell(5, 5, "- ", ln=0)
            pdf.multi_cell(90, 5, addr)

    # BLOQUE DERECHO: DETALLES FACTURA
    pdf.set_y(55)
    pdf.set_x(115)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(85, 5, "INVOICE DETAILS:", ln=1)
    
    details_y = 62
    details = [
        ("Invoice #:", data['inv_num']),
        ("Date:", data['date']),
        ("Due Date:", data['due_date']),
        ("Payable to:", data['payable_to'])
    ]
    
    for label, val in details:
        pdf.set_y(details_y)
        pdf.set_x(115)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(30, 5, label)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(55, 5, val)
        details_y += 5
    
    pdf.ln(15)
    # TABLA DE PRODUCTOS
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
    
    # TOTAL
    pdf.ln(5)
    pdf.set_x(140)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(220, 130, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 12, f" TOTAL: ${total_val:,.2f}", fill=True, align="C", ln=1)

    # GARANTÍA
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*dark_blue)
    pdf.cell(0, 5, "WARRANTY TERMS", ln=True)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(180, 4, "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***\n1-year warranty on factory defects/installation, 6 months in Opener.")
    
    return pdf.output()

# --- SIDEBAR (EMISOR EDITABLE) ---
with st.sidebar:
    st.header("⚙️ My Business Info")
    my_address = st.text_area("Your Header Info", "31411 Terri Ln, Magnolia, TX 77354\n(661) 648-6043 | alemanperez99@gmail.com")
    my_payable = st.text_input("Payable to", "Henrry Perez")

# --- INTERFAZ PRINCIPAL ---
st.title("🛠️ Henrry's Garage Invoice System")

col1, col2 = st.columns(2)
inv_no = col1.text_input("Invoice #")
c_name = col2.text_input("Client Name")

# CASILLAS SEPARADAS PARA DIRECCIONES
st.subheader("📍 Project Addresses")
addr_df = st.data_editor(
    pd.DataFrame([{"Address": ""}]),
    num_rows="dynamic", use_container_width=True, key="addr_editor"
)

# CASILLAS SEPARADAS PARA PRODUCTOS
st.subheader("📦 Services & Products")
items_df = st.data_editor(
    pd.DataFrame([{"Description": "", "Quantity": 1, "Unit Price": 0.0}]),
    num_rows="dynamic", use_container_width=True, key="item_editor"
)

due_date = st.date_input("Due Date")

if st.button("SAVE & GENERATE PDF"):
    total_invoice = (items_df['Quantity'] * items_df['Unit Price']).sum()
    hoy = datetime.now().strftime("%m/%d/%Y")
    
    # Unimos las direcciones en un solo texto para la base de datos
    all_addrs = " | ".join(addr_df['Address'].tolist())

    try:
        with conn.session as session:
            res = session.execute(text("""
                INSERT INTO invoices (invoice_number, cliente, project_addr, total_amount, fecha_hoy)
                VALUES (:inv, :clie, :proj, :total, :hoy) RETURNING id
            """), {"inv": inv_no, "clie": c_name, "proj": all_addrs, "total": float(total_invoice), "hoy": hoy})
            invoice_id = res.fetchone()[0]
            
            for _, row in items_df.iterrows():
                session.execute(text("""
                    INSERT INTO invoice_items (invoice_id, description, quantity, unit_price)
                    VALUES (:iid, :desc, :qty, :prc)
                """), {"iid": invoice_id, "desc": row['Description'], "qty": int(row['Quantity']), "prc": float(row['Unit Price'])})
            session.commit()
            
        st.success("Data Saved in Neon!")
        
        pdf_info = {
            "emisor_info": my_address, "client_name": c_name, "inv_num": inv_no,
            "date": hoy, "due_date": due_date.strftime("%m/%d/%Y"), "payable_to": my_payable
        }
        
        pdf_bytes = generate_pdf(pdf_info, items_df, addr_df)
        st.download_button("📥 Download PDF", data=bytes(pdf_bytes), file_name=f"Invoice_{inv_no}.pdf")
        
    except Exception as e:
        st.error(f"Error: {e}")
