import csv
from pathlib import Path

from database import engine
from models import Student
from sqlmodel import Session, SQLModel, create_engine
from tqdm import tqdm

BASE_DIR = Path(__file__).parent
# CSV_FILE = BASE_DIR / "all.csv"


def seed_mahasiswa(csv_file: str):
    SQLModel.metadata.create_all(engine)
    csv_path = Path(__file__).parent / csv_file

    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        with Session(engine) as session:
            print("[*] Seeding data...")
            batch = []

            for row in tqdm(reader):
                row = {k.strip(): v.strip() for k, v in row.items()}

                student = Student(
                    nim=row["nim"],
                    nama=row["nama"],
                    jenis_kelamin=row["gender"],
                    prodi=row["prodi"],
                    angkatan=row["angkatan"],
                    foto_url=row["photo_url"],
                )
                batch.append(student)

                # Commit every 100 records instead of every row
                if len(batch) >= 100:
                    session.bulk_save_objects(batch)
                    session.commit()
                    batch.clear()

            # Commit remaining records
            if batch:
                session.bulk_save_objects(batch)
                session.commit()

            print("[*] Seed database berhasil!")


if __name__ == "__main__":
    # print(BASE_DIR)
    seed_mahasiswa("all.csv")

