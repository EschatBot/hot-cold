#!/bin/bash
# Fetch top cited papers across all domains relevant to Hot/Cold
# Uses OpenAlex API (free, no key needed)

OUT="/tmp/hot-cold/research-archive"
mkdir -p "$OUT"

QUERIES=(
  "vocal+emotion+recognition+acoustic+features"
  "speech+prosody+interpersonal+attraction"
  "vocal+accommodation+dominance+status"
  "deception+detection+voice+pitch"
  "conversation+turn+taking+analysis"
  "group+dynamics+social+network+interaction"
  "vocal+rapport+synchrony+entrainment"
  "speech+depression+detection+biomarker"
  "persuasion+charisma+voice+prosody"
  "nonverbal+communication+power+dominance"
  "laughter+social+bonding+conversation"
  "cognitive+load+speech+patterns"
  "sentiment+analysis+conversation+text"
  "game+theory+social+interaction+cooperation"
  "negotiation+communication+strategy+outcome"
  "microexpression+vocal+correlate+emotion"
  "speaker+diarization+identification"
  "social+signal+processing+interaction"
  "voice+stress+analysis+detection"
  "interpersonal+warmth+coldness+behavior"
)

for i in "${!QUERIES[@]}"; do
  q="${QUERIES[$i]}"
  echo "[$((i+1))/${#QUERIES[@]}] Searching: ${q//+/ }"
  
  curl -s "https://api.openalex.org/works?search=${q}&sort=cited_by_count:desc&per_page=25&select=id,title,publication_year,cited_by_count,doi,open_access,authorships" \
    -o "$OUT/search_$(printf '%02d' $i)_${q//+/_}.json" 2>&1
  
  sleep 1  # rate limit courtesy
done

echo ""
echo "Done. Fetched ${#QUERIES[@]} queries."
echo "Extracting paper list..."

# Combine all results into a single summary
python3 -c "
import json, glob, os

papers = {}
for f in sorted(glob.glob('$OUT/search_*.json')):
    try:
        data = json.load(open(f))
        query = os.path.basename(f).split('_', 2)[2].replace('.json','').replace('_',' ')
        for r in data.get('results', []):
            doi = r.get('doi','')
            if doi and doi not in papers:
                authors = []
                for a in r.get('authorships', [])[:3]:
                    name = a.get('author',{}).get('display_name','')
                    if name: authors.append(name)
                papers[doi] = {
                    'title': r['title'],
                    'year': r.get('publication_year'),
                    'citations': r.get('cited_by_count',0),
                    'doi': doi,
                    'oa_url': r.get('open_access',{}).get('oa_url'),
                    'is_oa': r.get('open_access',{}).get('is_oa', False),
                    'authors': authors,
                    'query': query
                }
    except: pass

# Sort by citations
ranked = sorted(papers.values(), key=lambda x: x['citations'], reverse=True)

print(f'Total unique papers: {len(ranked)}')
print(f'Open access: {sum(1 for p in ranked if p[\"is_oa\"])}')

# Save full index
with open('$OUT/paper-index.json', 'w') as f:
    json.dump(ranked, f, indent=2)

# Save readable summary
with open('$OUT/paper-index.md', 'w') as f:
    f.write('# Research Archive — Paper Index\n\n')
    f.write(f'**Total papers:** {len(ranked)}\n')
    f.write(f'**Open access available:** {sum(1 for p in ranked if p[\"is_oa\"])}\n\n')
    f.write('## Top 50 by Citation Count\n\n')
    for i, p in enumerate(ranked[:50]):
        auth = ', '.join(p['authors'][:2])
        oa = '📄' if p['is_oa'] else '🔒'
        f.write(f\"{i+1}. {oa} **{p['title']}** ({p['year']}) — {auth} — {p['citations']} citations\n\")
        if p.get('doi'): f.write(f\"   DOI: {p['doi']}\n\")
        if p.get('oa_url'): f.write(f\"   PDF: {p['oa_url']}\n\")
        f.write('\n')

print('Saved paper-index.json and paper-index.md')
"
