import streamlit as st
from fpdf import FPDF
from datetime import datetime
import pandas as pd
from sqlalchemy import text
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Henrry's Garage | Professional System", layout="wide")

# Conexión a Neon
conn = st.connection("postgresql", type="sql")

# Inicializar estados
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

    pdf.set_y(60)
    pdf.set_x(120)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, f"Invoice #: {data['inv_num']}", ln=True)
    pdf.set_x(120)
    pdf.cell(0, 5, f"Date: {data['date']}", ln=True)
    pdf.set_x(120)
    pdf.cell(0, 5, f"Due Date: {data['due_date']}", ln=True)

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
    pdf.cell(60, 12, f" TOTAL: ${total_gral:,.2f}", fill=True, align="C", ln=1)
    
    # --- BLOQUE DE GARANTÍA ---
    pdf.set_y(-55) 
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 60, 90)
    
    # Aseguramos que el cursor esté en el margen izquierdo para centrar bien
    pdf.set_x(10)
    pdf.cell(190, 5, "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***", ln=1, align="C")
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    warranty_text = (
        "For installation on a new garage door, it has a 1-year warranty on factory defects "
        "and installation by HENRRY DOORS we are not responsible for damages or bad "
        "manipulation when opening or closing the garage door And 6 months in Opener"
    )
    pdf.set_x(10)
    pdf.multi_cell(190, 5, warranty_text, align="C")
    
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 60, 90)
    
    # CORRECCIÓN: Resetear el margen X a 10 y usar un ancho fijo de 190 para forzar el centro
    pdf.set_x(10)
    pdf.cell(190, 10, "Thank You For Your Business", ln=1, align="C")

    return pdf.output(dest='S')

def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- INTERFAZ ---
st.title("🛠️ Henrry's Garage System")

with st.sidebar:
    st.header("⚙️ My Business Info")
    my_address = st.text_area("Your Header Info", "31411 Terri Ln, Magnolia, TX 77354\n(661) 648-6043 | alemanperez99@gmail.com")
    my_payable = st.text_input("Payable to", "Henrry Perez")

tab1, tab2 = st.tabs(["🆕 Create Invoice", "📜 Invoice History"])

with tab1:
    with st.container():
        st.subheader("👤 Invoice & Client Details")
        c1, c2, c3 = st.columns([1, 2, 1])
        inv_no = c1.text_input("Invoice #")
        c_name = c2.text_input("Client Name")
        due_d = c3.date_input("Due Date")

    st.subheader("📍 Project Addresses")
    for i, addr in enumerate(st.session_state.address_rows):
        col_in, col_del = st.columns([0.9, 0.1])
        st.session_state.address_rows[i] = col_in.text_input(f"Address {i+1}", value=addr, key=f"addr_{i}")
        if col_del.button("🗑️", key=f"del_a_{i}"):
            st.session_state.address_rows.pop(i)
            st.rerun()
    if st.button("➕ Add Address"):
        st.session_state.address_rows.append("")
        st.rerun()

    st.subheader("📦 Services")
    current_total = 0
    for i, serv in enumerate(st.session_state.service_rows):
        d, q, p, x = st.columns([0.5, 0.15, 0.25, 0.1])
        st.session_state.service_rows[i]['desc'] = d.text_input("Desc", value=serv['desc'], key=f"d_{i}")
        st.session_state.service_rows[i]['qty'] = q.number_input("Qty", min_value=1, value=serv['qty'], key=f"q_{i}")
        st.session_state.service_rows[i]['price'] = p.number_input("Price", min_value=0.0, value=serv['price'], key=f"p_{i}")
        current_total += st.session_state.service_rows[i]['qty'] * st.session_state.service_rows[i]['price']
        if x.button("🗑️", key=f"del_s_{i}"):
            st.session_state.service_rows.pop(i)
            st.rerun()
    
    st.info(f"### **Total: ${current_total:,.2f}**")
    if st.button("➕ Add Service"):
        st.session_state.service_rows.append({"desc": "", "qty": 1, "price": 0.0})
        st.rerun()

    if st.button("💾 SAVE & GENERATE"):
        hoy = datetime.now().strftime("%m/%d/%Y")
        try:
            with conn.session as session:
                all_addrs = " | ".join([a for a in st.session_state.address_rows if a.strip()])
                res = session.execute(text("INSERT INTO invoices (inv_num, cliente, project_addr, total_amount, fecha_hoy) VALUES (:inv, :clie, :proj, :total, :hoy) RETURNING id"), 
                                    {"inv": inv_no, "clie": c_name, "proj": all_addrs, "total": float(current_total), "hoy": hoy})
                invoice_id = res.fetchone()[0]
                for s in st.session_state.service_rows:
                    if s['desc'].strip():
                        session.execute(text("INSERT INTO invoice_items (invoice_id, description, quantity, unit_price) VALUES (:iid, :desc, :qty, :prc)"),
                                        {"iid": invoice_id, "desc": s['desc'], "qty": int(s['qty']), "prc": float(s['price'])})
                session.commit()
            
            pdf_info = {"emisor_info": my_address, "client_name": c_name, "inv_num": inv_no, "date": hoy, "due_date": due_d.strftime("%m/%d/%Y"), "payable_to": my_payable}
            pdf_bytes = generate_pdf(pdf_info, st.session_state.service_rows, st.session_state.address_rows)
            
            st.success("Saved! You can view it below or check the History tab.")
            st.download_button("📥 Download PDF", data=bytes(pdf_bytes), file_name=f"Invoice_{inv_no}.pdf", mime="application/pdf")
            st.subheader("📄 Preview")
            display_pdf(bytes(pdf_bytes))
        except Exception as e:
            st.error(f"Error: {e}")

# --- PESTAÑA DE HISTORIAL ---
with tab2:
    st.subheader("📜 Saved Invoices")
    try:
        # CORRECCIÓN: Agregar ttl=0 apaga el caché, obligando a Streamlit a actualizar la lista de inmediato.
        history_df = conn.query("SELECT id, inv_num, cliente, total_amount, fecha_hoy, project_addr FROM invoices ORDER BY id DESC", ttl=0)
        
        if not history_df.empty:
            for index, row in history_df.iterrows():
                with st.expander(f"📅 {row['fecha_hoy']} | Inv: {row['inv_num']} | Client: {row['cliente']}"):
                    st.write(f"**Total:** ${row['total_amount']:,.2f}")
                    st.write(f"**Addresses:** {row['project_addr']}")
                    
                    if st.button(f"Re-Generate PDF #{row['inv_num']}", key=f"re_{row['id']}"):
                        # También le decimos a las sub-consultas que ignoren el caché
                        items_df = conn.query(f"SELECT description as desc, quantity as qty, unit_price as price FROM invoice_items WHERE invoice_id = {row['id']}", ttl=0)
                        
                        items_list = items_df.to_dict('records')
                        addr_list = str(row['project_addr']).split(" | ")
                        
                        pdf_info_re = {
                            "emisor_info": my_address, "client_name": row['cliente'], "inv_num": row['inv_num'],
                            "date": row['fecha_hoy'], "due_date": row['fecha_hoy'], "payable_to": my_payable
                        }
                        re_pdf_bytes = generate_pdf(pdf_info_re, items_list, addr_list)
                        st.download_button("📥 Click here to Download", data=bytes(re_pdf_bytes), file_name=f"Invoice_{row['inv_num']}.pdf", key=f"dl_{row['id']}")
        else:
            st.info("No invoices found.")
    except Exception as e:
        st.error(f"Error loading history: {e}")
