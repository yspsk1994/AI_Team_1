import torch
from transformers import BertTokenizer, AutoTokenizer
from transformers import BertForSequenceClassification
import torch.nn as nn 
# 학습에서 사용한 KoBERTWithDropout 모델을 불러와야 합니다
class KoBERTWithDropout(nn.Module):
    def __init__(self, bert_model, dropout_prob=0.3):
        super(KoBERTWithDropout, self).__init__()
        self.bert = bert_model
        self.dropout = nn.Dropout(dropout_prob)
        self.classifier = nn.Linear(self.bert.config.hidden_size, 3)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        dropped_output = self.dropout(logits)
        return dropped_output

# 모델 및 토크나이저 로드
tokenizer = AutoTokenizer.from_pretrained("skt/kobert-base-v1", use_fast=False)
bert_model = BertForSequenceClassification.from_pretrained('skt/kobert-base-v1', num_labels=3)

# 학습에서 사용한 KoBERTWithDropout 모델 로드
model = KoBERTWithDropout(bert_model)

# 저장된 가중치 불러오기
model.load_state_dict(torch.load('best_model_weights.pth', map_location=torch.device('cuda' if torch.cuda.is_available() else 'cpu')))

# 모델을 평가 모드로 전환
model.eval()

# 모델을 GPU로 이동 (가능한 경우)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# 예측할 텍스트 데이터 준비
new_text = "자본과"

# 텍스트를 토크나이저로 인코딩
inputs = tokenizer.encode_plus(
    new_text,
    add_special_tokens=True,
    max_length=128,
    return_token_type_ids=False,
    padding='max_length',
    truncation=True,
    return_attention_mask=True,
    return_tensors='pt',
)

# 입력 데이터를 GPU 또는 CPU로 이동
input_ids = inputs['input_ids'].to(device)
attention_mask = inputs['attention_mask'].to(device)

# 예측 수행
with torch.no_grad():
    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    prediction = torch.argmax(outputs, dim=1)

# 예측 결과 출력
print(f"Prediction: {prediction.item()}")
