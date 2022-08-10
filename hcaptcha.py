from flask import Flask, Request, render_template
from ssl import SSLContext
import ssl

app = Flask(__name__)

context = SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert/ssl_key.pem', "cert/ssl_cert.pem")

@app.get('/')
def index():
    key = Request.args.get('key')
    return render_template('index.html', siteKey=key)


app.run(host='127.0.0.0', port=79000, debug=True, ssl_context=context)