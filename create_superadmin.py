from sqlmodel import Session, select
from app.database import engine
from app.models import User, RoleEnum
from app.security import hash_password


def main():
    phone_number = input("Superadmin uchun telefon raqam: ").strip()
    username = input("Superadmin uchun username: ").strip()
    password = input("Superadmin uchun parol: ").strip()

    with Session(engine) as session:
        if session.exec(select(User).where(User.phone_number == phone_number)).first():
            print("Bu telefon raqam band, boshqasini tanlang.")
            return
        user = User(
            phone_number=phone_number,
            username=username,
            hashed_password=hash_password(password),
            role=RoleEnum.superadmin,
        )
        session.add(user)
        session.commit()
        print(f"Superadmin '{username}' muvaffaqiyatli yaratildi!")


if __name__ == "__main__":
    main()

