import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from sqlalchemy import text

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Henrry's Garage | Modern Invoice", layout="wide")

# Conexión a Neon
conn = st.connection("postgresql", type="sql")

# --- ESTADO DE LA SESIÓN (Para manejar filas sin tablas) ---
if 'address_rows' not in st.session_state:
    st.session_state.address_rows = [""] # Inicia con una casilla de dirección
if 'service_rows' not in st.session_state:
    st.session_state.service_rows = [{"desc": "", "qty": 1, "price": 0.0}]

# --- CLASE PDF PROFESIONAL ---
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
            self.set_xy(52, 18) 
        except:
            self.set_xy(15, 18)
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "HENRRY'S GARAGE DOOR SERVICE", ln=True)
        self.set_y(32)
        if self.get_x() < 50: self.set_x(52)
        self.set_font("Helvetica", "", 9)
        self.multi_cell(0, 4, f"{data['emisor_info']}")

def generate_pdf(data, services, addresses):
    pdf = ModernInvoice()
    pdf.add_page()
    pdf.draw_header(data)
    
    # Bloque de Cliente y Direcciones de Proyecto
    pdf.set_y(60)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(95, 5, "BILL TO:", ln=1)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(95, 7, data['client_name'].upper(), ln=1)
    
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(95, 5, "Project Addresses:", ln=1)
    pdf.set_font("Helvetica", "", 9)
    for addr in addresses:
        if addr.strip():
            pdf.cell(5, 5, "- ", ln=0)
            pdf.multi_cell(90, 5, addr)

    # Detalles de Factura
    pdf.set_y(60)
    pdf.set_x(120)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, f"Invoice #: {data['inv_num']}", ln=True)
    pdf.set_x(120)
    pdf.cell(0, 5, f"Date: {data['date']}", ln=True)
    pdf.set_x(120)
    pdf.cell(0, 5, f"Due Date: {data['due_date']}", ln=True)

    # Tabla de Servicios
    pdf.ln(15)
    pdf.set_fill_color(30, 60, 90)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(110, 10, " DESCRIPTION", fill=True)
    pdf.cell(20, 10, "QTY", fill=True, align="C")
    pdf.cell(35, 10, "PRICE", fill=True, align="C")
    pdf.cell(35, 10, "TOTAL", fill=True, align="C", ln=1)

    pdf.set_text_color(0, 0, 0)
    total_gral = 0
    for s in services:
        line_total = s['qty'] * s['price']
        total_gral += line_total
        pdf.cell(110, 10, f" {s['desc']}", border='B')
        pdf.cell(20, 10, str(s['qty']), border='B', align="C")
        pdf.cell(35, 10, f"${s['price']:,.2f}", border='B', align="C")
        pdf.cell(35, 10, f"${line_total:,.2f}", border='B', align="C", ln=1)

    pdf.ln(8)
    pdf.set_x(140)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(220, 130, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 12, f" TOTAL: ${total_gral:,.2f}", fill=True, align="C")
    
    return pdf.output()

# --- INTERFAZ DE USUARIO ---
st.title("🚀 Henrry's Garage Management System")

# Panel lateral con tu información de negocio (Editable)
with st.sidebar:
    st.header("⚙️ My Business Info")
    my_address = st.text_area("Your Header Info", "31411 Terri Ln, Magnolia, TX 77354\n(661) 648-6043 | alemanperez99@gmail.com")
    my_payable = st.text_input("Payable to", "Henrry Perez")

# SECCIÓN 1: CLIENTE Y FACTURA
with st.container():
    st.subheader("👤 Client Details")
    c1, c2, c3 = st.columns([1, 2, 1])
    inv_no = c1.text_input("Invoice #")
    c_name = c2.text_input("Client Name")
    due_d = c3.date_input("Due Date")

# SECCIÓN 2: DIRECCIONES DE PROYECTO (DISEÑO MODERNO)
st.markdown("---")
st.subheader("📍 Project Addresses")
for i, addr in enumerate(st.session_state.address_rows):
    # Creamos una fila limpia con el campo y el botón de borrar
    col_input, col_action = st.columns([0.9, 0.1])
    st.session_state.address_rows[i] = col_input.text_input(f"Address {i+1}", value=addr, key=f"addr_field_{i}", placeholder="Enter project address...")
    if col_action.button("🗑️", key=f"del_addr_btn_{i}"):
        st.session_state.address_rows.pop(i)
        st.rerun()

if st.button("➕ Add Another Address"):
    st.session_state.address_rows.append("")
    st.rerun()

# SECCIÓN 3: SERVICIOS (DISEÑO MODERNO)
st.markdown("---")
st.subheader("📦 Services & Products")
current_total = 0
for i, serv in enumerate(st.session_state.service_rows):
    c_desc, c_qty, c_price, c_del = st.columns([0.5, 0.15, 0.25, 0.1])
    st.session_state.service_rows[i]['desc'] = c_desc.text_input("Description", value=serv['desc'], key=f"s_desc_{i}")
    st.session_state.service_rows[i]['qty'] = c_qty.number_input("Qty", min_value=1, value=serv['qty'], key=f"s_qty_{i}")
    st.session_state.service_rows[i]['price'] = c_price.number_input("Price", min_value=0.0, value=serv['price'], key=f"s_price_{i}")
    
    line_total = st.session_state.service_rows[i]['qty'] * st.session_state.service_rows[i]['price']
    current_total += line_total
    
    if c_del.button("🗑️", key=f"s_del_{i}"):
        st.session_state.service_rows.pop(i)
        st.rerun()

st.info(f"### **Total Amount: ${current_total:,.2f}**")
if st.button("➕ Add Another Service"):
    st.session_state.service_rows.append({"desc": "", "qty": 1, "price": 0.0})
    st.rerun()

# BOTÓN DE GUARDADO Y PDF
st.markdown("---")
if st.button("💾 SAVE TO NEON & GENERATE PDF"):
    hoy = datetime.now().strftime("%m/%d/%Y")
    try:
        with conn.session as session:
            # Unimos las direcciones para guardarlas en una sola celda en Neon como historial
            all_addrs = " | ".join([a for a in st.session_state.address_rows if a.strip()])
            
            res = session.execute(text("""
                INSERT INTO invoices (invoice_number, cliente, project_addr, total_amount, fecha_hoy)
                VALUES (:inv, :clie, :proj, :total, :hoy) RETURNING id
            """), {"inv": inv_no, "clie": c_name, "proj": all_addrs, "total": current_total, "hoy": hoy})
            invoice_id = res.fetchone()[0]
            
            for s in st.session_state.service_rows:
                if s['desc'].strip():
                    session.execute(text("""
                        INSERT INTO invoice_items (invoice_id, description, quantity, unit_price)
                        VALUES (:iid, :desc, :qty, :prc)
                    """), {"iid": invoice_id, "desc": s['desc'], "qty": s['qty'], "prc": s['price']})
            session.commit()
            
        pdf_info = {
            "emisor_info": my_address, "client_name": c_name, "inv_num": inv_no,
            "date": hoy, "due_date": due_d.strftime("%m/%d/%Y"), "payable_to": my_payable
        }
        pdf_bytes = generate_pdf(pdf_info, st.session_state.service_rows, st.session_state.address_rows)
        st.download_button("📥 Download Invoice PDF", data=bytes(pdf_bytes), file_name=f"Invoice_{inv_no}.pdf")
        st.success("Invoice successfully archived in Neon!")
        
    except Exception as e:
        st.error(f"Error saving data: {e}")
