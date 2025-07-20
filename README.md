# 🔒 QuickPortCheck - Port Tarama Web Uygulaması

Bu proje, temel düzeyde ağ güvenliği testi amacıyla geliştirilmiş bir **port tarama** web uygulamasıdır. Kullanıcılar, belirli bir IP adresine ait **tekil** veya **yaygın portları** tarayarak, bu portların açık veya kapalı olduğunu görüntüleyebilir. Proje, Flask tabanlı arka uç (backend), HTML-CSS-JS ile tasarlanmış kullanıcı dostu bir ön yüz (frontend) ve verilerin saklandığı Firebase veritabanından oluşmaktadır.

---

## 🚀 Proje Amacı

Ağ güvenliğine giriş düzeyinde bir analiz ortamı sunarak:

- Kullanıcıların port durumlarını test etmesini sağlamak,
- Port yönlendirme ve güvenlik duvarı ayarlarını sınamalarına yardımcı olmak,
- Gerçek zamanlı olarak portların açık/kapalı durumunu kullanıcıya göstermek,
- Yapılan taramaların **tarihsel olarak** saklanmasını ve görüntülenmesini sağlamak hedeflenmiştir.

---

## ⚙️ Kullanılan Teknolojiler

- **Python** – Arka uç geliştirme (Flask)
- **HTML, CSS, JavaScript** – Ön yüz tasarımı
- **Firebase Firestore** – Gerçek zamanlı veritabanı
- **Socket Kütüphanesi** – Port kontrol işlemleri
- **Jinja2** – HTML şablonlama

---

## 📌 Temel Özellikler

- 🔎 **Tekil Port Taraması** – Belirtilen IP adresi ve port üzerinden durum kontrolü.
- 🌐 **Popüler Port Taraması** – Yaygın kullanılan portların listesi üzerinden otomatik kontrol.
- 📅 **Geçmiş Taramalar** – Kullanıcının daha önce yaptığı sorguların tarih bazlı kaydı ve listelenmesi.
- 📊 **İstatistiksel Görselleştirme (geliştiriliyor)** – Kullanıcıya ait tarama geçmişinden grafiksel özet sunma (geliştirme aşamasında).
