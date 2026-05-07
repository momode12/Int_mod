import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_seq_len=256, dropout=0.1):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        pe  = torch.zeros(max_seq_len, d_model)
        pos = torch.arange(0, max_seq_len, dtype=torch.float).unsqueeze(1)
        div = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        return self.dropout(x + self.pe[:, :x.size(1), :])


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads, dropout=0.1):
        super().__init__()
        assert d_model % num_heads == 0
        self.d_k       = d_model // num_heads
        self.num_heads = num_heads
        self.d_model   = d_model
        self.W_q     = nn.Linear(d_model, d_model, bias=False)
        self.W_k     = nn.Linear(d_model, d_model, bias=False)
        self.W_v     = nn.Linear(d_model, d_model, bias=False)
        self.W_o     = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def split_heads(self, x):
        B, S, _ = x.shape
        return x.view(B, S, self.num_heads, self.d_k).transpose(1, 2)

    def forward(self, x, mask=None):
        B, S, _ = x.shape
        Q = self.split_heads(self.W_q(x))
        K = self.split_heads(self.W_k(x))
        V = self.split_heads(self.W_v(x))
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float("-inf"))
        w   = self.dropout(F.softmax(scores, dim=-1))
        out = torch.matmul(w, V).transpose(1, 2).contiguous().view(B, S, self.d_model)
        return self.W_o(out)


class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(d_ff, d_model), nn.Dropout(dropout),
        )
    def forward(self, x): return self.net(x)


class TransformerBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()
        self.attn  = MultiHeadAttention(d_model, num_heads, dropout)
        self.ffn   = FeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.drop  = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        x = x + self.drop(self.attn(self.norm1(x), mask))
        return x + self.ffn(self.norm2(x))


class MiniTransformerEncoder(nn.Module):
    def __init__(self, vocab_size, d_model=256, num_heads=8, num_layers=4,
                 d_ff=512, max_seq_len=256, dropout=0.3, pad_idx=0):
        super().__init__()
        self.d_model         = d_model
        self.token_embedding = nn.Embedding(vocab_size, d_model, padding_idx=pad_idx)
        self.pos_encoding    = PositionalEncoding(d_model, max_seq_len, dropout)
        self.layers          = nn.ModuleList([
            TransformerBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])
        self.norm      = nn.LayerNorm(d_model)
        self.attn_pool = nn.Linear(d_model, 1)
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):      nn.init.xavier_uniform_(m.weight)
            elif isinstance(m, nn.Embedding): nn.init.normal_(m.weight, std=0.02)

    def create_padding_mask(self, ids):
        return (ids != 0).unsqueeze(1).unsqueeze(2)

    def attention_pooling(self, hidden, mask):
        scores   = self.attn_pool(hidden).squeeze(-1)
        pad_mask = (mask.squeeze(1).squeeze(1) == 0)
        scores   = scores.masked_fill(pad_mask, float("-inf"))
        weights  = F.softmax(scores, dim=-1).unsqueeze(-1)
        return (weights * hidden).sum(dim=1)

    def forward(self, input_ids):
        mask = self.create_padding_mask(input_ids)
        x    = self.token_embedding(input_ids) * math.sqrt(self.d_model)
        x    = self.pos_encoding(x)
        for layer in self.layers:
            x = layer(x, mask)
        x = self.norm(x)
        return self.attention_pooling(x, mask), x


class CategoryClassifier(nn.Module):
    def __init__(self, d_model, num_classes, dropout=0.4):
        super().__init__()
        self.classifier = nn.Sequential(
            nn.Linear(d_model, d_model // 2), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(d_model // 2, d_model // 4), nn.GELU(), nn.Dropout(dropout),
            nn.Linear(d_model // 4, num_classes),
        )
    def forward(self, x): return self.classifier(x)


class TextGeneratorHead(nn.Module):
    def __init__(self, d_model, vocab_size, dropout=0.3):
        super().__init__()
        self.d_model     = d_model
        self.ctx_proj    = nn.Linear(d_model, d_model)
        self.token_emb   = nn.Embedding(vocab_size, d_model)
        self.combine     = nn.Sequential(
            nn.Linear(d_model * 2, d_model), nn.GELU(), nn.Dropout(dropout)
        )
        self.self_attn   = MultiHeadAttention(d_model, num_heads=4, dropout=dropout)
        self.norm        = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, vocab_size)

    def forward(self, context, input_ids):
        B, S     = input_ids.shape
        tok_embs = self.token_emb(input_ids)
        ctx      = self.ctx_proj(context).unsqueeze(1).expand(B, S, self.d_model)
        combined = self.combine(torch.cat([ctx, tok_embs], dim=-1))
        hidden   = combined + self.self_attn(self.norm(combined))
        return self.output_proj(hidden)


class MiniMedicalLLM(nn.Module):
    def __init__(self, vocab_size, num_classes, d_model=256, num_heads=8,
                 num_layers=4, d_ff=512, max_seq_len=256, dropout=0.0):
        super().__init__()
        self.encoder    = MiniTransformerEncoder(
            vocab_size, d_model, num_heads, num_layers, d_ff, max_seq_len, dropout
        )
        self.classifier = CategoryClassifier(d_model, num_classes, dropout)
        self.generator  = TextGeneratorHead(d_model, vocab_size, dropout)

    def forward(self, input_ids, gen_input_ids=None):
        pooled, hidden = self.encoder(input_ids)
        result = {
            "class_logits": self.classifier(pooled),
            "pooled"      : pooled,
            "hidden"      : hidden,
        }
        if gen_input_ids is not None:
            result["gen_logits"] = self.generator(pooled, gen_input_ids)
        return result

    @torch.no_grad()
    def generate(self, enc_out, tokenizer, max_new_tokens=60,
                 temperature=0.75, top_k=30):
        self.eval()
        device    = enc_out.device
        generated = [tokenizer.sos_id]
        for _ in range(max_new_tokens):
            ids     = torch.tensor([generated], device=device)
            pad_len = max(64, len(generated))
            if pad_len > len(generated):
                ids = F.pad(ids, (0, pad_len - len(generated)),
                            value=tokenizer.pad_id)
            logits     = self.generator(enc_out, ids)[0, len(generated) - 1, :]
            logits     = logits / temperature
            if top_k > 0:
                top_vals, _ = torch.topk(logits, top_k)
                logits[logits < top_vals[-1]] = float("-inf")
            probs      = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, 1).item()
            if next_token == tokenizer.eos_id:
                break
            generated.append(next_token)
        return tokenizer.decode(generated[1:])
