import io
import json
from datetime import datetime, timezone
from typing import Dict, Any


# ─── Clinical interpretation text per detected class ─────────────────────────
CLINICAL_INTERPRETATION = {
    "polyp": (
        "The analyzed frame contains a detected mucosal protrusion consistent with a colonic polyp. "
        "The AI model identified a raised, lobulated sessile lesion with altered surface pit pattern. "
        "Adenomatous polyps carry significant malignant transformation risk and require endoscopic "
        "resection with histopathological evaluation. This AI output is a research decision-support "
        "result and must be confirmed by a qualified gastroenterologist."
    ),
    "ulcer": (
        "The analyzed frame contains a detected mucosal defect consistent with peptic or inflammatory "
        "ulceration. The AI model identified a focal mucosal breach with surrounding erythema and "
        "possible fibrinopurulent exudate. Biopsy of the ulcer margins is recommended to exclude "
        "malignant transformation and to test for H. pylori infection. This result is for clinical "
        "decision support only."
    ),
    "bleeding": (
        "The analyzed frame contains evidence of active or recent gastrointestinal hemorrhage. "
        "The AI model identified intraluminal blood or an exposed bleeding vessel. Immediate "
        "endoscopic haemostatic intervention may be required depending on the clinical context. "
        "This AI output does not replace emergency clinical assessment by a licensed physician."
    ),
    "esophagitis": (
        "The analyzed frame contains features consistent with erosive reflux esophagitis. "
        "The AI model identified mucosal breaks in the distal esophagus above the gastroesophageal "
        "junction. Los Angeles classification grading and PPI therapy initiation are recommended. "
        "This result is for research and clinical decision support only."
    ),
    "mucosal_lesion": (
        "The analyzed frame contains a detected region that the configured research model has "
        "identified as a suspicious mucosal lesion. The reported confidence values represent model "
        "outputs and should not be interpreted as a confirmed clinical diagnosis. The result is "
        "intended to support further review by a qualified healthcare professional."
    ),
    "default": (
        "The analyzed frame contains a detected region that the configured research model has "
        "identified as suspicious. The reported confidence values represent model outputs and should "
        "not be interpreted as a confirmed clinical diagnosis. The result is intended to support "
        "further review by a qualified healthcare professional."
    ),
}


def _get_interpretation(class_name: str) -> str:
    key = (class_name or "").lower().replace(" ", "_").replace("(", "").replace(")", "")
    for k in CLINICAL_INTERPRETATION:
        if k in key:
            return CLINICAL_INTERPRETATION[k]
    return CLINICAL_INTERPRETATION["default"]


def _blur_label(score: float) -> str:
    if score >= 150:
        return "Sharp"
    if score >= 80:
        return "Acceptable"
    return "Blurry"


def _brightness_label(score: float) -> str:
    if 80 <= score <= 190:
        return "Acceptable"
    if score < 80:
        return "Under-exposed"
    return "Over-exposed"


def _quality_score(blur: float, brightness: float) -> float:
    b = min(1.0, blur / 200.0)
    br = 1.0 - abs(brightness - 130.0) / 130.0
    return round(min(1.0, (b * 0.6 + br * 0.4)), 2)


def _review_label(status: str) -> str:
    s = (status or "PENDING").upper()
    mapping = {
        "ACCEPTED": "Accepted by clinician",
        "ACCEPT": "Accepted by clinician",
        "REJECTED": "Rejected by clinician",
        "REJECT": "Rejected by clinician",
        "FURTHER_REVIEW": "Further review requested",
        "PENDING": "Pending clinician review",
    }
    for k, v in mapping.items():
        if k in s:
            return v
    return "Pending clinician review"


class ReportGenerator:
    """Generates structured EndoAI Vision PDF reports in the reference format."""

    @staticmethod
    def generate_json_report(exam_data: Dict[str, Any]) -> str:
        return json.dumps({
            "title": "EndoAI Vision - Endoscopic Analysis Report",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "examination": exam_data,
        }, indent=2, default=str)

    @staticmethod
    def generate_pdf_report_bytes(exam_data: Dict[str, Any]) -> bytes:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer,
                Table, TableStyle, HRFlowable, KeepTogether,
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import mm

            # ── Page Setup ───────────────────────────────────────────────────
            buf = io.BytesIO()
            doc = SimpleDocTemplate(
                buf,
                pagesize=letter,
                leftMargin=18 * mm,
                rightMargin=18 * mm,
                topMargin=14 * mm,
                bottomMargin=16 * mm,
            )
            W = letter[0] - 36 * mm  # usable width

            # ── Color Palette (matching reference) ────────────────────────────
            C_DARK    = colors.HexColor("#0f172a")   # near-black text
            C_HEADER  = colors.HexColor("#1e3a5f")   # dark navy section headers
            C_TH_BG   = colors.HexColor("#e8edf3")   # table header background
            C_ROW_ALT = colors.HexColor("#f7f9fb")   # alternating row
            C_GREEN   = colors.HexColor("#16a34a")   # accepted status
            C_RED     = colors.HexColor("#dc2626")   # rejected / high risk
            C_AMBER   = colors.HexColor("#d97706")   # further review
            C_MUTED   = colors.HexColor("#64748b")   # secondary text
            C_BORDER  = colors.HexColor("#cbd5e1")   # table border
            C_LOGO    = colors.HexColor("#059669")   # EndoAI green

            # ── Styles ────────────────────────────────────────────────────────
            styles = getSampleStyleSheet()
            base = styles["Normal"]

            logo_style = ParagraphStyle("Logo", parent=base, fontName="Helvetica-Bold",
                                        fontSize=20, leading=24, textColor=C_LOGO)
            tag_style  = ParagraphStyle("Tag", parent=base, fontName="Helvetica-Bold",
                                        fontSize=7.5, textColor=C_DARK, alignment=2)
            tag2_style = ParagraphStyle("Tag2", parent=base, fontName="Helvetica",
                                        fontSize=7, textColor=C_MUTED, alignment=2)

            sec_style  = ParagraphStyle("Sec", parent=base, fontName="Helvetica-Bold",
                                        fontSize=9.5, textColor=colors.white,
                                        leftIndent=4, leading=14)
            body_style = ParagraphStyle("Body", parent=base, fontName="Helvetica",
                                        fontSize=8.5, leading=12, textColor=C_DARK)
            bold_style = ParagraphStyle("Bold", parent=body_style, fontName="Helvetica-Bold")
            sm_style   = ParagraphStyle("Sm", parent=base, fontName="Helvetica",
                                        fontSize=7.5, leading=11, textColor=C_MUTED)
            footer_imp = ParagraphStyle("FootImp", parent=base, fontName="Helvetica-Bold",
                                        fontSize=7, textColor=C_DARK)
            footer_sm  = ParagraphStyle("FootSm", parent=base, fontName="Helvetica",
                                        fontSize=6.5, textColor=C_MUTED, alignment=1)

            story = []

            # ═══════════════════════════════════════════════════════════════
            # HEADER: Logo + Report type tag
            # ═══════════════════════════════════════════════════════════════
            header_data = [[
                Paragraph("EndoAI Vision", logo_style),
                [
                    Paragraph("ENDOSCOPIC ANALYSIS REPORT", tag_style),
                    Paragraph("AI-assisted clinical decision support", tag2_style),
                ]
            ]]
            header_tbl = Table(header_data, colWidths=[W * 0.55, W * 0.45])
            header_tbl.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            story.append(header_tbl)
            story.append(HRFlowable(width="100%", thickness=1.5,
                                    color=C_BORDER, spaceBefore=4, spaceAfter=10))

            # ── Helper: Section Title Bar ─────────────────────────────────
            def section_title(num: str, title: str):
                t = Table([[Paragraph(f"{num}. {title.upper()}", sec_style)]],
                          colWidths=[W])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), C_HEADER),
                    ("TOPPADDING",    (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
                ]))
                return t

            # ── Helper: Two-column key-value table ────────────────────────
            def kv_table(rows, col_w=None):
                """rows = list of (label, value, label, value)"""
                col_w = col_w or [W * 0.22, W * 0.28, W * 0.22, W * 0.28]
                data = []
                for r in rows:
                    data.append([
                        Paragraph(str(r[0]), bold_style),
                        Paragraph(str(r[1]), body_style),
                        Paragraph(str(r[2]), bold_style),
                        Paragraph(str(r[3]), body_style),
                    ])
                t = Table(data, colWidths=col_w)
                t.setStyle(TableStyle([
                    ("GRID",         (0, 0), (-1, -1), 0.4, C_BORDER),
                    ("BACKGROUND",   (0, 0), (0, -1), C_TH_BG),
                    ("BACKGROUND",   (2, 0), (2, -1), C_TH_BG),
                    ("VALIGN",       (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING",   (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
                    ("LEFTPADDING",  (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1),
                     [colors.white, C_ROW_ALT]),
                ]))
                return t

            # ── Gather data ───────────────────────────────────────────────
            exam_id    = exam_data.get("id", "DEMO-EXAM-001")
            input_type = exam_data.get("input_type", "IMAGE")
            created_raw= exam_data.get("created_at", "")
            try:
                dt = datetime.fromisoformat(str(created_raw).replace("Z", "+00:00"))
                date_str = dt.strftime("%d/%m/%Y %H:%M")
            except Exception:
                date_str = datetime.now().strftime("%d/%m/%Y %H:%M")

            frames     = exam_data.get("frames", [])
            detections = exam_data.get("detections", [])
            if not detections:
                for f in frames:
                    detections.extend(f.get("detections", []))

            quality    = exam_data.get("quality", {})
            blur_sc    = float(quality.get("blur_score", 120.0))
            bright_sc  = float(quality.get("brightness_score", 120.0))
            overall_q  = quality.get("overall_quality", "GOOD")

            input_label = {
                "IMAGE": "Endoscopic Image",
                "VIDEO": "Endoscopic Video",
            }.get(input_type, "Endoscopic Image")

            # ════════════════════════════════════════════════════════════════
            # SECTION 1 — EXAMINATION INFORMATION
            # ════════════════════════════════════════════════════════════════
            story.append(section_title("1", "Examination Information"))
            story.append(Spacer(1, 2))
            story.append(kv_table([
                ("Examination ID", exam_id[:20], "Date / Time", date_str),
                ("Input Type",     input_label,  "Frames Analyzed", str(len(frames) or 1)),
                ("Model",          "EndoAI Detector (YOLOv8) + ResNet50",
                 "Model Status",   "DEMO / RESEARCH"),
            ]))
            story.append(Spacer(1, 8))

            # ════════════════════════════════════════════════════════════════
            # SECTION 2 — IMAGE QUALITY ASSESSMENT
            # ════════════════════════════════════════════════════════════════
            q_score = _quality_score(blur_sc, bright_sc)
            story.append(section_title("2", "Image Quality Assessment"))
            story.append(Spacer(1, 2))
            story.append(kv_table([
                ("Quality Status",   overall_q.capitalize(),
                 "Quality Score",    str(q_score)),
                ("Blur Assessment",  _blur_label(blur_sc),
                 "Brightness",       _brightness_label(bright_sc)),
            ]))
            story.append(Spacer(1, 8))

            # ════════════════════════════════════════════════════════════════
            # SECTION 3 — AI ANALYSIS FINDINGS
            # ════════════════════════════════════════════════════════════════
            story.append(section_title("3", "AI Analysis Findings"))
            story.append(Spacer(1, 2))

            # Table header
            th_style = ParagraphStyle("TH", parent=base, fontName="Helvetica-Bold",
                                      fontSize=8, textColor=C_DARK)
            findings_header = [
                Paragraph("Region", th_style),
                Paragraph("Detected Finding", th_style),
                Paragraph("Detection\nConfidence", th_style),
                Paragraph("Classification\nConfidence", th_style),
                Paragraph("Status", th_style),
            ]
            findings_rows = [findings_header]

            for det in detections:
                region_n = det.get("region_index", 1)
                cls_name = (
                    det.get("prediction", {}).get("predicted_class")
                    or det.get("class_name")
                    or "Suspicious region"
                )
                det_conf  = det.get("detection_confidence") or det.get("confidence") or 0.0
                cls_conf  = det.get("prediction", {}).get("class_confidence") or det_conf
                rev_raw   = det.get("review", {}).get("status", "PENDING")
                rev_label = _review_label(rev_raw)

                # Status colour
                if "ACCEPT" in (rev_raw or "").upper():
                    rev_color = C_GREEN
                elif "REJECT" in (rev_raw or "").upper():
                    rev_color = C_RED
                elif "FURTHER" in (rev_raw or "").upper():
                    rev_color = C_AMBER
                else:
                    rev_color = C_MUTED

                findings_rows.append([
                    Paragraph(f"Region {region_n}", body_style),
                    Paragraph(cls_name.replace("_", " ").title(), body_style),
                    Paragraph(f"{float(det_conf):.2f}", body_style),
                    Paragraph(f"{float(cls_conf):.2f}", body_style),
                    Paragraph(rev_label,
                              ParagraphStyle("RevSt", parent=body_style,
                                             textColor=rev_color,
                                             fontName="Helvetica-Bold")),
                ])

            if len(findings_rows) == 1:
                findings_rows.append([
                    Paragraph("—", body_style),
                    Paragraph("No abnormalities detected", body_style),
                    Paragraph("—", body_style),
                    Paragraph("—", body_style),
                    Paragraph("—", body_style),
                ])

            findings_tbl = Table(
                findings_rows,
                colWidths=[W*0.12, W*0.30, W*0.16, W*0.18, W*0.24],
            )
            findings_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), C_TH_BG),
                ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 5),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, C_ROW_ALT]),
            ]))
            story.append(findings_tbl)
            story.append(Spacer(1, 8))

            # ════════════════════════════════════════════════════════════════
            # SECTION 4 — AI-ASSISTED INTERPRETATION
            # ════════════════════════════════════════════════════════════════
            story.append(section_title("4", "AI-Assisted Interpretation"))
            story.append(Spacer(1, 4))

            # Build combined interpretation for all detected classes
            seen_classes = []
            for det in detections:
                cls_name = (
                    det.get("prediction", {}).get("predicted_class")
                    or det.get("class_name") or "default"
                )
                if cls_name not in seen_classes:
                    seen_classes.append(cls_name)

            if seen_classes:
                interp_text = " ".join([_get_interpretation(c) for c in seen_classes])
            else:
                interp_text = _get_interpretation("default")

            story.append(Paragraph(interp_text, body_style))
            story.append(Spacer(1, 8))

            # ════════════════════════════════════════════════════════════════
            # SECTION 5 — EXPLAINABILITY
            # ════════════════════════════════════════════════════════════════
            story.append(section_title("5", "Explainability"))
            story.append(Spacer(1, 2))

            # Collect explanation target layers
            exp_regions = []
            for det in detections:
                exp = det.get("explanation", {})
                tgt = exp.get("target_layer", "layer4")
                ridx = det.get("region_index", 1)
                exp_regions.append((ridx, tgt))

            region_list = ", ".join([f"Region {r}" for r, _ in exp_regions]) if exp_regions else "Region 1"
            layer_list  = ", ".join(set([t for _, t in exp_regions])) if exp_regions else "layer4"

            expl_data = [
                [
                    Paragraph("Explanation Method", bold_style),
                    Paragraph("Grad-CAM", body_style),
                    Paragraph("Associated Region", bold_style),
                    Paragraph(region_list, body_style),
                ],
                [
                    Paragraph("Purpose", bold_style),
                    Paragraph(
                        "Highlights image areas associated with the selected model prediction.",
                        body_style),
                    Paragraph("Review", bold_style),
                    Paragraph("Human review required", body_style),
                ],
            ]
            expl_tbl = Table(expl_data,
                             colWidths=[W*0.20, W*0.30, W*0.20, W*0.30])
            expl_tbl.setStyle(TableStyle([
                ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
                ("BACKGROUND",    (0, 0), (0, -1), C_TH_BG),
                ("BACKGROUND",    (2, 0), (2, -1), C_TH_BG),
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 5),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1),
                 [colors.white, C_ROW_ALT]),
            ]))
            story.append(expl_tbl)
            story.append(Spacer(1, 8))

            # ════════════════════════════════════════════════════════════════
            # SECTION 6 — REVIEW RECORD (current status per region)
            # ════════════════════════════════════════════════════════════════
            story.append(section_title("6", "Review Record"))
            story.append(Spacer(1, 2))

            if detections:
                # Per-region review record
                rev_header = [
                    Paragraph("Region", th_style),
                    Paragraph("AI Review Status", th_style),
                    Paragraph("Reviewer Notes", th_style),
                    Paragraph("Reviewer", th_style),
                    Paragraph("Date", th_style),
                ]
                rev_rows = [rev_header]
                for det in detections:
                    rev = det.get("review", {})
                    rv_raw   = rev.get("status", "PENDING")
                    rv_label = _review_label(rv_raw)
                    rv_notes = rev.get("notes") or "—"
                    rv_user  = rev.get("reviewer_id") or "—"
                    ridx = det.get("region_index", 1)

                    if "ACCEPT" in (rv_raw or "").upper():
                        rv_color = C_GREEN
                    elif "REJECT" in (rv_raw or "").upper():
                        rv_color = C_RED
                    elif "FURTHER" in (rv_raw or "").upper():
                        rv_color = C_AMBER
                    else:
                        rv_color = C_MUTED

                    rev_rows.append([
                        Paragraph(f"Region {ridx}", body_style),
                        Paragraph(rv_label,
                                  ParagraphStyle("RvSt2", parent=body_style,
                                                 textColor=rv_color,
                                                 fontName="Helvetica-Bold")),
                        Paragraph(str(rv_notes), body_style),
                        Paragraph(str(rv_user), body_style),
                        Paragraph("—", body_style),
                    ])

                rev_tbl = Table(rev_rows,
                                colWidths=[W*0.12, W*0.28, W*0.28, W*0.18, W*0.14])
                rev_tbl.setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, 0), C_TH_BG),
                    ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
                    ("VALIGN",        (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING",    (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.white, C_ROW_ALT]),
                ]))
            else:
                # No detections fallback
                rev_data = [
                    [
                        Paragraph("AI Review Status", bold_style),
                        Paragraph("No detections — no review required", body_style),
                        Paragraph("Reviewer", bold_style),
                        Paragraph("—", body_style),
                    ],
                    [
                        Paragraph("Reviewer Notes", bold_style),
                        Paragraph("—", body_style),
                        Paragraph("Date", bold_style),
                        Paragraph("—", body_style),
                    ],
                ]
                rev_tbl = Table(rev_data, colWidths=[W*0.22, W*0.28, W*0.22, W*0.28])
                rev_tbl.setStyle(TableStyle([
                    ("GRID",          (0, 0), (-1, -1), 0.4, C_BORDER),
                    ("BACKGROUND",    (0, 0), (0, -1), C_TH_BG),
                    ("BACKGROUND",    (2, 0), (2, -1), C_TH_BG),
                    ("VALIGN",        (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING",    (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
                ]))

            story.append(rev_tbl)
            story.append(Spacer(1, 14))

            # ════════════════════════════════════════════════════════════════
            # FOOTER — Disclaimer + generated by line
            # ════════════════════════════════════════════════════════════════
            story.append(HRFlowable(width="100%", thickness=0.6,
                                    color=C_BORDER, spaceBefore=2, spaceAfter=6))

            disclaimer = (
                "<b>Important:</b> EndoAI Vision is a research and decision-support prototype. "
                "AI-generated outputs are not a substitute for professional medical judgment "
                "and must not be used as an autonomous diagnosis. Clinical use requires "
                "appropriate validation, calibration, safety assessment, regulatory "
                "compliance, and review by qualified healthcare professionals."
            )
            story.append(Paragraph(disclaimer, sm_style))
            story.append(Spacer(1, 4))
            story.append(Paragraph(
                f"Generated by EndoAI Vision  •  Report type: {input_label} Analysis  "
                f"•  Research/Demo Output  •  {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                footer_sm,
            ))

            doc.build(story)
            buf.seek(0)
            return buf.getvalue()

        except ImportError:
            content = (
                f"EndoAI Vision Report\n"
                f"Examination ID: {exam_data.get('id')}\n"
                f"Generated: {datetime.now(timezone.utc)}\n\n"
            )
            content += json.dumps(exam_data, indent=2, default=str)
            return content.encode("utf-8")


ReportGenerator = ReportGenerator
