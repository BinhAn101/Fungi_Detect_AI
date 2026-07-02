import os
import mysql.connector

def main():
    # Cấu hình kết nối MySQL
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "my-secret-pw")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "fungitastic")
    MYSQL_TABLE = os.getenv("MYSQL_TABLE", "fungitastic_dataset")

    print(f"Đang kết nối đến MySQL ({MYSQL_HOST}:{MYSQL_PORT}) - Database: {MYSQL_DATABASE}...")
    try:
        # Kết nối tới database
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        # Sử dụng dictionary=True để khi fetch dữ liệu sẽ trả về dạng key-value dễ đọc
        cursor = conn.cursor(dictionary=True)
        
        print("Kết nối thành công!\n")
        
        # 1. Xem bảng có những cột nào
        cursor.execute(f"SHOW COLUMNS FROM `{MYSQL_TABLE}`")
        columns = cursor.fetchall()
        print(f"--- CÁC CỘT TRONG BẢNG `{MYSQL_TABLE}` ---")
        column_names = [col['Field'] for col in columns]
        print(column_names)
        print("-" * 60)
        
        # 2. Truy xuất 3 dòng đầu tiên từ bảng để kiểm tra (tập train)
        print("\n--- 3 DÒNG DỮ LIỆU MẪU (TẬP TRAIN) ---")
        query = f"SELECT * FROM `{MYSQL_TABLE}` WHERE split='train' LIMIT 3"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            print("Bảng hiện tại chưa có dữ liệu. Bạn đã chạy script import chưa?")
        else:
            for i, row in enumerate(rows, 1):
                print(f"==== Dòng {i} ====")
                print(f"ID: {row.get('id')}")
                print(f"Split: {row.get('split')}")
                print(f"Đường dẫn ảnh (Image Path): {row.get('image_path')}")
                
                # Tìm in ra cột nhãn (nếu có các từ khóa như 'poisonous', 'class', 'edible')
                for key, value in row.items():
                    # Bỏ qua in những nội dung quá dài hoặc đã in rồi
                    if key not in ['id', 'split', 'image_path', 'captions']:
                        print(f"[{key}]: {value}")
                print()
                
        cursor.close()
        conn.close()
        print("Đã đóng kết nối MySQL.")
        
    except mysql.connector.Error as err:
        print(f"Lỗi khi truy xuất MySQL: {err}")
        print("Vui lòng kiểm tra lại Username/Password hoặc xem MySQL server đã chạy chưa.")

if __name__ == "__main__":
    main()
