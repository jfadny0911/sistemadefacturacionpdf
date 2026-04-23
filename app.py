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
        # Colores definidos (Adaptados del diseño anterior para mantener coherencia)
        azul_oscuro = (30, 60, 90) 
        naranja = (220, 130, 50)  
        gris_fondo = (245, 245, 245)

        # 1. ENCABEZADO SUPERIOR (Dos bloques azul oscuro)
        self.set_fill_color(*azul_oscuro)
        # Bloque izquierdo para el logo e info del cliente
        self.rect(0, 0, 105, 50, 'F')
        # Bloque derecho para "INVOICE" y detalles
        self.rect(105, 0, 105, 50, 'F')

        # -- Bloque Izquierdo --
        # Logo
        try:
            self.image("logo.png", 12, 8, 33) 
            self.set_xy(52, 12) 
        except:
            self.set_xy(15, 12)
        # Información de la empresa (adaptada del diseño anterior)
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "HENRRY'S GARAGE", ln=True)
        
        self.set_font("Helvetica", "B", 11)
        self.set_x(52 if self.get_x() > 20 else 15)
        self.cell(0, 7, "Invoice To:", ln=True)
        self.set_font("Helvetica", "", 10)
        self.set_x(52 if self.get_x() > 20 else 15)
        self.cell(0, 5, data['client_name'].upper(), ln=True)
        # Direcciones (puede ser larga, usar multi_cell)
        self.set_x(52 if self.get_x() > 20 else 15)
        self.multi_cell(0, 5, data['project_addr'], align='L')

        # -- Bloque Derecho --
        self.set_xy(115, 12)
        # "INVOICE" en naranja grande
        self.set_font("Helvetica", "B", 42)
        self.set_text_color(*naranja)
        self.cell(0, 15, "INVOICE", ln=True, align="L")
        
        # Detalles de la factura (Inv #, Fecha Venc, Fecha Inv)
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

        # 2. BARRA HORIZONTAL NARANJA CON ICONO Y DIRECCIÓN
        self.set_fill_color(*naranja)
        self.rect(0, 50, 210, 15, 'F')
        self.set_xy(15, 50)
        # Icono de ubicación (simulado con un círculo)
        self.set_draw_color(*azul_oscuro)
        self.set_fill_color(*azul_oscuro)
        self.circle(18, 57.5, 2, 'F')
        # Dirección de la empresa (Del sidebar)
        self.set_xy(25, 55)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*azul_oscuro)
        self.cell(0, 5, data['emisor_info_one_line'])

        # 3. DETALLES DE PAGO Y CONTACTO
        self.set_y(70)
        # Columna izquierda: Información de contacto
        contacto_x = 15
        self.set_x(contacto_x)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        label_w_contact = 25
        # Enviar emisor_info como lineas separadas para Phone, Email, Address
        emisor_lines = data['emisor_info'].split('\n')
        # Adaptar las líneas si es posible (asumiendo formato del sidebar original)
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

        # Columna derecha: Método de Pago
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
        self.cell(0, 5, data['inv_num'], ln=True) # Usamos Inv Num como ejemplo

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

        self.set_y(100) # Espacio para la tabla

def generate_pdf(data, services, addresses):
    # Combinar direcciones para el PDF
    project_addr_str = "\n".join([a for a in addresses if a.strip()])
    
    pdf = ModernInvoice()
    pdf.add_page()
    # Preparar datos extendidos para el encabezado
    header_data = data.copy()
    header_data['project_addr'] = project_addr_str
    # Convertir dirección del emisor en una sola línea para la barra naranja
    emisor_lines = data['emisor_info'].split('\n')
    header_data['emisor_info_one_line'] = emisor_lines[0] + " | " + " ".join(emisor_lines[1:])
    
    pdf.draw_header(header_data)
    
    # 4. TABLA DE SERVICIOS PROFESIONAL
    pdf.set_y(100)
    
    # Cabecera de la tabla (Azul oscuro, texto blanco bold)
    azul_oscuro = (30, 60, 90)
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
        # padding para DESCRIPTION
        pdf.set_xy(current_x if col['name'] != "DESCRIPTION" else current_x+2, 100)
        pdf.cell(col['w'] if col['name'] != "DESCRIPTION" else col['w']-2, 10, col['name'], fill=True, align=align)
        current_x += col['w']
    pdf.ln()

    # Filas de datos
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
            
            # Dibujar celda con borde inferior
            pdf.set_xy(current_x, current_y)
            # Altura de celda mayor para multi_cell si es necesario para descripción
            pdf.cell(col['w'], 10, "", border='B')
            # Texto dentro de la celda
            pdf.set_xy(current_x + (2 if col['name'] == "DESCRIPTION" else 0), current_y)
            pdf.cell(col['w'] - (2 if col['name'] == "DESCRIPTION" else 0), 10, val, align=align)
            
            current_x += col['w']
        
        pdf.ln()
        current_y += 10
        if current_y > 250: # Salto de página simple
            pdf.add_page()
            current_y = 60 # Reiniciar Y después del header en nueva página (se puede mejorar)
            pdf.set_y(current_y)
            # Re-dibujar cabecera de tabla opcionalmente

    # 5. TOTALES, TÉRMINOS Y CONDICIONES, GRACIAS
    # Totales (A la derecha, fondo gris claro con Total en azul)
    pdf.set_y(current_y + 10)
    totals_x = 115
    pdf.set_x(totals_x)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 100, 100)
    
    # Filas de totales (Sub-total, Discount, Tax)
    labels = ["Sub-total:", "Discount:", "Tax (0%):"]
    vals = [f"${total_gral:,.2f}", "$0.00", "$0.00"]
    
    totals_y = current_y + 10
    total_col_w = 40
    val_col_w = 40
    
    # Usamos celdas simples para Sub-total, Discount, Tax
    # Estilizamos el cuadro de totales completo con fondo gris claro
    gris_fondo = (245, 245, 245)
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

    # Fila de TOTAL (Fondo azul oscuro, texto blanco)
    pdf.set_xy(totals_x - 5, totals_y+21)
    pdf.set_fill_color(*azul_oscuro)
    pdf.cell(90, 12, "", fill=True)
    
    pdf.set_xy(totals_x, totals_y+21)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(total_col_w, 12, "Total:", align='R')
    # Valor del TOTAL grande
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(val_col_w, 12, f"${total_gral:,.2f}", align='R')

    # Términos y Condiciones (A la izquierda)
    terms_y = current_y + 10
    pdf.set_y(terms_y)
    pdf.set_x(15)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*azul_oscuro)
    pdf.cell(0, 7, "TERM AND CONDITIONS", ln=True)
    
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    # Reemplazamos la garantía original con el texto de términos y condiciones de la imagen
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
    
    # Gracias (Abajo, centrado)
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*azul_oscuro)
    pdf.cell(0, 10, "THANK YOU FOR YOUR BUSINESS", ln=True, align="C")

    # 6. PIE DE PÁGINA (Datos de contacto y firma) Adaptado al diseño de la imagen
    # Datos de contacto con iconos (utilizando labels para recrear estructura)
    footer_x = 15
    pdf.set_x(footer_x)
    
    # Enviar emisor_info como lineas separadas para Phone, Email, Address
    emisor_lines = data['emisor_info'].split('\n')
    # Adaptar las líneas si es posible (asumiendo formato del sidebar original)
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

    # Firma (A la derecha)
    signature_x = 115
    pdf.set_xy(signature_x, pdf.get_y() - (5 * 2)) # Ajustar Y basado en multi_cell
    
    pdf.set_draw_color(*azul_oscuro)
    pdf.set_line_width(0.5)
    # Línea de firma
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
    # Franja naranja
    pdf.rect(0, 285, 210, 3, 'F')
    # Franja azul oscuro encima
    pdf.set_fill_color(*azul_oscuro)
    pdf.rect(0, 280, 210, 5, 'F')

    return pdf.output(dest='S')

def display_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    # Usamos un objeto embebido que funciona mejor en Chrome/Safari
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

# --- PESTAÑA DE HISTORIAL CORREGIDA ---
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
