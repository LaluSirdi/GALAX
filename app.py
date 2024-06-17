from datetime import datetime
from flask import Flask, redirect, url_for, render_template, request, jsonify, flash, session
from pymongo import MongoClient
from bson import ObjectId
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_bcrypt import generate_password_hash
import os
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)

client = MongoClient('mongodb://sparta:123@ac-noo9u4e-shard-00-00.uurp56w.mongodb.net:27017,ac-noo9u4e-shard-00-01.uurp56w.mongodb.net:27017,ac-noo9u4e-shard-00-02.uurp56w.mongodb.net:27017/?ssl=true&replicaSet=atlas-g38sd1-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0&connectTimeoutMS=30000')
db = client.dbfjkt
users_collection = db['users']

app.secret_key = 'galax'
SECRET_KEY = "GALAX"
bcrypt = Bcrypt(app)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session['username'] == '':
            flash('Harap login terlebih dahulu.', 'error')
            return redirect(url_for('index'))
        if 'status' not in session or session['status'] != 'login':
            flash('Anda harus login terlebih dahulu untuk mengakses halaman ini.', 'error')
            return redirect(url_for('index'))
        if session['username'] != 'admin1':
            flash('Akses ditolak. Hanya admin yang dapat mengakses halaman ini.', 'error')
            return redirect(url_for('beranda'))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session['username'] == '':
            flash('Harap login terlebih dahulu.', 'error')
            return redirect(url_for('index'))
        if 'status' not in session or session['status'] != 'login':
            flash('Anda harus login terlebih dahulu untuk mengakses halaman ini.', 'error')
            return redirect(url_for('index'))
        if session['username'] == 'admin1':
            flash('Akses ditolak, harus login sebagai user.', 'error')
            return redirect(url_for('upmerchandise'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    session.clear()
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
        login_user = users_collection.find_one({'username': request.form['username']})

        if login_user and bcrypt.check_password_hash(login_user['password'], request.form['password']):
            session['username'] = request.form['username']
            session['_id'] = str(login_user['_id'])
            session['status'] = 'login'
            if request.form['username'] == 'admin1':
                return redirect(url_for('upmerchandise'))
            else:
                return redirect(url_for('beranda'))

        flash('Kombinasi username/password tidak valid', 'error')
        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/beranda')
@user_required
def beranda():
    return render_template('beranda.html')

@app.route('/merchandise')
@user_required
def merchandise():
    merchandise = list(db.merchandise.find({}))
    return render_template('merchandise.html', merchandise=merchandise)

@app.route('/beli')
@user_required
def beli():
    nama = request.args.get('nama')
    harga = request.args.get('harga')
    whatsapp = '6289617338298'
    return redirect(f'https://wa.me/{whatsapp}?text=Saya tertarik dengan {nama} seharga {harga}. Tolong informasi lebih lanjut.')

@app.route('/contact')
@user_required
def contact():
    return render_template('contact.html')

@app.route('/about')
@user_required
def about():
    return render_template('about.html')

@app.route('/user')
@admin_required
def user():
    user = list(users_collection.find({}))
    return render_template('user.html', user=user)

@app.route('/deleteUser/<_id>', methods=['GET', 'POST'])
@admin_required
def deleteUser(_id):
    users_collection.delete_one({"_id": ObjectId(_id)})
    return redirect(url_for("user"))

@app.route('/upmerchandise', methods=['GET', 'POST'])
@admin_required
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
@admin_required
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

@app.route('/deleteMerchandise/<_id>', methods=['GET', 'POST'])
@admin_required
def deleteMerchandise(_id):
    id = ObjectId(_id)
    db.merchandise.delete_one({"_id": id})
    return redirect(url_for("upmerchandise"))

@app.route('/gallery')
def gallery():
    fjkt_items = list(db.fjkt.find({"archived": {"$ne": True}}))
    fan_art_items = list(db.fan_art.find({"archived": {"$ne": True}}))
    return render_template('gallery.html', fjkt_items=fjkt_items, fan_art_items=fan_art_items)

@app.route('/upgallery')
def upgallery():
    fjkt_items = list(db.fjkt.find())
    fan_art_items = list(db.fan_art.find())
    return render_template('up-gallery.html', fjkt_items=fjkt_items, fan_art_items=fan_art_items)

@app.route('/submitgallery', methods=['POST'])
def submitgallery():
    category = request.form['category']
    title = request.form.get('fjkt-name') or request.form.get('fan-art-title')
    description = request.form.get('fjkt-description') or request.form.get('fan-art-description')
    image = request.files.get('fjkt-image') or request.files.get('fan-art-image')

    if image:
        image_filename = secure_filename(image.filename)
        
        if category == 'FJKT':
            image_path = f'static/assets/img/gallery/fjkt/{image_filename}'
        elif category == 'FAN ART':
            image_path = f'static/assets/img/gallery/fan_art/{image_filename}'
        else:
            # Handle jika kategori tidak dikenali
            return "Kategori tidak valid"

        image.save(image_path)
    else:
        image_path = None

    current_date = datetime.now()
    day = current_date.day
    month = current_date.strftime('%B')
    year = current_date.year

    data = {
        'title': title,
        'category': category,
        'description': description,
        'image': image_path,
        'day': day,
        'month': month,
        'year': year,
        'archived': False  
    }

    if category == 'FJKT':
        db.fjkt.insert_one(data)
    elif category == 'FAN ART':
        db.fan_art.insert_one(data)

    return redirect(url_for('upgallery'))

@app.route('/deletegallery/<item_id>', methods=['POST'])
def delete_gallery(item_id):
    # Temukan item berdasarkan kategori
    fjkt_item = db.fjkt.find_one({"_id": ObjectId(item_id)})
    fan_art_item = db.fan_art.find_one({"_id": ObjectId(item_id)})
    
    # Hapus item dari koleksi yang sesuai
    if fjkt_item:
        db.fjkt.delete_one({"_id": ObjectId(item_id)})
    elif fan_art_item:
        db.fan_art.delete_one({"_id": ObjectId(item_id)})
    else:
        return jsonify({"status": "error", "message": "Item tidak ditemukan"}), 404
    
    return jsonify({"status": "success", "message": "Item berhasil dihapus"})

@app.route('/editgallery', methods=['POST'])
def edit_gallery():
    item_id = request.form['item_id']
    category = request.form['edit-category']
    title = request.form['edit-name']
    description = request.form['edit-description']
    image = request.files.get('edit-image')
    current_image_path = request.form['current_image_path']

    if image:
        image_filename = secure_filename(image.filename)
        if category == 'FJKT':
            image_path = f'static/assets/img/gallery/fjkt/{image_filename}'
        elif category == 'Fan Art':
            image_path = f'static/assets/img/gallery/fan_art/{image_filename}'
        else:
            return "Kategori tidak valid", 400
        image.save(image_path)
    else:
        image_path = current_image_path

    db_collection = db.fjkt if category == 'FJKT' else db.fan_art
    
    result = db_collection.update_one(
        {"_id": ObjectId(item_id)},
        {"$set": {
            "title": title,
            "description": description,
            "image": image_path,
            "archived": False  # Tambahkan atribut archived di sini
        }}
    )
    
    if result.modified_count == 1:
        return redirect(url_for('upgallery'))
    else:
        return "Gagal memperbarui data", 500

@app.route('/archive_item/<item_id>', methods=['POST'])
def archive_item(item_id):
    data = request.json
    category = data.get('category')
    
    db_collection = db.fjkt if category == 'FJKT' else db.fan_art
    item = db_collection.find_one({"_id": ObjectId(item_id)})

    if item:
        new_status = not item.get('archived', False)
        db_collection.update_one({"_id": ObjectId(item_id)}, {"$set": {"archived": new_status}})
        return jsonify(success=True, archived=new_status)
    return jsonify(success=False), 404

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)