"""
โมดูลสำหรับจัดการการเชื่อมต่อและคำสั่งที่กระทำกับฐานข้อมูล SQLite (Database Controller)
ทำหน้าที่ดึงข้อมูล เพิ่ม ลบ แก้ไข และบันทึกคำสั่งซื้อ
"""

import sqlite3

DB_NAME = "bookstore.db"

def get_active_books():
    """
    ดึงข้อมูลหนังสือทั้งหมดที่ยังเปิดขายอยู่ (is_active = 1)
    
    Returns:
        list: รายการหนังสือที่ประกอบด้วย (id, isbn, bookname, price, qty)
    """
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    # ดึง id, isbn, bookname, price และ qty (สต็อก) มาให้ครบ 5 ตัว
    cur.execute("SELECT id, isbn, bookname, price, qty FROM books WHERE is_active = 1")
    books = cur.fetchall()
    con.close()
    return books

def add_book(isbn, bookname, price, qty):
    """
    เพิ่มข้อมูลหนังสือเล่มใหม่ลงในฐานข้อมูล
    
    Args:
        isbn (str): รหัส ISBN ของหนังสือ
        bookname (str): ชื่อหนังสือ
        price (float): ราคาหนังสือ
        qty (int): จำนวนสต็อกตั้งต้น
        
    Returns:
        tuple: (สถานะความสำเร็จ True/False, ข้อความแจ้งเตือน)
    """
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO books (isbn, bookname, price, qty) VALUES (?, ?, ?, ?)",
            (isbn, bookname, price, qty)
        )
        con.commit()
        return True, "เพิ่มหนังสือสำเร็จ"
    except sqlite3.IntegrityError:
        return False, "ISBN นี้มีในระบบแล้ว"
    except Exception as e:
        return False, str(e)
    finally:
        con.close()

def delete_book(book_id):
    """
    ยกเลิกการขายหนังสือ (Soft Delete) โดยปรับค่า is_active เป็น 0
    
    Args:
        book_id (int): ID ของหนังสือที่ต้องการลบ
    """
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("UPDATE books SET is_active = 0 WHERE id = ?", (book_id,))
    con.commit()
    con.close()

def save_order(total_amount, customer_info_str, cart_items):
    """
    บันทึกข้อมูลคำสั่งซื้อและตัดสต็อกสินค้าในฐานข้อมูล
    
    Args:
        total_amount (float): ยอดรวมสุทธิของคำสั่งซื้อ
        customer_info_str (str): ข้อมูลของลูกค้า (ชื่อ, ที่อยู่ ฯลฯ)
        cart_items (list): รายการสินค้าในตะกร้า
        
    Returns:
        tuple: (สถานะความสำเร็จ True/False, ข้อความแจ้งเตือน)
    """
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        # 1. สร้างใบสั่งซื้อหลัก
        cur.execute("INSERT INTO orders (total, customer_info) VALUES (?, ?)", (total_amount, customer_info_str))
        order_id = cur.lastrowid
        
        # 2. เพิ่มรายการสินค้าและตัดสต็อก
        for item in cart_items:
            subtotal = item['price'] * item['qty']
            cur.execute(
                "INSERT INTO order_items (order_id, book_id, qty, price, subtotal) VALUES (?, ?, ?, ?, ?)",
                (order_id, item['id'], item['qty'], item['price'], subtotal)
            )
            # ตัดสต็อกสินค้าในฐานข้อมูลจริงๆ
            cur.execute("UPDATE books SET qty = qty - ? WHERE id = ?", (item['qty'], item['id']))
            
        con.commit()
        return True, "สั่งซื้อและตัดสต็อกสำเร็จ!"
    except Exception as e:
        con.rollback()
        return False, f"เกิดข้อผิดพลาด: {str(e)}"
    finally:
        con.close()

def update_book_info(book_id, new_name, new_qty):
    """
    อัปเดตข้อมูลรายละเอียดและสต็อกของหนังสือ
    
    Args:
        book_id (int): ID ของหนังสือที่ต้องการแก้ไข
        new_name (str): ชื่อหนังสือใหม่
        new_qty (int): จำนวนสต็อกใหม่
        
    Returns:
        tuple: (สถานะความสำเร็จ True/False, ข้อความแจ้งเตือน)
    """
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    try:
        # อัปเดตทั้งชื่อหนังสือ (bookname) และ จำนวนสต็อก (qty)
        cur.execute("UPDATE books SET bookname = ?, qty = ? WHERE id = ?", (new_name, new_qty, book_id))
        con.commit()
        return True, "อัปเดตข้อมูลสินค้าสำเร็จ"
    except Exception as e:
        con.rollback()
        return False, f"เกิดข้อผิดพลาด: {str(e)}"
    finally:
        con.close()