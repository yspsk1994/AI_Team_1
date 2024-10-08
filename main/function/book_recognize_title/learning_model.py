import json
from transformers import BertTokenizer
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertForSequenceClassification, AdamW
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer
import numpy as np
import torch.nn as nn
from sklearn.utils.class_weight import compute_class_weight

# JSON 파일에서 데이터 로드
def load_dataset(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    texts = [item['text'] for item in data]
    labels = [item['label'] for item in data]
    return texts, labels

# KoBERT를 위한 데이터셋 클래스
class KoBERTDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]

        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }

# KoBERT 모델에 드롭아웃 추가
class KoBERTWithDropout(nn.Module):
    def __init__(self, bert_model, dropout_prob=0.8):
        super(KoBERTWithDropout, self).__init__()
        self.bert = bert_model
        self.dropout = nn.Dropout(dropout_prob)  # 드롭아웃 확률 설정
        self.classifier = nn.Linear(self.bert.config.hidden_size, 3)  # 출력 레이어

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits  # 모델의 최종 출력인 logits 사용
        dropped_output = self.dropout(logits)  # 드롭아웃 적용
        return dropped_output

# 데이터 로드 및 토크나이저 설정
texts, labels = load_dataset('books_info.json')
tokenizer = AutoTokenizer.from_pretrained("skt/kobert-base-v1", use_fast=False)

# 데이터셋을 훈련, 검증, 테스트로 나누기 (80% train, 10% val, 10% test)
train_texts, temp_texts, train_labels, temp_labels = train_test_split(texts, labels, test_size=0.3, random_state=42)
val_texts, test_texts, val_labels, test_labels = train_test_split(temp_texts, temp_labels, test_size=0.5, random_state=42)

# 각각의 데이터셋에 대해 KoBERTDataset 생성
train_dataset = KoBERTDataset(texts=train_texts, labels=train_labels, tokenizer=tokenizer, max_len=128)
val_dataset = KoBERTDataset(texts=val_texts, labels=val_labels, tokenizer=tokenizer, max_len=128)
test_dataset = KoBERTDataset(texts=test_texts, labels=test_labels, tokenizer=tokenizer, max_len=128)

# DataLoader 설정
train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=4, shuffle=False)

# 모델과 장치 설정
device = 'cuda' if torch.cuda.is_available() else 'cpu'
bert_model = BertForSequenceClassification.from_pretrained('skt/kobert-base-v1', num_labels=3)
model = KoBERTWithDropout(bert_model).to(device)

# 옵티마이저 및 손실 함수 설정 (가중치 감소 포함)
optimizer = AdamW(model.parameters(), lr=1e-6, weight_decay=0.01)

# 클래스 가중치 계산
class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(labels), y=labels)
class_weights = torch.tensor(class_weights, dtype=torch.float).to(device)

# 가중치를 적용한 손실 함수
loss_fn = torch.nn.CrossEntropyLoss(weight=class_weights).to(device)

# 조기 종료를 위한 변수 설정
best_val_loss = np.inf
patience = 5
patience_counter = 0

# 학습 및 검증 루프
epochs = 500
for epoch in range(epochs):
    model.train()
    total_train_loss = 0
    total_val_loss = 0

    # 훈련 단계
    for batch in train_loader:
        optimizer.zero_grad()

        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['label'].to(device)

        # 훈련 및 검증 단계에서의 출력 사용
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        loss = loss_fn(outputs, labels)

        total_train_loss += loss.item()
        
        # 역전파 및 가중치 업데이트
        loss.backward()
        optimizer.step()

    avg_train_loss = total_train_loss / len(train_loader)

    # 검증 단계
    model.eval()
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            loss = loss_fn(outputs, labels)
                
            total_val_loss += loss.item()

    avg_val_loss = total_val_loss / len(val_loader)

    print(f"Epoch {epoch+1}/{epochs}, Train Loss: {avg_train_loss:.4f}, Validation Loss: {avg_val_loss:.4f}")

    # 조기 종료 조건 체크
    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        patience_counter = 0  # 개선되었으므로 카운터 초기화
        # 모델의 가중치 저장 (가장 좋은 검증 성능일 때)
        torch.save(model.state_dict(), './best_model_weights.pth')
    else:
        patience_counter += 1  # 개선되지 않으면 카운터 증가

    if patience_counter >= patience:
        print(f"Early stopping on epoch {epoch+1}")
        break  # 개선되지 않은 에포크 수가 참을 수 있는 범위를 넘으면 학습 중단

# 테스트 단계
model.eval()
total_test_loss = 0
with torch.no_grad():
    for batch in test_loader:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['label'].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        loss = loss_fn(outputs, labels)
        
        total_test_loss += loss.item()

    avg_test_loss = total_test_loss / len(test_loader)
    print(f"Test Loss: {avg_test_loss:.4f}")

# 가장 좋은 가중치로 모델 로드
model.load_state_dict(torch.load('./best_model_weights.pth'))
