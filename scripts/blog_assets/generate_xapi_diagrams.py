"""Generate 3 diagrams for the X API pricing update note article."""
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

matplotlib.rcParams["font.family"] = "Meiryo"
matplotlib.rcParams["axes.unicode_minus"] = False
matplotlib.rcParams["text.parse_math"] = False

OUT = Path(
    r"C:\Users\mitam\Desktop\work\50_ブログ\02_note\01_XToolsPro3\01_LP・販売記事\_attachments\20260418_XAPI改定"
)
OUT.mkdir(parents=True, exist_ok=True)

C_BLUE = "#1DA1F2"
C_GREEN = "#17BF63"
C_RED = "#E0245E"
C_ORANGE = "#F4A261"
C_BG = "#FFFFFF"
C_DARK = "#14171A"
C_GRAY = "#657786"
C_LIGHT = "#F5F8FA"


def fig_1_summary():
    fig, ax = plt.subplots(figsize=(14, 7), dpi=150)
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.axis("off")

    ax.text(
        0.5, 0.94,
        "X API 大改定 2026/4/20 施行 ― 3つの大きな柱",
        ha="center", va="center", fontsize=22, fontweight="bold", color=C_DARK,
        transform=ax.transAxes,
    )
    ax.text(
        0.5, 0.87,
        "2026-04-17 X Developer Platform Team 発表",
        ha="center", va="center", fontsize=12, color=C_GRAY,
        transform=ax.transAxes,
    )

    cards = [
        {
            "num": "①",
            "num_plain": "1",
            "title": "読み取り 激安化",
            "subtitle": "Owned Reads が $0.001/req に",
            "points": [
                "1,000リクエスト=$1",
                "自分のツイート/フォロワー",
                "/いいね/ブックマーク 等",
                "「吸い出し系」ほぼ無料圏",
            ],
            "color": C_GREEN,
            "badge": "値下げ",
        },
        {
            "num": "②",
            "num_plain": "2",
            "title": "投稿 値上げ",
            "subtitle": "プレーン$0.015 / URL付き$0.20",
            "points": [
                "プレーン +50% ($0.01→$0.015)",
                "URL付き +1,900% (20倍)",
                "100本/日・URL付きなら",
                "  月 約97,200円 コース",
            ],
            "color": C_RED,
            "badge": "値上げ",
        },
        {
            "num": "③",
            "num_plain": "3",
            "title": "書込み系 廃止",
            "subtitle": "API書込みがSelf-Serveから消滅",
            "points": [
                "自動フォロー/アンフォロー",
                "自動いいね",
                "引用RT (quote_tweet_id)",
                "Self-Serveでは今後不可",
            ],
            "color": C_ORANGE,
            "badge": "機能削除",
        },
    ]

    positions = [0.03, 0.355, 0.68]
    w, h = 0.29, 0.68

    for i, card in enumerate(cards):
        x = positions[i]
        y = 0.11

        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.015,rounding_size=0.02",
            linewidth=2.5, edgecolor=card["color"], facecolor=C_LIGHT,
            transform=ax.transAxes,
        )
        ax.add_patch(box)

        circle = plt.Circle(
            (x + 0.045, y + h - 0.085), 0.028,
            facecolor=card["color"], edgecolor="white", linewidth=2,
            transform=ax.transAxes,
        )
        ax.add_patch(circle)
        ax.text(
            x + 0.045, y + h - 0.085,
            card["num_plain"],
            ha="center", va="center", fontsize=20, fontweight="bold", color="white",
            transform=ax.transAxes,
        )

        badge = FancyBboxPatch(
            (x + w - 0.105, y + h - 0.11), 0.09, 0.055,
            boxstyle="round,pad=0.005,rounding_size=0.015",
            linewidth=0, facecolor=card["color"],
            transform=ax.transAxes,
        )
        ax.add_patch(badge)
        ax.text(
            x + w - 0.06, y + h - 0.0825,
            card["badge"],
            ha="center", va="center", fontsize=10, fontweight="bold", color="white",
            transform=ax.transAxes,
        )

        ax.text(
            x + 0.025, y + h - 0.18,
            card["title"],
            ha="left", va="center", fontsize=18, fontweight="bold", color=card["color"],
            transform=ax.transAxes,
        )
        ax.text(
            x + 0.025, y + h - 0.25,
            card["subtitle"],
            ha="left", va="center", fontsize=11, color=C_DARK,
            transform=ax.transAxes,
        )

        line_y = y + h - 0.30
        ax.plot(
            [x + 0.02, x + w - 0.02], [line_y, line_y],
            color=card["color"], linewidth=1, alpha=0.3,
            transform=ax.transAxes,
        )

        for j, point in enumerate(card["points"]):
            ax.text(
                x + 0.03, y + h - 0.37 - j * 0.07,
                "・" + point,
                ha="left", va="center", fontsize=11, color=C_DARK,
                transform=ax.transAxes,
            )

    ax.text(
        0.5, 0.04,
        "1ドル=162円（2026-04-01 手数料込レート） / 月30日換算",
        ha="center", va="center", fontsize=10, color=C_GRAY, style="italic",
        transform=ax.transAxes,
    )

    out = OUT / "diagram_01_xapi_summary.png"
    plt.savefig(out, bbox_inches="tight", facecolor=C_BG, dpi=150)
    plt.close(fig)
    print(f"saved: {out}")


def fig_2_write_pricing():
    fig, ax = plt.subplots(figsize=(12, 7), dpi=150)
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)

    categories = ["プレーン投稿", "URL付き投稿"]
    before = [0.01, 0.01]
    after = [0.015, 0.20]

    x = range(len(categories))
    width = 0.35

    bars1 = ax.bar(
        [i - width / 2 for i in x], before, width,
        label="旧料金 (〜2026/4/19)", color=C_GRAY, edgecolor="white", linewidth=2,
    )
    bars2 = ax.bar(
        [i + width / 2 for i in x], after, width,
        label="新料金 (2026/4/20〜)", color=[C_BLUE, C_RED], edgecolor="white", linewidth=2,
    )

    for bar, val in zip(bars1, before):
        ax.text(
            bar.get_x() + bar.get_width() / 2, val + 0.003,
            f"${val:.3f}",
            ha="center", va="bottom", fontsize=12, fontweight="bold", color=C_DARK,
        )

    for bar, val, old_val in zip(bars2, after, before):
        pct = (val - old_val) / old_val * 100
        color = C_BLUE if pct < 100 else C_RED
        ax.text(
            bar.get_x() + bar.get_width() / 2, val + 0.003,
            f"${val:.3f}",
            ha="center", va="bottom", fontsize=12, fontweight="bold", color=color,
        )
        label = f"+{pct:.0f}%" if pct < 200 else f"20倍 (+{pct:.0f}%)"
        ax.text(
            bar.get_x() + bar.get_width() / 2, val + 0.018,
            label,
            ha="center", va="bottom", fontsize=14, fontweight="bold", color=color,
        )

    ax.set_xticks(list(x))
    ax.set_xticklabels(categories, fontsize=14, fontweight="bold")
    ax.set_ylabel("1投稿あたりの単価 (USD)", fontsize=13)
    ax.set_title(
        "POST /2/tweets の単価 Before / After ― URL付きは20倍の衝撃",
        fontsize=18, fontweight="bold", pad=20, color=C_DARK,
    )
    ax.legend(loc="upper left", fontsize=12, framealpha=0.95)
    ax.set_ylim(0, 0.25)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.annotate(
        "",
        xy=(1 + width / 2, 0.20), xytext=(1 - width / 2, 0.01),
        arrowprops=dict(arrowstyle="->", color=C_RED, lw=2.5, alpha=0.7),
    )

    plt.tight_layout()
    out = OUT / "diagram_02_xapi_write_pricing.png"
    plt.savefig(out, bbox_inches="tight", facecolor=C_BG, dpi=150)
    plt.close(fig)
    print(f"saved: {out}")


def fig_3_monthly_cost():
    fig, axes = plt.subplots(1, 2, figsize=(15, 7.5), dpi=150)
    fig.patch.set_facecolor(C_BG)
    fig.suptitle(
        "月額コスト試算 ― 投稿本数 × プレーン/URL付き (1USD=162円, 月30日換算)",
        fontsize=17, fontweight="bold", y=0.995, color=C_DARK,
    )

    daily = [10, 50, 100]
    plain_monthly_jpy = [d * 30 * 0.015 * 162 for d in daily]
    url_monthly_jpy = [d * 30 * 0.20 * 162 for d in daily]
    plain_monthly_usd = [d * 30 * 0.015 for d in daily]
    url_monthly_usd = [d * 30 * 0.20 for d in daily]

    x = range(len(daily))
    width = 0.38

    ax = axes[0]
    ax.set_facecolor(C_BG)
    bars_p = ax.bar(
        [i - width / 2 for i in x], plain_monthly_jpy, width,
        label="プレーン投稿", color=C_BLUE, edgecolor="white", linewidth=2,
    )
    bars_u = ax.bar(
        [i + width / 2 for i in x], url_monthly_jpy, width,
        label="URL付き投稿", color=C_RED, edgecolor="white", linewidth=2,
    )
    for bar, jpy, usd in zip(bars_p, plain_monthly_jpy, plain_monthly_usd):
        ax.text(
            bar.get_x() + bar.get_width() / 2, jpy + 1500,
            f"約{int(jpy):,}円\n(${usd:.2f})",
            ha="center", va="bottom", fontsize=10, fontweight="bold", color=C_BLUE,
        )
    for bar, jpy, usd in zip(bars_u, url_monthly_jpy, url_monthly_usd):
        ax.text(
            bar.get_x() + bar.get_width() / 2, jpy + 1500,
            f"約{int(jpy):,}円\n(${usd:.2f})",
            ha="center", va="bottom", fontsize=10, fontweight="bold", color=C_RED,
        )
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{d}本/日" for d in daily], fontsize=13, fontweight="bold")
    ax.set_ylabel("月額コスト (円)", fontsize=12)
    ax.set_title("1ヶ月のAPI投稿コスト", fontsize=14, fontweight="bold", pad=10)
    ax.legend(loc="upper left", fontsize=11, framealpha=0.95)
    ax.set_ylim(0, max(url_monthly_jpy) * 1.2)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}")
    )

    ax = axes[1]
    ax.set_facecolor(C_BG)
    diff_jpy = [u - p for u, p in zip(url_monthly_jpy, plain_monthly_jpy)]
    bars_d = ax.bar(
        list(x), diff_jpy, width * 1.3, color=C_ORANGE, edgecolor="white", linewidth=2,
    )
    for bar, d in zip(bars_d, diff_jpy):
        ax.text(
            bar.get_x() + bar.get_width() / 2, d + 1500,
            f"+約{int(d):,}円/月",
            ha="center", va="bottom", fontsize=12, fontweight="bold", color="#C15A1E",
        )

    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{d}本/日" for d in daily], fontsize=13, fontweight="bold")
    ax.set_ylabel("月額差分 (円)", fontsize=12)
    ax.set_title(
        "同本数をURL付きに切り替えたときの追加コスト",
        fontsize=14, fontweight="bold", pad=10,
    )
    ax.set_ylim(0, max(diff_jpy) * 1.25)
    ax.grid(axis="y", alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}")
    )

    ax.text(
        0.5, 0.92,
        "100本/日 をURL付きに切り替えたら\n月 約9万円 の追加コスト",
        ha="center", va="top", fontsize=11, fontweight="bold",
        color="#C15A1E",
        transform=ax.transAxes,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#FFF4E6", edgecolor=C_ORANGE, linewidth=1.5),
    )

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out = OUT / "diagram_03_xapi_monthly_cost.png"
    plt.savefig(out, bbox_inches="tight", facecolor=C_BG, dpi=150)
    plt.close(fig)
    print(f"saved: {out}")


if __name__ == "__main__":
    fig_1_summary()
    fig_2_write_pricing()
    fig_3_monthly_cost()
    print("all diagrams generated.")
