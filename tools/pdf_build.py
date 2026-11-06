"""Genera el PDF «Tablero de control APN · Trienio nov 2023 – oct 2026» (láminas 16:9, formato del Informe de deudas)."""
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import ImageReader
from PIL import Image

W, H = 960, 540
FD = '/home/claude/work/fonts/'
for n in ['Regular', 'Bold', 'Italic', 'Black', 'Semibold', 'BoldItalic']:
    pdfmetrics.registerFont(TTFont('Lato-' + n, FD + f'Lato-{n}.ttf'))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily('Lato', normal='Lato-Regular', bold='Lato-Bold', italic='Lato-Italic', boldItalic='Lato-BoldItalic')

COVER = HexColor('#1C3F1D'); G = HexColor('#2C5F2D'); G2 = HexColor('#4E8A45'); LG = HexColor('#8BBF6A')
CARD = HexColor('#F5F9EF'); CARD2 = HexColor('#EDF4E4'); SUB = HexColor('#DCE9CE'); INK = HexColor('#26302A')
MUTED = HexColor('#6E7A68'); EYE = HexColor('#5E8E4E'); LINE = HexColor('#C9D8BC'); RED = HexColor('#A6472B'); GREY = HexColor('#B8C0B2')

T = json.load(open('/home/claude/work/tables.json'))
MD = json.load(open('/home/claude/work/md.json'))
OUT = '/home/claude/work/out/Tablero_de_control_APN_nov23-oct26.pdf'
SRC = 'Fuente: elaboración propia con datos disponibles en ReNaRI.'
SRCX = 'Fuente: elaboración propia sobre los tableros de accesos, cobranzas y deuda (ReNaRI), al 31 de octubre de 2026.'


def nf(v, d=0):
    s = f"{abs(v):,.{d}f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('−' if v < 0 and round(abs(v), d) != 0 else '') + s


def S(name, **kw):
    base = dict(fontName='Lato-Regular', fontSize=10.5, leading=14.5, textColor=INK, alignment=TA_JUSTIFY)
    base.update(kw)
    return ParagraphStyle(name, **base)


BODY = S('body')
BODY_S = S('bodys', fontSize=9.5, leading=13)
NOTE = S('note', fontSize=8.6, leading=11.8, textColor=INK, alignment=TA_LEFT)

c = canvas.Canvas(OUT, pagesize=(W, H))
c.setTitle('Tablero de control APN · Trienio noviembre 2023 – octubre 2026')
c.setAuthor('Dirección Nacional de Uso Público · Dirección de Concesiones')
c.setSubject('Accesos, cobranzas y deuda de prestadores turísticos — ciclos nov–oct, pesos de octubre de 2026')
PAGE = [0]


def eyebrow(text, x=50, y=H - 40, color=EYE):
    c.setFont('Lato-Bold', 6.6); c.setFillColor(color)
    c.drawString(x, y, '  '.join(' '.join(w) for w in text.upper().split(' ')).replace('   ', '  '))


def spaced(text):
    return ' '.join(text.upper())


def header(eye, title, sub=None):
    c.setFont('Lato-Bold', 6.6); c.setFillColor(EYE)
    c.drawString(50, H - 40, spaced(eye))
    c.setFont('Lato-Bold', 23); c.setFillColor(G)
    c.drawString(50, H - 72, title)
    if sub:
        c.setFont('Lato-Italic', 10); c.setFillColor(MUTED)
        c.drawString(50, H - 92, sub)


def footer(src=SRC):
    c.setFont('Lato-Italic', 6.6); c.setFillColor(MUTED)
    c.drawString(50, 30, src)
    c.setFont('Lato-Regular', 6.6)
    c.drawRightString(W - 50, 30, f'Tablero de control APN · nov 2023 – oct 2026 · {PAGE[0]}')


def newpage():
    if PAGE[0]:
        c.showPage()
    PAGE[0] += 1


def para(text, x, ytop, w, style=BODY):
    p = Paragraph(text, style)
    _, h = p.wrap(w, 1000)
    p.drawOn(c, x, ytop - h)
    return h


def card(x, y, w, h, big, small, dark=False, bigsize=24):
    c.setFillColor(G if dark else CARD); c.setStrokeColor(LINE if not dark else G)
    c.roundRect(x, y, w, h, 5, stroke=0 if dark else 1, fill=1)
    c.setFillColor(white if dark else G); c.setFont('Lato-Bold', bigsize)
    c.drawCentredString(x + w / 2, y + h / 2 + 2, big)
    st = S('cs', fontSize=7.2, leading=9.2, textColor=white if dark else MUTED, alignment=TA_CENTER)
    p = Paragraph(small, st); _, ph = p.wrap(w - 20, 100)
    p.drawOn(c, x + 10, y + h / 2 - 8 - ph)


def notebox(x, ytop, w, text):
    p = Paragraph(text, NOTE); _, ph = p.wrap(w - 20, 400)
    h = ph + 16
    c.setFillColor(CARD); c.setStrokeColor(LINE); c.roundRect(x, ytop - h, w, h, 4, stroke=1, fill=1)
    p.drawOn(c, x + 10, ytop - h + 8)
    return h


def table(rows, colw, x, ytop, *, fs=8, rh=21, align=None, sub_rows=(), tot_rows=(), bold_cols=(), zebra=True, wrap_first=False):
    """rows[0] = encabezado. sub_rows/tot_rows = índices de fila."""
    hdr = [Paragraph(f'<font name="Lato-Bold" color="#FFFFFF">{h.upper()}</font>', S('h', fontSize=fs - 1, leading=fs + 1, alignment=(0 if i == 0 or (align and align[i] == 'L') else 2))) for i, h in enumerate(rows[0])]
    data = [hdr]
    for r in rows[1:]:
        data.append(list(r))
    t = Table(data, colWidths=colw, rowHeights=[rh + 2] + [rh] * (len(rows) - 1))
    st = [('FONT', (0, 1), (-1, -1), 'Lato-Regular', fs), ('TEXTCOLOR', (0, 1), (-1, -1), INK),
          ('BACKGROUND', (0, 0), (-1, 0), G), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
          ('ALIGN', (1, 0), (-1, -1), 'RIGHT'), ('ALIGN', (0, 0), (0, -1), 'LEFT'),
          ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8)]
    if align:
        for i, a in enumerate(align):
            if a == 'L':
                st.append(('ALIGN', (i, 0), (i, -1), 'LEFT'))
            if a == 'C':
                st.append(('ALIGN', (i, 0), (i, -1), 'CENTER'))
    if zebra:
        for i in range(1, len(rows)):
            if i % 2 == 0 and i not in sub_rows and i not in tot_rows:
                st.append(('BACKGROUND', (0, i), (-1, i), CARD))
    for i in sub_rows:
        st += [('BACKGROUND', (0, i), (-1, i), SUB), ('FONT', (0, i), (-1, i), 'Lato-Bold', fs), ('TEXTCOLOR', (0, i), (-1, i), G)]
    for i in tot_rows:
        st += [('BACKGROUND', (0, i), (-1, i), G), ('FONT', (0, i), (-1, i), 'Lato-Bold', fs), ('TEXTCOLOR', (0, i), (-1, i), white)]
    for j in bold_cols:
        st.append(('FONT', (j, 1), (j, -1), 'Lato-Bold', fs))
    t.setStyle(TableStyle(st))
    w, h = t.wrap(0, 0)
    t.drawOn(c, x, ytop - h)
    return h


def md_rows(key, strip_bold=True):
    """Convierte una tabla markdown de md.json en filas (lista de listas)."""
    lines = [l for l in MD[key].split('\n') if l.strip()]
    out = []
    for i, l in enumerate(lines):
        if i == 1:
            continue
        cells = [x.strip() for x in l.strip().strip('|').split('|')]
        if strip_bold:
            cells = [x.replace('**', '') for x in cells]
        out.append(cells)
    return out


def logo_disc(cx, cy, r):
    """Logo institucional sobre disco blanco, recortado en círculo: sin recuadros de fondo."""
    im = Image.open('/home/claude/work/assets/logo.png').convert('RGBA')
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    flat = bg.convert('RGB')
    c.saveState()
    c.setFillColor(white); c.circle(cx, cy, r, stroke=0, fill=1)
    p = c.beginPath(); p.circle(cx, cy, r * 0.985); c.clipPath(p, stroke=0, fill=0)
    s = r * 2 * 0.93
    c.drawImage(ImageReader(flat), cx - s / 2, cy - s / 2, s, s)
    c.restoreState()


# ---------------------------------------------------------------- datos derivados
t1 = T['t1']; t2 = T['t2']; t3 = T['t3']; t4 = T['t4']; t5 = T['t5']; t6 = T['t6']; t9 = T['t9']; D = T['deu']

# ================================================================ 1. PORTADA
newpage()
c.setFillColor(COVER); c.rect(0, 0, W, H, stroke=0, fill=1)
logo_disc(190, 270, 92)
c.setFillColor(LG); c.setFont('Lato-Bold', 7.5); c.drawString(375, 365, spaced('Administración de Parques Nacionales'))
c.setFillColor(HexColor('#D9E6CF')); c.setFont('Lato-Regular', 9.5)
c.drawString(375, 345, 'Dirección Nacional de Uso Público'); c.drawString(375, 328, 'Dirección de Concesiones')
c.setFillColor(white); c.setFont('Lato-Bold', 30)
c.drawString(375, 270, 'TABLERO DE CONTROL APN')
c.setFont('Lato-Bold', 17); c.drawString(375, 243, 'ACCESOS, COBRANZAS Y DEUDA')
c.setFillColor(LG); c.setFont('Lato-Italic', 11)
c.drawString(375, 205, 'Trienio noviembre 2023 – octubre 2026 · deuda al 31 de octubre de 2026')
c.setFillColor(HexColor('#B9CDB0')); c.setFont('Lato-Regular', 8.5)
c.drawString(375, 186, 'Flujos en pesos constantes de octubre de 2026 (CER) · deuda en pesos nominales y en dólares a $ 1.550')

# ================================================================ 2. UNIVERSO
newpage()
header('Tablero de control', 'Universo relevado y criterio de corte')
y = H - 120
for txt in [
    'Este tablero consolida tres fuentes de la Administración disponibles en ReNaRI: la venta de accesos de 11 dependencias, la cobranza de prestadores y demás pagadores, y la deuda exigible de prestadores turísticos al 31 de octubre de 2026.',
    'Los flujos se comparan en tres ciclos de doce meses, de noviembre a octubre: <b>nov 23–oct 24, nov 24–oct 25 y nov 25–oct 26</b>. La deuda es un stock al cierre del último ciclo.',
    f'En el último ciclo se emitieron {t2[3]["t"]} tickets, que dejaron $ 54.295,9 millones netos de comisiones. La cobranza a prestadores turísticos sumó $ 27.049,2 millones, ambos en pesos de octubre de 2026.',
    'La deuda neta exigible asciende a $ 1.317,9 millones. La deuda bruta, $ 1.507,0 millones, equivale al 5,6% de la cobranza anual a prestadores.']:
    y -= para(txt, 50, y, 520) + 10
card(610, 372, 300, 70, '$ 54.296 M', 'ingreso neto de accesos nov 25–oct 26 · −11,0% interanual', dark=True)
card(610, 292, 300, 70, '$ 27.049 M', 'cobranza a prestadores turísticos · −18,6% en el trienio')
card(610, 212, 300, 70, '$ 1.317,9 M', 'deuda neta exigible al 31/10/2026 · −4,4% frente a septiembre')
card(610, 132, 300, 70, '3,71 M', 'tickets de acceso en el último ciclo · +8,6% en el trienio')
footer()

# ================================================================ 3. NOTA METODOLÓGICA
newpage()
header('Nota metodológica', 'Criterios de medición y comparabilidad')
rows = [['Fuente', 'Qué mide', 'Período usado', 'Cobertura'],
        ['Accesos', 'Tickets, días de visita, ingreso neto, comisiones e ingreso teórico', 'nov 2023 – oct 2026', '11 dependencias · 158.215 registros diarios'],
        ['Cobranzas', 'Pagos de prestadores y demás pagadores', 'nov 2023 – oct 2026', '3 universos · 250 mayores pagadores'],
        ['Deuda', 'Capital, intereses y pagos a cuenta', 'Corte al 31/10/2026', '33 dependencias · 3.904 deudores · 11.035 comprob.']]
table(rows, [80, 300, 120, 360], 50, H - 105, fs=8, rh=20, align=['L', 'L', 'L', 'L'])
for k, u in enumerate(['https://ffa-argentina.github.io/APN_Estadistica_Accesos/', 'https://ffa-argentina.github.io/ingresos-APN/', 'https://ffa-argentina.github.io/APN_Informe_Deudores/']):
    yy0 = H - 105 - 22 - (k + 1) * 20
    c.linkURL(u, (50, yy0, 910, yy0 + 20), relative=0)
c.setFont('Lato-Italic', 7.5); c.setFillColor(MUTED)
c.drawString(50, H - 105 - 22 - 3 * 20 - 12, 'Cada fila enlaza al tablero web de origen, con su informe PDF: ffa-argentina.github.io/APN_Estadistica_Accesos · /ingresos-APN · /APN_Informe_Deudores')
y = H - 218
items = [
    ('Ciclos.', 'Doce meses de noviembre a octubre, contados hacia atrás desde el 31/10/2026. «Var. i.a.» compara el último ciclo con el anterior; «trienal», el último con el primero. Si el ciclo base no llega a la décima parte del comparado, la variación se informa como «s/base».'),
    ('Pesos de octubre de 2026.', 'Los tableros ya expresan los flujos en pesos constantes al 31/10/2026 (cada importe diario × CER del cierre, 862,80 / CER del día). Se usan sin factor adicional; la deuda, en pesos nominales al 31/10/2026, queda en la misma moneda.'),
    ('Dólares.', 'Accesos y cobranzas, a la cotización de cada día: blue hasta el 12/12/2023 y oficial minorista vendedor desde el 13/12/2023. Deuda: paridad de referencia de $ 1.550, la del informe de deudas.'),
    ('Universos de cobranza.', 'Concesionarios y permisionarios (42 con DDJJ) dentro de prestadores turísticos, y éstos dentro de todos los pagos. La cifra principal es prestadores turísticos. Se excluyen los medios electrónicos, registrados sólo hasta julio de 2025.'),
    ('Deuda.', 'Comprobantes vencidos al 31/10/2026 con saldo impago, con intereses a tasa activa del BNA desde el vencimiento. La deuda neta descuenta pagos a cuenta conciliados.'),
    ('Deuda / cobranza.', 'Se calcula sobre la cobranza en pesos de octubre de 2026. El informe de cobranzas usa pesos corrientes y obtiene cocientes algo mayores (4,6% y 1,7%, contra 4,0% y 1,4% aquí).'),
    ('Accesos y cobranzas no se suman.', 'Provienen de sistemas distintos y «todos los pagos» puede incluir importes vinculados a accesos.')]
colx = [50, 495]; yy = [y, y]
for i, (b, t) in enumerate(items):
    k = 0 if i < 4 else 1
    yy[k] -= para(f'<font name="Lato-Bold" color="#2C5F2D">{b}</font> {t}', colx[k], yy[k], 415, BODY_S) + 8
footer()

# ================================================================ 4. PRINCIPALES OBSERVACIONES
newpage()
header('Principales observaciones', 'Más visitas, menos ingreso real por visita')
card(50, 345, 200, 85, '+8,6%', 'tickets entre el primer y el último ciclo', dark=True, bigsize=26)
card(265, 345, 200, 85, '−11,0%', 'ingreso neto real de accesos frente al ciclo anterior', bigsize=26)
card(480, 345, 200, 85, '−18,6%', 'cobranza real a prestadores en el trienio', bigsize=26)
card(695, 345, 215, 85, '5,6%', 'deuda bruta sobre la cobranza anual a prestadores', bigsize=26)
y = 325
for b, t in [
    ('Accesos.', 'Los tickets de no residentes subieron 24,6% interanual y los de residentes cayeron 16,1%. El neto por ticket de no residentes bajó de $ 36.921 a $ 27.596 (−25,3%), y eso explica la caída del ingreso neto.'),
    ('Comisiones.', 'Las tercerizadoras retuvieron el 49,0% de lo percibido en el último ciclo (44,9% en el anterior): $ 52.213 M, casi lo mismo que el ingreso neto que quedó para la APN. En Iguazú, el 61,7%.'),
    ('Cobranzas.', 'La cobranza a prestadores cayó en los tres ciclos (−18,6% en el trienio), con Tierra del Fuego en −52,8% y Glaciares en −27,4%. En dólares sube 23,1% porque el tipo de cambio aumentó menos que la inflación.'),
    ('Deuda.', 'Nahuel Huapi concentra el 42,2% y los diez mayores deudores, el 36,2%. Sólo el 25,8% es de prestadores con habilitación vigente. En Lanín la deuda equivale al 31,6% de su cobranza anual; en El Palmar, al 24,2%.')]:
    y -= notebox(50, y, 860, f'<font name="Lato-Bold" color="#2C5F2D">{b}</font> {t}') + 8
footer(SRCX)

# ================================================================ 5. TABLA I
newpage()
header('Tabla I', 'Indicadores consolidados por ciclo', 'Importes en millones de pesos de octubre de 2026, salvo indicación · Var. i.a.: último ciclo contra el anterior')
rows = md_rows('t1')
table(rows, [300, 112, 112, 112, 112, 112], 50, H - 110, fs=8.6, rh=27)
notebox(50, 150, 860, '<font name="Lato-Bold" color="#2C5F2D">Lectura.</font> El volumen crece en el trienio (tickets +8,6%, días de visita +41,5%) mientras los ingresos reales retroceden en el último ciclo: el neto de accesos cae 11,0% y la cobranza a prestadores 11,1%. Las comisiones son la única línea que sube en pesos constantes (+5,2%). En dólares el trienio luce mejor porque el tipo de cambio aumentó menos que los precios.')
footer(SRCX)

# ================================================================ 6. ACCESOS – gráfico
newpage()
header('Accesos', 'Neto −11,0% interanual: en no residentes el neto por ticket cayó 25%', 'Variación nov 25–oct 26 contra nov 24–oct 25, por categoría de visitante · pesos de octubre de 2026')
groups = []
for r in t2:
    tk = r.get('t_raw') ;
groups = [('Residentes', -16.1, -8.9, -23.5), ('No residentes', 24.6, -25.3, -6.9), ('Total', -1.8, -9.3, -11.0)]
x0, zy, k = 70, 255, 4.3
c.setStrokeColor(MUTED); c.setLineWidth(0.6); c.line(55, zy, 610, zy)
cols = [(GREY, 'Tickets'), (G2, 'Neto por ticket'), (G, 'Ingreso neto')]
for gi, (name, *vals) in enumerate(groups):
    for j, v in enumerate(vals):
        x = x0 + gi * 185 + j * 50; h = abs(v) * k
        c.setFillColor(cols[j][0]); c.rect(x, zy if v >= 0 else zy - h, 42, h, stroke=0, fill=1)
        c.setFillColor(INK); c.setFont('Lato-Bold' if j == 2 else 'Lato-Regular', 8.5)
        lbl = ('+' if v > 0 else '−') + nf(abs(v), 1) + '%'
        c.drawCentredString(x + 21, zy + h + 5 if v >= 0 else zy - h - 11, lbl)
    c.setFont('Lato-Bold', 9.5); c.setFillColor(INK); c.drawCentredString(x0 + gi * 185 + 71, 105, name)
lx = 70
for col, lab in cols:
    c.setFillColor(col); c.rect(lx, 430, 9, 9, stroke=0, fill=1)
    c.setFillColor(MUTED); c.setFont('Lato-Regular', 8.5); c.drawString(lx + 14, 431, lab); lx += 110
y = 440
for txt in ['Los accesos crecieron en volumen durante el trienio (+8,6% en tickets y +41,5% en días de visita), pero el ingreso neto real del último ciclo, <b>$ 54.296 M</b>, quedó 11,0% debajo del anterior.',
            'En no residentes las ventas subieron 24,6%, pero cada ticket dejó 25,3% menos en pesos constantes: la tarifa no acompañó la inflación. En residentes cayeron a la vez las ventas (−16,1%) y el neto por ticket (−8,9%).',
            'Los días por ticket pasaron de 1,05 a 1,37 por el mayor peso de pases de varios días y pasaportes anuales, lo que reduce el ingreso por día de visita.']:
    y -= para(txt, 640, y, 270, BODY_S) + 10
footer()

# ================================================================ 7. TABLA II
newpage()
header('Tabla II', 'Accesos por categoría de visitante', 'Ciclo nov 25–oct 26 · neto en millones de pesos de octubre de 2026')
rows = md_rows('t2')
table(rows, [210, 110, 90, 120, 90, 130, 110], 50, H - 110, fs=8.6, rh=28, tot_rows=(4,))
card(50, 150, 270, 90, '78,3%', 'del ingreso neto aportan los no residentes, con el 41,5% de los tickets', dark=True)
card(345, 150, 270, 90, '34,6%', 'del ingreso teórico (tarifa filtro de 1 día) recauda el neto de residentes')
card(640, 150, 270, 90, '146,4%', 'del ingreso teórico recauda el neto de no residentes')
footer()

# ================================================================ 8. TABLA III
newpage()
header('Tabla III', 'Accesos por dependencia', 'Ciclo nov 25–oct 26 · neto en millones de pesos de octubre de 2026 · ordenado por ingreso neto')
rows = md_rows('t3')
rows[0] = ['Dependencia', 'Tickets', 'Var. i.a.', 'Neto ($ M)', 'Var. i.a.', 'Var. trienal', 'No resid. (% tickets)', 'Neto por ticket ($)', 'Comisión / percibido']
table(rows, [170, 85, 70, 90, 70, 80, 95, 100, 100], 50, H - 110, fs=8.3, rh=24)
notebox(50, 125, 860, 'Los Alerces y Casa Central (pasaportes) se incorporaron al registro durante el primer ciclo: su variación trienal figura como s/base. Lago Puelo y Laguna Blanca sólo registraron ventas residuales en 2023–2024. La comisión de Iguazú (61,7% de lo percibido) es la más alta y conviene validarla con el contrato de la tercerizadora.')
footer()

# ================================================================ 9. TABLA III – LECTURA
newpage()
header('Tabla III — Lectura', 'Precio, volumen y comisiones')
y = H - 120
for txt in ['Iguazú y Glaciares concentran el <b>72,6%</b> del neto de accesos. Iguazú sostiene su ingreso neto (+0,7%) y pasa al primer lugar.',
            'Glaciares cae 18,2% interanual aun con 7,2% más tickets: desde mayo de 2025 cambió el agente de cobro y aumentó la comisión retenida. Tierra del Fuego retrocede 12,2% con 5,8% más tickets, y Nahuel Huapi acumula 14,5% de pérdida real en el trienio.',
            'Las comisiones están más concentradas que el neto: Iguazú, Glaciares y Tierra del Fuego reúnen el 95% de lo retenido por los agentes de cobro. Iguazú es además la excepción en la venta en línea: cobra en línea sólo el 42% de sus ingresos, contra más del 98% en el resto.']:
    y -= para(txt, 50, y, 520) + 12
card(610, 362, 300, 80, '−25,3%', 'neto por ticket de no residentes en el último ciclo', dark=True)
card(610, 270, 300, 80, '49,0%', 'de lo percibido retienen las tercerizadoras (44,9% en el ciclo anterior)')
card(610, 178, 300, 80, '72,6%', 'del neto de accesos aportan Iguazú y Glaciares')
footer('Fuente: elaboración propia con datos disponibles en ReNaRI y el Informe de accesos (nov 2023 – oct 2026).')

# ================================================================ 10. COBRANZAS – gráfico
newpage()
header('Cobranzas', 'La cobranza a prestadores cae tres ciclos seguidos', 'Cobranza anual a prestadores turísticos por dependencia, $ M de octubre de 2026 · nov 23–oct 24 contra nov 25–oct 26')
rowsd = [r for r in t5 if r['n'] not in ('El Palmar', 'Otras dependencias')]
xl, xr, mx = 175, 560, 12000
sx = lambda v: xl + v / mx * (xr - xl)
y0 = 385
c.setFont('Lato-Regular', 7.5)
for tk in range(0, 12001, 3000):
    c.setStrokeColor(LINE); c.setLineWidth(0.4); c.line(sx(tk), y0 + 12, sx(tk), y0 - len(rowsd) * 32 + 8)
    c.setFillColor(MUTED); c.drawCentredString(sx(tk), y0 - len(rowsd) * 32 - 2, nf(tk))
c.setFont('Lato-Bold', 7.5); c.setFillColor(MUTED); c.drawRightString(612, y0 + 16, 'VAR. TRIENAL')
for i, r in enumerate(rowsd):
    y = y0 - i * 32
    a, b = r['raw'][0], r['raw'][2]
    c.setFillColor(INK); c.setFont('Lato-Regular', 9); c.drawString(55, y - 3, r['n'])
    c.setStrokeColor(GREY); c.setLineWidth(2.2); c.line(sx(a), y, sx(b), y)
    c.setFillColor(GREY); c.circle(sx(a), y, 4.5, stroke=0, fill=1)
    c.setFillColor(G); c.circle(sx(b), y, 5, stroke=0, fill=1)
    c.setFillColor(INK); c.setFont('Lato-Regular', 8); c.drawString(max(sx(a), sx(b)) + 9, y - 3, nf(b))
    v = (b / a - 1) * 100
    c.setFont('Lato-Bold', 9); c.setFillColor(RED if v < -15 else INK); c.drawRightString(612, y - 3, ('+' if v > 0 else '−') + nf(abs(v), 1) + '%')
c.setFillColor(GREY); c.circle(60, 418, 4, stroke=0, fill=1); c.setFillColor(MUTED); c.setFont('Lato-Regular', 8); c.drawString(68, 415, 'nov 23–oct 24')
c.setFillColor(G); c.circle(150, 418, 4, stroke=0, fill=1); c.setFillColor(MUTED); c.drawString(158, 415, 'nov 25–oct 26')
y = 440
for txt in ['En pesos constantes la cobranza a prestadores turísticos pasó de <b>$ 33.248 M</b> a <b>$ 27.049 M</b> de octubre de 2026 (−18,6%). La caída se repite en los tres universos.',
            'Tierra del Fuego cae a menos de la mitad (−52,8%) y Glaciares pierde 27,4%. Lanín es la única dependencia relevante que crece en el trienio (+19,9%), aunque cayó 7,1% en el último año.',
            'En dólares la cobranza sube 23,1% en el trienio porque el tipo de cambio aumentó menos que la inflación.']:
    y -= para(txt, 650, y, 260, BODY_S) + 10
footer()

# ================================================================ 11. TABLA IV
newpage()
header('Tabla IV', 'Cobranza por universo de pagadores', 'Millones de pesos de octubre de 2026 · excluye medios de pago electrónicos')
rows = md_rows('t4')
rows[0] = ['Universo', 'nov 23–oct 24', 'nov 24–oct 25', 'nov 25–oct 26', 'Var. i.a.', 'Var. trienal', 'US$ M (nov 25–oct 26)']
table(rows, [260, 100, 100, 100, 90, 90, 120], 50, H - 110, fs=8.8, rh=30, sub_rows=(2,))
card(50, 165, 270, 90, '92,6%', 'de la cobranza a prestadores aportan los 42 concesionarios y permisionarios con DDJJ', dark=True)
card(345, 165, 270, 90, '71,4%', 'de todos los pagos corresponde a prestadores turísticos')
card(640, 165, 270, 90, '−33,7%', 'mostraría «todos los pagos» si se incluyeran los medios electrónicos, sólo por su baja del registro')
footer()

# ================================================================ 12. TABLA V
newpage()
header('Tabla V', 'Cobranza a prestadores por dependencia', 'Prestadores turísticos · millones de pesos de octubre de 2026')
rows = md_rows('t5')
rows[0] = ['Dependencia', 'nov 23–oct 24', 'nov 24–oct 25', 'nov 25–oct 26', 'Var. i.a.', 'Var. trienal', 'Participación']
table(rows, [230, 105, 105, 105, 100, 100, 115], 50, H - 110, fs=8.6, rh=25, tot_rows=(len(rows) - 1,))
notebox(50, 90, 860, 'Iguazú, Glaciares y Nahuel Huapi explican el 87,0% de la cobranza a prestadores. El salto de El Palmar en nov 24–oct 25 responde a la regularización de pagos adeudados por un permisionario.')
footer()

# ================================================================ 13. TABLA VI
newpage()
header('Tabla VI', 'Principales pagadores', 'Prestadores turísticos · nov 25–oct 26 en millones de pesos de octubre de 2026')
rows = md_rows('t6')
rows[0] = ['Razón social', 'nov 25–oct 26 ($ M)', 'Var. i.a.', 'Var. trienal', 'Participación']
table(rows, [330, 140, 130, 130, 130], 50, H - 110, fs=8.6, rh=27, sub_rows=(len(rows) - 1,))
footer()

# ================================================================ 14. TABLA VI – LECTURA
newpage()
header('Tabla VI — Lectura', 'Concentración de la cobranza')
y = H - 120
for txt in ['Iguazú Argentina S.A. aporta el 29,3% de la cobranza a prestadores y los diez primeros, el <b>86,7%</b>. Nueve de los diez pagan menos que hace tres años en términos reales; sólo Iguazú Argentina crece (+2,7%).',
            'Tranex Turismo (−54,0%), Marpatag (−44,3%) y Solo Patagonia (−29,6%) registran las mayores bajas trienales. Tranex cae además 36,6% en el último año y arrastra la cobranza de Tierra del Fuego.',
            'Por dependencia, Iguazú, Glaciares y Nahuel Huapi reúnen el 87,0% de lo cobrado: la recaudación depende de pocas dependencias y de pocos operadores.']:
    y -= para(txt, 50, y, 520) + 12
card(610, 362, 300, 80, '86,7%', 'de la cobranza aportan los diez mayores pagadores', dark=True)
card(610, 270, 300, 80, '29,3%', 'aporta Iguazú Argentina S.A.')
card(610, 178, 300, 80, '9 de 10', 'grandes pagadores aportan menos que hace tres años')
footer()

# ================================================================ 15. DEUDA – composición
newpage()
header('Deuda exigible al 31/10/2026', 'La deuda total y su composición')
card(50, 345, 200, 85, '$ 1.317,9 M', 'deuda neta exigible · −4,4% frente a septiembre', dark=True, bigsize=22)
card(265, 345, 200, 85, '$ 1.507,0 M', 'deuda bruta, antes de imputar pagos a cuenta', bigsize=22)
card(480, 345, 200, 85, 'US$ 850 mil', 'deuda neta a la paridad de referencia de $ 1.550', bigsize=22)
card(695, 345, 215, 85, '3.904', 'deudores en 33 dependencias · 11.035 comprobantes', bigsize=22)
rows = md_rows('dcomp')
table(rows, [210, 110, 130, 130], 50, 325, fs=8.6, rh=24, sub_rows=(3,), tot_rows=(5,))
y = 325
y -= notebox(650, y, 260, '<font name="Lato-Bold" color="#2C5F2D">Pagos a cuenta.</font> $ 189,0 M reducen 12,5% el saldo exigible; el 88,3% corresponde a Nahuel Huapi ($ 167,0 M). Siguen Glaciares ($ 13,3 M), Los Alerces ($ 4,9 M) y Tierra del Fuego ($ 2,3 M).') + 8
notebox(650, y, 260, '<font name="Lato-Bold" color="#2C5F2D">Movimiento del mes.</font> El capital cayó $ 47,9 M: salieron comprobantes por $ 83,5 M —$ 55,8 M de Marpatag S.R.L., en Glaciares— e ingresaron 44 altas por $ 37,0 M.')
footer('Fuente: elaboración propia sobre el Informe de deudas al 31/10/2026 y datos disponibles en ReNaRI.')

# ================================================================ 16. ANTIGÜEDAD
newpage()
header('Antigüedad', 'El 78,9% del capital adeudado se originó en 2025 y 2026', 'Capital impago al 31/10/2026 según año de origen del comprobante · millones de pesos nominales')
og = T['origen']; tot = sum(o['cap'] for o in og); mxv = max(o['cap'] for o in og)
xl, bw, yb, hh = 60, 78, 100, 300
c.setStrokeColor(MUTED); c.setLineWidth(0.6); c.line(xl, yb, xl + bw * len(og), yb)
for i, o in enumerate(og):
    v = o['cap'] / 1e6; h = v / (mxv / 1e6) * hh; x = xl + i * bw + 12
    new = i >= len(og) - 2
    c.setFillColor(G if new else GREY); c.rect(x, yb, bw - 24, max(h, 0.8), stroke=0, fill=1)
    c.setFillColor(INK); c.setFont('Lato-Bold' if new else 'Lato-Regular', 9)
    c.drawCentredString(x + (bw - 24) / 2, yb + h + 16, f'$ {nf(v, 1)} M')
    c.setFillColor(MUTED); c.setFont('Lato-Regular', 8); c.drawCentredString(x + (bw - 24) / 2, yb + h + 5, nf(o['cap'] / tot * 100, 1) + '%')
    c.drawCentredString(x + (bw - 24) / 2, yb - 13, o['y'])
y = 440
for txt in ['La deuda es reciente: el capital de 2023 o anterior suma <b>$ 83,4 M</b> (8,2%) y el de 2025–2026, <b>$ 807,5 M</b> (78,9%).',
            'Los intereses pesan más en la deuda vieja. Según el informe de deudas, los 5.172 documentos anteriores a 2021 suman sólo el 5,7% del monto, pero con un 80,4% de intereses acumulados.',
            'En Casa Central, cuya cartera es casi toda judicial, los intereses representan el 83,7% del saldo.']:
    y -= para(txt, 650, y, 260, BODY_S) + 10
footer('Fuente: elaboración propia sobre datos de ReNaRI al 31 de octubre de 2026. El año de origen mide cuándo se generó el capital hoy impago; no reconstruye el stock histórico.')

# ================================================================ 17–18. TABLA VII
dep_rows = md_rows('t7')
hdr = ['Dependencia', 'Capital', 'Interés', 'Deuda total', '%', '% acum.', 'Deudores']
body = dep_rows[1:-1]; totr = dep_rows[-1]
for part, chunk in enumerate([body[:17], body[17:]]):
    newpage()
    header(f'Tabla VII — {part + 1} de 2', 'Capital e intereses por dependencia', 'Universo completo de obligaciones documentadas en deuda · en pesos')
    rows = [hdr] + chunk + ([totr] if part == 1 else [])
    table(rows, [230, 130, 130, 140, 80, 80, 70], 50, H - 105, fs=8, rh=20.5, tot_rows=((len(rows) - 1,) if part == 1 else ()))
    if part == 1:
        para('La suma de deudores por dependencia (3.964) supera el total (3.904) porque 58 deudores tienen saldo en más de una dependencia.', 50, 70, 860, NOTE)
    footer('Fuente: elaboración propia sobre el Informe de deudas al 31/10/2026 (importes) y datos de ReNaRI (deudores por dependencia).')

# ================================================================ 19. TABLA VIII
newpage()
header('Tabla VIII', 'Capital e intereses por razón social', 'Diez mayores deudores y subtotales por categoría de deuda — al 31 de octubre de 2026 · % int.: intereses sobre capital')
rows = md_rows('t8')
rows[0] = ['Razón social', 'Dependencia', 'Capital', 'Interés', '% int.', 'Deuda total', '%', '% acum.', '#']
table(rows, [200, 95, 105, 100, 60, 115, 60, 65, 60], 50, H - 105, fs=7.8, rh=22, align=['L', 'L', 'R', 'R', 'R', 'R', 'R', 'R', 'R'], sub_rows=(11, 12, 13), tot_rows=(14,))
footer('Fuente: elaboración propia con datos disponibles en ReNaRI. Importes en pesos, antes de imputar saldos a favor.')

# ================================================================ 20. CONCENTRACIÓN Y HABILITACIÓN
newpage()
header('Tabla VIII — Lectura', 'Concentración, habilitación vigente y gestión judicial')
rows = md_rows('tram')
table(rows, [200, 90, 110, 120], 50, H - 105, fs=8.6, rh=24)
y = H - 260
for txt in ['El mayor deudor tiene el 8,9% de la deuda, los diez primeros el 36,2% y los cien primeros el 67,1%. En el otro extremo, 2.607 deudores con menos de $ 0,1 M suman apenas el 4,0%.',
            'Los 390 deudores habilitados deben $ 389,4 M (25,8%), con intereses del 18,8% de su saldo porque su deuda es más reciente; el 97,9% de ese monto es de concesionarios y permisionarios. Ocho de los diez mayores deudores no tienen habilitación vigente.',
            'La cartera en gestión judicial es chica: $ 27,1 M (1,8%) en 60 comprobantes de 39 deudores, con 75,5% de intereses; una sola factura de Los Alpes S.R.L. explica el 82,7%.']:
    y -= para(txt, 50, y, 520, BODY_S) + 10
card(610, 362, 300, 80, '36,18%', 'de la deuda concentran los diez mayores deudores', dark=True)
card(610, 270, 300, 80, '74,2%', 'de la deuda es de prestadores sin habilitación vigente')
card(610, 178, 300, 80, '1,80%', 'de la deuda está en gestión judicial ($ 27,1 M)')
footer()

# ================================================================ 21. CRUZADOS – gráfico
newpage()
header('Indicadores cruzados', 'Relación entre volumen de la deuda y de las cobranzas', 'Deuda exigible al 31/10/2026 sobre cobranza a prestadores de nov 25–oct 26 (pesos de oct-26), en %')
rt = T['ratio_tot'] * 100
xl, xr, mx = 150, 540, 35
sx = lambda v: xl + v / mx * (xr - xl)
y0 = 395
for i, r in enumerate(t9):
    v = r['ratio'] * 100; y = y0 - i * 33
    c.setFillColor(INK); c.setFont('Lato-Regular', 9); c.drawString(55, y + 3, r['n'])
    c.setFillColor(G if v > 2 * rt else GREY); c.rect(xl, y - 2, sx(v) - xl, 17, stroke=0, fill=1)
    c.setFillColor(INK); c.setFont('Lato-Bold' if v > 2 * rt else 'Lato-Regular', 9); c.drawString(sx(v) + 6, y + 3, nf(v, 1) + '%')
    c.setFillColor(MUTED); c.setFont('Lato-Regular', 8); c.drawRightString(610, y + 3, f'$ {nf(r["deuda"], 1)} M')
c.setStrokeColor(INK); c.setDash(3, 2); c.setLineWidth(0.7); c.line(sx(rt), y0 + 24, sx(rt), y0 - len(t9) * 33 + 18); c.setDash()
c.setFillColor(MUTED); c.setFont('Lato-Regular', 8); c.drawString(sx(rt) + 4, y0 + 24, f'Total APN {nf(rt, 1)}%')
c.setFont('Lato-Bold', 7.5); c.drawRightString(610, y0 + 24, 'DEUDA')
c.setFont('Lato-Italic', 7.5); c.drawString(55, y0 - len(t9) * 33 + 8, 'En verde oscuro, las dependencias que duplican el promedio APN.')
y = 440
for txt in ['Para el conjunto de la APN la deuda exigible equivale al <b>5,6%</b> de la cobranza anual a prestadores. En Lanín llega al 31,6% y en El Palmar, Lago Puelo, Los Alerces y Nahuel Huapi supera el 13%.',
            'En Iguazú y Glaciares, donde se concentra la cobranza, la deuda es marginal (1,4% y 1,6%).',
            'Medida sólo con los prestadores habilitados, la deuda equivale al 1,4% de la cobranza anual; Nahuel Huapi reúne el 62,2% de esa deuda.']:
    y -= para(txt, 650, y, 260, BODY_S) + 10
footer(SRCX)

# ================================================================ 22. TABLA IX
newpage()
header('Tabla IX', 'Flujos y stock por dependencia', 'Flujos del ciclo nov 25–oct 26 en millones de pesos de octubre de 2026 · deuda al 31/10/2026 en millones de pesos')
rows = md_rows('t9')
rows[0] = ['Dependencia', 'Neto de accesos', 'Cobranza a prestadores', 'Deuda exigible', 'Intereses / deuda', 'Habilitados / deuda']
table(rows, [210, 130, 150, 130, 120, 120], 50, H - 110, fs=8.6, rh=27)
notebox(50, 150, 860, 'En Lanín y Tierra del Fuego casi toda la deuda es de prestadores sin habilitación vigente (89,9% y 91,0%), lo que la vuelve más difícil de cobrar. En Glaciares y Tierra del Fuego el neto de accesos duplica o más la cobranza a prestadores; en Lanín, Nahuel Huapi y Lago Puelo pesa más la cobranza. Lago Puelo no registra venta de accesos en el último ciclo.')
footer(SRCX)

# ================================================================ 23. SÍNTESIS
newpage()
c.setFillColor(COVER); c.rect(0, 0, W, H, stroke=0, fill=1)
c.setFont('Lato-Bold', 6.6); c.setFillColor(LG); c.drawString(50, H - 40, spaced('Síntesis'))
c.setFont('Lato-Bold', 23); c.setFillColor(white); c.drawString(50, H - 72, 'Siete conclusiones del trienio')
concl = [
    ('Más visitas, menos ingreso real por visita.', 'Los tickets crecen 8,6% en el trienio y los días de visita 41,5%, pero el ingreso neto real del último ciclo cae 11,0% interanual.'),
    ('La tarifa no acompañó la inflación.', 'El neto por ticket baja 9,3% en el último ciclo y 25,3% en no residentes, que aportan el 78,3% del ingreso.'),
    ('Las comisiones igualan al ingreso neto.', 'Las tercerizadoras retienen el 49,0% de lo percibido, $ 52.213 millones; en Iguazú el 61,7%, valor que conviene validar contra el contrato.'),
    ('La cobranza a prestadores cae tres ciclos seguidos.', 'Retrocede 18,6% en el trienio, con Tierra del Fuego (−52,8%) y Glaciares (−27,4%) como principales bajas.'),
    ('La recaudación está concentrada.', 'Iguazú y Glaciares sostienen el 69,7% de la cobranza a prestadores y el 72,6% del neto de accesos; los diez mayores pagadores aportan el 86,7%.'),
    ('La deuda es reciente y de no habilitados.', 'El 78,9% del capital se originó en 2025–2026 y el 74,2% de la deuda es de prestadores sin habilitación vigente. La salida de Marpatag redujo la deuda neta 4,4% en octubre.'),
    ('Lanín y Nahuel Huapi concentran el riesgo de cobro.', 'En Lanín la deuda equivale al 31,6% de su cobranza anual; Nahuel Huapi reúne el 42,2% de la deuda total y el 62,2% de la de prestadores habilitados.')]
y = H - 105
st = S('cc', fontSize=9, leading=12, textColor=white, alignment=TA_LEFT)
for i, (b, t) in enumerate(concl):
    p = Paragraph(f'<font name="Lato-Bold">{b}</font> {t}', st); _, ph = p.wrap(720, 100)
    h = max(ph + 18, 44)
    c.setFillColor(HexColor('#25502A')); c.roundRect(90, y - h, 780, h, 4, stroke=0, fill=1)
    c.setFillColor(LG); c.setFont('Lato-Regular', 15); c.drawString(108, y - h / 2 - 5, f'{i + 1:02d}')
    p.drawOn(c, 145, y - h / 2 - ph / 2)
    y -= h + 7
c.setFont('Lato-Italic', 6.6); c.setFillColor(HexColor('#9DB792')); c.drawString(50, 30, SRCX)
c.setFont('Lato-Regular', 6.6); c.drawRightString(W - 50, 30, f'Tablero de control APN · nov 2023 – oct 2026 · {PAGE[0]}')

# ================================================================ 24. ANEXO
newpage()
header('Anexo', 'Cobranza por universo y de todos los pagos por dependencia', 'Millones de pesos de octubre de 2026')
rows = md_rows('anA')
rows[0] = ['A. Universo', 'nov 23–oct 24', 'nov 24–oct 25', 'nov 25–oct 26', 'Var. trienal', 'US$ M 25/26', '$ M corr. 25/26']
table(rows, [270, 95, 95, 95, 95, 100, 110], 50, H - 105, fs=8, rh=20)
rows = md_rows('anB')
rows[0] = ['B. Todos los pagos por dependencia', 'nov 23–oct 24', 'nov 24–oct 25', 'nov 25–oct 26', 'Var. trienal']
table(rows, [270, 110, 110, 110, 110], 50, H - 225, fs=8, rh=19)
para('Los medios electrónicos se registran sólo hasta julio de 2025: incluirlos simula una caída de 33,7% en el trienio. La tabla B excluye medios de pago electrónicos.', 50, 60, 860, NOTE)
footer('Fuentes: tableros e informes de accesos, cobranzas y deudas de la Dirección Nacional de Uso Público y la Dirección de Concesiones (ReNaRI), al 31/10/2026.')

c.save()
print('ok', PAGE[0], 'páginas')
