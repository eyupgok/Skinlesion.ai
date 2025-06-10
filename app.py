import os
import torch
import torchvision.transforms as T
from flask import Flask, request, render_template, redirect, url_for
from PIL import Image
from werkzeug.utils import secure_filename
import sys
from pymongo import MongoClient
from datetime import datetime

# Yerel model dosyasından içe aktarma
from model import CNN as CNN_from_model

# --- Konfigürasyon ---
# Cihazı ayarla
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Model ve Sınıf Bilgileri
MODEL_PATH = 'checkpoint.pt'
NUM_CLASSES = 7
CHOSEN_MODEL = 'mobilenet_v2'

# Sınıf isimleri (train.ipynb dosyasından alınmıştır)
CLASSES = {
    0: ('akiec', 'Actinic keratoses (Aktinik keratoz)'),
    1: ('bcc', 'Basal cell carcinoma (Bazal hücreli karsinom)'),
    2: ('bkl', 'Benign keratosis-like lesions (İyi huylu keratoz benzeri lezyonlar)'),
    3: ('df', 'Dermatofibroma (Dermatofibrom)'),
    4: ('nv', 'Melanocytic nevi (Melanositik nevüs)'),
    5: ('vasc', 'Pyogenic granulomas and hemorrhage (Piyojenik granülomlar ve kanama)'),
    6: ('mel', 'Melanoma (Melanom)'),
}
CLASS_NAMES = [CLASSES[i][1] for i in range(NUM_CLASSES)]

# Flask Uygulaması Kurulumu
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

# --- MongoDB Bağlantısı ---
client = None
collection = None
try:
    # Sunucuya 5 saniye içinde bağlanamazsa hata ver
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    # Bağlantıyı doğrulamak için sunucuya basit bir komut gönder
    client.admin.command('ismaster')
    db = client['cilt_analizi_db']
    collection = db['tahminler']
    print("✅ MongoDB bağlantısı başarılı.")
except Exception as e:
    print(f"❌ MongoDB bağlantı hatası: {e}\nMongoDB sunucusu çalışmıyor olabilir. Geçmiş tahminler özelliği devre dışı bırakıldı.")
    client = None
    collection = None

# --- Model Yükleme ---
def load_model():
    """Modeli ve ağırlıkları yükler."""
    
    # Bu, .pt dosyasının 'train.ipynb' içinde __main__.CNN olarak kaydedilmesiyle ilgili
    # bir sorunu çözmek için geçici bir çözümdür. Pickle'ın sınıfı bulmasını sağlar.
    sys.modules['__main__'].CNN = CNN_from_model
    
    try:
        # Not defterinde modelin tamamı bir sözlük içinde kaydedilmiş.
        # Bu yüzden önce sözlüğü yüklüyoruz. `weights_only=False` gereklidir.
        checkpoint = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=False)
        
        # Sözlüğün içinden asıl model nesnesini alıyoruz.
        # 'model' yaygın olarak kullanılan bir anahtardır.
        model = checkpoint['model']
        print("✅ Model başarıyla yüklendi (sözlükten çıkarıldı).")

    except Exception as e:
        print(f"❌ Model yüklenirken hata: {e}")
        return None

    model.to(DEVICE)
    model.eval()  # Modeli değerlendirme moduna al
    return model

model = load_model()

# --- Görüntü İşleme ---
def transform_image(image_bytes):
    """Yüklenen görüntüyü modele uygun formata dönüştürür."""
    transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor()  # Bu işlem görüntüyü [0, 1] aralığına normalize eder
    ])
    image = Image.open(image_bytes).convert('RGB')
    return transform(image).unsqueeze(0)  # Batch boyutu ekle (1, C, H, W)

# --- Flask Rotaları ---
@app.route('/', methods=['GET'])
def index():
    """Ana sayfayı render eder ve geçmiş tahminleri listeler."""
    predictions = []
    if client is not None and collection is not None:
        try:
            # Tahminleri en yeniden en eskiye doğru sırala
            predictions = list(collection.find().sort('tarih', -1))
        except Exception as e:
            print(f"DB okuma hatası: {e}")
            # Hata durumunda boş liste gönder
            predictions = []
    return render_template('index.html', predictions=predictions)

@app.route('/predict', methods=['POST'])
def predict():
    """Görüntüyü alır, tahmin yapar ve sonucu gösterir."""
    if 'file' not in request.files:
        return render_template('index.html', error="Dosya seçilmedi.")
    
    file = request.files['file']
    
    if file.filename == '':
        return render_template('index.html', error="Dosya seçilmedi.")

    if file and model:
        try:
            # Görüntüyü kaydetme
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.seek(0) # Dosya okuma konumunu başa al
            file.save(filepath)

            # Tahmin
            file.seek(0) # Tekrar başa al
            tensor = transform_image(file.stream)
            tensor = tensor.to(DEVICE)
            
            with torch.no_grad():
                outputs = model(tensor)
                _, predicted_idx = torch.max(outputs, 1)
            
            prediction = CLASS_NAMES[predicted_idx.item()]
            
            # Tahmini veritabanına kaydet
            if client is not None and collection is not None:
                try:
                    prediction_data = {
                        'dosya_adi': filename,
                        'tahmin': prediction,
                        'tarih': datetime.utcnow()
                    }
                    collection.insert_one(prediction_data)
                except Exception as e:
                    print(f"DB yazma hatası: {e}")

            # Ana sayfayı hem tahmin sonucuyla hem de güncel geçmişle render et
            all_predictions = []
            if client is not None and collection is not None:
                all_predictions = list(collection.find().sort('tarih', -1))
                
            return render_template('index.html', prediction=prediction, image_file=filename, predictions=all_predictions)

        except Exception as e:
            print(f"Tahmin sırasında bir hata oluştu: {e}")
            return render_template('index.html', error="Tahmin sırasında bir hata oluştu. Lütfen geçerli bir resim dosyası yüklediğinizden emin olun.")
            
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 'static/uploads' klasörünün varlığını kontrol et
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    app.run(debug=True) 