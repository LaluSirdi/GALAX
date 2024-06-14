import bcrypt
from flask import Flask, redirect, url_for, render_template, request, jsonify, flash, session
from pymongo import MongoClient 
from bson import ObjectId 
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_bcrypt import generate_password_hash
import os

app = Flask(__name__)

client = MongoClient('mongodb+srv://nawangandrian:xfDGGaRjSPR5TPoJ@cluster0.eqhmd7k.mongodb.net/')
db = client.dbfjkt
users_collection = db['users']  

app.secret_key = 'galax'
bcrypt = Bcrypt()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password != confirm_password:
            flash('Password dan konfirmasi password tidak cocok.', 'error')
            return redirect(url_for('index'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        user_exists = users_collection.find_one({'username': username})
        email_exists = users_collection.find_one({'email': email})
        
        if user_exists:
            flash('Username sudah ada. Silakan pilih username lain.', 'error')
            return redirect(url_for('register'))

        if email_exists:
            flash('Email sudah digunakan. Silakan gunakan email lain.', 'error')
            return redirect(url_for('register'))
        
        users_collection.insert_one({'username': username, 'email': email, 'password': hashed_password})
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        users = db.users
        login_user = users.find_one({'username': request.form['username']})

        if login_user and bcrypt.check_password_hash(login_user['password'], request.form['password']):
            session['username'] = request.form['username']
            if request.form['username'] == 'admin1' and request.form['password'] == 'admin1234':
                return redirect(url_for('upmerchandise'))
            else:
                return redirect(url_for('beranda'))

        return render_template('index.html', error_message="Kombinasi username/password tidak valid")

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