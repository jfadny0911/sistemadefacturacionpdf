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

# --- CLASE PDF (CON FOCUS EN EL CLIENTE) ---
class ModernInvoice(FPDF):
    def draw_header(self, data):
        self.azul_vivo = (22, 58, 105)    
        self.naranja_vivo = (255, 165, 0) 
        self.gris_fondo = (245, 245, 245) 

        # 1. ENCABEZADO SUPERIOR (Datos del Administrador)
        self.set_fill_color(*self.azul_vivo)
        self.rect(0, 0, 210, 45, 'F') # Altura ajustada
        
        self.set_fill_color(*self.naranja_vivo)
        self.rect(0, 0, 210, 2, 'F')

        # Logo
        try:
            self.image("logo.png", 10, 6, 36) 
        except:
            pass

        # Bloque ADMINISTRADOR (Donde pediste, debajo del logo)
        admin_x = 52 
        self.set_xy(admin_x, 8)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.cell(70, 8, "HENRRY'S GARAGE", ln=True) 
        
        # Datos de tu empresa en gris claro para que se vea elegante
        self.set_xy(admin_x, 18)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(210, 210, 210) 
        admin_info = f"{data['address']}\nPhone: {data['phone']}\nEmail: {data['email']}"
        self.multi_cell(75, 5, admin_info, align='L') 

        # Bloque INVOICE (Derecha)
        detalles_x = 135
        self.set_xy(120, 8)
        self.set_font("Helvetica", "B", 40)
        self.set_text_color(*self.naranja_vivo)
        self.cell(80, 15, "INVOICE", ln=False, align="R")
        
        self.set_text_color(255, 255, 255)
        
        self.set_xy(detalles_x, 25)
        self.set_font("Helvetica", "", 10)
        self.cell(25, 5, "Invoice No:")
        self.set_font("Helvetica", "B", 10)
        self.cell(40, 5, f"#{data['inv_num']}", align="R", ln=False)

        self.set_xy(detalles_x, 30)
        self.set_font("Helvetica", "", 10)
        self.cell(25, 5, "Due Date:")
        self.set_font("Helvetica", "B", 10)
        self.cell(40, 5, f"{data['due_date']}", align="R", ln=False)

        self.set_xy(detalles_x, 35)
        self.set_font("Helvetica", "", 10)
        self.cell(25, 5, "Invoice Date:")
        self.set_font("Helvetica", "B", 10)
        self.cell(40, 5, f"{data['date']}", align="R", ln=False)

        # 2. BARRA NARANJA (Línea divisoria limpia)
        self.set_fill_color(*self.naranja_vivo)
        self.rect(0, 45, 210, 5, 'F')
        
        self.set_fill_color(*self.azul_vivo)
        self.rect(0, 45, 8, 5, 'F')

        # 3. MEGA FOCUS EN EL CLIENTE Y PAGO
        self.set_y(58)
        cliente_x = 15
        
        # Título Invoice To en Naranja
        self.set_xy(cliente_x, 58)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*self.naranja_vivo)
        self.cell(80, 6, "INVOICE TO:", ln=True)
        
        # Nombre del cliente grande y en azul
        self.set_xy(cliente_x, 64)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*self.azul_vivo)
        self.cell(80, 6, data['client_name'].upper(), ln=True)
        
        # Dirección del cliente clara
        self.set_xy(cliente_x, 71)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(30, 30, 30)
        self.multi_cell(80, 5, data['project_addr'], align='L')

        # PAYMENT METHOD (Derecha)
        pago_x = 120
        self.set_xy(pago_x, 58)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*self.azul_vivo)
        self.cell(80, 6, "PAYMENT METHOD", ln=False)
        
        self.set_draw_color(*self.naranja_vivo)
        self.set_line_width(0.5)
        self.line(pago_x, 64, pago_x + 45, 64)

        label_pago = 30
        self.set_text_color(30, 30, 30)
        
        self.set_xy(pago_x, 67)
        self.set_font("Helvetica", "", 10)
        self.cell(label_pago, 5, "Account No:")
        self.set_font("Helvetica", "B", 10)
        self.cell(50, 5, data['inv_num'], ln=False)

        self.set_xy(pago_x, 73)
        self.set_font("Helvetica", "", 10)
        self.cell(label_pago, 5, "Account Name:")
        self.set_font("Helvetica", "B", 10)
        self.cell(50, 5, data['client_name'].upper(), ln=False)

        self.set_xy(pago_x, 79)
        self.set_font("Helvetica", "", 10)
        self.cell(label_pago, 5, "Branch Name:")
        self.set_font("Helvetica", "B", 10)
        self.cell(50, 5, "HENRRY'S GARAGE", ln=False)

def generate_pdf(data, services, addresses):
    project_addr_str = "\n".join([a for a in addresses if a.strip()])
    
    pdf = ModernInvoice()
    pdf.add_page()
    
    header_data = data.copy()
    header_data['project_addr'] = project_addr_str
    
    pdf.draw_header(header_data)
    
    # 4. TABLA DE SERVICIOS
    # Se subió a 95 para aprovechar el espacio que dejó la barra gruesa
    pdf.set_y(95)
    pdf.set_fill_color(*pdf.azul_vivo)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 255, 255)
    
    cols = [
        {"name": "DESCRIPTION", "w": 100},
        {"name": "UNIT PRICE", "w": 35},
        {"name": "QTY", "w": 20},
        {"name": "TOTAL", "w": 35}
    ]
    
    current_x = 10
    for col in cols:
        align = "C" if col['name'] != "DESCRIPTION" else "L"
        pdf.set_xy(current_x if col['name'] != "DESCRIPTION" else current_x+2, 95)
        pdf.cell(col['w'] if col['name'] != "DESCRIPTION" else col['w']-2, 10, col['name'], fill=True, align=align)
        current_x += col['w']
    pdf.ln()

    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 10)
    
    total_gral = 0
    current_y = 105
    
    for s in services:
        line_total = s['qty'] * s['price']
        total_gral += line_total
        current_x = 10
        
        for col in cols:
            val = ""
            if col['name'] == "DESCRIPTION": val = f" {s['desc']}"
            elif col['name'] == "UNIT PRICE": val = f"${s['price']:,.2f}"
            elif col['name'] == "QTY": val = str(s['qty'])
            elif col['name'] == "TOTAL": val = f"${line_total:,.2f}"
            
            align = "C" if col['name'] != "DESCRIPTION" else "L"
            
            pdf.set_xy(current_x, current_y)
            pdf.cell(col['w'], 10, "", border='B') 
            pdf.set_xy(current_x + (2 if col['name'] == "DESCRIPTION" else 0), current_y)
            pdf.cell(col['w'] - (2 if col['name'] == "DESCRIPTION" else 0), 10, val, align=align)
            
            current_x += col['w']
        
        pdf.ln()
        current_y += 10
        if current_y > 230:
            pdf.add_page()
            current_y = 20
            pdf.set_y(current_y)

    # 5. TOTALES, TÉRMINOS Y CONDICIONES
    pdf.set_y(current_y + 10)
    totals_x = 110
    
    labels = ["Sub-total:", "Discount:", "Tax (0%):"]
    vals = [f"${total_gral:,.2f}", "$0.00", "$0.00"]
    
    totals_y = current_y + 15
    total_col_w = 40
    val_col_w = 40
    
    pdf.set_fill_color(*pdf.gris_fondo)
    pdf.rect(totals_x, totals_y - 2, 90, 25, 'F')
    
    for i in range(3):
        pdf.set_xy(totals_x, totals_y + (i*7))
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(total_col_w, 7, labels[i], align='R')
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(val_col_w, 7, vals[i], align='R')

    pdf.set_fill_color(*pdf.azul_vivo)
    pdf.rect(totals_x, totals_y + 23, 90, 14, 'F')
    
    pdf.set_xy(totals_x, totals_y + 24)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(total_col_w, 12, "Total:", align='R')
    
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(val_col_w, 12, f"${total_gral:,.2f}", align='R')

    pdf.set_y(totals_y - 2)
    pdf.set_x(10)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*pdf.azul_vivo)
    pdf.cell(0, 7, "TERM AND CONDITIONS", ln=True)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    terms_text = (
        "***WARRANTY BEGINS FROM THE DATE OF THE INVOICE***\n"
        "Please send payment within 30 days of receiving this invoice. There will be a 10% "
        "interest charge per month on late invoice. For installation on a new garage "
        "door, it has a 1-year warranty on factory defects and installation by HENRRY DOORS "
        "we are not responsible for damages or bad manipulation when opening or closing "
        "the garage door And 6 months in Opener"
    )
    pdf.set_x(10)
    pdf.multi_cell(95, 5, terms_text, align="L")
    
    pdf.set_y(totals_y + 45)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*pdf.azul_vivo)
    pdf.cell(0, 10, "THANK YOU FOR YOUR BUSINESS", ln=True, align="C")

    # 6. PIE DE PÁGINA
    footer_y = 250
    
    signature_x = 130
    pdf.set_draw_color(*pdf.azul_vivo)
    pdf.set_line_width(0.5)
    pdf.line(signature_x, footer_y, 200, footer_y)
    
    pdf.set_xy(signature_x, footer_y + 2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*pdf.azul_vivo)
    pdf.cell(70, 7, data['payable_to'].upper(), ln=True, align='C')
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.set_x(signature_x)
    pdf.cell(70, 5, "Administrator", align='C')

    pdf.set_fill_color(*pdf.azul_vivo)
    pdf.rect(0, 282, 210, 15, 'F')
    
    pdf.set_fill_color(*pdf.naranja_vivo)
    pdf.rect(0, 279, 100, 3, 'F')
    pdf.rect(170, 279, 40, 3, 'F')

    return pdf.output(dest='S')

def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)

# --- INTERFAZ ---
st.title("🛠️ Henrry's Garage System")

with st.sidebar:
    st.header("⚙️ My Business Info")
    my_address = st.text_input("Address", "31411 Terri Ln, Magnolia, TX 77354")
    my_phone = st.text_input("Phone", "(661) 648-6043")
    my_email = st.text_input("Email", "alemanperez99@gmail.com")
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
            
            pdf_info = {
                "address": my_address, "phone": my_phone, "email": my_email,
                "client_name": c_name, "inv_num": inv_no, "date": hoy, 
                "due_date": due_d.strftime("%m/%d/%Y"), "payable_to": my_payable
            }
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
        history_df = conn.query("SELECT id, inv_num, cliente, total_amount, fecha_hoy, project_addr FROM invoices ORDER BY id DESC", ttl=0)
        
        if not history_df.empty:
            for index, row in history_df.iterrows():
                with st.expander(f"📅 {row['fecha_hoy']} | Inv: {row['inv_num']} | Client: {row['cliente']}"):
                    st.write(f"**Total:** ${row['total_amount']:,.2f}")
                    st.write(f"**Addresses:** {row['project_addr']}")
                    
                    if st.button(f"Re-Generate PDF #{row['inv_num']}", key=f"re_{row['id']}"):
                        items_df = conn.query(f"SELECT description as desc, quantity as qty, unit_price as price FROM invoice_items WHERE invoice_id = {row['id']}", ttl=0)
                        
                        items_list = items_df.to_dict('records')
                        addr_list = str(row['project_addr']).split(" | ")
                        
                        pdf_info_re = {
                            "address": my_address, "phone": my_phone, "email": my_email,
                            "client_name": row['cliente'], "inv_num": row['inv_num'],
                            "date": row['fecha_hoy'], "due_date": row['fecha_hoy'], "payable_to": my_payable
                        }
                        re_pdf_bytes = generate_pdf(pdf_info_re, items_list, addr_list)
                        st.download_button("📥 Click here to Download", data=bytes(re_pdf_bytes), file_name=f"Invoice_{row['inv_num']}.pdf", key=f"dl_{row['id']}")
        else:
            st.info("No invoices found.")
    except Exception as e:
        st.error(f"Error loading history: {e}")
