#!/usr/bin/env python3
"""
Seed Data Script for Santexnika Backend API
Fills the production database with realistic, structured sample data via FastAPI endpoints.

Usage:
    python seed_data.py [--url BASE_URL] [--phone SUPERADMIN_PHONE] [--password SUPERADMIN_PASSWORD]
"""

import os
import sys
import argparse
import getpass
import requests
from typing import Dict, List, Optional, Tuple

DEFAULT_BASE_URL = os.getenv("BASE_URL", "https://santexnika-loyha.duckdns.org")

# Sample Categories
CATEGORIES_DATA = [
    "Trubalar va fitinglar",
    "Kranlar va aralashtirgichlar",
    "Dush tizimlari va kabinalari",
    "Unitazlar va bidelar",
    "Rakovinalar va vannalar",
    "Isitish jihozlari (boyler, konvektor)",
    "Filtrlar va suv tozalash",
    "Santexnika asboblari va yordamchi qurilmalar"
]

# Sample Products by Category Name
PRODUCTS_DATA = {
    "Trubalar va fitinglar": [
        {
            "name": "Polipropilen truba PN20 20mm (metr)",
            "description": "Sovuq va issiq suv ta'minoti uchun yuqori sifatli polipropilen truba.",
            "price": 18000,
            "wholesale_price": 14000,
            "wholesale_min_qty": 20,
            "stock": 150,
            "image_url": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop"
        },
        {
            "name": "Polipropilen truba PN25 shisha tolali 25mm (metr)",
            "description": "Isitish tizimlari uchun shisha tolali mustahkamlangan truba.",
            "price": 28000,
            "discount_price": 24000,
            "wholesale_price": 21000,
            "wholesale_min_qty": 15,
            "stock": 120,
            "image_url": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop"
        },
        {
            "name": "Kanalizatsiya trubasi 110mm 2m PVC",
            "description": "Ichki kanalizatsiya tizimlari uchun shovqinsiz PVX truba.",
            "price": 65000,
            "stock": 45,
            "image_url": "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39?w=600&auto=format&fit=crop"
        },
        {
            "name": "Polipropilen tirsak 90° 20mm",
            "description": "Trubalarni 90 daraja burish uchun burchak fitingi.",
            "price": 4500,
            "wholesale_price": 3500,
            "wholesale_min_qty": 50,
            "stock": 200,
            "image_url": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop"
        },
        {
            "name": "Burchakli sharli kran 1/2' brass",
            "description": "Gurunj korpusli, rezbali burchakli suv uzish krani.",
            "price": 45000,
            "discount_price": 38000,
            "stock": 60,
            "image_url": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop"
        },
        {
            "name": "Metalloplastik truba 16mm (metr)",
            "description": "Moslashuvchan issiq pol va santexnika trubasi.",
            "price": 15000,
            "stock": 0,  # Intentional out of stock item
            "image_url": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop"
        }
    ],
    "Kranlar va aralashtirgichlar": [
        {
            "name": "Oshxona uchun aralashtirgich Ferro Smile",
            "description": "Xrom qoplamali, buriluvchi jo'mrakli zamonaviy oshxona kran modelidir.",
            "price": 320000,
            "discount_price": 285000,
            "stock": 18,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Vanna uchun sharli aralashtirgich Grohe Eurosmart",
            "description": "Germaniya brendi, keramik kartrijli va dush leykasi biriktirgichi bilan.",
            "price": 1450000,
            "stock": 8,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Rakovina uchun moslashuvchan aralashtirgich Black Edition",
            "description": "Qora mat rangli, silikon moslashuvchan shlangli premium kran.",
            "price": 420000,
            "discount_price": 370000,
            "stock": 25,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Oshxona kran-filtr 2-in-1 Nerjaveyka",
            "description": "Nervajeyka korpusli, ham toza ichimlik suvi ham maishiy suv uchun alohida jo'mrakli.",
            "price": 580000,
            "stock": 12,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Termostatli aralashtirgich Hansgrohe Ecostat",
            "description": "Suv haroratini avtomatik ushlab turuvchi xavfsiz dush aralashtirgichi.",
            "price": 2800000,
            "stock": 4,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Sensorli avtomatik kran SmartTap",
            "description": "Infraqizil datchikli, suvsizlanish va gigiyena uchun teginishsiz kran.",
            "price": 950000,
            "stock": 2,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        }
    ],
    "Dush tizimlari va kabinalari": [
        {
            "name": "Dush kabinasi 90x90 shaffof oyna va baland poddon",
            "description": "Toblangan shisha (6mm), alyuminiy profil va mustahkam akril poddonli kabina.",
            "price": 3400000,
            "discount_price": 3100000,
            "stock": 5,
            "image_url": "https://images.unsplash.com/photo-1620626011761-996317b8d101?w=600&auto=format&fit=crop"
        },
        {
            "name": "Tropik dush tizimi rolikli stoyka bilan Black Matt",
            "description": "Keng tropik yomg'ir leykasi va qo'l leykasi bilan qora mot dush ustuni.",
            "price": 1250000,
            "stock": 14,
            "image_url": "https://images.unsplash.com/photo-1620626011761-996317b8d101?w=600&auto=format&fit=crop"
        },
        {
            "name": "Dush ustuni Hansgrohe Crometta 160",
            "description": "Yuqori sifatli nemis dush stoykasi va aralashtirgich to'plami.",
            "price": 2100000,
            "stock": 6,
            "image_url": "https://images.unsplash.com/photo-1620626011761-996317b8d101?w=600&auto=format&fit=crop"
        },
        {
            "name": "Gidromassaj dush paneli Edelstahl Premium",
            "description": "Zanglamaydigan po'latdan 4 xil gidromassaj forsunka va tropik dushli panel.",
            "price": 1850000,
            "discount_price": 1600000,
            "stock": 3,
            "image_url": "https://images.unsplash.com/photo-1620626011761-996317b8d101?w=600&auto=format&fit=crop"
        },
        {
            "name": "Dush uchun quvur va leyka komplekti Lemark",
            "description": "5 xil rejimda suv purkovchi leyka va 1.5m moslashuvchan zanglamaydigan shlang.",
            "price": 185000,
            "stock": 35,
            "image_url": "https://images.unsplash.com/photo-1620626011761-996317b8d101?w=600&auto=format&fit=crop"
        }
    ],
    "Unitazlar va bidelar": [
        {
            "name": "Osilma unitaz Cersanit CleanOn installyatsiya bilan",
            "description": "Rimless (jiyeksiz) gigiyenik osilma unitaz va yashirin installyatsiya tizimi.",
            "price": 2350000,
            "discount_price": 2150000,
            "stock": 10,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Kompakt unitaz Kola monoblok micro-lift",
            "description": "Keramik monoblok unitaz, micro-lift sekin tushuvchi qopqoq bilan.",
            "price": 1100000,
            "stock": 15,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Devorga osiladigan elektron bide-unitaz SmartClean",
            "description": "Suv isitkich, quritgich va pult bilan boshqariladigan smart unitaz.",
            "price": 3500000,
            "stock": 2,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Tualet uchun hygienic dush komplekti Bossini",
            "description": "Devorga o'rnatiladigan gigiyenik dush va aralashtirgich krani.",
            "price": 380000,
            "stock": 22,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Unitaz uchun o'rindiq cover soft-close",
            "description": "Duroplast materialidan tayyorlangan, zarbga chidamli va sekin yopiladigan qopqoq.",
            "price": 160000,
            "stock": 40,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        }
    ],
    "Rakovinalar va vannalar": [
        {
            "name": "Akril vanna Ravak 170x75cm oyoqlari bilan",
            "description": "Yuqori zichlikdagi akril, issiqlikni uzoq saqlaydi va chizilishga chidamli.",
            "price": 3200000,
            "discount_price": 2900000,
            "stock": 4,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Granit oshxona rakovinasi Blanco 2-chashka",
            "description": "Sun'iy granit toshidan tayyorlangan, dog' va issiqqa chidamli oshxona moykasi.",
            "price": 1950000,
            "stock": 7,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Keramik ustki rakovina Cersanit Oval 50cm",
            "description": "Stol ustiga qo'yiladigan zamonaviy oval keramik rakovina.",
            "price": 520000,
            "stock": 16,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Tumbali rakovina komplekti 80cm MDF Suvga chidamli",
            "description": "Yoritgichli ko'zgu va MDF suvga chidamli shkafi bilan tayyor mebel komplekti.",
            "price": 1800000,
            "discount_price": 1650000,
            "stock": 9,
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        },
        {
            "name": "Choyug'un vanna Roca Continental 150x70",
            "description": "Klassik cho'yan vanna, emal qoplamali va shovqinsiz.",
            "price": 3500000,
            "stock": 0,  # Intentional out of stock item
            "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=600&auto=format&fit=crop"
        }
    ],
    "Isitish jihozlari (boyler, konvektor)": [
        {
            "name": "Elektr suv isitgich (Boyler) Ariston PRO1 R 80L",
            "description": "80 litrli emallangan bak va TitanShield zanglashdan hidoya tizimi.",
            "price": 1850000,
            "discount_price": 1680000,
            "stock": 12,
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600&auto=format&fit=crop"
        },
        {
            "name": "Ikki konturli gaz qozoni Navien Deluxe 24kW",
            "description": "Uy isitish va issiq suv uchun tejamkor ikki konturli gaz kotyoli.",
            "price": 3500000,
            "discount_price": 3250000,
            "stock": 5,
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600&auto=format&fit=crop"
        },
        {
            "name": "Alyuminiy radiatsiya seksiyasi Tenrad 500/80",
            "description": "Yuqori issiqlik o'tkazuvchanlikka ega bimetall radiator seksiyasi.",
            "price": 115000,
            "wholesale_price": 102000,
            "wholesale_min_qty": 30,
            "stock": 180,
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600&auto=format&fit=crop"
        },
        {
            "name": "Elektr konvektor isitgich Midea 2000W",
            "description": "Termostat va taymerli, devorga hamda oyoqqa o'rnatiladigan konvektor.",
            "price": 650000,
            "discount_price": 580000,
            "stock": 20,
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600&auto=format&fit=crop"
        },
        {
            "name": "Issiq pol uchun kollektor guruhi 4 yolli",
            "description": "Rasmxodomerlar va balansirovkali gurunj kollektor tarqatgich.",
            "price": 1150000,
            "stock": 8,
            "image_url": "https://images.unsplash.com/photo-1585338107529-13afc5f02586?w=600&auto=format&fit=crop"
        }
    ],
    "Filtrlar va suv tozalash": [
        {
            "name": "Teskari osmos suv filtri Aquaphor OSMO 50",
            "description": "5 bosqichli tozalash, 10 litrli bak va alohida jo'mrakli zamonaviy filtr.",
            "price": 1750000,
            "discount_price": 1550000,
            "stock": 14,
            "image_url": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop"
        },
        {
            "name": "Asosiy kirish suv filtri Big Blue 20 kunjut",
            "description": "Butun xonadonga kiruvchi suvni qum va zangdan tozalovchi kolba.",
            "price": 3400000,
            "stock": 28,
            "image_url": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop"
        },
        {
            "name": "Almashtiriladigan kartrijlar to'plami 3 bosqichli",
            "description": "Mexanik, ko'mir va ion almashinuvchi 3 dona kartrij komplekti.",
            "price": 145000,
            "wholesale_price": 125000,
            "wholesale_min_qty": 5,
            "stock": 75,
            "image_url": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop"
        },
        {
            "name": "Suv yumshatuvchi magnetik filtr 1/2'",
            "description": "Kir yuvish mashinasi va boyler uchun qaqshash (nakip) ga qarshi polifosfat filtr.",
            "price": 95000,
            "stock": 40,
            "image_url": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop"
        },
        {
            "name": "Kattalashgan sig'imli UB sterilizator suv filtri",
            "description": "Suvdagi bakteriya va mikroblarni ultrabinafsha nurlar bilan yo'qotuvchi modul.",
            "price": 1200000,
            "stock": 3,
            "image_url": "https://images.unsplash.com/photo-1584992236310-6edddc08acff?w=600&auto=format&fit=crop"
        }
    ],
    "Santexnika asboblari va yordamchi qurilmalar": [
        {
            "name": "Polipropilen borularni payvandlash apparati 1500W",
            "description": "Dazmol komplekti: 20, 25, 32, 40mm nasadkalar va metall chemodan.",
            "price": 480000,
            "discount_price": 420000,
            "stock": 15,
            "image_url": "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=600&auto=format&fit=crop"
        },
        {
            "name": "Sozlanuvchi santexnik kaliti Knipex Cobra 250mm",
            "description": "Professional avtomatik sozlanuvchi quvur kaliti.",
            "price": 680000,
            "stock": 10,
            "image_url": "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=600&auto=format&fit=crop"
        },
        {
            "name": "Santexnika silikoni germetik Transparent 310ml",
            "description": "Zamburug'ga va suvga chidamli shaffof sanitariya silikoni.",
            "price": 35000,
            "wholesale_price": 29000,
            "wholesale_min_qty": 12,
            "stock": 150,
            "image_url": "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=600&auto=format&fit=crop"
        },
        {
            "name": "Fum lenta PTFE 19mm x 15m yuqori sifat",
            "description": "Rezbali birikmalarni zanglash va suv sizib chiqishidan zichlovchi lenta.",
            "price": 8000,
            "wholesale_price": 6000,
            "wholesale_min_qty": 50,
            "stock": 300,
            "image_url": "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=600&auto=format&fit=crop"
        },
        {
            "name": "Trubalar uchun qaychi (Truborez) 42mm metal",
            "description": "Polipropilen va plastmassa trubalarni to'g'ri kesish uchun tishli truborez.",
            "price": 120000,
            "stock": 25,
            "image_url": "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=600&auto=format&fit=crop"
        }
    ]
}

# Test Users Sample Data
TEST_USERS = [
    {
        "username": "test_user_1",
        "phone_number": "+998901112233",
        "password": "Password123!",
        "address": "Toshkent shahri, Yunusobod tumani, 14-mavze",
        "payment_method": "cash",
        "order_status": "yangi"
    },
    {
        "username": "test_user_2",
        "phone_number": "+998901112234",
        "password": "Password123!",
        "address": "Toshkent shahri, Chilonzor tumani, Qatortol ko'chasi 25",
        "payment_method": "payme",
        "order_status": "tayyorlanmoqda"
    },
    {
        "username": "test_user_3",
        "phone_number": "+998901112235",
        "password": "Password123!",
        "address": "Samarqand shahri, Dagbitskaya ko'chasi 8",
        "payment_method": "click",
        "order_status": "yetkazildi"
    }
]


def parse_args():
    parser = argparse.ArgumentParser(description="Santexnika Backend Seed Script")
    parser.add_argument("--url", default=DEFAULT_BASE_URL, help="Base API URL")
    parser.add_argument("--phone", default=os.getenv("SUPERADMIN_PHONE"), help="Superadmin Phone Number")
    parser.add_argument("--password", default=os.getenv("SUPERADMIN_PASSWORD"), help="Superadmin Password")
    return parser.parse_args()


def get_credentials(args) -> Tuple[str, str]:
    phone = args.phone
    password = args.password

    if not phone:
        phone = input("Superadmin telefon raqami (masalan: +998901234567): ").strip()
    if not password:
        password = getpass.getpass("Superadmin paroli: ").strip()

    if not phone or not password:
        print("[XATO] Telefon raqam va parol kiritilishi shart!")
        sys.exit(1)

    return phone, password


def login_superadmin(base_url: str, phone: str, password: str) -> str:
    print(f"\n[1/5] Superadmin sifatini tasdiqlash ({base_url}/auth/login)...")
    url = f"{base_url.rstrip('/')}/auth/login"
    payload = {"phone_number": phone, "password": password}
    
    try:
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            print("  [OK] Superadmin muvaffaqiyatli tizimga kirdi.")
            return token
        else:
            print(f"  [XATO] Login bajarilmadi! Status code: {resp.status_code}, Javob: {resp.text}")
            sys.exit(1)
    except Exception as e:
        print(f"  [XATO] Server bilan ulanishda xatolik: {e}")
        sys.exit(1)


def sync_categories(base_url: str, token: str) -> Tuple[Dict[str, int], int, int]:
    print(f"\n[2/5] Kategoriyalarni tekshirish va yaratish (POST /categories/)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Fetch existing categories
    existing_map: Dict[str, int] = {}
    try:
        r = requests.get(f"{base_url.rstrip('/')}/categories/", timeout=15)
        if r.status_code == 200:
            for cat in r.json():
                existing_map[cat["name"]] = cat["id"]
    except Exception as e:
        print(f"  [OGOHLANTIRISH] Kategoriyalarni olishda xatolik: {e}")

    created_count = 0
    existing_count = 0

    for cat_name in CATEGORIES_DATA:
        if cat_name in existing_map:
            existing_count += 1
            print(f"  - Category: '{cat_name}' (mavjud, ID: {existing_map[cat_name]})")
        else:
            resp = requests.post(
                f"{base_url.rstrip('/')}/categories/",
                json={"name": cat_name},
                headers=headers,
                timeout=15
            )
            if resp.status_code in (200, 201):
                cat_obj = resp.json()
                existing_map[cat_name] = cat_obj["id"]
                created_count += 1
                print(f"  + Category: '{cat_name}' (Yaratildi, ID: {cat_obj['id']})")
            else:
                print(f"  ! Category xato '{cat_name}': {resp.status_code} - {resp.text}")

    return existing_map, created_count, existing_count


def sync_products(base_url: str, token: str, category_map: Dict[str, int]) -> Tuple[List[dict], int, int]:
    print(f"\n[3/5] Mahsulotlarni tekshirish va yaratish (POST /products/)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Fetch existing products
    existing_products: Dict[str, int] = {}
    try:
        r = requests.get(f"{base_url.rstrip('/')}/products/", timeout=15)
        if r.status_code == 200:
            for p in r.json():
                existing_products[p["name"]] = p["id"]
    except Exception as e:
        print(f"  [OGOHLANTIRISH] Mavjud mahsulotlarni olishda xatolik: {e}")

    created_count = 0
    existing_count = 0
    all_products_list = []

    for cat_name, products in PRODUCTS_DATA.items():
        cat_id = category_map.get(cat_name)
        if not cat_id:
            print(f"  ! Kategoriya topilmadi '{cat_name}', o'tkazib yuborilmoqda.")
            continue

        for p_data in products:
            p_name = p_data["name"]
            if p_name in existing_products:
                existing_count += 1
                all_products_list.append({"id": existing_products[p_name], "name": p_name, "stock": p_data.get("stock", 10)})
                print(f"  - Product: '{p_name}' (mavjud)")
            else:
                payload = {**p_data, "category_id": cat_id}
                resp = requests.post(
                    f"{base_url.rstrip('/')}/products/",
                    json=payload,
                    headers=headers,
                    timeout=15
                )
                if resp.status_code in (200, 201):
                    new_p = resp.json()
                    existing_products[p_name] = new_p["id"]
                    all_products_list.append(new_p)
                    created_count += 1
                    print(f"  + Product: '{p_name}' -> {p_data['price']:,} so'm (Yaratildi)")
                else:
                    print(f"  ! Product xato '{p_name}': {resp.status_code} - {resp.text}")

    return all_products_list, created_count, existing_count


def sync_users_and_orders(
    base_url: str,
    admin_token: str,
    available_products: List[dict]
) -> Tuple[int, int, int]:
    print(f"\n[4/5] Test foydalanuvchilar va buyurtmalarni shakllantirish...")
    
    users_created = 0
    users_existing = 0
    orders_created = 0

    # Filter products that have stock > 0
    in_stock_products = [p for p in available_products if p.get("stock", 0) > 0]
    if not in_stock_products:
        print("  ! Omborda yetarli mahsulot topilmadi, buyurtmalar yaratilmadi.")
        return users_created, users_existing, orders_created

    for idx, u_info in enumerate(TEST_USERS):
        user_token = None
        # Try register
        reg_resp = requests.post(
            f"{base_url.rstrip('/')}/auth/register",
            json={
                "username": u_info["username"],
                "phone_number": u_info["phone_number"],
                "password": u_info["password"]
            },
            timeout=15
        )
        
        if reg_resp.status_code in (200, 201):
            users_created += 1
            print(f"  + User: '{u_info['username']}' ({u_info['phone_number']}) (Yaratildi)")
        else:
            users_existing += 1
            print(f"  - User: '{u_info['username']}' (mavjud yoki ro'yxatdan o'tgan)")

        # Login user
        login_resp = requests.post(
            f"{base_url.rstrip('/')}/auth/login",
            json={
                "phone_number": u_info["phone_number"],
                "password": u_info["password"]
            },
            timeout=15
        )
        if login_resp.status_code == 200:
            user_token = login_resp.json().get("access_token")

        if not user_token:
            print(f"  ! Foydalanuvchi '{u_info['username']}' sifatida login qilib bo'lmadi.")
            continue

        # Create 1 order for user if products available
        prod1 = in_stock_products[idx % len(in_stock_products)]
        prod2 = in_stock_products[(idx + 1) % len(in_stock_products)]

        order_payload = {
            "address": u_info["address"],
            "payment_method": u_info["payment_method"],
            "items": [
                {"product_id": prod1["id"], "quantity": 1},
                {"product_id": prod2["id"], "quantity": 2}
            ]
        }

        u_headers = {"Authorization": f"Bearer {user_token}"}
        order_resp = requests.post(
            f"{base_url.rstrip('/')}/orders/",
            json=order_payload,
            headers=u_headers,
            timeout=15
        )

        if order_resp.status_code in (200, 201):
            order_data = order_resp.json()
            order_id = order_data["id"]
            orders_created += 1
            print(f"  + Order: ID #{order_id} ({u_info['username']} - Total: {float(order_data['total_price']):,} so'm)")

            # Update status using Superadmin Token
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            target_status = u_info["order_status"]
            status_resp = requests.put(
                f"{base_url.rstrip('/')}/orders/{order_id}/status",
                json={"status": target_status},
                headers=admin_headers,
                timeout=15
            )
            if status_resp.status_code == 200:
                print(f"    └─ Order status updated -> '{target_status}'")
        else:
            print(f"  ! Buyurtma yaratishda xato: {order_resp.status_code} - {order_resp.text}")

    return users_created, users_existing, orders_created


def main():
    args = parse_args()
    base_url = args.url

    print("==================================================================")
    print("      SANTEXNIKA BACKEND - PRODUCTION SEED DATA GENERATOR         ")
    print("==================================================================")
    print(f"Target Server URL: {base_url}")

    phone, password = get_credentials(args)
    admin_token = login_superadmin(base_url, phone, password)

    category_map, cat_created, cat_existing = sync_categories(base_url, admin_token)
    all_products, prod_created, prod_existing = sync_products(base_url, admin_token, category_map)
    users_created, users_existing, orders_created = sync_users_and_orders(base_url, admin_token, all_products)

    print("\n==================================================================")
    print("                     SEED DATA HISOBOTI                           ")
    print("==================================================================")
    print(f" Kategoriyalar : {cat_created} ta yangi yaratildi | {cat_existing} ta avvaldan bor | Jami: {len(category_map)} ta")
    print(f" Mahsulotlar    : {prod_created} ta yangi yaratildi | {prod_existing} ta avvaldan bor | Jami: {len(all_products)} ta")
    print(f" Test Userlar   : {users_created} ta yangi yaratildi | {users_existing} ta avvaldan bor")
    print(f" Buyurtmalar    : {orders_created} ta yangi yaratildi")
    print("==================================================================")
    print(" [TUGATILDI] Baza real va mazmunli namuna ma'lumotlar bilan to'ldirildi!\n")


if __name__ == "__main__":
    main()
