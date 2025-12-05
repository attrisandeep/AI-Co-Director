import torch
import torch.nn as nn
import numpy as np
import cv2
from moviepy import VideoFileClip
from transformers import BertTokenizer, BertModel
import os

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# ---------- MODEL DEFINITION ----------
class MultimodalModel(nn.Module):
    def __init__(self, num_classes=7):
        super(MultimodalModel, self).__init__()

        # --- Text (BERT) ---
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        for param in self.bert.parameters():
            param.requires_grad = False
        self.text_fc = nn.Linear(768, 128)

        # --- Audio CNN ---
        self.audio_cnn = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=5, stride=2, padding=2),
            nn.ReLU(),
            nn.Conv1d(16, 32, kernel_size=5, stride=2, padding=2),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(128)
        )

        # --- Video CNN ---
        self.video_cnn = nn.Sequential(
            nn.Conv3d(3, 16, kernel_size=(3,3,3), stride=1, padding=1),
            nn.ReLU(),
            nn.Conv3d(16, 32, kernel_size=(3,3,3), stride=1, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool3d((16,1,1))
        )

        # --- Fusion Head ---
        fusion_input_dim = 128 + 32 + 512
        self.fc = nn.Sequential(
            nn.Linear(fusion_input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )

    def forward(self, input_ids, attention_mask, audio, video):
        bert_out = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        text_feat = self.text_fc(bert_out.last_hidden_state.mean(dim=1))
        audio_feat = self.audio_cnn(audio).mean(dim=2)
        video_feat = self.video_cnn(video).view(video.size(0), -1)
        fusion = torch.cat([text_feat, audio_feat, video_feat], dim=1)
        return self.fc(fusion)

# ---------- PREDICTOR ----------
class EmotionPredictor:
    def __init__(self, model_path: str, emotions: list):
        self.model = MultimodalModel(num_classes=len(emotions)).to(device)
        self.model.load_state_dict(torch.load(model_path, map_location=device))
        self.model.eval()
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.emotions = emotions

    def extract_audio(self, video_path, target_len=16000):
        try:
            clip = VideoFileClip(video_path)
            audio_array = clip.audio.to_soundarray(fps=16000)
            clip.close()
            if audio_array.ndim == 2:
                audio_array = audio_array.mean(axis=1)
            if len(audio_array) > target_len:
                audio_array = audio_array[:target_len]
            elif len(audio_array) < target_len:
                pad = target_len - len(audio_array)
                audio_array = np.pad(audio_array, (0, pad))
        except Exception:
            audio_array = np.zeros(target_len, dtype=np.float32)
        return torch.tensor(audio_array, dtype=torch.float32).unsqueeze(0).unsqueeze(0)

    def extract_video_frames(self, video_path, num_frames=16, frame_size=112):
        cap = cv2.VideoCapture(video_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step = max(total // num_frames, 1)
        frames = []
        for i in range(0, total, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (frame_size, frame_size))
            frames.append(frame)
            if len(frames) >= num_frames:
                break
        cap.release()

        if len(frames) == 0:
            frames = [np.zeros((frame_size, frame_size, 3), dtype=np.uint8)] * num_frames
        while len(frames) < num_frames:
            frames.append(frames[-1])

        video_tensor = torch.tensor(np.stack(frames), dtype=torch.float32).permute(3,0,1,2) / 255.0
        return video_tensor.unsqueeze(0)

    def predict_from_video(self, video_path: str, text_hint: str = ""):
        enc = self.tokenizer(text_hint, return_tensors='pt', truncation=True, padding='max_length', max_length=128)
        input_ids = enc['input_ids'].to(device)
        attention_mask = enc['attention_mask'].to(device)
        audio = self.extract_audio(video_path).to(device)
        video = self.extract_video_frames(video_path).to(device)

        with torch.no_grad():
            logits = self.model(input_ids, attention_mask, audio, video)
            probs = torch.softmax(logits, dim=1)
            conf, idx = torch.max(probs, dim=1)
            pred_emo = self.emotions[idx.item()]

        return {
            "predicted_emotion": pred_emo,
            "confidence": float(conf.item()),
            "modalities": {
                "audio": round(probs[0].mean().item(), 3),
                "text": round(probs[0].mean().item(), 3),
                "visual": round(probs[0].mean().item(), 3)
            }
        }

# ---------- Singleton Predictor ----------
_emotions = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]
_model_path = os.getenv("MODEL_PATH", "best_multimodal_model.pth")
_predictor = EmotionPredictor(_model_path, _emotions)

def predict_from_video(video_path: str):
    return _predictor.predict_from_video(video_path)
