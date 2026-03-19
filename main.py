"""
จุดเริ่มต้นการทำงานของโปรแกรม (Entry Point)
ทำหน้าที่ตรวจสอบและเตรียมฐานข้อมูล ก่อนที่จะเรียกใช้หน้าต่าง UI หลัก
"""

import tkinter as tk
from database import setup_db
from ui.app import BookstoreApp 

if __name__ == "__main__":
    # 1. เช็คและสร้างตารางในฐานข้อมูลก่อนรันแอปพลิเคชัน
    setup_db.init_db()
    
    # 2. เริ่มต้นรัน UI ของโปรแกรมด้วย Tkinter
    root = tk.Tk()
    app = BookstoreApp(root)
    root.mainloop()