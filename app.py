import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from sqlalchemy import text

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Henrry's Garage | Modern System", layout="wide")

# Conexión a Neon
conn = st.connection("postgresql", type="sql")

# --- LÓGICA DE ESTADO (Para manejar filas dinámicas sin tablas) ---
if 'address_rows' not in st.session_state:
    st.session_state.address_rows = [""]
if 'service_rows' not in st.session_state:
    st.session_state.service_rows = [{"desc": "", "qty": 1, "price": 0.0}]

# --- CLASE PDF ---
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
    
    # Datos de Cliente y Direcciones
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
        if addr: pdf.cell(0, 5, f"- {addr}", ln=True)

    # Detalles de Factura a la derecha
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

    pdf.ln(5)
    pdf.set_x(140)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_fill_color(220, 130, 50)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(60, 12, f" TOTAL: ${total_gral:,.2f}", fill=True, align="C")
    
    return pdf.output()

# --- INTERFAZ ---
st.title("🚀 Henrry's Garage System")

# Barra Lateral (Emisor)
with st.sidebar:
    st.header("⚙️ My Business Info")
    my_address = st.text_area("Your Header Info", "31411 Terri Ln, Magnolia, TX 77354\n(661) 648-6043 | alemanperez99@gmail.com")
    my_payable = st.text_input("Payable to", "Henrry Perez")

# SECCIÓN 1: DATOS GENERALES
with st.expander("👤 Client & Invoice Details", expanded=True):
    c1, c2, c3 = st.columns([1,2,1])
    inv_no = c1.text_input("Invoice #")
    c_name = c2.text_input("Client Name")
    due_d = c3.date_input("Due Date")

# SECCIÓN 2: DIRECCIONES (Dinámicas)
st.subheader("📍 Project Addresses")
for i, addr in enumerate(st.session_state.address_rows):
    col_addr, col_del = st.columns([0.9, 0.1])
    st.session_state.address_rows[i] = col_addr.text_input(f"Address {i+1}", value=addr, key=f"addr_{i}")
    if col_del.button("🗑️", key=f"del_addr_{i}"):
        st.session_state.address_rows.pop(i)
        st.rerun()
if st.button("➕ Add Address"):
    st.session_state.address_rows.append("")
    st.rerun()

# SECCIÓN 3: SERVICIOS (Dinámicos)
st.subheader("📦 Services & Products")
total_preview = 0
for i, serv in enumerate(st.session_state.service_rows):
    col_d, col_q, col_p, col_x = st.columns([0.5, 0.15, 0.25, 0.1])
    st.session_state.service_rows[i]['desc'] = col_d.text_input("Description", value=serv['desc'], key=f"desc_{i}")
    st.session_state.service_rows[i]['qty'] = col_q.number_input("Qty", min_value=1, value=serv['qty'], key=f"qty_{i}")
    st.session_state.service_rows[i]['price'] = col_p.number_input("Price", min_value=0.0, value=serv['price'], key=f"price_{i}")
    total_preview += st.session_state.service_rows[i]['qty'] * st.session_state.service_rows[i]['price']
    if col_x.button("🗑️", key=f"del_serv_{i}"):
        st.session_state.service_rows.pop(i)
        st.rerun()

st.markdown(f"### **Current Total: ${total_preview:,.2f}**")
if st.button("➕ Add Service"):
    st.session_state.service_rows.append({"desc": "", "qty": 1, "price": 0.0})
    st.rerun()

# BOTÓN FINAL
if st.button("💾 SAVE & GENERATE PDF"):
    hoy = datetime.now().strftime("%m/%d/%Y")
    # Guardar en Neon (Cabecera)
    try:
        with conn.session as session:
            # Lógica para insertar cabecera y luego items uno a uno
            all_addrs = " | ".join(st.session_state.address_rows)
            res = session.execute(text("""
                INSERT INTO invoices (invoice_number, cliente, project_addr, total_amount, fecha_hoy)
                VALUES (:inv, :clie, :proj, :total, :hoy) RETURNING id
            """), {"inv": inv_no, "clie": c_name, "proj": all_addrs, "total": total_preview, "hoy": hoy})
            invoice_id = res.fetchone()[0]
            
            for s in st.session_state.service_rows:
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
        st.download_button("📥 Download PDF", data=bytes(pdf_bytes), file_name=f"Invoice_{inv_no}.pdf")
        st.success("Successfully Saved in Neon!")
    except Exception as e:
        st.error(f"Error: {e}")
