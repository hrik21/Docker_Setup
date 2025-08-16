from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import secrets
import os
import pandas

# Import our custom modules
from database import init_database, save_pdf_to_db, get_pdf_by_id, get_pdf_file_path, get_all_pdfs, get_database_stats
from file_handler import setup_upload_folder, save_uploaded_file

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route("/")
def upload_form():
    return render_template('upload.html')

@app.route("/upload", methods=['POST'])
def upload_file():
    # Check if file exists in request
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    
    # Try to save the file
    filename, file_path = save_uploaded_file(file)
    
    if filename and file_path:
        # Save to database
        pdf_id = save_pdf_to_db(filename, file.filename, file_path)
        
        flash('File uploaded successfully!')
        return redirect(url_for('view_pdf', pdf_id=pdf_id))
    else:
        flash('Please upload a valid PDF file only')
        return redirect(url_for('upload_form'))

@app.route("/view/<int:pdf_id>")
def view_pdf(pdf_id):
    pdf = get_pdf_by_id(pdf_id)
    
    if pdf:
        return render_template('view_pdf.html', pdf=pdf)
    else:
        flash('PDF not found')
        return redirect(url_for('upload_form'))

@app.route("/pdf/<int:pdf_id>")
def serve_pdf(pdf_id):
    file_path = get_pdf_file_path(pdf_id)
    
    if file_path:
        return send_file(file_path, mimetype='application/pdf')
    else:
        return "PDF not found", 404

@app.route("/list")
def list_pdfs():
    pdfs = get_all_pdfs()
    return render_template('list_pdfs.html', pdfs=pdfs)

@app.route("/admin/db")
def admin_db():
    stats = get_database_stats()
    data = get_all_pdfs()
    
    return f"""
    <h1>Database Admin</h1>
    <h2>Table Structure:</h2>
    <pre>{stats['columns']}</pre>
    
    <h2>Stats:</h2>
    <p>Total PDFs: {stats['total_count']}</p>
    
    <h2>All Data:</h2>
    <table border="1" style="border-collapse: collapse;">
        <tr><th>ID</th><th>Filename</th><th>Original Name</th><th>Path</th><th>Upload Date</th></tr>
        {''.join([f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>' for row in data])}
    </table>
    
    <br><a href="/">Back to Upload</a> | <a href="/list">View PDFs</a>
    """

@app.route("/api/stats")
def api_stats():
    """JSON API endpoint for database statistics"""
    stats = get_database_stats()
    return jsonify(stats)

if __name__ == "__main__":
    # Setup everything when app starts
    setup_upload_folder()
    init_database()
    
    print("🚀 PDF Upload App Starting...")
    print("📁 Database: pdfs.db")
    print("📂 Upload folder: uploads/")
    print("🌐 Server: http://localhost:8080")
    
    app.run(host='0.0.0.0', port=8080)