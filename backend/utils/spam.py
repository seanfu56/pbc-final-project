import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 載入模型與 tokenizer（只執行一次）
model_name = "Goodmotion/spam-mail-classifier"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def spam_detection(text):
    """
    接收多筆郵件文字，回傳 'spam' 或 'normal' 的列表。
    """
    texts = [text]
    inputs = tokenizer(texts, padding=True, truncation=True, max_length=128, return_tensors="pt")
    outputs = model(**inputs)

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=1)

    label_map = {0: "normal", 1: "spam"}
    return [label_map[pred.item()] for pred in predictions][0]

# 測試
if __name__ == "__main__":
    sample_emails = [
        "Urgent: Verify your account immediately.",
        "Happy Birthday!",
        "Claim your free prize now!",
        "Let's meet at 3 PM"
    ]
    results = spam_detection(sample_emails)

    for email, label in zip(sample_emails, results):
        print(f"Text: {email}")
        print(f"Label: {label}\n")
