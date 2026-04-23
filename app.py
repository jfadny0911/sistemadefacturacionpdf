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

# --- CLASE PDF PROFESIONAL CON NUEVO DISEÑO ---
class ModernInvoice(FPDF):
    def draw_header(self, data):
        # Colores definidos
        azul_oscuro = (30, 60, 90) 
        naranja = (220, 130, 50)  

        # 1. ENCABEZADO SUPERIOR
        self.set_fill_color(*azul_oscuro)
        self.rect(0, 0, 105, 50, 'F')
        self.rect(105, 0, 105, 50, 'F')

        # -- Bloque Izquierdo --
        try:
            self.image("logo.png", 12, 8, 33) 
            self.set_xy(52, 12) 
        except:
            self.set_xy(15, 12)
            
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "HENRRY'S GARAGE", ln=True)
        
        self.set_font("Helvetica", "B", 11)
        self.set_x(52 if self.get_x() > 20 else 15)
        self.cell(0, 7, "Invoice To:", ln=True)
        self.set_font("Helvetica", "", 10)
        self.set_x(52 if self.get_x() > 20 else 15)
        self.cell(0, 5, data['client_name'].upper(), ln=True)
        
        self.set_x(52 if self.get_x() > 20 else 15)
        self.multi_cell(0, 5, data['project_addr'], align='L')

        # -- Bloque Derecho --
        self.set_xy(115, 12)
        self.set_font("Helvetica", "B", 42)
        self.set_text_color(*naranja)
        self.cell(0, 15, "INVOICE", ln=True, align="L")
        
        self.set_font("Helvetica", "", 10)
        self.set_text_color(255, 255, 255)
        details_x = 115
        label_w = 30
        
        self.set_xy(details_x, 32)
        self.cell(label_w, 5, "Invoice No:")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, f"#{data['inv_num']}", ln=True)

        self.set_font("Helvetica", "", 10)
        self.set_xy(details_x, 37)
        self.cell(label_w, 5, "Due Date:")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, f"{data['due_date']}", ln=True)

        self.set_font("Helvetica", "", 10)
        self.set_xy(details_x, 42)
        self.cell(label_w, 5, "Invoice Date:")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, f"{data['date']}", ln=True)

        # 2. BARRA HORIZONTAL NARANJA CON DIRECCIÓN
        self.set_fill_color(*naranja)
        self.rect(0, 50, 210, 15, 'F')
        self.set_xy(15, 50)
        
        self.set_draw_color(*azul_oscuro)
        self.set_fill_color(*azul_oscuro)
        self.circle(18, 57.5, 2, 'F')
        
        self.set_xy(25, 55)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*azul_oscuro)
        self.cell(0, 5, data['emisor_info_one_line'])

        # 3. DETALLES DE PAGO Y CONTACTO
        self.set_y(70)
        contacto_x = 15
        self.set_x(contacto_x)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        label_w_contact = 25
        
        emisor_lines = data['emisor_info'].split('\n')
        phone = ""
        email = ""
        address = ""
        for line in emisor_lines:
            if '(' in line and ')' in line and '-' in line: phone = line
            elif '@' in line: email = line
            else: address += line + " "

        self.set_xy(contacto_x, 70)
        self.cell(label_w_contact, 5, "Phone:")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, phone, ln=True)

        self.set_font("Helvetica", "", 10)
        self.set_xy(contacto_x, 75)
        self.cell(label_w_contact, 5, "Email:")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, email, ln=True)

        self.set_font("Helvetica", "", 10)
        self.set_xy(contacto_x, 80)
        self.cell(label_w_contact, 5, "Address:")
        self.set_font("Helvetica", "B", 10)
        self.multi_cell(75, 5, address.strip(), align='L')

        pago_x = 115
        self.set_xy(pago_x, 70)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*azul_oscuro)
        self.cell(0, 7, "PAYMENT METHOD", ln=True)

        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        label_w_pago = 40

        self.set_xy(pago_x, 77)
        self.cell(label_w_pago, 5, "Account No:")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, data['inv_num'], ln=True)

        self.set_font("Helvetica", "", 10)
        self.set_xy(pago_x, 82)
        self.cell(label_w_pago, 5, "Account Name:")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, data['client_name'].upper(), ln=True)

        self.set_font("Helvetica", "", 10)
        self.set_xy(pago_x, 87)
        self.cell(label_w_pago, 5, "Branch Name:")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, "HENRRY'S GARAGE", ln=True)

        self.set_y(100)

def generate_pdf(data, services, addresses):
    # Colores definidos para usar en todo el documento
    azul_oscuro = (30, 60, 90)
    naranja = (220, 130, 50)
    gris_fondo = (245, 245, 245)

    project_addr_str = "\n".join([a for a in addresses if a.strip()])
    
    pdf = ModernInvoice()
    pdf.add_page()
    
    header_data = data.copy()
    header_data['project_addr'] = project_addr_str
    emisor_lines = data['emisor_info'].split('\n')
    header_data['emisor_info_one_line'] = emisor_lines[0] + " | " + " ".join(emisor_lines[1:])
    
    pdf.draw_header(header_data)
    
    # 4. TABLA DE SERVICIOS
    pdf.set_y(100)
    pdf.set_fill_color(*azul_oscuro)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 255, 255)
    
    cols = [
        {"name": "DESCRIPTION", "w": 100},
        {"name": "UNIT PRICE", "w": 35},
        {"name": "QTY", "w": 20},
        {"name": "TOTAL", "w": 40}
    ]
    
    current_x = 15
    for col in cols:
        align = "C" if col['name'] != "DESCRIPTION" else "L"
        pdf.set_xy(current_x if col['name'] != "DESCRIPTION" else current_x+2, 100)
        pdf.cell(col['w'] if col['name'] != "DESCRIPTION" else col['w']-2, 10, col['name'], fill=True, align=align)
        current_x += col['w']
    pdf.ln()

    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 10)
    total_gral = 0
    current_y = 110
    
    for s in services:
        line_total = s['qty'] * s['price']
        total_gral += line_total
        
        current_x = 15
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
        if current_y > 250:
            pdf.add_page()
            current_y = 60
            pdf.set_y(current_y)

    # 5. TOTALES, TÉRMINOS Y CONDICIONES
    pdf.set_y(current_y + 10)
    totals_x = 115
    pdf.set_x(totals_x)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 100, 100)
    
    labels = ["Sub-total:", "Discount:", "Tax (0%):"]
    vals = [f"${total_gral:,.2f}", "$0.00", "$0.00"]
    
    totals_y = current_y + 10
    total_col_w = 40
    val_col_w = 40
    
    pdf.set_fill_color(*gris_fondo)
    pdf.rect(totals_x - 5, totals_y - 2, 90, 30, 'F')
    
    pdf.set_xy(totals_x, totals_y)
    pdf.cell(total_col_w, 7, labels[0], align='R')
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(val_col_w, 7, vals[0], align='R', ln=True)

    pdf.set_xy(totals_x, totals_y+7)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(total_col_w, 7, labels[1], align='R')
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(val_col_w, 7, vals[1], align='R', ln=True)

    pdf.set_xy(totals_x, totals_y+14)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(total_col_w, 7, labels[2], align='R')
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(val_col_w, 7, vals[2], align='R', ln=True)

    pdf.set_xy(totals_x - 5, totals_y+21)
    pdf.set_fill_color(*azul_oscuro)
    pdf.cell(90, 12, "", fill=True)
    
    pdf.set_xy(totals_x, totals_y+21)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(total_col_w, 12, "Total:", align='R')
    
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(val_col_w, 12, f"${total_gral:,.2f}", align='R')

    # Términos y Condiciones
    terms_y = current_y + 10
    pdf.set_y(terms_y)
    pdf.set_x(15)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*azul_oscuro)
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
    pdf.set_x(15)
    pdf.multi_cell(90, 5, terms_text, align="L")
    
    # Gracias
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*azul_oscuro)
    pdf.cell(0, 10, "THANK YOU FOR YOUR BUSINESS", ln=True, align="C")

    # 6. PIE DE PÁGINA (Datos de contacto y firma)
    footer_x = 15
    pdf.set_x(footer_x)
    
    emisor_lines = data['emisor_info'].split('\n')
    phone = ""
    email = ""
    address = ""
    for line in emisor_lines:
        if '(' in line and ')' in line and '-' in line: phone = line
        elif '@' in line: email = line
        else: address += line + " "

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(30, 30, 30)
    label_w_footer = 25
    
    pdf.cell(label_w_footer, 5, "Phone:")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, phone, ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(footer_x)
    pdf.cell(label_w_footer, 5, "Email:")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, email, ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(footer_x)
    pdf.cell(label_w_footer, 5, "Address:")
    pdf.set_font("Helvetica", "B", 10)
    pdf.multi_cell(75, 5, address.strip(), align='L')

    # Firma
    signature_x = 115
    pdf.set_xy(signature_x, pdf.get_y() - 10) 
    
    pdf.set_draw_color(*azul_oscuro)
    pdf.set_line_width(0.5)
    pdf.line(signature_x + 10, pdf.get_y(), 200, pdf.get_y())
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*azul_oscuro)
    pdf.set_xy(signature_x + 10, pdf.get_y() + 2)
    pdf.cell(0, 7, data['payable_to'].upper(), ln=True, align='L')
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.set_x(signature_x + 10)
    pdf.cell(0, 5, "Administrator", align='L')

    # Franjas decorativas al pie
    pdf.set_fill_color(*naranja)
    pdf.rect(0, 285, 210, 3, 'F')
    
    pdf.set_fill_color(*azul_oscuro)
    pdf.rect(0, 280, 210, 5, 'F')

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
                            "emisor_info": my_address, "client_name": row['cliente'], "inv_num": row['inv_num'],
                            "date": row['fecha_hoy'], "due_date": row['fecha_hoy'], "payable_to": my_payable
                        }
                        re_pdf_bytes = generate_pdf(pdf_info_re, items_list, addr_list)
                        st.download_button("📥 Click here to Download", data=bytes(re_pdf_bytes), file_name=f"Invoice_{row['inv_num']}.pdf", key=f"dl_{row['id']}")
        else:
            st.info("No invoices found.")
    except Exception as e:
        st.error(f"Error loading history: {e}")
