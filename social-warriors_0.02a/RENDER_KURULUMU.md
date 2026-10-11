# 🚀 Social Wars Çok Oyunculu Sunucu - Render.com Kurulum Rehberi

Bu proje, orijinal **Social Wars** oyununu arkadaşlarınızla birlikte oynayabilmeniz için geliştirilmiş özel bir Python/Flask sunucusudur.

---

## 🌟 Neler Eklendi & Yenilikler?

1. **🔐 E-posta & Şifreli Hesap Sistemi:**
   - Oyuncular e-posta ve şifre belirleyerek kendi imparatorluklarını oluşturabilir.
   - Şifreler SQLite veritabanında güvenli hash (Werkzeug PBKDF2) ile saklanır.
2. **👤 Komutan Profil Paneli (`/profile`):**
   - Seviye (Level), XP, Social Cash ve Altın miktarlarını gösterir.
   - Şifre ve Komutan adı değiştirme imkanı sunar.
3. **👥 Otomatik Arkadaş / Komşu Entegrasyonu:**
   - Sunucuya kaydolan tüm arkadaşlarınız oyun içindeki komşu çubuğunda (`friendsInfo`) otomatik olarak müttefikiniz olarak listelenir.
   - Birbirinizin köylerini ziyaret edebilir, yardım edebilir veya savaşabilirsiniz.
4. **🎁 Başlangıç Kaynak Bonusu:**
   - Arkadaşlarla keyifli ve akıcı bir oyun için yeni kayıt olan her hesaba 500 Cash, 50.000 Altın, 50.000 Odun, 25.000 Çelik ve 25.000 Petrol tanımlanır.
5. **☁️ Render.com & Dinamik Domain Desteği:**
   - Render'ın verdiği rastgele port (`PORT`) ve SSL/HTTPS alan adı (`.onrender.com`) dinamik olarak algılanır, Flash SWF loader'a otomatik aktarılır.

---

## 💻 1. Kendi Bilgisayarınızda (Yerel) Çalıştırma

Sunucuyu yerel ağda veya kendi bilgisayarınızda test etmek çok kolay:
1. `social-warriors_0.02a` klasöründeki `baslat.bat` dosyasına çift tıklayın (veya terminalde `python server.py` çalıştırın).
2. Tarayıcınızdan **`http://localhost:5055`** adresine gidin.
3. **"Yeni İmparatorluk Kur (Kayıt Ol)"** seçeneğiyle hesabınızı açıp oynamaya başlayın!

---

## ☁️ 2. dashboard.render.com'a Yükleme Adımları

Render.com üzerinde sunucunuz 7/24 ücretsiz olarak çalışır ve arkadaşlarınızla internet üzerinden istediğiniz zaman oynayabilirsiniz.

### Adım 1: Kodları GitHub'a Yükleyin
1. [GitHub](https://github.com/) üzerinde yeni bir repo oluşturun (Örn: `social-wars-server`, Private veya Public yapabilirsiniz).
2. `social-warriors_0.02a` klasörünün içindeki tüm dosyaları reponuza push edin:
   ```bash
   cd "social-warriors_0.02a"
   git init
   git add .
   git commit -m "Social Wars multiplayer server ready"
   git branch -M main
   git remote add origin https://github.com/KULLANICI_ADINIZ/social-wars-server.git
   git push -u origin main
   ```

### Adım 2: Render.com'da Web Servisi Oluşturun
1. [dashboard.render.com](https://dashboard.render.com/) adresine giriş yapın.
2. Sağ üstteki **"New +"** butonuna tıklayın ve **"Web Service"** seçeneğini seçin.
3. GitHub reponuzu bağlayın (**Connect repository**).
4. Ayarları aşağıdaki gibi doldurun:
   - **Name:** `social-wars-server` (veya istediğiniz bir ad)
   - **Language / Runtime:** `Python`
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 2 -b 0.0.0.0:$PORT server:app`
   - **Instance Type:** `Free` (Ücretsiz plan)
5. Sayfanın altındaki **"Create Web Service"** butonuna tıklayın.

### Adım 3: Oyunu Oynama
- Kurulum tamamlandığında Render size bir adres verecektir (Örn: `https://social-wars-server.onrender.com`).
- Bu linki arkadaşlarınıza gönderin!
- Her arkadaşınız o linkten **Kayıt Ol** diyerek kendi hesabını açacak ve oyuna girebilecektir.

---

## 🎮 Flash Oyuncusu İpucu
Modern tarayıcılarda Flash engelli olduğu için oyunu sorunsuz oynamak için:
- **Ruffle:** Tarayıcı uzantısı olarak Ruffle kurabilirsiniz.
- Veya Flash desteği entegre gelen **Flash Browser**, **Waterfox** veya **Pale Moon** kullanabilirsiniz.
