import os
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import pymysql

import os
import PIL
import clip
import torch
import csv

from os.path import join, dirname, realpath

app = Flask(__name__, static_url_path="/static")
# java file upload_path
UPLOADS_PATH = join(dirname(realpath(__file__)), 'C:/Users/User/Documents/spring/H&S/src/main/webapp/data/')
# python upload_path
# UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/images/')

# UPLOAD_FOLDER = '/static/images/'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/')
def image():
    return render_template('product_get.html')

@app.route('/insert', methods=['GET', 'POST'])
def imagefile():
    if request.method == 'POST':

        os.chdir("/")

        f = open(join(dirname(realpath(__file__)), 'keywords.csv'), 'r', encoding='utf-8')
        rdr = csv.reader(f)
        text = []
        change = []
        for line in rdr:
            text.append(line[0])
            change.append(line[1])
        f.close()   

        # Load the model
        device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        model, preprocess = clip.load('ViT-B/32', device)

        """## Zero-shot Prediction"""

        # Prepare the inputs
        user_img = request.files['user_img']
        user_img.save(UPLOADS_PATH + secure_filename(user_img.filename))
        # user_img.save(os.path.join(app.config['UPLOAD_FOLDER'], user_imgname))
        image = PIL.Image.open(user_img)

        #display(image)
        image_input = preprocess(image).unsqueeze(0).to(device)
        text_inputs = torch.cat([clip.tokenize(f"a photo of a {c}") for c in text]).to(device)

        PATH = './moodmodel.pth'
        batch_size = 1

        # Calculate features
        with torch.no_grad():
            image_features = model.encode_image(image_input)
            text_features = model.encode_text(text_inputs)

        # Pick the top 5 most similar labels for the image
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)


        values, indices = similarity[0].topk(1)


        # Print the result
        keyword = []
        for value, index in zip(values, indices):
            
            keyword.append(text[index])
                
            print(f"{text[index]:>16s}: {100 * value.item():.2f}%%")

        print (keyword)

        db = pymysql.connect(host="localhost", port=3306,
        user="root", password="1234", database="smartproject",
        charset="utf8")
        cursor = db.cursor()
        
        name = request.form['name']
        price = request.form['price']
        detail = request.form['detail']
        stock = request.form['stock']
        gender = request.form['gender']
        size = request.form['size']
        image = secure_filename(user_img.filename)
        keyword = keyword

        # DB 데이터 삽입하기
        cursor.execute('use smartproject;')
        cursor.execute('insert into shop_product (name, price, detail, stock, gender, size, image, keyword) values (%s,%s,%s,%s,%s,%s,%s,%s)', (name, price, detail, stock, gender, size, image, keyword))

        # DB에 수정사항 반영하기
        db.commit()
        # mysql cursor 종료하기
        db.close()
        return redirect("http://localhost:8080/H&S/admin/ProductMgr.jsp")

# MySQL connect Test
@app.route('/dbtest', methods=['POST'])
def dbtest():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        detail = request.form['detail']
        stock = request.form['stock']
        gender = request.form['gender']
        size = request.form['size']

        db = pymysql.connect(host='localhost', port=3306,
            user='root', password='1234', database='smartproject',
            charset='utf8')
        cursor = db.cursor()

        # DB 데이터 삽입하기
        cursor.execute('use smartproject;')
        cursor.execute('INSERT INTO shop_product (name, price, detail, stock, gender, size) VALUES (%s,%s,%s,%s,%s,%s)',(name, price, detail, stock, gender, size,))

        # DB에 수정사항 반영하기
        db.commit()
        # mysql cursor 종료하기
        db.close()

        return render_template('product_post.html')



# @app.route('/upload')
# def render_file():
#     return render_template('index.html')

# @app.route('/fileUpload', methods = ['GET', 'POST'])
# def file_upload():
#     if request.method == 'POST':
#         f = request.files['file']
#         f.save('static/images/' + secure_filename(f.filename))
#         return '파일이 저장되었습니다'

if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)