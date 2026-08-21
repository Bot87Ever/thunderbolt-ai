import csv
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ============================================================
# CONFIGURATION
# ============================================================

REPORT_FILE = "Thunderbolt_AI_Final_Benchmark_Report.pdf"

ANALYSIS_FILE = "benchmark/final_analysis.csv"

GRAPH_FOLDER = "benchmark/graphs"


# ============================================================
# READ RESULTS
# ============================================================

results = []

with open(ANALYSIS_FILE, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        results.append(row)


results.sort(key=lambda row: int(row["rank"]))

winner = results[0]["model"]


# ============================================================
# PAGE HEADER / FOOTER
# ============================================================

def draw_page(canvas, document):

    canvas.saveState()

    width, height = A4

    # Top line
    canvas.setStrokeColor(colors.HexColor("#1F2937"))
    canvas.setLineWidth(0.7)

    canvas.line(
        20 * mm,
        height - 15 * mm,
        width - 20 * mm,
        height - 15 * mm
    )

    # Header
    canvas.setFont("Helvetica-Bold", 8)

    canvas.setFillColor(colors.HexColor("#374151"))

    canvas.drawString(
        20 * mm,
        height - 11.5 * mm,
        "THUNDERBOLT.AI"
    )

    canvas.setFont("Helvetica", 8)

    canvas.drawRightString(
        width - 20 * mm,
        height - 11.5 * mm,
        "LOCAL LLM BENCHMARK REPORT"
    )

    # Bottom line
    canvas.setStrokeColor(colors.HexColor("#D1D5DB"))

    canvas.line(
        20 * mm,
        14 * mm,
        width - 20 * mm,
        14 * mm
    )

    # Footer
    canvas.setFont("Helvetica", 7)

    canvas.setFillColor(colors.HexColor("#6B7280"))

    canvas.drawString(
        20 * mm,
        9 * mm,
        "Thunderbolt.ai - Benchmark Evaluation"
    )

    canvas.drawRightString(
        width - 20 * mm,
        9 * mm,
        f"Page {document.page}"
    )

    canvas.restoreState()


# ============================================================
# DOCUMENT
# ============================================================

doc = SimpleDocTemplate(
    REPORT_FILE,
    pagesize=A4,
    rightMargin=20 * mm,
    leftMargin=20 * mm,
    topMargin=23 * mm,
    bottomMargin=20 * mm
)


# ============================================================
# COLORS
# ============================================================

NAVY = colors.HexColor("#111827")
DARK = colors.HexColor("#1F2937")
GRAY = colors.HexColor("#6B7280")
LIGHT_GRAY = colors.HexColor("#F3F4F6")
BORDER = colors.HexColor("#D1D5DB")
BLUE = colors.HexColor("#2563EB")
GREEN = colors.HexColor("#059669")
WHITE = colors.white


# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()


cover_title = ParagraphStyle(
    "CoverTitle",
    fontName="Helvetica-Bold",
    fontSize=28,
    leading=34,
    textColor=NAVY,
    alignment=TA_CENTER,
    spaceAfter=10
)


cover_subtitle = ParagraphStyle(
    "CoverSubtitle",
    fontName="Helvetica",
    fontSize=13,
    leading=19,
    textColor=GRAY,
    alignment=TA_CENTER,
    spaceAfter=8
)


section_title = ParagraphStyle(
    "SectionTitle",
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=23,
    textColor=NAVY,
    spaceBefore=5,
    spaceAfter=12
)


subsection_title = ParagraphStyle(
    "SubsectionTitle",
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=16,
    textColor=DARK,
    spaceBefore=10,
    spaceAfter=7
)


body = ParagraphStyle(
    "Body",
    fontName="Helvetica",
    fontSize=9.5,
    leading=15,
    textColor=DARK,
    spaceAfter=8
)


small = ParagraphStyle(
    "Small",
    fontName="Helvetica",
    fontSize=8,
    leading=12,
    textColor=GRAY,
    spaceAfter=5
)


winner_title = ParagraphStyle(
    "WinnerTitle",
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=26,
    textColor=GREEN,
    alignment=TA_CENTER,
    spaceBefore=10,
    spaceAfter=10
)


metric_value = ParagraphStyle(
    "MetricValue",
    fontName="Helvetica-Bold",
    fontSize=16,
    leading=19,
    textColor=NAVY,
    alignment=TA_CENTER
)


metric_label = ParagraphStyle(
    "MetricLabel",
    fontName="Helvetica",
    fontSize=8,
    leading=10,
    textColor=GRAY,
    alignment=TA_CENTER
)


# ============================================================
# HELPERS
# ============================================================

def section(number, title):

    return Paragraph(
        f"{number}. {title}",
        section_title
    )


def add_metric_card(label, value):

    data = [
        [
            Paragraph(str(value), metric_value)
        ],
        [
            Paragraph(label, metric_label)
        ]
    ]

    table = Table(
        data,
        colWidths=[42 * mm],
        rowHeights=[12 * mm, 9 * mm]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
            ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ])
    )

    return table


def add_graph(filename, title, height=82 * mm):

    path = os.path.join(GRAPH_FOLDER, filename)

    if not os.path.exists(path):
        return []

    elements = []

    elements.append(
        Paragraph(
            title,
            subsection_title
        )
    )

    image = Image(
        path,
        width=165 * mm,
        height=height
    )

    elements.append(image)
    elements.append(Spacer(1, 6))

    return elements


# ============================================================
# STORY
# ============================================================

story = []


# ============================================================
# COVER PAGE
# ============================================================

story.append(Spacer(1, 38 * mm))

story.append(
    Paragraph(
        "THUNDERBOLT.AI",
        cover_title
    )
)

story.append(
    Paragraph(
        "Local Large Language Model Benchmark",
        cover_subtitle
    )
)

story.append(
    Paragraph(
        "Performance, Quality and Hardware Efficiency Evaluation",
        cover_subtitle
    )
)

story.append(Spacer(1, 18 * mm))


cover_table = Table(
    [
        [
            Paragraph(
                "<b>BENCHMARK STATUS</b><br/>"
                "Completed evaluation",
                body
            ),
            Paragraph(
                "<b>MODELS TESTED</b><br/>"
                "3 local language models",
                body
            )
        ],
        [
            Paragraph(
                "<b>TEST QUESTIONS</b><br/>"
                "10 standardized questions",
                body
            ),
            Paragraph(
                "<b>INFERENCE</b><br/>"
                "Local Ollama runtime",
                body
            )
        ]
    ],
    colWidths=[78 * mm, 78 * mm]
)

cover_table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("BOX", (0, 0), (-1, -1), 0.8, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ])
)

story.append(cover_table)

story.append(Spacer(1, 25 * mm))

story.append(
    Paragraph(
        "Prepared from measured local inference results",
        cover_subtitle
    )
)

story.append(PageBreak())


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================

story.append(section("1", "Executive Summary"))

story.append(
    Paragraph(
        "Thunderbolt.ai was evaluated as a local large language model "
        "benchmarking system using three models running through Ollama "
        "on a laptop equipped with an Intel Core i7-13620H processor and "
        "an NVIDIA GeForce RTX 4050 Laptop GPU with 6 GB of VRAM.",
        body
    )
)

story.append(
    Paragraph(
        "The evaluation used a common set of ten questions covering "
        "coding, debugging, reasoning and technical knowledge. "
        "For each request, the system recorded response latency, "
        "generated tokens, generation speed and hardware utilization.",
        body
    )
)

story.append(
    Paragraph(
        f"The measured results produced <b>{winner}</b> as the highest-"
        "scoring model under the weighting scheme used by this benchmark. "
        "The result is specific to the tested workload and hardware "
        "configuration and is not intended to represent a universal "
        "ranking of the evaluated models.",
        body
    )
)

story.append(Spacer(1, 5 * mm))


# Metric cards

cards = Table(
    [
        [
            add_metric_card("Overall Winner", winner),
            add_metric_card(
                "Best Quality",
                max(
                    results,
                    key=lambda x: float(x["quality"])
                )["model"]
            ),
            add_metric_card(
                "Fastest",
                max(
                    results,
                    key=lambda x: float(x["tokens_per_second"])
                )["model"]
            )
        ]
    ],
    colWidths=[54 * mm, 54 * mm, 54 * mm]
)

cards.setStyle(
    TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ])
)

story.append(cards)


# ============================================================
# SYSTEM CONFIGURATION
# ============================================================

story.append(Spacer(1, 10 * mm))

story.append(section("2", "Evaluation Environment"))

environment_data = [
    ["Component", "Measured Configuration"],
    ["Processor", "13th Gen Intel Core i7-13620H"],
    ["Graphics", "NVIDIA GeForce RTX 4050 Laptop GPU"],
    ["GPU Memory", "6 GB"],
    ["Inference Runtime", "Ollama"],
    ["Execution", "Local inference"],
    ["Models", "Qwen2.5-Coder 7B, Gemma 3 4B, Qwen3 8B"],
    ["Benchmark Questions", "10"]
]

table = Table(
    environment_data,
    colWidths=[52 * mm, 104 * mm]
)

table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("BACKGROUND", (0, 1), (0, -1), LIGHT_GRAY),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 1), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
)

story.append(table)


# ============================================================
# MODELS
# ============================================================

story.append(Spacer(1, 10 * mm))

story.append(section("3", "Models Evaluated"))

model_data = [
    ["Model", "Parameter Class", "Primary Evaluation Role"],
    ["Qwen2.5-Coder 7B", "7B", "Coding and debugging"],
    ["Gemma 3 4B", "4B", "General-purpose local inference"],
    ["Qwen3 8B", "8B", "General reasoning and technical tasks"]
]

table = Table(
    model_data,
    colWidths=[58 * mm, 35 * mm, 63 * mm]
)

table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
)

story.append(table)


# ============================================================
# METHODOLOGY
# ============================================================

story.append(PageBreak())

story.append(section("4", "Benchmark Methodology"))

story.append(
    Paragraph(
        "All three models were evaluated using the same benchmark "
        "questions and the same local inference environment. "
        "This provides a controlled basis for comparing their measured "
        "performance.",
        body
    )
)

story.append(
    Paragraph(
        "The benchmark categories were coding, debugging, reasoning "
        "and technical knowledge. Each model received ten questions "
        "through the same benchmark runner.",
        body
    )
)

story.append(
    Paragraph(
        "<b>Measured inference metrics:</b>",
        body
    )
)

method_data = [
    ["Metric", "Purpose"],
    ["Response time", "Measures total request latency."],
    ["Generated tokens", "Measures response length."],
    ["Tokens per second", "Measures generation throughput."],
    ["CPU utilization", "Measures processor load."],
    ["RAM usage", "Measures system memory consumption."],
    ["GPU utilization", "Measures GPU workload."],
    ["VRAM usage", "Measures GPU memory consumption."]
]

table = Table(
    method_data,
    colWidths=[55 * mm, 101 * mm]
)

table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("BACKGROUND", (0, 1), (0, -1), LIGHT_GRAY),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
)

story.append(table)


# ============================================================
# OVERALL RESULTS
# ============================================================

story.append(Spacer(1, 10 * mm))

story.append(section("5", "Measured Results"))

performance_data = [
    [
        "Rank",
        "Model",
        "Quality",
        "Time",
        "Tok/s",
        "VRAM",
        "Score"
    ]
]

for row in results:

    performance_data.append([
        row["rank"],
        row["model"],
        row["quality"],
        f'{float(row["response_time"]):.2f}s',
        f'{float(row["tokens_per_second"]):.2f}',
        f'{float(row["vram_average_gb"]):.2f} GB',
        row["final_score"]
    ])


table = Table(
    performance_data,
    colWidths=[
        13 * mm,
        48 * mm,
        18 * mm,
        20 * mm,
        20 * mm,
        22 * mm,
        20 * mm
    ]
)

table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#ECFDF5")),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ])
)

story.append(table)


# ============================================================
# QUALITY
# ============================================================

story.append(PageBreak())

story.append(section("6", "Quality Evaluation"))

story.append(
    Paragraph(
        "The quality evaluation assigns a score to each benchmark "
        "response according to predefined criteria associated with "
        "the individual question. The resulting scores represent "
        "performance on this benchmark set rather than a universal "
        "measure of model intelligence.",
        body
    )
)

story.extend(
    add_graph(
        "quality_comparison.png",
        "Figure 1. Quality Score Comparison",
        82 * mm
    )
)


# ============================================================
# SPEED
# ============================================================

story.append(section("7", "Inference Speed and Latency"))

story.append(
    Paragraph(
        "Generation speed is reported as tokens generated per second. "
        "Response time represents the total elapsed time for each "
        "benchmark request.",
        body
    )
)

story.extend(
    add_graph(
        "tokens_per_second_comparison.png",
        "Figure 2. Generation Throughput",
        72 * mm
    )
)

story.extend(
    add_graph(
        "response_time_comparison.png",
        "Figure 3. Average Response Time",
        72 * mm
    )
)


# ============================================================
# HARDWARE
# ============================================================

story.append(PageBreak())

story.append(section("8", "Hardware Utilization"))

story.append(
    Paragraph(
        "Hardware measurements show how heavily each model used the "
        "available CPU, system memory, GPU and VRAM during inference. "
        "These measurements are particularly relevant for local "
        "deployment because the laptop has a finite 6 GB VRAM budget.",
        body
    )
)

story.extend(
    add_graph(
        "cpu_comparison.png",
        "Figure 4. Average CPU Utilization",
        67 * mm
    )
)

story.extend(
    add_graph(
        "ram_comparison.png",
        "Figure 5. Average RAM Usage",
        67 * mm
    )
)

story.append(PageBreak())

story.extend(
    add_graph(
        "gpu_comparison.png",
        "Figure 6. Average GPU Utilization",
        72 * mm
    )
)

story.extend(
    add_graph(
        "vram_comparison.png",
        "Figure 7. Average VRAM Usage",
        72 * mm
    )
)


# ============================================================
# FINAL ANALYSIS
# ============================================================

story.append(PageBreak())

story.append(section("9", "Final Analysis"))

story.append(
    Paragraph(
        f"<b>{winner}</b> achieved the highest overall benchmark score "
        "under the weighting scheme implemented by Thunderbolt.ai.",
        body
    )
)

story.append(
    Paragraph(
        "The measured results show that Gemma 3 4B achieved a quality "
        "score of 10.00/10, an average generation speed of 54.70 "
        "tokens per second, an average response time of 23.93 seconds "
        "and an average VRAM usage of approximately 3.78 GB.",
        body
    )
)

story.append(
    Paragraph(
        "Qwen2.5-Coder 7B achieved a quality score of 9.50/10 and "
        "provided a coding-oriented alternative, while Qwen3 8B "
        "provided the largest parameter class among the evaluated "
        "models but produced substantially lower generation throughput "
        "on the tested hardware.",
        body
    )
)

story.append(
    Paragraph(
        "These findings demonstrate the importance of evaluating "
        "models using both output quality and system-level performance. "
        "Parameter count alone does not determine the most suitable "
        "model for a local deployment.",
        body
    )
)


# ============================================================
# WEIGHTING
# ============================================================

story.append(Spacer(1, 5 * mm))

story.append(
    Paragraph(
        "Benchmark Scoring Model",
        subsection_title
    )
)

weight_data = [
    ["Component", "Weight"],
    ["Quality", "40%"],
    ["Generation speed", "25%"],
    ["Response latency", "15%"],
    ["Hardware efficiency", "20%"],
    ["Total", "100%"]
]

table = Table(
    weight_data,
    colWidths=[105 * mm, 51 * mm]
)

table.setStyle(
    TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT_GRAY),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("PADDING", (0, 0), (-1, -1), 6),
    ])
)

story.append(table)


# ============================================================
# CONCLUSION
# ============================================================

story.append(Spacer(1, 10 * mm))

story.append(section("10", "Conclusion"))

story.append(
    Paragraph(
        "The benchmark successfully established a repeatable local "
        "evaluation pipeline for comparing language models under a "
        "controlled hardware environment.",
        body
    )
)

story.append(
    Paragraph(
        "For the tested workload, Gemma 3 4B provided the strongest "
        "overall balance between answer quality, generation speed, "
        "response latency and hardware requirements.",
        body
    )
)

story.append(
    Paragraph(
        "Qwen2.5-Coder 7B remains a relevant option for coding-focused "
        "workloads, while Qwen3 8B demonstrates the performance cost "
        "associated with running a larger model on hardware with a "
        "6 GB VRAM constraint.",
        body
    )
)

story.append(
    Paragraph(
        "The results documented in this report are measurements from "
        "the specified benchmark environment and should be interpreted "
        "as an engineering comparison of local inference performance.",
        body
    )
)


# ============================================================
# BENCHMARK RECORD
# ============================================================

story.append(Spacer(1, 8 * mm))

story.append(
    Paragraph(
        "Benchmark Record",
        subsection_title
    )
)

record_data = [
    ["Models evaluated", "3"],
    ["Questions per model", "10"],
    ["Evaluation categories", "Coding, Debugging, Reasoning, Technical"],
    ["Inference runtime", "Ollama"],
    ["GPU memory available", "6 GB"],
    ["Report basis", "Measured local inference results"]
]

table = Table(
    record_data,
    colWidths=[65 * mm, 91 * mm]
)

table.setStyle(
    TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("PADDING", (0, 0), (-1, -1), 6),
    ])
)

story.append(table)


# ============================================================
# BUILD
# ============================================================

doc.build(
    story,
    onFirstPage=draw_page,
    onLaterPages=draw_page
)


print()
print("=" * 70)
print("THUNDERBOLT.AI")
print("FINAL PROFESSIONAL REPORT GENERATED")
print("=" * 70)
print()
print(f"Report: {REPORT_FILE}")
print()