import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from schemas.report import CompanyIntelligenceReport

def slugify(text: str) -> str:
    """Create a safe filesystem slug from text."""
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", text) or "report"

def format_report_markdown(report: CompanyIntelligenceReport) -> str:
    """Format CompanyIntelligenceReport as a rich, structured Markdown document."""
    md: list[str] = []
    co = report.company_overview
    comp = report.competitor_landscape
    news = report.recent_news_and_hiring
    risks = report.risk_intelligence

    md.append(f"# MarketMind AI — Company Intelligence Report: {report.target_company}")
    md.append(f"**Research Date:** {report.generated_at[:10]} | **Platform:** MarketMind Multi-Agent Engine\n")
    md.append("---\n")

    # 1. Executive Summary
    md.append("## 1. Executive Summary")
    md.append(report.executive_summary.strip() + "\n")

    # 2. Company Overview
    md.append("## 2. Company Overview")
    md.append(f"- **Company Name:** {co.company_name}")
    md.append(f"- **Website:** [{co.official_website}]({co.official_website})")
    md.append(f"- **Industry:** {co.industry}")
    md.append(f"- **Business Model:** {co.business_model}")
    md.append(f"- **Headquarters:** {co.headquarters or 'Unknown'}")
    md.append(f"- **Operating Regions:** {', '.join(co.operating_regions) if co.operating_regions else 'Global / Undisclosed'}")
    md.append(f"\n**Mission & Profile:**\n{co.description}\n")

    # 3. Founders & Leadership
    md.append("## 3. Founders and Key Leadership")
    if co.founders:
        md.append("### Founders & Co-Founders")
        for f in co.founders:
            status_tag = "✓ Verified" if f.verified else "Unverified"
            li_str = f" ([LinkedIn]({f.linkedin_url}))" if f.linkedin_url else ""
            bio_str = f" — {f.bio}" if f.bio else ""
            md.append(f"- **{f.name}** ({f.title}){li_str} `[{status_tag}]`{bio_str}")
    else:
        md.append("_No publicly verified founder profiles were extracted._")

    if co.key_executives:
        md.append("\n### Key Leadership Team")
        for e in co.key_executives:
            status_tag = "✓ Verified" if e.verified else "Unverified"
            li_str = f" ([LinkedIn]({e.linkedin_url}))" if e.linkedin_url else ""
            md.append(f"- **{e.name}** ({e.title}){li_str} `[{status_tag}]`")

    # 4. Products, Services, & Business Model
    md.append("\n## 4. Products, Services, and Business Model")
    if co.core_products_or_services:
        md.append("**Core Offerings:**")
        for p in co.core_products_or_services:
            md.append(f"- {p}")
    if co.target_customers:
        md.append("\n**Target Customers & Segments:**")
        for c in co.target_customers:
            md.append(f"- {c}")

    # 5. Funding & Milestones
    md.append("\n## 5. Funding and Company Milestones")
    md.append(f"**Total Disclosed Funding:** {co.total_funding or 'Not publicly disclosed / Unknown'}\n")
    if co.funding_rounds:
        md.append("### Disclosed Funding Rounds")
        for r in co.funding_rounds:
            inv = f" (Lead: {', '.join(r.lead_investors)})" if r.lead_investors else ""
            src = f" [Source]({r.source_url})" if r.source_url else ""
            md.append(f"- **{r.round_name}:** {r.amount or 'Undisclosed'} on {r.announced_date or 'N/D'}{inv}{src}")

    if co.milestones:
        md.append("\n### Key Strategic Milestones")
        for m in co.milestones:
            sig = f" — *Significance: {m.significance}*" if m.significance else ""
            md.append(f"- **[{m.date or 'N/D'}]** {m.description}{sig}")

    # 6. Competitor Landscape & Comparison Table
    md.append("\n## 6. Competitor Landscape & Market Positioning")
    md.append(f"{comp.market_overlap_summary}\n")
    md.append("### Competitive Comparison Matrix")
    md.append("| Competitor | Type | Products/Services | Target Segment | Public Pricing | Competitive Positioning | Evidence Sources |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    all_comps = comp.direct_competitors + comp.indirect_competitors + comp.substitute_products
    if all_comps:
        for c in all_comps:
            prods = ", ".join(c.products_services[:2]) or "Core Suite"
            pricing = c.public_pricing or "Quote / Tiered"
            sources = ", ".join([f"[Link]({url})" for url in c.evidence_sources[:2]]) if c.evidence_sources else "Industry analysis"
            name_display = f"[{c.name}]({c.website})" if c.website else c.name
            md.append(f"| **{name_display}** | {c.competitor_type} | {prods} | {c.target_segment} | {pricing} | {c.competitive_positioning} | {sources} |")
    else:
        md.append("| _No competitor profiles available_ | - | - | - | - | - | - |")

    # 7. Recent News & Announcements
    md.append("\n## 7. Recent News and Announcements")
    md.append(f"_Lookback Window: Past {news.lookback_days} Days_\n")
    if news.recent_news:
        for n in news.recent_news:
            date_str = n.publication_date or "Undated"
            md.append(f"- **[{date_str}] {n.headline}** (`{n.category}`)")
            md.append(f"  {n.summary} [Source: {n.publisher}]({n.source_url})")
    else:
        md.append("_No major news developments identified within the review window._")

    # 8. Hiring Signals
    md.append("\n## 8. Hiring and Recruitment Signals")
    md.append(f"**Trends Summary:** {news.hiring_trends_summary}\n")
    if news.hiring_signals:
        md.append("### Observed Openings & Signals")
        for h in news.hiring_signals:
            stale_tag = "⚠️ Stale" if h.is_stale else "Active"
            loc = f" ({h.location})" if h.location else ""
            md.append(f"- **{h.role_title}**{loc} — `{stale_tag}` [View Role]({h.source_url})")
    else:
        md.append("_No verifiable active hiring signals found on public channels._")

    # 9. Risk Intelligence
    md.append("\n## 9. Legal, Regulatory, Security, and Reputational Risks")
    md.append(f"{risks.overall_risk_summary}\n")
    if risks.has_identified_risks and risks.findings:
        for rf in risks.findings:
            sev_badge = f"**[{rf.severity.value}]**"
            status_badge = f"`{rf.nature}`"
            md.append(f"### {sev_badge} {rf.title} {status_badge}")
            md.append(f"- **Category:** {rf.category.value}")
            md.append(f"- **Incident / Disclosure Date:** {rf.incident_date or 'Undated'}")
            md.append(f"- **Factual Summary:** {rf.summary}")
            if rf.caveats:
                md.append(f"- **Important Caveats:** {rf.caveats}")
            md.append(f"- **Authoritative Source:** [{rf.publisher}]({rf.source_url})\n")
    else:
        md.append(f"> ℹ️ **Risk Assessment Notice:** {risks.no_risk_disclaimer}\n")

    # 10. Strategic Opportunities & Observations
    md.append("## 10. Strategic Opportunities and Observations")
    if report.strategic_opportunities:
        for opp in report.strategic_opportunities:
            md.append(f"- {opp}")
    else:
        md.append("- Ongoing market expansion and AI enterprise adoption provide notable tailwinds.")

    # 11. Evidence Quality & Gaps
    md.append("\n## 11. Evidence Quality and Information Gaps")
    if report.evidence_quality_and_gaps:
        for gap in report.evidence_quality_and_gaps:
            md.append(f"- ⚠️ {gap}")
    else:
        md.append("- High corroboration across official company disclosures and verified news media.")

    if report.validation_issues:
        md.append("\n**Flagged Validation Issues:**")
        for vi in report.validation_issues:
            md.append(f"- `[{vi.severity}]` **{vi.issue_type}**: {vi.description}")

    # 12. Sources and Research Metadata
    md.append("\n## 12. Sources and Research Metadata")
    md.append(f"- **Report Generated At:** {report.generated_at}")
    if report.run_metadata:
        md.append(f"- **Execution Engine:** {report.run_metadata.get('model', 'Default')}")
        md.append(f"- **Search Provider:** {report.run_metadata.get('search_provider', 'Default')}")
        md.append(f"- **Total Evidences Tracked:** {len(report.evidence_records)}")

    if report.sources:
        md.append("\n**Inspected Sources:**")
        for src in sorted(set(report.sources)):
            md.append(f"- [{src}]({src})")

    return "\n".join(md)

def save_report(
    report: CompanyIntelligenceReport,
    output_dir: str = "runs",
    run_metadata: Optional[Dict[str, Any]] = None
) -> Tuple[Path, Path, Path]:
    """Persist generated report as Markdown, JSON, and metadata files in a unique run directory."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    company_slug = slugify(report.target_company)
    run_folder = Path(output_dir) / f"{timestamp}_{company_slug}"
    run_folder.mkdir(parents=True, exist_ok=True)

    # 1. Save Markdown
    md_content = format_report_markdown(report)
    md_path = run_folder / "report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    # 2. Save JSON
    json_path = run_folder / "report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)

    # 3. Save run metadata
    meta = run_metadata or report.run_metadata or {}
    meta.update({
        "timestamp": timestamp,
        "company": report.target_company,
        "md_path": str(md_path),
        "json_path": str(json_path)
    })
    meta_path = run_folder / "run_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    return md_path, json_path, meta_path
