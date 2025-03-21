from datasets import Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import TrainingArguments, Trainer
import torch

model_name = "bert-base-uncased"
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)  
tokenizer = AutoTokenizer.from_pretrained(model_name)



class CustomTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs["labels"]
        if isinstance(labels, np.ndarray):  # 兼容 NumPy 格式
            labels = torch.tensor(labels, dtype=torch.float32).to(model.device)

        model_inputs = {k: v for k, v in inputs.items() if k != "labels"}
        outputs = model(**model_inputs)
        logits = outputs.logits
        loss_fct = torch.nn.MSELoss()
        loss = loss_fct(logits, labels)
        return (loss, outputs) if return_outputs else loss


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    if isinstance(predictions, tuple): 
        predictions = predictions[0]

    mse = np.mean((predictions - labels) ** 2)
    return {"mse": mse}
