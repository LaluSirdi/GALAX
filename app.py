import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from bson.objectid import ObjectId
app = Flask(__name__)

client = MongoClient('mongodb+srv://laloesirdy:mama1000@cluster0.t2dmoad.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['coba'] 
collection = db.coba  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/beranda')
def beranda():
    return render_template('beranda.html')

@app.route('/merchandise')
def merchandise():
    return render_template('merchandise.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upmerch')
def upmerch():
    return render_template('upmerch.html')

@app.route('/add', methods=['POST'])
def add_merchandise():
    if 'image' not in request.files:
        return 'No file part'
    file = request.files['image']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        description = request.form['description']
        price = float(request.form['price'])
        merchandise = {
            'image': filename,
            'description': description,
            'price': price
        }
        collection.insert_one(merchandise)
        return redirect(url_for('index'))

@app.route('/delete/<id>')
def delete_merchandise(id):
    merchandise = collection.find_one({'_id': ObjectId(id)})
    if merchandise:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], merchandise['image']))
        collection.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('index'))

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_merchandise(id):
    merchandise = collection.find_one({'_id': ObjectId(id)})
    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                merchandise['image'] = filename
        merchandise['description'] = request.form['description']
        merchandise['price'] = float(request.form['price'])
        collection.update_one({'_id': ObjectId(id)}, {'$set': merchandise})
        return redirect(url_for('index'))
    return render_template('edit.html', merchandise=merchandise)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)