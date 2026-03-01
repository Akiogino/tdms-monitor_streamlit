from __future__ import annotations

from typing import Iterable

import pandas as pd
import plotly.graph_objects as go


def vs_to_xy(score_v: float, score_s: float) -> tuple[float, float]:
    """
    V/Sを図上のx/yへ変換する。

    x = A = V - S, y = P = V + S とすることで、
    - 右上: 活性度Vが高い
    - 左上: 安定度Sが高い
    - 上:   快適度Pが高い
    - 右下: 覚醒度Aが高い
    - 左下: 覚醒度Aが低い
    の関係が読み取りやすくなる。
    """
    x = score_v - score_s
    y = score_v + score_s
    return float(x), float(y)


def create_mood_diagram(
    score_v: int,
    score_s: int,
    recent_vs: Iterable[tuple[int, int]] | None = None,
) -> go.Figure:
    fig = go.Figure()

    diamond_x = [0, 20, 0, -20, 0]
    diamond_y = [20, 0, -20, 0, 20]

    fig.add_trace(
        go.Scatter(
            x=diamond_x,
            y=diamond_y,
            mode="lines",
            name="外枠",
            line={"color": "#7a7a7a", "width": 2},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[-20, 20],
            y=[0, 0],
            mode="lines",
            line={"color": "#c9c9c9", "width": 1, "dash": "dot"},
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 0],
            y=[-20, 20],
            mode="lines",
            line={"color": "#c9c9c9", "width": 1, "dash": "dot"},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    if recent_vs:
        recent_points = list(recent_vs)
        if recent_points:
            recent_xy = [vs_to_xy(v, s) for v, s in recent_points]
            fig.add_trace(
                go.Scatter(
                    x=[point[0] for point in recent_xy],
                    y=[point[1] for point in recent_xy],
                    mode="markers",
                    marker={"size": 9, "color": "rgba(44, 127, 184, 0.30)"},
                    name="直近",
                    showlegend=False,
                )
            )

    current_x, current_y = vs_to_xy(score_v, score_s)
    fig.add_trace(
        go.Scatter(
            x=[current_x],
            y=[current_y],
            mode="markers",
            marker={"size": 14, "color": "#d84a4a", "line": {"width": 1, "color": "#ffffff"}},
            name="現在",
            showlegend=False,
        )
    )

    fig.update_layout(
        height=420,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        xaxis={
            "title": "",
            "range": [-22, 22],
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False,
            "constrain": "domain",
        },
        yaxis={
            "title": "",
            "range": [-22, 22],
            "showgrid": False,
            "zeroline": False,
            "showticklabels": False,
            "scaleanchor": "x",
            "scaleratio": 1,
        },
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
    )

    fig.add_annotation(x=0, y=21, text="快適", showarrow=False, font={"size": 12})
    fig.add_annotation(x=0, y=-21, text="不快", showarrow=False, font={"size": 12})
    fig.add_annotation(x=21, y=0, text="覚醒高", showarrow=False, font={"size": 12})
    fig.add_annotation(x=-21, y=0, text="覚醒低", showarrow=False, font={"size": 12})
    fig.add_annotation(x=13, y=13, text="活性高", showarrow=False, font={"size": 11, "color": "#666666"})
    fig.add_annotation(x=-13, y=13, text="安定高", showarrow=False, font={"size": 11, "color": "#666666"})
    fig.add_annotation(x=12, y=-12, text="覚醒高方向", showarrow=False, font={"size": 10, "color": "#666666"})
    fig.add_annotation(x=-12, y=-12, text="覚醒低方向", showarrow=False, font={"size": 10, "color": "#666666"})

    return fig


def create_score_timeseries_figure(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    if df.empty:
        return fig

    plot_df = df.copy()
    plot_df["created_at"] = pd.to_datetime(plot_df["created_at"], errors="coerce")
    plot_df = plot_df.dropna(subset=["created_at"])
    plot_df = plot_df.sort_values("created_at")

    if plot_df.empty:
        return fig

    series_definitions = [
        ("score_v", "V", "#1f77b4"),
        ("score_s", "S", "#2ca02c"),
        ("score_p", "P", "#9467bd"),
        ("score_a", "A", "#ff7f0e"),
    ]

    for column, label, color in series_definitions:
        fig.add_trace(
            go.Scatter(
                x=plot_df["created_at"],
                y=plot_df[column],
                mode="lines+markers",
                name=label,
                line={"color": color, "width": 2},
                marker={"size": 7},
            )
        )

    fig.update_layout(
        height=360,
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        xaxis={"title": "日時"},
        yaxis={"title": "スコア"},
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
    )

    return fig
