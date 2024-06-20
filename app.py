from flask import Flask, redirect, url_for, render_template, request, jsonify, flash, session
from pymongo import MongoClient
from bson import ObjectId
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
from functools import wraps
load_dotenv()
app = Flask(__name__)

# Use environment variables
mongo_uri = os.getenv('MONGO_URI')
db_name = os.getenv('DB_NAME')
app.secret_key = os.getenv('SECRET_KEY')
bcrypt_secret_key = os.getenv('BCRYPT_SECRET_KEY')

# Debugging prints to check if environment variables are loaded correctly
print(f"mongo_uri: {mongo_uri}")
print(f"db_name: {db_name}")
print(f"app.secret_key: {app.secret_key}")
print(f"bcrypt_secret_key: {bcrypt_secret_key}")

# Ensure db_name is a string
if not isinstance(db_name, str):
    raise TypeError("DB_NAME environment variable must be a string")

client = MongoClient(mongo_uri)
db = client[db_name]
users_collection = db['users']

bcrypt = Bcrypt(app)
client = MongoClient('mongodb://sparta:123@ac-noo9u4e-shard-00-00.uurp56w.mongodb.net:27017,ac-noo9u4e-shard-00-01.uurp56w.mongodb.net:27017,ac-noo9u4e-shard-00-02.uurp56w.mongodb.net:27017/?ssl=true&replicaSet=atlas-g38sd1-shard-0&authSource=admin&retryWrites=true&w=majority&appName=Cluster0&connectTimeoutMS=30000')
db = client.dbfjkt
users_collection = db['users']

app.secret_key = 'galax'
SECRET_KEY = "GALAX"
bcrypt = Bcrypt(app)

def datetimeformat(value, format='%Y-%m-%d'):
    """Format a date time to (Default): yyyy-mm-dd"""
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime(format)

app.jinja_env.filters['datetimeformat'] = datetimeformat

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session['username'] == '':
            flash('Harap login terlebih dahulu.', 'error')
            return redirect(url_for('index'))
        if 'status' not in session or session['status'] != 'login':
            flash('Anda harus login terlebih dahulu untuk mengakses halaman ini.', 'error')
            return redirect(url_for('index'))
        if session['username'] != 'admin':
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
        if session['username'] == 'admin':
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
            return jsonify({"status": "error", "message": "Password dan konfirmasi password tidak cocok"}), 404

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user_exists = users_collection.find_one({'username': username})
        email_exists = users_collection.find_one({'email': email})

        if user_exists:
            return jsonify({"status": "error", "message": "Username sudah ada, gunakan yang lain"}), 404

        if email_exists:
            return jsonify({"status": "error", "message": "Email sudah ada, gunakan yang lain"}), 404

        users_collection.insert_one({'username': username, 'email': email, 'password': hashed_password, "profile_pic_real": "profile_placeholder.png",})

        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        login_user = users_collection.find_one({'username': request.form['username']})

        if login_user and bcrypt.check_password_hash(login_user['password'], request.form['password']):
            session['username'] = request.form['username']
            session['profile_pic_real'] = login_user['profile_pic_real']
            session['email'] = login_user['email']
            session['password'] = login_user['password']
            session['_id'] = str(login_user['_id'])
            session['status'] = 'login'
            if request.form['username'] == 'admin':
                return jsonify({"status": "success", "redirect_url": url_for('upmerchandise')}), 200
            else:
                return jsonify({"status": "success", "redirect_url": url_for('beranda')}), 200

        return jsonify({"status": "error", "message": "Kombinasi username/password tidak valid"}), 404

    return render_template('index.html')

@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile(user_id):
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        profile_pic = request.files['profile_pic']
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        nama_file_gambar = None

        if profile_pic.filename != '':
            allowed_extensions = {'png', 'jpg', 'jpeg'}
            if profile_pic.filename.split('.')[-1].lower() not in allowed_extensions:
                flash('Hanya file gambar dengan ekstensi .png, .jpg, atau .jpeg yang diperbolehkan.', 'error')
                return redirect(request.url)

            UPLOAD_FOLDER = 'static/assets/img/profile_pics'

            filename = secure_filename(profile_pic.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            profile_pic.save(file_path)
            nama_file_gambar = filename

        user_exists = users_collection.find_one({'username': username, '_id': {'$ne': ObjectId(user_id)}})
        email_exists = users_collection.find_one({'email': email, '_id': {'$ne': ObjectId(user_id)}})

        if user_exists:
            return jsonify({"status": "error", "message": "Username sudah ada, gunakan yang lain"}), 404

        if email_exists:
            return jsonify({"status": "error", "message": "Email sudah ada, gunakan yang lain"}), 404

        update_data = {
            'username': username,
            'email': email
        }

        if nama_file_gambar:
            update_data['profile_pic_real'] = nama_file_gambar

        pw_user = users_collection.find_one({'_id': ObjectId(user_id)})['password']

        if current_password and new_password and confirm_password:
            if new_password and confirm_password:
                if check_password_hash(pw_user, current_password):
                    print('Password saat ini tidak sesuai.', 'error')
                    return jsonify({"status": "error", "message": "Password saat ini tidak sesuai."}), 404

                if new_password != confirm_password:
                    print('Password baru dan konfirmasi password tidak cocok.', 'error')
                    return jsonify({"status": "error", "message": "Password baru dan konfirmasi password tidak cocok."}), 404

                hashed_password = generate_password_hash(new_password).decode('utf-8')
                update_data['password'] = hashed_password

        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )

        db.comment.update_many(
            {'id_user': str(user_id)},
            {'$set': {'image': nama_file_gambar, 'username': username}}
        )

        db.comment.update_many(
            {'replies.id_user': str(user_id)},
            {'$set': {'replies.$.image': nama_file_gambar, 'replies.$.username': username}}
        )

        session['username'] = username
        session['email'] = email
        if new_password and confirm_password:
            session['password'] = hashed_password
        if nama_file_gambar:
            session['profile_pic_real'] = nama_file_gambar

        flash('Profil berhasil diperbarui!', 'success')
        return redirect(url_for('profile', user_id=user_id))

    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        flash('User tidak ditemukan.', 'error')
        return redirect(url_for('index'))

    if user['username'] == 'admin':
        return redirect(url_for('upmerchandise'))
    else:
        return redirect(url_for('beranda'))

@app.route('/beranda')
@user_required
def beranda():
    return render_template('beranda.html')

@app.route('/merchandise')
@user_required
def merchandise():
    merchandise = list(db.merchandise.find({'archived': False}))
    return render_template('merchandise.html', merchandise=merchandise)

@app.route('/beli')
def beli():
    nama = request.args.get('nama')
    harga = request.args.get('harga')
    whatsapp = '6289617338298'
    return redirect(f'https://wa.me/{whatsapp}?text=Saya tertarik dengan {nama} seharga {harga}. Tolong informasi lebih lanjut.')

@app.route('/gallery')
@user_required
def gallery():
    fjkt = list(db.fjkt.find({'archived': False}))
    fanart = list(db.fanart.find({'archived': False}))

    for item in fjkt:
        item['jumlah_komentar'] = db.comment.count_documents({'id_gallery': str(item['_id'])})
        last_comment = db.comment.find_one({'id_gallery': str(item['_id'])}, sort=[('_id', -1)])
        item['last_comment_username'] = last_comment['username'] if last_comment else 'User'
        item['type'] = 'FJKT'  

    for item in fanart:
        item['jumlah_komentar'] = db.comment.count_documents({'id_gallery': str(item['_id'])})
        last_comment = db.comment.find_one({'id_gallery': str(item['_id'])}, sort=[('_id', -1)])
        item['last_comment_username'] = last_comment['username'] if last_comment else 'User'
        item['type'] = 'Fan Art'  

    combined = []
    max_length = max(len(fjkt), len(fanart))
    for i in range(max_length):
        if i < len(fjkt):
            combined.append(fjkt[i])
        if i < len(fanart):
            combined.append(fanart[i])

    return render_template('gallery.html', fjkt=fjkt, fanart=fanart, gallery_items=combined)

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
    users = list(users_collection.find({}))
    return render_template('user.html', users=users)

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
            'deskripsi': deskripsi,
            'archived': False 
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

@app.route('/upgallery', methods=['GET', 'POST'])
@admin_required
def upgallery():
    if request.method == 'POST':
        nama = request.form['nama']
        type = request.form['type']
        deskripsi = request.form['deskripsi']
        nama_gambar = request.files['gambar']
        tanggal_post = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 

        if nama_gambar:
            nama_file_asli = nama_gambar.filename
            nama_file_gambar = nama_file_asli.split('/')[-1]
            file_path = f'static/assets/img/gallery/{type}/{nama_file_gambar}'
            nama_gambar.save(file_path)
        else:
            nama_file_gambar = None

        doc = {
            'type': type,
            'nama': nama,
            'gambar': nama_file_gambar,
            'deskripsi': deskripsi,
            'tanggal': tanggal_post,
            'archived': False 
        }

        if type == 'fjkt':
            db.fjkt.insert_one(doc)
        elif type == 'fanart':
            db.fanart.insert_one(doc)

        return redirect(url_for('upgallery'))

    fjkt = list(db.fjkt.find({}))
    fanart = list(db.fanart.find({}))
    for item in fjkt:
        item['jumlah_komentar'] = db.comment.count_documents({'id_gallery': str(item['_id'])})
        last_comment = db.comment.find_one({'id_gallery': str(item['_id'])}, sort=[('_id', -1)])
        item['last_comment_username'] = last_comment['username'] if last_comment else 'User'
        item['type'] = 'FJKT'  

    for item in fanart:
        item['jumlah_komentar'] = db.comment.count_documents({'id_gallery': str(item['_id'])})
        last_comment = db.comment.find_one({'id_gallery': str(item['_id'])}, sort=[('_id', -1)])
        item['last_comment_username'] = last_comment['username'] if last_comment else 'User'
        item['type'] = 'Fan Art'  

    combined = []
    max_length = max(len(fjkt), len(fanart))
    for i in range(max_length):
        if i < len(fjkt):
            combined.append(fjkt[i])
        if i < len(fanart):
            combined.append(fanart[i])

    return render_template('up-gallery.html', fjkt=fjkt, fanart=fanart, gallery_items=combined)

@app.route('/editGallery/<type>/<_id>', methods=['GET', 'POST'])
@admin_required
def editGallery(type, _id):
    if request.method == 'POST':
        id = request.form['_id']
        type = request.form['type']
        nama = request.form['nama']
        deskripsi = request.form['deskripsi']
        nama_gambar = request.files['gambar']
        tanggal_post = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        
        doc = {
            'type': type,
            'nama': nama,
            'deskripsi': deskripsi,
            'tanggal': tanggal_post
        }
        if nama_gambar:
            nama_file_asli = nama_gambar.filename
            nama_file_gambar = nama_file_asli.split('/')[-1]
            file_path = f'static/assets/img/gallery/{type}/{nama_file_gambar}'
            nama_gambar.save(file_path)
            doc['gambar'] = nama_file_gambar
        
        if type == 'fjkt':
            db.fjkt.update_one({"_id": ObjectId(_id)}, {"$set": doc})
        elif type == 'fanart':
            db.fanart.update_one({"_id": ObjectId(_id)}, {"$set": doc})
        return redirect(url_for("upgallery"))
    
    id = ObjectId(_id)
    if type == 'fjkt':
        gallery = db.fjkt.find_one({"_id": id})
    elif type == 'fanart':
        gallery = db.fanart.find_one({"_id": id})
    return jsonify({'nama': gallery['nama'], 'deskripsi': gallery['deskripsi'], 'gambar': gallery['gambar']})

@app.route('/deleteGallery/<type>/<_id>', methods=['GET', 'POST'])
@admin_required
def deleteGallery(type, _id):
    id = ObjectId(_id)
    if type == 'fjkt':
        db.fjkt.delete_one({"_id": id})
    elif type == 'fanart':
        db.fanart.delete_one({"_id": id})
    else:
        return jsonify({'error': 'Invalid type'}), 400
    
    db.comment.delete_many({"id_gallery": str(id)})
    
    return redirect(url_for("upgallery"))

@app.route('/archive_item/<item_id>', methods=['POST'])
@admin_required
def archive_item(item_id):
    data = request.json
    category = data.get('type')
    
    db_collection = db.fjkt if category == 'fjkt' else db.fanart
    item = db_collection.find_one({"_id": ObjectId(item_id)})

    if item:
        new_status = not item.get('archived', False)
        db_collection.update_one({"_id": ObjectId(item_id)}, {"$set": {"archived": new_status}})
        return jsonify(success=True, archived=new_status)
    return jsonify(success=False), 404

@app.route('/archive_item_m/<item_id>', methods=['POST'])
@admin_required
def archive_item_m(item_id):
    data = request.json
    
    db_collection = db.merchandise
    item = db_collection.find_one({"_id": ObjectId(item_id)})

    if item:
        new_status = not item.get('archived', False)
        db_collection.update_one({"_id": ObjectId(item_id)}, {"$set": {"archived": new_status}})
        return jsonify(success=True, archived=new_status)
    return jsonify(success=False), 404

@app.route('/comments/<id_gallery>', methods=['GET'])
def comments(id_gallery):
    try:
        active_user = session.get('username', None)

        comments = list(db.comment.find({"id_gallery": id_gallery}))

        for comment in comments:
            liked_by = comment.get('liked_by', [])
            if active_user in liked_by:
                comment['liked_by_active_user'] = True
            else:
                comment['liked_by_active_user'] = False

            for reply in comment.get('replies', []):
                liked_by_reply = reply.get('liked_by', [])
                if active_user in liked_by_reply:
                    reply['liked_by_active_user'] = True
                else:
                    reply['liked_by_active_user'] = False

        formatted_comments = [{
            '_id': str(comment['_id']),
            'username': comment['username'],
            'image': comment['image'],
            'comment': comment['comment'],
            'likes': comment['likes'],
            'tanggal': comment['tanggal'],
            'liked_by_active_user': comment['liked_by_active_user'],
            'replies': [{
                'username': reply['username'],
                'image': reply['image'],
                'comment': reply['comment'],
                'likes': reply['likes'],
                'tanggal': reply['tanggal'],
                'liked_by_active_user': reply['liked_by_active_user']
            } for reply in comment.get('replies', [])]
        } for comment in comments]

        return jsonify(comments=formatted_comments, active_user=active_user)

    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/update_likes', methods=['POST'])
def update_likes():
    try:
        data = request.get_json()
        comment_id = data.get('comment_id')

        if not comment_id:
            return jsonify(success=False, error="Missing comment ID"), 400

        comment = db.comment.find_one({"_id": ObjectId(comment_id)})
        if not comment:
            return jsonify(success=False, error="Comment not found"), 404

        active_user = session.get('username')
        liked_by = comment.get('liked_by', [])

        if active_user in liked_by:
            db.comment.update_one(
                {"_id": ObjectId(comment_id)},
                {"$inc": {"likes": -1}, "$pull": {"liked_by": active_user}}
            )
            updated_comment = db.comment.find_one({"_id": ObjectId(comment_id)})

            formatted_comment = {
                '_id': str(updated_comment['_id']), 
                'username': updated_comment['username'],
                'comment': updated_comment['comment'],
                'likes': updated_comment['likes'],
                'tanggal': updated_comment['tanggal']
            }

            return jsonify(comment=formatted_comment, success=True, liked=False)
        else:
            db.comment.update_one(
                {"_id": ObjectId(comment_id)},
                {"$inc": {"likes": 1}, "$push": {"liked_by": active_user}}
            )

            updated_comment = db.comment.find_one({"_id": ObjectId(comment_id)})

            formatted_comment = {
                '_id': str(updated_comment['_id']), 
                'username': updated_comment['username'],
                'comment': updated_comment['comment'],
                'likes': updated_comment['likes'],
                'tanggal': updated_comment['tanggal']
            }
            
            return jsonify(comment=formatted_comment, success=True, liked=True)

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

from bson.objectid import ObjectId

@app.route('/update_likes_reply', methods=['POST'])
def update_likes_reply():
    try:
        data = request.get_json()
        comment_id = data.get('comment_id')
        reply_index = data.get('reply_index')

        if not comment_id or reply_index is None:
            return jsonify(success=False, error="Missing comment ID or reply index"), 400

        comment = db.comment.find_one({"_id": ObjectId(comment_id)})
        if not comment or 'replies' not in comment:
            return jsonify(success=False, error="Comment or replies not found"), 404

        replies = comment['replies']
        if reply_index < 0 or reply_index >= len(replies):
            return jsonify(success=False, error="Invalid reply index"), 400

        reply = replies[reply_index]
        active_user = session.get('username')
        liked_by = reply.get('liked_by', [])

        if active_user in liked_by:
            db.comment.update_one(
                {"_id": ObjectId(comment_id), "replies": {"$elemMatch": reply}},
                {"$inc": {"replies.$.likes": -1}, "$pull": {"replies.$.liked_by": active_user}}
            )
            updated_comment = db.comment.find_one({"_id": ObjectId(comment_id)})

            updated_reply = next((r for r in updated_comment['replies'] if r['tanggal'] == reply['tanggal']), None)

            if updated_reply:
                formatted_reply = {
                    'username': updated_reply['username'],
                    'comment': updated_reply['comment'],
                    'likes': updated_reply['likes'],
                    'tanggal': updated_reply['tanggal']
                }

                return jsonify(reply=formatted_reply, success=True, liked=False)
            else:
                return jsonify(success=False, error="Updated reply not found"), 404

        else:
            db.comment.update_one(
                {"_id": ObjectId(comment_id), "replies": {"$elemMatch": reply}},
                {"$inc": {"replies.$.likes": 1}, "$push": {"replies.$.liked_by": active_user}}
            )
            updated_comment = db.comment.find_one({"_id": ObjectId(comment_id)})

            updated_reply = next((r for r in updated_comment['replies'] if r['tanggal'] == reply['tanggal']), None)

            if updated_reply:
                formatted_reply = {
                    'username': updated_reply['username'],
                    'comment': updated_reply['comment'],
                    'likes': updated_reply['likes'],
                    'tanggal': updated_reply['tanggal']
                }

                return jsonify(reply=formatted_reply, success=True, liked=True)
            else:
                return jsonify(success=False, error="Updated reply not found"), 404

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
    
@app.route('/update_comment', methods=['POST'])
def update_comment():
    try:
        comment_id = request.json.get('comment_id')
        new_comment = request.json.get('new_comment')
        active_user = session.get('username', None)

        if not active_user:
            return jsonify({'error': 'User not logged in'}), 403

        comment = db.comment.find_one({"_id": ObjectId(comment_id)})

        if not comment:
            return jsonify({'error': 'Comment not found'}), 404

        if comment['username'] != active_user:
            return jsonify({'error': 'Permission denied'}), 403

        tanggal_post = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        db.comment.update_one(
            {"_id": ObjectId(comment_id)},
            {"$set": {"comment": new_comment, "tanggal": tanggal_post}}
        )

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    try:
        data = request.get_json()
        comment_id = data.get('comment_id')

        if not comment_id:
            return jsonify(success=False, error="Missing comment ID"), 400

        result = db.comment.delete_one({"_id": ObjectId(comment_id)})

        if result.deleted_count == 1:
            return jsonify(success=True)
        else:
            return jsonify(success=False, error="Comment not found"), 404

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/add_reply', methods=['POST'])
def add_reply():
    try:
        data = request.get_json()
        comment_id = data.get('comment_id')
        reply_text = data.get('reply')
        id_user = session.get('_id')
        active_user = session.get('username')
        user_image = session.get('profile_pic_real')
        tanggal_post = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not comment_id or not reply_text:
            return jsonify(success=False, error="Missing comment ID or reply text"), 400

        reply = {
            'id_user': id_user,
            'username': active_user,
            'image': user_image,
            'comment': reply_text,
            'tanggal': tanggal_post,
            'likes': 0,
            'liked_by': []
        }

        db.comment.update_one(
            {"_id": ObjectId(comment_id)},
            {"$push": {"replies": reply}}
        )

        return jsonify(success=True)

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
    
@app.route('/update_reply', methods=['POST'])
def update_reply():
    try:
        data = request.get_json()
        comment_id = data.get('comment_id')
        reply_index = data.get('reply_index')
        new_reply = data.get('new_reply')
        active_user = session.get('username', None)

        if not comment_id or reply_index is None:
            return jsonify(success=False, error="Missing comment ID or reply index"), 400

        comment = db.comment.find_one({"_id": ObjectId(comment_id)})

        if not comment or 'replies' not in comment:
            return jsonify(success=False, error="Comment or replies not found"), 404

        replies = comment['replies']
        if reply_index < 0 or reply_index >= len(replies):
            return jsonify(success=False, error="Invalid reply index"), 400

        reply = replies[reply_index]

        if reply['username'] != active_user:
            return jsonify({'error': 'Permission denied'}), 403

        reply['comment'] = new_reply
        reply['tanggal'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        db.comment.update_one(
            {"_id": ObjectId(comment_id)},
            {"$set": {f"replies.{reply_index}": reply}}
        )

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/delete_reply', methods=['POST'])
def delete_reply():
    try:
        data = request.get_json()
        comment_id = data.get('comment_id')
        reply_index = data.get('reply_index')
        active_user = session.get('username', None)

        if not comment_id or reply_index is None:
            return jsonify(success=False, error="Missing comment ID or reply index"), 400

        comment = db.comment.find_one({"_id": ObjectId(comment_id)})

        if not comment or 'replies' not in comment:
            return jsonify(success=False, error="Comment or replies not found"), 404

        replies = comment['replies']
        if reply_index < 0 or reply_index >= len(replies):
            return jsonify(success=False, error="Invalid reply index"), 400

        reply = replies[reply_index]

        if reply['username'] != active_user:
            return jsonify({'error': 'Permission denied'}), 403

        replies.pop(reply_index)

        db.comment.update_one(
            {"_id": ObjectId(comment_id)},
            {"$set": {"replies": replies}}
        )

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/postDetail/<type>/<_id>', methods=['GET', 'POST'])
def postDetail(type, _id):
    if request.method == 'POST':
        id = request.form['_id']
        id_user = session.get('_id')
        user = session.get('username')
        image = session.get('profile_pic_real')
        type_ = request.form['type']
        comment = request.form['comment']
        tanggal_post = datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
        
        doc = {
            'id_gallery': id,
            'id_user': id_user,
            'username': user,
            'image': image,
            'type_gal': type_,
            'comment': comment,
            'likes': 0,
            'tanggal': tanggal_post,
            'replies': []
        }
        
        db.comment.insert_one(doc)
        return redirect(url_for("postDetail", type=type, _id=_id))
    
    id = ObjectId(_id)
    if type == 'fjkt':
        type_gal = db.fjkt.find_one({"_id": id})
    elif type == 'fanart':
        type_gal = db.fanart.find_one({"_id": id})
    else:
        return jsonify({'error': 'Invalid type'}), 400

    return jsonify({'nama': type_gal['nama'], 'deskripsi': type_gal['deskripsi'], 'gambar': type_gal.get('gambar', '')})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)