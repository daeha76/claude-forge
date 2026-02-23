"""Markdown report builder for data research reports."""

from typing import Optional, List, Dict
from datetime import date as date_type
from pathlib import Path


class ReportBuilder:
    """Builds structured markdown reports with method chaining."""

    def __init__(self) -> None:
        self._sections: list[str] = []

    def add_header(
        self,
        title: str,
        subtitle: Optional[str] = None,
        date: Optional[str] = None,
        sources: Optional[List[str]] = None,
    ) -> "ReportBuilder":
        """Add report title block with metadata."""
        lines = [f"# {title}"]
        if subtitle:
            lines.append(f"\n{subtitle}")
        report_date = date or date_type.today().isoformat()
        lines.append(f"\n**작성일**: {report_date}")
        if sources:
            lines.append(f"**데이터 출처**: {', '.join(sources)}")
        self._sections.append("\n".join(lines))
        return self

    def add_summary(self, text: str) -> "ReportBuilder":
        """Add Executive Summary section."""
        self._sections.append(f"## Executive Summary\n\n{text}")
        return self

    def add_data_overview(
        self,
        period: str,
        sources: List[str],
        indicators: List[str],
    ) -> "ReportBuilder":
        """Add analysis overview section with metadata."""
        lines = [
            "## 분석 개요",
            "",
            f"- **분석 기간**: {period}",
            f"- **데이터 출처**: {', '.join(sources)}",
            "- **주요 지표**:",
        ]
        for indicator in indicators:
            lines.append(f"  - {indicator}")
        self._sections.append("\n".join(lines))
        return self

    def add_trend_analysis(
        self,
        title: str,
        chart_path: str,
        interpretation: str,
    ) -> "ReportBuilder":
        """Add trend analysis section with chart and interpretation."""
        section = f"### {title}\n\n![{title}]({chart_path})\n\n{interpretation}"
        self._sections.append(section)
        return self

    def add_comparison_analysis(
        self,
        title: str,
        chart_path: str,
        table_data: Dict[str, list],
        interpretation: str,
    ) -> "ReportBuilder":
        """Add comparison section with chart, table, and interpretation."""
        table_md = self._format_table(table_data["headers"], table_data["rows"])
        section = (
            f"### {title}\n\n"
            f"![{title}]({chart_path})\n\n"
            f"{table_md}\n\n"
            f"{interpretation}"
        )
        self._sections.append(section)
        return self

    def add_correlation_analysis(
        self,
        title: str,
        chart_path: str,
        interpretation: str,
    ) -> "ReportBuilder":
        """Add correlation analysis section."""
        section = (
            f"## 상관관계 분석\n\n"
            f"### {title}\n\n"
            f"![{title}]({chart_path})\n\n"
            f"{interpretation}"
        )
        self._sections.append(section)
        return self

    def add_table(
        self,
        title: str,
        headers: List[str],
        rows: List[List[str]],
    ) -> "ReportBuilder":
        """Add a standalone markdown table section."""
        table_md = self._format_table(headers, rows)
        self._sections.append(f"### {title}\n\n{table_md}")
        return self

    def add_insights(self, insights_list: List[str]) -> "ReportBuilder":
        """Add key insights as a numbered list."""
        lines = ["## 주요 인사이트", ""]
        for i, insight in enumerate(insights_list, 1):
            lines.append(f"{i}. {insight}")
        self._sections.append("\n".join(lines))
        return self

    def add_conclusion(self, text: str) -> "ReportBuilder":
        """Add conclusion section."""
        self._sections.append(f"## 결론\n\n{text}")
        return self

    def add_methodology(self, text: str) -> "ReportBuilder":
        """Add methodology section."""
        self._sections.append(f"## 분석 방법론\n\n{text}")
        return self

    def build(self, output_path: Optional[str] = None) -> str:
        """Join all sections and optionally write to file. Returns content string."""
        content = "\n\n---\n\n".join(self._sections)
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_text(content, encoding="utf-8")
        return content

    def _format_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """Generate aligned markdown table from headers and rows."""
        str_headers = [str(h) for h in headers]
        str_rows = [[str(cell) for cell in row] for row in rows]

        col_widths = [len(h) for h in str_headers]
        for row in str_rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(cell))

        def pad_row(cells: List[str]) -> str:
            padded = [
                cells[i].ljust(col_widths[i]) if i < len(col_widths) else cells[i]
                for i in range(len(cells))
            ]
            return "| " + " | ".join(padded) + " |"

        header_line = pad_row(str_headers)
        separator = "|" + "|".join(
            "-" * (w + 2) for w in col_widths
        ) + "|"

        lines = [header_line, separator]
        for row in str_rows:
            lines.append(pad_row(row))
        return "\n".join(lines)


if __name__ == "__main__":
    report = (
        ReportBuilder()
        .add_header(
            title="한국 경제 지표 분석 보고서",
            subtitle="주요 거시경제 지표의 추세 및 상관관계 분석",
            sources=["한국은행", "FRED", "World Bank"],
        )
        .add_summary(
            "본 보고서는 2015년부터 2024년까지의 한국 주요 경제 지표를 분석하여 "
            "거시경제 동향과 지표 간 상관관계를 파악합니다."
        )
        .add_data_overview(
            period="2015-2024",
            sources=["한국은행 경제통계시스템", "FRED", "World Bank Open Data"],
            indicators=["GDP 성장률", "소비자물가지수", "실업률", "기준금리"],
        )
        .add_trend_analysis(
            title="GDP 성장률 추이",
            chart_path="./charts/gdp_trend.png",
            interpretation="GDP 성장률은 2020년 코로나 팬데믹으로 급락 후 회복세를 보임.",
        )
        .add_comparison_analysis(
            title="주요 지표 비교",
            chart_path="./charts/comparison.png",
            table_data={
                "headers": ["지표", "2020", "2021", "2022", "2023"],
                "rows": [
                    ["GDP 성장률", "-0.7%", "4.3%", "2.6%", "1.4%"],
                    ["물가상승률", "0.5%", "2.5%", "5.1%", "3.6%"],
                    ["실업률", "4.0%", "3.7%", "2.9%", "2.7%"],
                ],
            },
            interpretation="2022년 물가상승률이 급등하며 실질 성장에 부담으로 작용.",
        )
        .add_correlation_analysis(
            title="경제 지표 간 상관관계",
            chart_path="./charts/correlation_heatmap.png",
            interpretation="금리와 물가 간 강한 양의 상관관계(r=0.82)가 관찰됨.",
        )
        .add_insights([
            "2020년 팬데믹 충격 이후 V자 반등 확인",
            "물가-금리 간 강한 양의 상관관계 존재",
            "실업률은 지속적 하락 추세",
            "GDP 성장률 둔화 추세가 2023년부터 뚜렷",
        ])
        .add_conclusion(
            "한국 경제는 팬데믹 이후 회복세를 보였으나, "
            "글로벌 긴축 기조와 물가 압력으로 성장 둔화가 진행 중입니다."
        )
        .add_methodology(
            "시계열 분석, 피어슨 상관계수, 이동평균 등의 통계적 방법론을 활용하였습니다."
        )
    )

    content = report.build()
    for line in content.split("\n")[:50]:
        print(line)
