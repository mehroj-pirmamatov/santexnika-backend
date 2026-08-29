# Xavfsizlik Tuzatishlari va Majburiy Qadamlar (SECURITY_FIX.md)

Ushbu hujjat loyihadagi maxfiy ma'lumotlar (server IP, root parol, JWT secret_key, PostgreSQL paroli) ochiq holda GitHub'ga chiqqanidan so'ng amalga oshirilgan tuzatishlar va loyiha egasi (superadmin) tomonidan serverda **zudlik bilan bajarilishi shart bo'lgan** xavfsizlik amallarini o'z ichiga oladi.

---

## 1. Nima uchun oddiy `git rm` yetarli emas?

Git versiya boshqaruv tizimi har bir commit'ning to'liq tarixini va o'zgarishlarini saqlab boradi. Agar siz maxfiy ma'lumot (masalan `deploy_remote.py`) bo'lgan faylni shunchaki `git rm` qilib o'chirsangiz ham, fayl yangi commit'da o'chadi, lekin **o'tmishdagi commit tarixida (masalan `b73fd24` commitda) parol baribir saqlanib qolaveradi**. Har qanday odam `git log -p` yoki eski commit'ni checkout qilib maxfiy parollarni o'qib olishi mumkin.

Shu sababli, `git filter-repo` yordamida **butun Git commit tarixini qayta yozish** va ochiq ma'lumotlarni tarixdan butunlay o'chirib tashlash talab etiladi.

---

## 2. Git Tarixidan Maxfiylikni To'liq O'chirish va Force Push

Lokal kompyuteringizda quyidagi buyruqni bering:

```bash
# 1. Git tarixini tozalash skriptini ishga tushiring:
bash cleanup_git_history.sh

# 2. GitHub-ga tozalangan tarixni majburiy (force) push qiling:
git remote add origin https://github.com/mehroj-pirmamatov/santexnika-backend.git 2>/dev/null || true
git push origin --force --all
git push origin --force --tags
```

---

## 3. Server Egasining QO'LDA Bajarishi Shart Bo'lgan Amallar

Chunki eski server paroli va bazaviy kalitlar ochiq internetga chiqqan, **serverda quyidagi 5 ta xavfsizlik amalni zudlik bilan qo'lda bajarishingiz shart**:

### 1. Server Root Parolini Zudlik bilan Almashtirish
Serverga SSH orqali kiring va parolni almashtiring:
```bash
passwd
```

### 2. SSH orqali Parol bilan Kirishni O'chirish (Faqat SSH Key ishlatish)
1. Serveringizga o'z SSH public key'ingizni qo'shing (`~/.ssh/authorized_keys`).
2. `/etc/ssh/sshd_config` faylini tahrirlang:
   ```bash
   nano /etc/ssh/sshd_config
   ```
   Quyidagi qatorlarni toping va o'zgartiring:
   ```ini
   PasswordAuthentication no
   PubkeyAuthentication yes
   ```
3. SSH xizmatini qayta ishga tushiring:
   ```bash
   systemctl restart sshd
   ```

### 3. `SECRET_KEY`ni Yangilash (JWT Tokenlarni bekor qilish)
Eski JWT secret key tarqalgani sababli, yangi maxfiy kalit generatsiya qiling:
```bash
openssl rand -hex 32
```
Hosil bo'lgan yangi matnni serverdagi `/root/santexnika-backend/.env` faylidagi `SECRET_KEY=` qiymatiga qo'ying.
> ⚠️ **Eslatma:** Bu amal ilgari foydalanuvchilarga berilgan barcha eski JWT tokenlarni yaroqsiz qiladi va ular qayta tizimga kirishi (login) kerak bo'ladi.

### 4. PostgreSQL Parolini Almashtirish
Serverdagi `.env` faylida PostgreSQL parolini yangilang (`POSTGRES_PASSWORD=` va `DATABASE_URL=` ichida), so'ngra konteynerlarni qayta ishga tushiring:
```bash
cd /root/santexnika-backend
docker compose down
docker compose up -d --build
```

### 5. Server Loglarini Tekshirish (Ruxsatsiz kirish bo'lmaganini tasdiqlash)
Eski parol bilan serverga begona shaxslar kirmaganini tekshirish uchun loglarni va oxirgi ulanishlarni ko'ring:
```bash
# Oxirgi ulanishlar ro'yxati:
last -a

# SSH autentifikatsiya loglari:
grep "Accepted" /var/log/auth.log || grep "Accepted" /var/log/secure
```
