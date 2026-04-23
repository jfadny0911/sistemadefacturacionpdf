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

# --- CLASE PDF PROFESIONAL CON DISEÑO VIVO Y ORDENADO ---
class ModernInvoice(FPDF):
    def draw_header(self, data):
        # Colores más vivos y modernos
        self.azul_vivo = (22, 58, 105)    # Azul Navy vibrante
        self.naranja_vivo = (255, 165, 0) # Naranja brillante/vivo
        self.gris_fondo = (245, 245, 245) # Gris muy claro para fondos

        # 1. ENCABEZADO SUPERIOR (Fondo Azul Vivo)
        self.set_fill_color(*self.azul_vivo)
        self.rect(0, 0, 210, 50, 'F')
        
        # Franja decorativa muy delgada arriba
        self.set_fill_color(*self.naranja_vivo)
        self.rect(0, 0, 210, 2, 'F')

        # Logo (Fijado a la izquierda)
        try:
            self.image("logo.png", 10, 6, 36) 
        except:
            pass # Si no hay logo, no hace nada

        # Bloque de "Invoice To:" y Cliente (Separado del logo)
        cliente_x = 52 # Empieza justo después del logo
        self.set_xy(cliente_x, 8)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, "HENRRY'S GARAGE DOOR SERVICE", ln=True)
        
        self.set_xy(cliente_x, 20)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*self.naranja_vivo) # Texto naranja para resaltar
        self.cell(0, 5, "Invoice To:", ln=True)
        
        self.set_xy(cliente_x, 25)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(255, 255, 255)
        self.cell(0, 5, data['client_name'].upper(), ln=True)
        
        self.set_xy(cliente_x, 30)
        self.set_font("Helvetica", "", 9)
        # Limitamos el ancho a 60 para que no choque con la fecha
        self.multi_cell(60, 4, data['project_addr'], align='L') 

        # Bloque Derecho (Título INVOICE y Detalles)
        detalles_x = 135
        self.set_xy(120, 8)
        self.set_font("Helvetica", "B", 40)
        self.set_text_color(*self.naranja_vivo)
        self.cell(80, 15, "INVOICE", ln=True, align="R")
        
        self.set_text_color(255, 255, 255)
        
        # Invoice No.
        self.set_xy(detalles_x, 27)
        self.set_font("Helvetica", "", 10)
        self.cell(30, 5, "Invoice No:")
        self.set_font("Helvetica", "B", 10)
        self.cell(35, 5, f"#{data['inv_num']}", align="R", ln=True)

        # Due Date
        self.set_xy(detalles_x, 32)
        self.set_font("Helvetica", "", 10)
        self.cell(30, 5, "Due Date:")
        self.set_font("Helvetica", "B", 10)
        self.cell(35, 5, f"{data['due_date']}", align="R", ln=True)

        # Invoice Date
        self.set_xy(detalles_x, 37)
        self.set_font("Helvetica", "", 10)
        self.cell(30, 5, "Invoice Date:")
        self.set_font("Helvetica", "B", 10)
        self.cell(35, 5, f"{data['date']}", align="R", ln=True)

        # 2. BARRA NARANJA VIVA (Dirección Emisor)
        self.set_fill_color(*self.naranja_vivo)
        self.rect(0, 50, 210, 12, 'F')
        
        # Detalle de diseño: Cuadrito azul oscuro al inicio de la barra naranja
        self.set_fill_color(*self.azul_vivo)
        self.rect(0, 50, 8, 12, 'F')

        self.set_xy(15, 53)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*self.azul_vivo) # Letra azul sobre fondo naranja
        self.cell(0, 6, data['emisor_info_one_line'])

        # 3. DETALLES DE CONTACTO Y PAGO (Ordenados)
        self.set_y(70)
        contacto_x = 15
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        label_w = 22
        
        # Extraer teléfono, email y dirección limpiamente
        emisor_lines = data['emisor_info'].split('\n')
        phone = ""
        email = ""
        address = ""
        for line in emisor_lines:
            if '(' in line and ')' in line and '-' in line: phone = line
            elif '@' in line: email = line
            else: address += line + " "

        self.set_xy(contacto_x, 70)
        self.cell(label_w, 5, "Phone:")
        self.set_font("Helvetica", "B", 10)
        self.cell(60, 5, phone, ln=True)

        self.set_font("Helvetica", "", 10)
        self.set_xy(contacto_x, 76)
        self.cell(label_w, 5, "Email:")
        self.set_font("Helvetica", "B", 10)
        self.cell(60, 5, email, ln=True)

        self.set_font("Helvetica", "", 10)
        self.set_xy(contacto_x, 82)
        self.cell(label_w, 5, "Address:")
        self.set_font("Helvetica", "B", 10)
        self.multi_cell(75, 5, address.strip(), align='L')

        # Bloque Payment Method
        pago_x = 120
        self.set_xy(pago_x, 70)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*self.azul_vivo)
        self.cell(0, 6, "PAYMENT METHOD", ln=True)
        
        # Línea sutil debajo del título
        self.set_draw_color(*self.naranja_vivo)
        self.set_line_width(0.5)
        self.line(pago_x, 76, pago_x + 45, 76)

        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        label_pago = 35

        self.set_xy(pago_x, 79)
        self.cell(label_pago, 5, "Account No:")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, data['inv_num'], ln=True)

        self.set_font("Helvetica", "", 10)
        self.set_xy(pago_x, 85)
        self.cell(label_pago, 5, "Account Name:")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, data['client_name'].upper(), ln=True)

        self.set_font("Helvetica", "", 10)
        self.set_xy(pago_x, 91)
        self.cell(label_pago, 5, "Branch Name:")
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, "HENRRY'S GARAGE", ln=True)

def generate_pdf(data, services, addresses):
    project_addr_str = "\n".join([a for a in addresses if a.strip()])
    
    pdf = ModernInvoice()
    pdf.add_page()
    
    header_data = data.copy()
    header_data['project_addr'] = project_addr_str
    emisor_lines = data['emisor_info'].split('\n')
    header_data['emisor_info_one_line'] = emisor_lines[0] + " | " + " ".join(emisor_lines[1:])
    
    pdf.draw_header(header_data)
    
    # 4. TABLA DE SERVICIOS (Diseño limpio y vivo)
    pdf.set_y(105)
    pdf.set_fill_color(*pdf.azul_vivo)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 255, 255)
    
    cols = [
        {"name": "DESCRIPTION", "w": 100},
        {"name": "UNIT PRICE", "w": 35},
        {"name": "QTY", "w": 20},
        {"name": "TOTAL", "w": 35} # Anchos ajustados para sumar 190
    ]
    
    current_x = 10
    for col in cols:
        align = "C" if col['name'] != "DESCRIPTION" else "L"
        pdf.set_xy(current_x if col['name'] != "DESCRIPTION" else current_x+2, 105)
        pdf.cell(col['w'] if col['name'] != "DESCRIPTION" else col['w']-2, 10, col['name'], fill=True, align=align)
        current_x += col['w']
    pdf.ln()

    # Configuración de líneas de la tabla
    pdf.set_draw_color(200, 200, 200) # Bordes grises sutiles
    pdf.set_line_width(0.3)
    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 10)
    
    total_gral = 0
    current_y = 115
    
    for s in services:
        line_total = s['qty'] * s['price']
        total_gral += line_total
        current_x = 10
        
        # Dibuja la fila
        for col in cols:
            val = ""
            if col['name'] == "DESCRIPTION": val = f" {s['desc']}"
            elif col['name'] == "UNIT PRICE": val = f"${s['price']:,.2f}"
            elif col['name'] == "QTY": val = str(s['qty'])
            elif col['name'] == "TOTAL": val = f"${line_total:,.2f}"
            
            align = "C" if col['name'] != "DESCRIPTION" else "L"
            
            pdf.set_xy(current_x, current_y)
            pdf.cell(col['w'], 10, "", border='B') # Borde inferior
            pdf.set_xy(current_x + (2 if col['name'] == "DESCRIPTION" else 0), current_y)
            pdf.cell(col['w'] - (2 if col['name'] == "DESCRIPTION" else 0), 10, val, align=align)
            
            current_x += col['w']
        
        pdf.ln()
        current_y += 10
        if current_y > 230: # Salto de página
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
    
    # Cuadro gris para subtotales
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

    # Cuadro Azul Vivo para el TOTAL
    pdf.set_fill_color(*pdf.azul_vivo)
    pdf.rect(totals_x, totals_y + 23, 90, 14, 'F')
    
    pdf.set_xy(totals_x, totals_y + 24)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(total_col_w, 12, "Total:", align='R')
    
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(val_col_w, 12, f"${total_gral:,.2f}", align='R')

    # Términos y Condiciones
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
    
    # Gracias Centrado
    pdf.set_y(totals_y + 45)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*pdf.azul_vivo)
    pdf.cell(0, 10, "THANK YOU FOR YOUR BUSINESS", ln=True, align="C")

    # 6. PIE DE PÁGINA Y FIRMA (Diseño Geométrico Fijo)
    footer_y = 250
    
    # Firma a la Derecha
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

    # Diseño Geométrico Inferior
    pdf.set_fill_color(*pdf.azul_vivo)
    pdf.rect(0, 282, 210, 15, 'F')
    
    # Franja naranja sobresaliendo en la esquina
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
