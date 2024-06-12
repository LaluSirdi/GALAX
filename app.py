import bcrypt
from flask import Flask, redirect, url_for, render_template, request, jsonify 
from pymongo import MongoClient 
from bson import ObjectId 
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_bcrypt import generate_password_hash
from flask import flash, session
import os

app = Flask(__name__)
app.secret_key = 'galax'

client = MongoClient('mongodb+srv://nawangandrian:xfDGGaRjSPR5TPoJ@cluster0.eqhmd7k.mongodb.net/')
db = client.dbfjkt
users_collection = db['users']  # Ganti 'users' dengan nama koleksi untuk pengguna

@app.route('/')
def index():
    return render_template('index.html')

bcrypt = Bcrypt()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = db.users
        login_user = users.find_one({'username': request.form['username']})

        if login_user:
            hashed_password = login_user['password']
            if bcrypt.check_password_hash(hashed_password, request.form['password']):
                session['username'] = request.form['username']
                if request.form['username'] == 'admin1' and request.form['password'] == 'admin1234':
                    return redirect(url_for('upmerchandise'))
                else:
                    return redirect(url_for('beranda'))
            else:
                flash('Kombinasi username/password tidak valid')
        else:
            flash('Kombinasi username/password tidak valid')

    return render_template('index.html')


@app.route('/beranda')
def beranda():
    return render_template('beranda.html')

@app.route('/merchandise')
def merchandise():
    merchandise = list(db.merchandise.find({}))
    return render_template('merchandise.html', merchandise=merchandise)

@app.route('/beli')
def beli():
    nama = request.args.get('nama')
    harga = request.args.get('harga')
    whatsapp = '6285865317821'
    return redirect(f'https://wa.me/{whatsapp}?text=Saya tertarik dengan {nama} seharga {harga}. Tolong informasi lebih lanjut.')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upmerchandise', methods=['GET', 'POST'])
def upmerchandise():
    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        deskripsi = request.form['deskripsi']
        nama_gambar = request.files['gambar']

        if nama_gambar:
            nama_file_asli = nama_gambar.filename
            nama_file_gambar = nama_file_asli.split('/')[-1]
            file_path = f'static/assets/img/product/{nama_file_gambar}'
            nama_gambar.save(file_path)
        else:
            nama_file_gambar = None

        doc = {
            'nama': nama,
            'harga': harga,
            'gambar': nama_file_gambar,
            'deskripsi': deskripsi
        }
        db.merchandise.insert_one(doc)
        return redirect(url_for('upmerchandise'))

    merchandise = list(db.merchandise.find({}))
    return render_template('up-merchandise.html', merchandise=merchandise)

@app.route('/editMerchandise/<_id>', methods=['GET', 'POST'])
def editMerchandise(_id):
    if request.method == 'POST':
        id = request.form['_id']
        nama = request.form['nama']
        harga = request.form['harga']
        deskripsi = request.form['deskripsi']
        nama_gambar = request.files['gambar']
        
        doc = {
            'nama': nama,
            'harga': harga,
            'deskripsi': deskripsi
        }
        if nama_gambar:
            nama_file_asli = nama_gambar.filename
            nama_file_gambar = nama_file_asli.split('/')[-1]
            file_path = f'static/assets/img/product/{nama_file_gambar}'
            nama_gambar.save(file_path)
            doc['gambar'] = nama_file_gambar
        
        db.merchandise.update_one({"_id": ObjectId(_id)}, {"$set": doc})
        return redirect(url_for("upmerchandise"))
    
    id = ObjectId(_id)
    merchandise = db.merchandise.find_one({"_id": id})
    return jsonify({'nama': merchandise['nama'], 'harga': merchandise['harga'], 'deskripsi': merchandise['deskripsi'], 'gambar': merchandise['gambar']})

@app.route('/deleteMerchandise/<_id>',methods=['GET','POST'])
def deleteMerchandise(_id):
   id = ObjectId(_id)
   db.merchandise.delete_one({"_id": ObjectId(_id)})
   return redirect(url_for("upmerchandise"))

@app.route('/upgallery')
def home():
    return render_template('up-gallery.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)