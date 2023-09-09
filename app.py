from flask import Flask, render_template, request, send_file, jsonify
import io
import json
from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas
from datetime import date

app = Flask(__name__)

def calculate_monthly_payment(P, annual_rate_percentage, amortization, payment_frequency):
    # Convert annual_rate_percentage to a decimal
    annual_rate = annual_rate_percentage / 100.0

    # Check for valid input
    if payment_frequency not in ['monthly', 'biweekly']:
        raise ValueError("payment_frequency must be either 'monthly' or 'biweekly'")
    
    # If the annual rate is not 0%
    if annual_rate > 0:
        monthly_rate = annual_rate / 12
        n_payments = amortization  # number of monthly payments
        
        # Monthly payment formula for loans with interest
        M = (P * monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)
        
        # If payment frequency is biweekly, adjust the monthly payment
        if payment_frequency == 'biweekly':
            M = M * 12 / 26

    # If the annual rate is 0%
    else:
        if payment_frequency == 'monthly':
            M = (P + 149) / amortization
        else:  # biweekly
            M = (P + 149) / ((amortization / 12) * 26)

    return round(M, 2)

def add_text_to_pdf(input_pdf, name, lastname, street, city, province, postal_code, interest, term, agreement_value, monthly_payment, options, payment_frequency, amortization):
    output_pdf = io.BytesIO()
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    pretax_value = float(agreement_value) / 1.13
    tax_value = float(agreement_value) - pretax_value
    current_date = date.today().strftime("%Y-%m-%d")
    base_option_price = float(pretax_value) / len(options)

    full_name = name + " " + lastname
    address = street + ", " + city + ", " + province

    for i, page in enumerate(reader.pages):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=page.MediaBox[-2:])
        c.setFont("Helvetica", 15)
        
        c.drawString(65, 635, name)
        c.drawString(210, 635, lastname)
        c.drawString(480, 612, street)
        c.drawString(350, 635, city)
        c.drawString(515, 635, province)
        c.drawString(360, 612, postal_code)
        c.drawString(265, 160, str(interest) + "%")
        c.drawString(130, 160, term)
        c.drawString(265, 31, current_date)
        c.setFont("Helvetica-Bold", 15)
        c.drawRightString(550, 120, f"${float(agreement_value):,.2f}")
        c.setFont("Helvetica", 15)
        c.drawRightString(550, 180, f"${pretax_value:,.2f}")
        c.drawRightString(550, 150, f"${tax_value:,.2f}")
        c.drawString(445, 80, full_name)
        c.setFont("Helvetica", 10)
        c.drawString(240, 80, address)
            
        y = 485  
        for index, option in enumerate(options):
                c.setFont("Helvetica", 15)
                option_price = base_option_price
                c.drawString(100, y, option['value'])
                y -= 21  

        c.drawRightString(90, 160, f"${monthly_payment:,.2f}")
            # Add payment frequency on the PDF
        c.setFont("Helvetica", 8)
        c.drawString(43, 145, payment_frequency.capitalize())

        
        c.save()

        packet.seek(0)
        watermark = PdfReader(packet)
        PageMerge(page).add(watermark.pages[0]).render()
        writer.addpage(page)

    writer.write(output_pdf)
    output_pdf.seek(0)
    return output_pdf

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        street = request.form['street']
        city = request.form['city']
        province = request.form['province']
        amortization = float(request.form['amortization'])
        postal_code = request.form['postal_code']
        interest = request.form['interest']
        term = request.form['term']
        agreement_value = request.form['agreement_value']
        payment_frequency = request.form['payment_frequency']

        options_json = request.form.get('options')
        options = json.loads(options_json)
        
        P = float(agreement_value)
        annual_rate = float(interest)
        monthly_payment = calculate_monthly_payment(P, annual_rate, amortization, payment_frequency)

        pdf_file_path = 'invoice.pdf'
        output_buffer = add_text_to_pdf(pdf_file_path, name, lastname, street, city, province, postal_code, interest, term, agreement_value, monthly_payment, options, payment_frequency, amortization)
        output_path = "invoice_filled.pdf"
        with open(output_path, "wb") as output_pdf:
            output_pdf.write(output_buffer.getbuffer())
        return send_file(
            output_path,
            mimetype='application/pdf',
            as_attachment=False
        )

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
