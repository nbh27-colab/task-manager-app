from database.connection import engine, Base

# Clear metadata tránh lỗi trùng table
Base.metadata.clear()

# Import models sau khi clear
from database import models

# Tạo bảng
Base.metadata.create_all(bind=engine)
print("✅ Migrated!")
