from __future__ import annotations

import json
import math
import random
from pathlib import Path
from ml_system.config.settings import CONFIG
from .tokenizer import Tokenizer
from .models import NaiveBayesModel, LinearSoftmaxModel


def load_dataset(path: str | Path) -> list[dict]:
    """Load JSONL dataset."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    return records


def split_xy(records: list[dict]) -> tuple[list[str], list[str]]:
    """Split records into texts and labels."""
    texts = [r.get("phrase") for r in records]
    labels = [r.get("label") for r in records]
    return texts, labels


def accuracy_score(y_true: list[str], y_pred: list[str]) -> float:
    """Calculate accuracy."""
    return sum(t == p for t, p in zip(y_true, y_pred)) / len(y_true) if y_true else 0.0


def macro_f1_score(y_true: list[str], y_pred: list[str], labels: list[str]) -> float:
    """Calculate macro F1 score."""
    f1_scores = []
    for label in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        f1_scores.append(f1)
    
    return sum(f1_scores) / len(f1_scores) if f1_scores else 0.0


class Trainer:
    """Model trainer orchestrator."""

    def __init__(
        self,
        train_path: str | Path,
        val_path: str | Path,
        test_path: str | Path,
        hardset_path: str | Path,
        output_dir: str | Path,
    ) -> None:
        self.train_path = Path(train_path)
        self.val_path = Path(val_path)
        self.test_path = Path(test_path)
        self.hardset_path = Path(hardset_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def train(self) -> dict:
        """Train models and return results."""
        
        train_rows = load_dataset(self.train_path)
        val_rows = load_dataset(self.val_path)
        test_rows = load_dataset(self.test_path)
        hard_rows = load_dataset(self.hardset_path)

        x_train, y_train = split_xy(train_rows)
        x_val, y_val = split_xy(val_rows)
        x_test, y_test = split_xy(test_rows)
        x_hard, y_hard = split_xy(hard_rows)

        focus_examples = [
            {"phrase": "going on a date", "label": "Indoor"},
            {"phrase": "going on a date with a girl", "label": "Indoor"},
            {"phrase": "going on a date with my girlfriend", "label": "Indoor"},
            {"phrase": "date night", "label": "Indoor"},
            {"phrase": "romantic date", "label": "Indoor"},
            {"phrase": "coffee date", "label": "Indoor"},
            {"phrase": "dinner date", "label": "Indoor"},
            {"phrase": "meeting my girlfriend for a date", "label": "Indoor"},
            {"phrase": "going to meet my girlfriend", "label": "Indoor"},
            {"phrase": "going out with my girlfriend", "label": "Indoor"},
            {"phrase": "seeing my girlfriend tonight", "label": "Indoor"},
            {"phrase": "social date plan", "label": "Indoor"},
            {"phrase": "planning a date", "label": "Indoor"},
            {"phrase": "date with a girl", "label": "Indoor"},
            {"phrase": "going on a date at a restaurant", "label": "Indoor"},
            {"phrase": "date night at home", "label": "Indoor"},
            {"phrase": "coffee date at a cafe", "label": "Indoor"},
            {"phrase": "movie date at the cinema", "label": "Indoor"},
            {"phrase": "going on a date at an amusement park", "label": "Outdoor"},
            {"phrase": "date at an amusement park", "label": "Outdoor"},
            {"phrase": "amusement park date", "label": "Outdoor"},
            {"phrase": "romantic date at the park", "label": "Outdoor"},
            {"phrase": "going on a date outside", "label": "Outdoor"},
            {"phrase": "date at the beach", "label": "Outdoor"},
            {"phrase": "going to get cigarettes from tobacco shop", "label": "Outdoor"},
            {"phrase": "buying cigarettes from tobacco store", "label": "Outdoor"},
            {"phrase": "going to tobacco shop", "label": "Outdoor"},
            {"phrase": "going to buy from local store", "label": "Outdoor"},
            {"phrase": "quick run to the grocery store", "label": "Outdoor"},
            {"phrase": "shopping at local market", "label": "Outdoor"},
            {"phrase": "buying cigarettes online", "label": "Indoor"},
            {"phrase": "ordering cigarettes from app", "label": "Indoor"},
            {"phrase": "shopping online", "label": "Indoor"},
            {"phrase": "buy groceries online", "label": "Indoor"},
        ]

        x_train.extend(example["phrase"] for example in focus_examples)
        y_train.extend(example["label"] for example in focus_examples)

        labels = sorted({*y_train, *y_val, *y_test, *y_hard})

        tokenizer = Tokenizer(
            min_token_freq=CONFIG.tokenizer_min_freq,
            max_vocab_size=CONFIG.tokenizer_max_vocab,
            use_char_ngrams=True,
            char_ngram_min=3,
            char_ngram_max=5,
        )
        tokenizer.train(x_train)

        nb = NaiveBayesModel(labels=labels, alpha=CONFIG.laplace_alpha)
        nb.fit(x_train, y_train, tokenizer)

        linear, linear_backend_used = self._train_linear_model(
            texts=x_train,
            y=y_train,
            labels=labels,
            tokenizer=tokenizer,
        )

        best_name = ""
        best_val_f1 = -1.0
        best_model = None

        for name, model in [("naive_bayes", nb), ("linear_softmax", linear)]:
            probs = model.predict_proba(x_val, tokenizer)
            preds = [max(p.items(), key=lambda x: x[1])[0] for p in probs]
            f1 = macro_f1_score(y_val, preds, labels)
            if f1 > best_val_f1:
                best_name = name
                best_val_f1 = f1
                best_model = model

        val_probs = best_model.predict_proba(x_val, tokenizer)
        temperature = self._calibrate_temperature(y_val, val_probs)

        def calibrated_predict(texts: list[str]) -> list[str]:
            probs = best_model.predict_proba(texts, tokenizer)
            calibrated = [self._apply_temperature(p, temperature) for p in probs]
            return [max(p.items(), key=lambda x: x[1])[0] for p in calibrated]

        test_preds = calibrated_predict(x_test)
        hard_preds = calibrated_predict(x_hard)

        test_f1 = macro_f1_score(y_test, test_preds, labels)
        hard_f1 = macro_f1_score(y_hard, hard_preds, labels)

        report = {
            "champion_model": best_name,
            "labels": labels,
            "linear_backend": linear_backend_used,
            "val": {"macro_f1": best_val_f1},
            "test": {"macro_f1": test_f1},
            "hardset": {"macro_f1": hard_f1},
            "temperature": temperature,
        }

        report_path = self.output_dir / "report.json"
        legacy_report_path = self.output_dir / "training_report.json"
        tokenizer_path = self.output_dir / "tokenizer.json"
        model_path = self.output_dir / "model.json"

        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        with legacy_report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        with tokenizer_path.open("w", encoding="utf-8") as f:
            json.dump(tokenizer.to_dict(), f, indent=2)

        with model_path.open("w", encoding="utf-8") as f:
            json.dump(best_model.to_dict(), f)

        return {
            "champion_model": best_name,
            "linear_backend": linear_backend_used,
            "val_f1": best_val_f1,
            "test_f1": test_f1,
            "hardset_f1": hard_f1,
            "temperature": temperature,
            "report_path": str(report_path),
            "tokenizer_path": str(tokenizer_path),
            "model_path": str(model_path),
        }

    @staticmethod
    def _encode_text_to_sparse_ids(text: str, tokenizer: Tokenizer) -> tuple[list[int], list[float]]:
        from collections import Counter

        counts = Counter(tokenizer.tokenize(text))
        ids: list[int] = []
        weights: list[float] = []
        unk_id = tokenizer.vocab.get("<UNK>", 1)
        for token, count in counts.items():
            ids.append(tokenizer.vocab.get(token, unk_id))
            weights.append(float(count))
        if not ids:
            ids = [unk_id]
            weights = [1.0]
        return ids, weights

    def _choose_linear_backend(self) -> str:
        requested = (CONFIG.linear_backend or "auto").strip().lower()

        def has_torch() -> bool:
            try:
                import torch  # noqa: F401

                return True
            except Exception:
                return False

        def has_tf() -> bool:
            try:
                import tensorflow as tf  # noqa: F401

                return True
            except Exception:
                return False

        if requested == "pytorch":
            if not has_torch():
                raise RuntimeError(
                    "Configured linear backend is 'pytorch' but torch is not installed. "
                    "Install torch or change CONFIG.linear_backend."
                )
            return "pytorch"
        if requested == "tensorflow":
            if not has_tf():
                raise RuntimeError(
                    "Configured linear backend is 'tensorflow' but tensorflow is not installed. "
                    "Install tensorflow or change CONFIG.linear_backend."
                )
            return "tensorflow"
        if requested == "scratch":
            return "scratch"

        if has_torch():
            return "pytorch"
        if has_tf():
            return "tensorflow"
        return "scratch"

    def _train_linear_model(
        self,
        texts: list[str],
        y: list[str],
        labels: list[str],
        tokenizer: Tokenizer,
    ) -> tuple[LinearSoftmaxModel, str]:
        backend = self._choose_linear_backend()

        if backend == "pytorch":
            model = self._train_linear_pytorch(texts, y, labels, tokenizer)
            if model is None:
                raise RuntimeError(
                    "PyTorch backend selected but accelerated training failed to initialize."
                )
            return model, "pytorch"

        if backend == "tensorflow":
            tf_model = self._train_linear_tensorflow(texts, y, labels, tokenizer)
            if tf_model is None:
                raise RuntimeError(
                    "TensorFlow backend selected but accelerated training failed to initialize."
                )
            return tf_model, "tensorflow"

        linear = LinearSoftmaxModel(
            labels=labels,
            lr=CONFIG.learning_rate,
            epochs=CONFIG.epochs,
            l2=CONFIG.l2_regularization,
        )
        linear.fit(texts, y, tokenizer)
        return linear, "scratch"

    def _train_linear_pytorch(
        self,
        texts: list[str],
        y: list[str],
        labels: list[str],
        tokenizer: Tokenizer,
    ) -> LinearSoftmaxModel | None:
        try:
            import torch
            import torch.nn as nn
            import torch.nn.functional as F
        except Exception:
            return None

        label_to_idx = {label: idx for idx, label in enumerate(labels)}
        encoded = [self._encode_text_to_sparse_ids(text, tokenizer) for text in texts]
        targets = [label_to_idx[label] for label in y]

        vocab_size = max(tokenizer.vocab.values()) + 1
        num_classes = len(labels)
        batch_size = max(1, int(CONFIG.linear_batch_size))

        class BowSoftmax(nn.Module):
            def __init__(self, vocab: int, classes: int) -> None:
                super().__init__()
                self.embedding = nn.Embedding(vocab, classes)
                self.bias = nn.Parameter(torch.zeros(classes))

            def forward(
                self,
                token_ids: torch.Tensor,
                offsets: torch.Tensor,
                weights: torch.Tensor,
            ) -> torch.Tensor:
                bag = F.embedding_bag(
                    token_ids,
                    self.embedding.weight,
                    offsets,
                    mode="sum",
                    per_sample_weights=weights,
                )
                return bag + self.bias

        model = BowSoftmax(vocab_size, num_classes)
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=float(CONFIG.learning_rate),
            weight_decay=float(CONFIG.l2_regularization),
        )

        rng = random.Random(42)
        indices = list(range(len(texts)))

        for _ in range(int(CONFIG.epochs)):
            rng.shuffle(indices)
            for start in range(0, len(indices), batch_size):
                batch_idx = indices[start : start + batch_size]
                flat_ids: list[int] = []
                flat_weights: list[float] = []
                offsets: list[int] = []
                cursor = 0
                for idx in batch_idx:
                    ids, weights = encoded[idx]
                    offsets.append(cursor)
                    flat_ids.extend(ids)
                    flat_weights.extend(weights)
                    cursor += len(ids)

                token_ids = torch.tensor(flat_ids, dtype=torch.long)
                token_weights = torch.tensor(flat_weights, dtype=torch.float32)
                offset_tensor = torch.tensor(offsets, dtype=torch.long)
                target_tensor = torch.tensor(
                    [targets[idx] for idx in batch_idx],
                    dtype=torch.long,
                )

                logits = model(token_ids, offset_tensor, token_weights)
                loss = F.cross_entropy(logits, target_tensor)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        linear = LinearSoftmaxModel(
            labels=labels,
            lr=CONFIG.learning_rate,
            epochs=CONFIG.epochs,
            l2=CONFIG.l2_regularization,
        )

        id_to_token = {idx: token for token, idx in tokenizer.vocab.items()}
        weights = model.embedding.weight.detach().cpu().numpy()
        biases = model.bias.detach().cpu().numpy()

        for class_idx, label in enumerate(labels):
            class_weights: dict[str, float] = {}
            for token_idx in range(weights.shape[0]):
                token = id_to_token.get(token_idx)
                if token is None:
                    continue
                value = float(weights[token_idx, class_idx])
                if abs(value) > 1e-12:
                    class_weights[token] = value
            linear.weights[label] = class_weights
            linear.bias[label] = float(biases[class_idx])

        return linear

    def _train_linear_tensorflow(
        self,
        texts: list[str],
        y: list[str],
        labels: list[str],
        tokenizer: Tokenizer,
    ) -> LinearSoftmaxModel | None:
        try:
            import numpy as np
            import tensorflow as tf
        except Exception:
            return None

        tf.random.set_seed(42)
        label_to_idx = {label: idx for idx, label in enumerate(labels)}
        encoded = [self._encode_text_to_sparse_ids(text, tokenizer) for text in texts]
        targets = np.array([label_to_idx[label] for label in y], dtype=np.int32)

        vocab_size = max(tokenizer.vocab.values()) + 1
        num_classes = len(labels)
        batch_size = max(1, int(CONFIG.linear_batch_size))

        embedding = tf.Variable(
            tf.random.normal([vocab_size, num_classes], stddev=0.01),
            trainable=True,
        )
        bias = tf.Variable(tf.zeros([num_classes]), trainable=True)
        optimizer = tf.keras.optimizers.Adam(learning_rate=float(CONFIG.learning_rate))

        idxs = np.arange(len(texts))
        rng = np.random.default_rng(42)

        def forward(sample_ids: tf.Tensor, sample_weights: tf.Tensor) -> tf.Tensor:
            gathered = tf.gather(embedding, sample_ids)
            weighted = gathered * tf.expand_dims(sample_weights, axis=-1)
            return tf.reduce_sum(weighted, axis=0) + bias

        for _ in range(int(CONFIG.epochs)):
            rng.shuffle(idxs)
            for start in range(0, len(idxs), batch_size):
                batch_idx = idxs[start : start + batch_size]
                with tf.GradientTape() as tape:
                    losses = []
                    for idx in batch_idx:
                        ids, weights = encoded[int(idx)]
                        ids_t = tf.constant(ids, dtype=tf.int32)
                        w_t = tf.constant(weights, dtype=tf.float32)
                        logits = forward(ids_t, w_t)
                        target = tf.constant([targets[int(idx)]], dtype=tf.int32)
                        sample_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(
                            labels=target,
                            logits=tf.expand_dims(logits, axis=0),
                        )[0]
                        losses.append(sample_loss)

                    batch_loss = tf.reduce_mean(tf.stack(losses))
                    if float(CONFIG.l2_regularization) > 0:
                        batch_loss = batch_loss + float(CONFIG.l2_regularization) * tf.reduce_mean(
                            tf.square(embedding)
                        )

                grads = tape.gradient(batch_loss, [embedding, bias])
                optimizer.apply_gradients(zip(grads, [embedding, bias]))

        linear = LinearSoftmaxModel(
            labels=labels,
            lr=CONFIG.learning_rate,
            epochs=CONFIG.epochs,
            l2=CONFIG.l2_regularization,
        )

        id_to_token = {idx: token for token, idx in tokenizer.vocab.items()}
        weights_np = embedding.numpy()
        biases_np = bias.numpy()

        for class_idx, label in enumerate(labels):
            class_weights: dict[str, float] = {}
            for token_idx in range(weights_np.shape[0]):
                token = id_to_token.get(token_idx)
                if token is None:
                    continue
                value = float(weights_np[token_idx, class_idx])
                if abs(value) > 1e-12:
                    class_weights[token] = value
            linear.weights[label] = class_weights
            linear.bias[label] = float(biases_np[class_idx])

        return linear

    @staticmethod
    def _calibrate_temperature(y_true: list[str], probs: list[dict[str, float]]) -> float:
        """Find best temperature scaling parameter."""
        best_temp = 1.0
        best_nll = float("inf")

        for temp in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.5, 2.0, 3.0]:
            nll = 0.0
            for label, prob_dict in zip(y_true, probs):
                calibrated = Trainer._apply_temperature(prob_dict, temp)
                label_prob = calibrated.get(label, 1e-10)
                nll += -math.log(max(label_prob, 1e-10))
            
            if nll < best_nll:
                best_nll = nll
                best_temp = temp

        return best_temp

    @staticmethod
    def _apply_temperature(logits: dict[str, float], temperature: float) -> dict[str, float]:
        """Apply temperature scaling."""
        import math
        max_logit = max(logits.values())
        scaled = {k: (v - max_logit) / temperature for k, v in logits.items()}
        exp_scores = {k: math.exp(v) for k, v in scaled.items()}
        total = sum(exp_scores.values())
        return {k: v / total for k, v in exp_scores.items()}
