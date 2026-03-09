from __future__ import annotations

from typing import Mapping

QUESTION_ITEMS: list[tuple[str, str]] = [
    ("calm", "落ち着いた"),
    ("irritated", "イライラした"),
    ("lethargic", "無気力な"),
    ("lively", "活気にあふれた"),
    ("relaxed", "リラックスした"),
    ("edgy", "ピリピリした"),
    ("lazy", "だらけた"),
    ("energetic", "イキイキした"),
]

SCALE_LABELS: dict[int, str] = {
    0: "全くそうでない",
    1: "少しはそう",
    2: "ややそう",
    3: "ある程度そう",
    4: "かなりそう",
    5: "非常にそう",
}


def validate_answers(answers: Mapping[str, object]) -> tuple[bool, str | None]:
    """8項目の必須入力と0〜5の範囲チェックを行う。"""
    missing_labels: list[str] = []

    for key, label in QUESTION_ITEMS:
        value = answers.get(key)
        if value is None:
            missing_labels.append(label)
            continue

        if not isinstance(value, int):
            return False, f"{label} の値が不正です。0〜5の整数を選んでください。"

        if value < 0 or value > 5:
            return False, f"{label} の値が範囲外です。0〜5で回答してください。"

    if missing_labels:
        return False, f"未回答の項目があります: {', '.join(missing_labels)}"

    return True, None


def calculate_scores(answers: Mapping[str, int]) -> dict[str, int]:
    """二次元気分尺度の計算式でV, S, P, Aを整数で計算する。"""
    v = answers["lively"] + answers["energetic"] - answers["lethargic"] - answers["lazy"]
    s = answers["calm"] + answers["relaxed"] - answers["irritated"] - answers["edgy"]
    p = v + s
    a = v - s

    return {
        "score_v": int(v),
        "score_s": int(s),
        "score_p": int(p),
        "score_a": int(a),
    }


def _score_phrase(value: int, positive: str, negative: str, neutral: str) -> str:
    if value > 0:
        return positive
    if value < 0:
        return negative
    return neutral


def build_score_report(
    created_at: str,
    score_v: int,
    score_s: int,
    score_p: int,
    score_a: int,
) -> str:
    """採点値と簡易評価を1つのテキストに整形する。"""
    evaluations = [
        _score_phrase(score_v, "活力は十分。", "やや疲労傾向。", "活力は平均的。"),
        _score_phrase(score_s, "情緒は安定。", "緊張気味。", "情緒は中間。"),
        _score_phrase(score_p, "気分は明るめ。", "気分は落ち込み気味。", "気分はニュートラル。"),
        _score_phrase(score_a, "覚醒度は高め。", "やや眠気傾向。", "覚醒度は標準。"),
    ]

    return (
        f"【タイムスタンプ】\n{created_at}\n\n"
        f"【数値】\n"
        f"活性度：{score_v}｜安定度：{score_s}｜快適度：{score_p}｜覚醒度：{score_a}\n\n"
        f"【評価】\n"
        f"{''.join(evaluations)}"
    )
