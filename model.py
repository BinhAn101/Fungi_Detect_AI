import torch.nn as nn
from torchvision.models import resnet50, ResNet50_Weights

def get_fungi_model(num_classes=2):
    """
    Sử dụng ResNet50 theo yêu cầu, thay đổi lớp cuối cùng để phân loại 2 lớp (Độc / Không độc)
    """
    # 1. Tải mô hình ResNet50 với trọng số đã huấn luyện sẵn (Transfer Learning)
    model = resnet50(weights=ResNet50_Weights.DEFAULT)
    
    # 2. Tuỳ chọn: Đóng băng (Freeze) các lớp Convolutional để train nhanh hơn
    #    Nếu muốn mô hình học sâu hơn thì bỏ comment đoạn dưới.
    # for param in model.parameters():
    #     param.requires_grad = False
        
    # 3. Lấy số lượng features của lớp cuối cùng (Fully Connected)
    num_ftrs = model.fc.in_features
    
    # 4. Thay thế lớp cuối cùng để dự đoán ra 2 lớp: 0 và 1
    model.fc = nn.Linear(num_ftrs, num_classes)
    
    return model
