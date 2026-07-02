import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms
from dotenv import load_dotenv

from dataset import FungiDataset
from model import get_fungi_model


load_dotenv()

def main():
    # 1. Thiết lập siêu tham số
    BATCH_SIZE = 16
    LEARNING_RATE = 0.001
    NUM_EPOCHS = 20  # chạy thử nghiệm 20 vòng
    
    # Kiểm tra xem CUDA có sẵn không
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Bắt đầu huấn luyện trên thiết bị: {device}")

    # 2. Tiền xử lý hình ảnh (theo chuẩn của ResNet)
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # 3. Khởi tạo Dataset và DataLoader
    print("Đang tải dữ liệu từ MySQL...")
    train_dataset = FungiDataset(split='train', transform=transform)
    # val_dataset = FungiDataset(split='val', transform=transform) # Bỏ comment nếu bạn muốn test tập val
    
    print(f"Tổng số ảnh trong tập train: {len(train_dataset)}")
    
    if len(train_dataset) == 0:
        print("Lỗi: Không tìm thấy dữ liệu ảnh. Hãy kiểm tra lại DB.")
        return

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

    # 4. Khởi tạo mô hình
    model = get_fungi_model(num_classes=2)
    model = model.to(device)

    # 5. Hàm mất mát (Loss Function) và Bộ tối ưu (Optimizer)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # 6. Vòng lặp huấn luyện (Training Loop)
    model.train()
    for epoch in range(NUM_EPOCHS):
        running_loss = 0.0
        
        # Chỉ chạy thử một vài batch đầu tiên để tiết kiệm thời gian chờ (bỏ `[:5]` nếu muốn chạy thật)
        for i, (images, labels) in enumerate(train_loader):
            # Di chuyển dữ liệu lên GPU
            images = images.to(device)
            labels = labels.to(device)
            
            # Forward pass (dự đoán)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Backward pass (cập nhật trọng số)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            if (i + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}/{NUM_EPOCHS}], Batch [{i+1}/{len(train_loader)}], Loss: {loss.item():.4f}")
            


    print("Huấn luyện thành công!")
    # Lưu mô hình
    torch.save(model.state_dict(), "fungi_resnet50_demo.pth")
    print("Đã lưu mô hình: fungi_resnet50_demo.pth")

if __name__ == "__main__":
    main()
