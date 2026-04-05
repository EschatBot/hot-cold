#!/usr/bin/env python3
"""
Hot/Cold Research Archive Builder
=================================
Fetches academic papers from OpenAlex API across all domains relevant to
social dynamics analysis. Extracts metadata, downloads open-access PDFs,
and builds a structured knowledge base.

Usage:
  python3 fetch-research.py                  # Full fetch (all domains)
  python3 fetch-research.py --domain vocal   # Single domain
  python3 fetch-research.py --download-pdfs  # Also download PDFs
  python3 fetch-research.py --extract        # Extract knowledge from downloaded PDFs (requires manual review)
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path

# ── Configuration ──────────────────────────────────────────

BASE_DIR = Path(__file__).parent.parent / "research-archive"
PDF_DIR = BASE_DIR / "pdfs"
INDEX_FILE = BASE_DIR / "paper-index.json"
KNOWLEDGE_FILE = BASE_DIR / "knowledge-base.json"
SUMMARY_FILE = BASE_DIR / "paper-index.md"

OPENALEX_BASE = "https://api.openalex.org/works"
RATE_LIMIT_DELAY = 1.1  # seconds between API calls

# ── Search Domains ─────────────────────────────────────────

DOMAINS = {
    "vocal_emotion": [
        "vocal emotion recognition acoustic features",
        "voice emotion detection prosody",
        "speech affect recognition",
        "vocal expression emotion classification",
        "paralinguistic speech analysis emotion",
    ],
    "vocal_attraction_rapport": [
        "vocal attraction interpersonal speech",
        "voice pitch attraction romantic",
        "vocal accommodation rapport convergence",
        "prosodic entrainment social bonding",
        "vocal mirroring synchrony conversation",
        "laughter social bonding vocal",
    ],
    "dominance_power": [
        "vocal dominance status power speech",
        "speaking time dominance hierarchy",
        "interruption patterns power dynamics",
        "nonverbal dominance communication",
        "vocal accommodation dominance status",
        "turn-taking power asymmetry conversation",
    ],
    "deception": [
        "deception detection voice speech cues",
        "lying vocal pitch cognitive load",
        "deception speech patterns meta-analysis",
        "verbal cues deception detection",
        "response latency deception",
    ],
    "conversation_structure": [
        "conversation turn taking analysis",
        "conversational dynamics interaction patterns",
        "dialogue structure sequential analysis",
        "conversation analysis pragmatics",
        "topic management conversation flow",
    ],
    "group_dynamics": [
        "group dynamics social interaction network",
        "coalition formation social groups",
        "social network interaction patterns",
        "group decision making communication",
        "collective intelligence team interaction",
    ],
    "persuasion_charisma": [
        "persuasion charisma voice prosody",
        "charismatic speech acoustic features",
        "rhetoric persuasion vocal delivery",
        "influence negotiation communication vocal",
    ],
    "mental_health_voice": [
        "depression detection speech voice biomarker",
        "anxiety voice analysis acoustic",
        "mental health vocal biomarkers screening",
        "cognitive decline speech patterns",
        "stress detection voice analysis",
    ],
    "sentiment_text": [
        "sentiment analysis conversation text NLP",
        "opinion mining dialogue systems",
        "emotion detection text conversation",
        "linguistic markers social dynamics text",
    ],
    "game_theory_social": [
        "game theory social interaction cooperation",
        "strategic interaction communication signaling",
        "social dilemma cooperation negotiation",
    ],
    "social_signal_processing": [
        "social signal processing interaction",
        "computational social science interaction",
        "multimodal social behavior analysis",
        "nonverbal behavior computational analysis",
    ],
    "warmth_coldness": [
        "interpersonal warmth coldness behavior",
        "social warmth competence perception",
        "approach avoidance social interaction",
        "affiliative behavior social signals",
    ],
    "speaker_identification": [
        "speaker diarization identification",
        "speaker recognition voice embedding",
        "voice fingerprinting speaker clustering",
    ],
    "negotiation": [
        "negotiation communication strategy outcome",
        "bargaining behavior linguistic analysis",
        "conflict resolution communication patterns",
    ],
    "interview_interrogation": [
        "interview assessment vocal behavior",
        "interrogation communication techniques",
        "hiring interview speech analysis",
    ],
}

# Keywords for filtering relevant papers
RELEVANCE_KEYWORDS = [
    'vocal', 'voice', 'speech', 'emotion', 'prosody', 'sentiment',
    'conversation', 'deception', 'dominance', 'rapport', 'social signal',
    'turn-taking', 'laughter', 'interpersonal', 'nonverbal', 'negotiation',
    'persuasion', 'charisma', 'acoustic', 'speaker', 'diarization',
    'affective', 'tone', 'pitch', 'warmth', 'coldness', 'interaction',
    'group dynamics', 'social network', 'game theory', 'cooperation',
    'depression', 'stress', 'cognitive load', 'attraction', 'mirroring',
    'entrainment', 'accommodation', 'power', 'status', 'dialogue',
    'discourse', 'interruption', 'backchannel', 'synchrony', 'coalition',
    'conflict', 'interview', 'interrogation', 'bargaining', 'influence',
    'empathy', 'engagement', 'disengagement', 'bonding', 'trust',
    'linguistic', 'paralinguistic', 'multimodal', 'computational social',
]


def fetch_openalex(query, per_page=25, max_pages=2):
    """Fetch papers from OpenAlex API."""
    all_results = []
    for page in range(1, max_pages + 1):
        params = urllib.parse.urlencode({
            'search': query,
            'sort': 'cited_by_count:desc',
            'per_page': per_page,
            'page': page,
            'select': 'id,title,publication_year,cited_by_count,doi,open_access,authorships,abstract_inverted_index',
        })
        url = f"{OPENALEX_BASE}?{params}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'HotCold/1.0 (research tool)'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                results = data.get('results', [])
                all_results.extend(results)
                if len(results) < per_page:
                    break
        except Exception as e:
            print(f"  ⚠ Error fetching page {page}: {e}")
            break
        time.sleep(RATE_LIMIT_DELAY)
    return all_results


def reconstruct_abstract(inverted_index):
    """Reconstruct abstract from OpenAlex inverted index format."""
    if not inverted_index:
        return None
    words = {}
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    if not words:
        return None
    max_pos = max(words.keys())
    return ' '.join(words.get(i, '') for i in range(max_pos + 1)).strip()


def is_relevant(title, abstract=None):
    """Check if a paper is relevant to our domains."""
    text = (title or '').lower()
    if abstract:
        text += ' ' + abstract.lower()
    return any(kw in text for kw in RELEVANCE_KEYWORDS)


def extract_paper_info(result, domain, query):
    """Extract structured paper info from OpenAlex result."""
    doi = result.get('doi', '')
    authors = []
    for a in result.get('authorships', [])[:5]:
        name = a.get('author', {}).get('display_name', '')
        institution = ''
        insts = a.get('institutions', [])
        if insts:
            institution = insts[0].get('display_name', '')
        if name:
            authors.append({'name': name, 'institution': institution})

    abstract = reconstruct_abstract(result.get('abstract_inverted_index'))
    oa = result.get('open_access', {})

    return {
        'title': result.get('title', ''),
        'year': result.get('publication_year'),
        'citations': result.get('cited_by_count', 0),
        'doi': doi,
        'authors': authors,
        'abstract': abstract,
        'is_oa': oa.get('is_oa', False),
        'oa_url': oa.get('oa_url'),
        'oa_status': oa.get('oa_status', 'closed'),
        'domain': domain,
        'query': query,
        'openalex_id': result.get('id', ''),
    }


def fetch_all_domains(domains=None):
    """Fetch papers across all domains."""
    if domains is None:
        domains = DOMAINS

    all_papers = {}  # doi → paper
    total_queries = sum(len(queries) for queries in domains.values())
    query_num = 0

    for domain, queries in domains.items():
        print(f"\n📚 Domain: {domain}")
        for query in queries:
            query_num += 1
            print(f"  [{query_num}/{total_queries}] {query}")
            results = fetch_openalex(query)
            new = 0
            for r in results:
                doi = r.get('doi', '')
                if not doi:
                    continue
                paper = extract_paper_info(r, domain, query)
                if not is_relevant(paper['title'], paper.get('abstract')):
                    continue
                if doi not in all_papers:
                    all_papers[doi] = paper
                    new += 1
                else:
                    # Add additional domain tag
                    existing = all_papers[doi]
                    if domain not in existing.get('domains', [existing['domain']]):
                        existing.setdefault('domains', [existing['domain']]).append(domain)
            print(f"    → {len(results)} results, {new} new relevant papers")

    # Sort by citations
    papers = sorted(all_papers.values(), key=lambda x: x['citations'], reverse=True)
    return papers


def download_pdfs(papers, max_papers=200):
    """Download open-access PDFs."""
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    downloadable = [p for p in papers if p.get('oa_url')][:max_papers]
    print(f"\n⬇️  Downloading {len(downloadable)} PDFs...")

    downloaded = 0
    for i, paper in enumerate(downloadable):
        title_safe = re.sub(r'[^a-zA-Z0-9 _-]', '', (paper['title'] or 'unknown')[:60]).strip().replace(' ', '_')
        filename = f"{title_safe}_{paper.get('year', '')}.pdf"
        filepath = PDF_DIR / filename
        paper['pdf_filename'] = filename

        if filepath.exists():
            downloaded += 1
            continue

        try:
            req = urllib.request.Request(paper['oa_url'], headers={'User-Agent': 'HotCold/1.0'})
            with urllib.request.urlopen(req, timeout=20) as resp:
                with open(filepath, 'wb') as f:
                    f.write(resp.read())
            downloaded += 1
            if (i + 1) % 10 == 0:
                print(f"  [{i+1}/{len(downloadable)}] downloaded")
        except Exception as e:
            print(f"  ⚠ Failed: {filename}: {e}")
        time.sleep(0.5)

    print(f"  ✅ {downloaded}/{len(downloadable)} PDFs downloaded")
    return papers


def build_knowledge_base(papers):
    """Build structured knowledge base from paper metadata and abstracts."""
    knowledge = {
        'generated': datetime.utcnow().isoformat() + 'Z',
        'total_papers': len(papers),
        'domains': {},
        'signals': [],
        'key_findings': [],
    }

    # Group by domain
    for paper in papers:
        domains = paper.get('domains', [paper.get('domain', 'unknown')])
        for domain in domains:
            knowledge['domains'].setdefault(domain, []).append({
                'title': paper['title'],
                'year': paper.get('year'),
                'citations': paper['citations'],
                'doi': paper['doi'],
                'authors': [a['name'] for a in paper.get('authors', [])[:3]],
                'abstract_excerpt': (paper.get('abstract') or '')[:300],
            })

    # Extract signal-relevant findings from abstracts
    signal_keywords = {
        'pitch': 'vocal_pitch',
        'f0': 'fundamental_frequency',
        'speech rate': 'speech_rate',
        'response time': 'response_latency',
        'response latency': 'response_latency',
        'turn-taking': 'turn_taking',
        'interruption': 'interruption_patterns',
        'laughter': 'laughter_detection',
        'energy': 'vocal_energy',
        'loudness': 'vocal_energy',
        'jitter': 'voice_quality',
        'shimmer': 'voice_quality',
        'mfcc': 'spectral_features',
        'formant': 'spectral_features',
        'accommodation': 'vocal_convergence',
        'convergence': 'vocal_convergence',
        'entrainment': 'vocal_convergence',
        'synchrony': 'vocal_convergence',
        'sentiment': 'text_sentiment',
        'valence': 'emotional_valence',
        'arousal': 'emotional_arousal',
        'dominance': 'social_dominance',
        'power': 'social_power',
        'deception': 'deception_detection',
        'rapport': 'rapport_building',
        'empathy': 'empathy_signals',
        'engagement': 'engagement_level',
        'charisma': 'charisma_markers',
    }

    for paper in papers:
        abstract = (paper.get('abstract') or '').lower()
        if not abstract:
            continue
        for keyword, signal_type in signal_keywords.items():
            if keyword in abstract:
                knowledge['signals'].append({
                    'signal_type': signal_type,
                    'paper_doi': paper['doi'],
                    'paper_title': paper['title'],
                    'year': paper.get('year'),
                    'citations': paper['citations'],
                    'context': abstract[:200],
                })

    # Deduplicate signals by type
    seen = set()
    unique_signals = []
    for s in knowledge['signals']:
        key = (s['signal_type'], s['paper_doi'])
        if key not in seen:
            seen.add(key)
            unique_signals.append(s)
    knowledge['signals'] = sorted(unique_signals, key=lambda x: x['citations'], reverse=True)

    return knowledge


def generate_summary(papers):
    """Generate readable markdown summary."""
    oa_count = sum(1 for p in papers if p.get('is_oa'))
    domains = {}
    for p in papers:
        d = p.get('domain', 'unknown')
        domains.setdefault(d, []).append(p)

    lines = [
        "# Hot/Cold Research Archive",
        f"\n**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Total papers:** {len(papers)}",
        f"**Open access:** {oa_count}",
        f"**Domains covered:** {len(domains)}",
        "",
        "## Domain Breakdown\n",
    ]

    for domain, domain_papers in sorted(domains.items()):
        lines.append(f"### {domain.replace('_', ' ').title()} ({len(domain_papers)} papers)")
        for i, p in enumerate(domain_papers[:5]):
            auth = ', '.join(a['name'] for a in p.get('authors', [])[:2])
            oa = '📄' if p['is_oa'] else '🔒'
            lines.append(f"  {i+1}. {oa} **{p['title']}** ({p.get('year', '?')}) — {auth} — {p['citations']} cites")
            if p.get('doi'):
                lines.append(f"     DOI: {p['doi']}")
        lines.append("")

    lines.extend([
        "## Top 50 Papers by Citation Count\n",
    ])
    for i, p in enumerate(papers[:50]):
        auth = ', '.join(a['name'] for a in p.get('authors', [])[:2])
        oa = '📄' if p['is_oa'] else '🔒'
        lines.append(f"{i+1}. {oa} **{p['title']}** ({p.get('year', '?')}) — {auth} — {p['citations']} cites")
        if p.get('doi'):
            lines.append(f"   DOI: {p['doi']}")
        if p.get('abstract'):
            lines.append(f"   _{p['abstract'][:150]}..._")
        lines.append("")

    return '\n'.join(lines)


def main():
    args = sys.argv[1:]
    do_download = '--download-pdfs' in args
    do_extract = '--extract' in args
    single_domain = None

    for arg in args:
        if arg.startswith('--domain='):
            single_domain = arg.split('=', 1)[1]
        elif arg == '--domain' and args.index(arg) + 1 < len(args):
            single_domain = args[args.index(arg) + 1]

    # Create directories
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    # Select domains
    if single_domain:
        matching = {k: v for k, v in DOMAINS.items() if single_domain.lower() in k.lower()}
        if not matching:
            print(f"Unknown domain: {single_domain}")
            print(f"Available: {', '.join(DOMAINS.keys())}")
            sys.exit(1)
        domains = matching
    else:
        domains = DOMAINS

    # Fetch
    print(f"🔍 Fetching papers across {len(domains)} domains...")
    papers = fetch_all_domains(domains)
    print(f"\n📊 Total unique relevant papers: {len(papers)}")
    print(f"📄 Open access: {sum(1 for p in papers if p.get('is_oa'))}")

    # Save index
    with open(INDEX_FILE, 'w') as f:
        json.dump(papers, f, indent=2, default=str)
    print(f"💾 Saved index: {INDEX_FILE}")

    # Generate summary
    summary = generate_summary(papers)
    with open(SUMMARY_FILE, 'w') as f:
        f.write(summary)
    print(f"📝 Saved summary: {SUMMARY_FILE}")

    # Download PDFs
    if do_download:
        papers = download_pdfs(papers)
        # Re-save index with pdf filenames
        with open(INDEX_FILE, 'w') as f:
            json.dump(papers, f, indent=2, default=str)

    # Build knowledge base
    print("\n🧠 Building knowledge base...")
    knowledge = build_knowledge_base(papers)
    with open(KNOWLEDGE_FILE, 'w') as f:
        json.dump(knowledge, f, indent=2, default=str)
    print(f"💾 Saved knowledge base: {KNOWLEDGE_FILE}")
    print(f"   → {len(knowledge['signals'])} signal references extracted")
    print(f"   → {len(knowledge['domains'])} domains indexed")

    print("\n✅ Done!")
    print(f"\nFiles:")
    print(f"  {INDEX_FILE} — Full paper metadata")
    print(f"  {SUMMARY_FILE} — Readable summary")
    print(f"  {KNOWLEDGE_FILE} — Structured knowledge base")
    if do_download:
        print(f"  {PDF_DIR}/ — Downloaded PDFs")


if __name__ == '__main__':
    main()
