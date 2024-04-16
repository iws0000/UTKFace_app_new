import os
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image

import numpy as np
import subprocess 

# モデルをダウンロードするコマンドを実行する
command = '''
curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=1o0ltPnpnjT7Ml-GK_UAQ37qXvi_PL8C9" > /dev/null
CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)" 
curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=1o0ltPnpnjT7Ml-GK_UAQ37qXvi_PL8C9" -o my_model.h5
'''

subprocess.run(command, shell=True)

image_size=198

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#import h5py
#model= h5py.File('./my_model.h5')
#import h5py
#model = h5py.File('./my_model.h5', 'r')
model = load_model('/Users/iwas/Desktop/UTKFace_app_new/my_model.keras')
#model = load_model('/Users/iwas/Desktop/UTKFace_app_new/model.h5',compile=False)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            #受け取った画像を読み込み、np形式に変換
            img = image.load_img(filepath, grayscale=False, target_size=(image_size,image_size))
            img = image.img_to_array(img)
            img = np.array([img])
            
            #変換したデータをモデルに渡して予測する
            result = model.predict(img)[0][0]
            pred_answer =  str(result)  + "years old."

            return render_template("index.html",answer=pred_answer)

    return render_template("index.html",answer="")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)

