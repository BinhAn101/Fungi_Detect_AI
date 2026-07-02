import os
import mysql.connector
import torch
from torch.utils.data import Dataset
from PIL import Image

class FungiDataset(Dataset):
    def __init__(self, split='train', transform=None):
        self.split = split
        self.transform = transform
        self.data = self._load_data_from_db()
        
    def _load_data_from_db(self):
        # Lấy thông tin từ biến môi trường (tái sử dụng cách thiết lập của bạn)
        MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
        MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
        MYSQL_USER = os.getenv("MYSQL_USER", "root")
        MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "my-secret-pw")
        MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "fungitastic")
        MYSQL_TABLE = os.getenv("MYSQL_TABLE", "fungitastic_dataset")
        
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cursor = conn.cursor(dictionary=True)
        
        # Chỉ lấy dữ liệu của tập tương ứng (train/val/test)
        # Chỉ chọn cột cần thiết để tối ưu bộ nhớ
        query = f"SELECT image_path, poisonous FROM `{MYSQL_TABLE}` WHERE split = %s"
        cursor.execute(query, (self.split,))
        
        # Trả về danh sách các dòng (list of dictionaries)
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return rows

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data[idx]
        img_path = row['image_path']
        label = int(row['poisonous'])
        
        # Xử lý trường hợp đường dẫn lưu trong DB có thể bị sai dạng trên Windows
        # Hoặc ảnh không tồn tại do chưa tải về hết
        try:
            image = Image.open(img_path).convert("RGB")
        except FileNotFoundError:
            # Nếu ảnh lỗi, có thể trả về một ảnh đen tạm thời, 
            # tuy nhiên để huấn luyện tốt nhất là ảnh phải tồn tại.
            print(f"Warning: Image not found at {img_path}")
            image = Image.new('RGB', (224, 224))
            
        if self.transform:
            image = self.transform(image)
            
        return image, torch.tensor(label, dtype=torch.long)
