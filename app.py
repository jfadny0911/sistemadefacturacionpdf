import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from sqlalchemy import text

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Henrry's Garage | Professional Invoice", layout="wide")

# Conexión a Neon (Asegúrate de configurar [connections.postgresql] en Secrets)
conn = st.connection("postgresql", type="sql")

class ModernInvoice(FPDF):
    def draw_header(self, data):
        azul_oscuro = (30, 60, 90) 
        naranja = (220, 130, 50)  

        # Encabezado sólido
        self.set_fill_color(*azul_oscuro)
        self.rect(0, 0, 210, 50, 'F')
        
        # Línea naranja decorativa (atrás del logo)
        self.set_draw_color(*naranja)
        self.set_line_width(1.2)
        self.line(0, 28, 110, 28)

        # Logo
        try:
            self.image("logo.png", 12, 8, 33) 
            self.set_xy(52, 15) 
        except:
            self.set_xy(15, 15)
        
        # Nombre de la empresa
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "HENRRY'S GARAGE DOOR SERVICE", ln=True)
        
        # Datos del emisor (Datos originales solicitados)
        self.set_y(32)
        if self.get_x() < 50: self.set_x(52)
        self.set_font("Helvetica", "", 9)
        # Usamos los datos originales de Terri Ln
        info = f"31411 Terri Ln, Magnolia, TX 77354  |  (661) 648-6043  |  alemanperez99@gmail.com"
        self.cell(0, 5, info, ln=True)

def generate_pdf(data, items_df):
    pdf = ModernInvoice(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.draw_header(data)
    
    dark_blue = (30, 60, 90)
    
    pdf.set_y(60)
    # Bloque de información (BILL TO e INVOICE DETAILS)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(95, 5, "BILL TO:", ln=0)
    pdf.cell(95, 5, "INVOICE DETAILS:", ln=1)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(95, 8, data['client_name'].upper(), ln=0)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(95, 8, f"Invoice #: {data['inv_num']}", ln=1)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 5, f"Project: {data['project_addr']}", ln=0)
    pdf.cell(95, 5, f"Date: {data['date']}", ln=1)
    pdf.cell(95, 5, f"Payable to: {data['payable_to']}", ln=0)
    pdf.cell(95, 5, f"Due Date: {data['due_date']}", ln=1)
    
    pdf.ln(12)

    # --- TABLA DE PRODUCTOS/SERVICIOS ---
    pdf.set_fill_color(*dark_blue)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(110, 10, " DESCRIPTION", fill=True)
    pdf.cell(20, 10, "QTY", fill=True, align="C")
    pdf.cell(30, 10, "UNIT PRICE", fill=True, align="C")
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
    
    # Total Resaltado
    pdf.ln(8)
    pdf.set_x(140)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(220, 130, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 12, f" TOTAL: ${total_val:,.2f}", fill=True, align="C", ln=1)

    # --- GARANTÍA (Texto Original) ---
    pdf.ln(15)
    pdf.set_x(15)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*dark_blue)
    pdf.cell(0, 5, "WARRANTY TERMS", ln=True)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    
    warranty_text = (
        "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***\n"
        "For installation on a new garage door, it has a 1-year warranty on factory defects "
        "and installation by HENRRY DOORS we are not responsible for damages or bad "
        "manipulation when opening or closing the garage door And 6 months in Opener."
    )
    pdf.multi_cell(180, 4.5, warranty_text)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*dark_blue)
    pdf.cell(0, 10, "Thank You For Your Business", align="C", ln=True)
    
    return pdf.output()

# --- INTERFAZ STREAMLIT ---
st.title("🛠️ Henrry's Garage | Premium SQL System")

c1, c2, c3 = st.columns(3)
inv_no = c1.text_input("Invoice #", value="005")
c_name = c2.text_input("Client Name", value="The Woodlands Living")
paga_a = c3.text_input("Payable to", value="Henrry Perez")

p_addr = st.text_input("Project Address", value="4919 Curiosity Ct")
d_date = st.date_input("Due Date")

# Tabla dinámica para múltiples productos
st.subheader("Services & Products")
items_df = st.data_editor(
    pd.DataFrame([{"Description": "Rail Repair in Genie Opener", "Quantity": 1, "Unit Price": 75.0}]),
    num_rows="dynamic",
    use_container_width=True
)

if st.button("SAVE TO NEON & GENERATE PDF"):
    total_invoice = (items_df['Quantity'] * items_df['Unit Price']).sum()
    hoy = datetime.now().strftime("%m/%d/%Y")
    
    try:
        # Guardar en Neon
        with conn.session as session:
            # 1. Insertar Cabecera
            res = session.execute(text("""
                INSERT INTO invoices (invoice_number, cliente, project_addr, total_amount, fecha_hoy)
                VALUES (:inv, :clie, :proj, :total, :hoy) RETURNING id
            """), {"inv": inv_no, "clie": c_name, "proj": p_addr, "total": float(total_invoice), "hoy": hoy})
            invoice_id = res.fetchone()[0]
            
            # 2. Insertar cada Item
            for _, row in items_df.iterrows():
                session.execute(text("""
                    INSERT INTO invoice_items (invoice_id, description, quantity, unit_price)
                    VALUES (:iid, :desc, :qty, :prc)
                """), {"iid": invoice_id, "desc": row['Description'], "qty": int(row['Quantity']), "prc": float(row['Unit Price'])})
            session.commit()
            
        st.success(f"Invoice {inv_no} saved successfully in Neon!")
        
        # Datos para el PDF
        pdf_info = {
            "emisor_dir": "31411 Terri Ln", "emisor_tel": "(661) 648-6043", "emisor_email": "alemanperez99@gmail.com",
            "client_name": c_name, "inv_num": inv_no, "project_addr": p_addr, 
            "date": hoy, "due_date": d_date.strftime("%m/%d/%Y"), "payable_to": paga_a
        }
        
        pdf_bytes = generate_pdf(pdf_info, items_df)
        st.download_button("📥 Download Invoice PDF", data=bytes(pdf_bytes), file_name=f"Invoice_{inv_no}.pdf")
        
    except Exception as e:
        st.error(f"Error connecting to Neon: {e}")
