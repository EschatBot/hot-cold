# Hot/Cold — Social Dynamic Reader + Interaction HUD

## What You're Building

A single-file HTML web app (no backend, no frameworks, runs entirely in-browser) that analyzes live or pasted conversations to reveal social dynamics between speakers. Two modes, one engine.

**Mode 1: Social Dynamic Reader** — Analytical view. Post-conversation or passive monitoring. Who's hot/cold to whom, speaker profiles, relationship trends, group dynamics.

**Mode 2: Interaction HUD** — Real-time situational awareness during live conversation. Subtle alerts about windows of opportunity, exit signals, rapport peaks, and "don't act now" warnings.

---

## Design Language: Keith Haring Meets Premium App

### Visual Identity
- **Keith Haring influence:** Bold outlines, vibrant colors, energetic figures, thick black borders on elements, playful but purposeful. Think his subway drawings — information-dense but immediately readable.
- **Color palette:**
  - Background: Deep black (#0a0a0a) — like a subway wall
  - Hot: Vivid red (#FF3333) → warm orange (#FF8C42) → warm yellow (#FFD700)
  - Cold: Electric blue (#3366FF) → ice (#88CCFF) → frost white
  - Neutral: Haring green (#00CC66)
  - Accent outlines: Bold white or bright yellow, 2-3px, on everything — the Haring signature
  - Speaker colors: Rotating through Haring primaries — red, yellow, blue, green, orange, pink
- **Typography:** Bold, chunky, high contrast. Use Inter 700/800 for labels, 400 for body.
- **Shapes:** Rounded but bold. Thick borders. Elements should feel hand-drawn but digital. Slight rounded corners (8-12px) with thick (2-3px) bright borders.
- **Energy:** The UI should feel alive. Subtle pulsing on active elements. Color transitions. Nothing static.
- **Icons/Figures:** Where possible, use simple Haring-style figure silhouettes — dancing figures for high energy, hunched for disengagement, reaching toward each other for rapport.

### UX Reference: Best Simple Paid Apps
Think the UX clarity of:
- **Headspace** — one action per screen, beautiful transitions, never overwhelming
- **Duolingo** — gamified feedback, delightful micro-interactions, progress feels tangible
- **Dark Sky (weather)** — glanceable primary info, detail on tap, timeline scrubbing
- **Calm** — minimal chrome, content-first, breathing room in the layout
- **Shazam** — one big action button, result appears beautifully, details underneath

**Principles:**
- Mobile-first (iPhone portrait primary viewport)
- One primary action visible at a time
- Information hierarchy: most important = biggest + most colorful
- Tap for depth, don't show everything at once
- Transitions between states should feel smooth and intentional
- Empty states should be inviting, not blank

---

## UI Layout

### Main Screen — Dynamic Reader View

Each speaker is a horizontal bar, full width, stacked vertically:

```
┌─────────────────────────────────────────────┐
│  [🔮 Full Dynamic]           [▶ HUD Mode]  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌───────────────────────────────┐  ② ③ ④  │
│  │ #1  Confident · Engaged      │  ○ ○ ○  │
│  └───────────────────────────────┘          │
│                                             │
│  ┌───────────────────────────────┐  ① ③ ④  │
│  │ #2  Guarded · Mirroring      │  ○ ○ ○  │
│  └───────────────────────────────┘          │
│                                             │
│  ┌───────────────────────────────┐  ① ② ④  │
│  │ #3  Low Energy · Fading      │  ○ ○ ○  │
│  └───────────────────────────────┘          │
│                                             │
│  ┌───────────────────────────────┐  ① ② ③  │
│  │ #4  Animated · Leading       │  ○ ○ ○  │
│  └───────────────────────────────┘          │
│                                             │
├─────────────────────────────────────────────┤
│  [📝 Paste Text]  [🎤 Live Audio]          │
└─────────────────────────────────────────────┘
```

**Bar behavior:**
- Bar background color reflects speaker's current state (energy/mood gradient)
- Bold thick Haring-style border (speaker's assigned color)
- Labels inside: speaker number + state descriptors
- Optional name field (tap the number to add a name label, e.g., "#1" → "Mom")
- **Tap the bar** → slide-up panel with deep speaker profile

**Circle behavior:**
- Each circle to the right represents another speaker
- Circle fill color = warmth/coldness of that person TOWARD the row speaker
- Hot = red/orange glow, Cold = blue/frost, Neutral = green
- Circle border = that other speaker's assigned color
- **Tap one circle** → slide-up detail panel showing the 1:1 relationship (A→B and B→A)
- **Tap multiple circles** → multi-party dynamic view (triangle/coalition analysis)

### Speaker Profile Panel (tap bar)

Slides up from bottom, half-screen:

- Speaker number + optional name
- Current state: mood, energy, engagement (with Haring-style figure illustration)
- Bio-state indicators: pitch patterns, speech rate, stress markers
- Speaking patterns: dominance %, interruptions, topic initiations
- Trend sparkline: engagement over conversation duration
- Key moments: timestamps of notable shifts

### Relationship Detail Panel (tap circle)

Slides up from bottom, half-screen:

- Two directional scores: A→B and B→A, shown as opposing arrows with color
- Asymmetry indicator (if one-sided)
- Evidence trail: list of signals driving the score
- Trend: warming / cooling / stable with sparkline
- Key moments: timestamps where the dynamic shifted

### Multi-Party View (tap multiple circles or "Full Dynamic")

Full screen overlay:

- Network graph with speakers as nodes (Haring-style figures)
- Lines between them colored by warmth
- Line thickness = confidence
- Animated: lines pulse, figures gesture
- Coalition highlighting: subgroups that are mutually warm
- Outlier detection: who's isolated
- Summary text at bottom: "Strongest bond: #1 ↔ #2 | #3 is peripheral | #4 bridges the group"

### HUD Mode

Minimal overlay optimized for glancing during live conversation:

```
┌─────────────────────────────────────────────┐
│  ● LIVE                        [Exit HUD]   │
├─────────────────────────────────────────────┤
│                                             │
│  #1 ████████░░  #2 ██████████               │
│  #3 ███░░░░░░░  #4 ████████░░               │
│                                             │
│  💡 Rapport peak: #1 ↔ #2                  │
│  ⚠️ #3 disengaging                          │
│                                             │
└─────────────────────────────────────────────┘
```

- Compact speaker bars (engagement level only, as progress bars)
- Alert feed: most recent 2-3 actionable insights
- Alerts auto-dismiss after 10 seconds
- Tier 1 alerts (audio-only, ~800ms): rapport peaks, energy shifts, silence cues
- Tier 2 alerts (text-aware, ~2-3s): exit language, topic exhaustion, disclosure moments
- Background dims slightly so alerts pop
- Tap any alert for 1-line detail, tap speaker bar to flip back to Reader

### Alert Types for HUD

| Alert | Icon | Trigger |
|-------|------|---------|
| Rapport peak | 💡 | Mutual warmth scores both rising, convergence detected |
| Window open | 🎯 | Laughter reciprocity + high engagement + rising warmth |
| Disengaging | ⚠️ | Energy dropping + pitch flattening + shorter responses |
| Wrapping up | 🚪 | Exit language detected ("anyway", "I should go") |
| Let it breathe | 🤫 | Long pause after emotional content — don't interrupt |
| Not now | 🔴 | Tension peaking, hasn't resolved, bad time to interject |
| Reciprocate | 💬 | Personal disclosure detected, rapport opportunity |
| Topic dead | 🔄 | Same topic circling, diminishing returns |
| Energy surge | 🔥 | Group energy spiking — high engagement moment |
| Power shift | 👑 | Dominance pattern changed — new person leading |

### Setup Screen

Clean, Headspace-style onboarding:

1. "How many people are in the conversation?" → number picker (2-8)
2. Speaker cards appear with assigned colors and numbers
3. Optional: tap to add names
4. "How are you capturing?" → [📝 Paste Text] [🎤 Live Audio]
5. If Live Audio: microphone permission request with friendly explanation
6. Go → transitions to Reader view

### Input Modes

**Paste Mode:**
- Full-screen text area
- Auto-detects format (WhatsApp export, Slack, generic "Name: message")
- Shows parsed preview: "Found 3 speakers, 47 messages"
- "Analyze" button → processes and shows Reader

**Live Audio Mode:**
- Microphone capture via Web Audio API
- Browser SpeechRecognition for transcription
- Manual speaker labeling: "Tap the speaker who's talking now" (v1)
- Live transcript feed scrolls at bottom
- Analysis updates in real-time as conversation progresses

---

## Analysis Engine

### Text Analysis
- AFINN-165 lexicon embedded as JSON (~3400 words, -5 to +5 scores)
- Per-message sentiment scoring
- Directional signals: questions asked, name usage, message length matching, inclusive language ("we"/"us"), future references, exclamation/emoji density
- Response latency tracking (time between messages)
- Topic initiation tracking (who starts new subjects)
- Exit language detection ("anyway", "well", "I should", "good catching up")

### Audio Analysis (Live mode)
- Web Audio API: AudioContext + AnalyserNode
- Feature extraction at ~30Hz:
  - Pitch (F0) via autocorrelation
  - RMS energy
  - Spectral centroid
  - Pitch range (variation over 5s window)
  - Speech rate (syllable detection via energy peaks)
- Per-speaker features (after speaker identification):
  - Pitch convergence between speaker pairs (cross-correlation)
  - Response latency
  - Interruption detection
  - Laughter detection (rapid pitch oscillation + high energy)
  - Energy trend (rising/falling over time)

### Relationship Scoring
```javascript
{
  from: "#1",
  to: "#2",
  textScore: 0.72,       // 0-1, cold to warm
  toneScore: 0.65,       // 0-1, from audio (null in paste mode)
  fusedScore: 0.69,      // weighted: text 0.6 + audio 0.4
  signals: [...],         // evidence trail
  trend: "warming",       // warming / cooling / stable
  history: [...]          // score over time for sparklines
}
```

- Directional: A→B scored independently from B→A
- Temporal weighting: recent signals 2x weight
- Per-conversation normalization (relative warmth, not absolute)
- Confidence based on sample size

### Speaker Profile
```javascript
{
  id: "#1",
  name: null,             // optional user label
  color: "#FF3333",       // assigned Haring primary
  state: {
    mood: "engaged",
    energy: 0.8,
    dominance: 0.6,
    stressLevel: 0.2
  },
  patterns: {
    avgMessageLength: 45,
    questionsAsked: 12,
    interruptions: 3,
    topicInitiations: 5,
    speakingTimePercent: 0.35
  },
  trend: [...]            // state over time
}
```

---

## Technical Constraints

- **Single HTML file.** Everything inline — CSS, JS, lexicon data, all of it.
- **No external JS libraries.** Only external dependency: Google Fonts (Inter).
- **Mobile-first.** iPhone portrait is primary viewport. Everything must work at 375px width.
- **No backend.** All processing in-browser. Audio never leaves the device.
- **Performance:** Analysis pipeline must complete within frame budget for smooth UI. Use requestAnimationFrame for visual updates, Web Workers for heavy computation if needed.

---

## Build Order

1. **Setup screen + participant creation** — the onboarding flow
2. **Paste mode + text analysis** — get the engine working with static text
3. **Reader view (bars + circles)** — the core visualization
4. **Speaker profile panel + relationship detail panel** — tap interactions
5. **Full Dynamic view** — network graph
6. **Live audio capture + STT** — real-time input
7. **Audio feature extraction + tone analysis** — layer on voice signals
8. **HUD mode** — real-time alerts
9. **Polish:** animations, transitions, Haring-style figure illustrations, micro-interactions

---

## AFINN-165 Lexicon

Embed the full AFINN-165 lexicon as a JavaScript object. It's ~15KB. Format:
```javascript
const AFINN = { "abandon": -2, "abandoned": -2, "abandons": -2, ... };
```
Source: https://github.com/fnielsen/afinn — MIT licensed.
Include ALL ~3400 entries. Do not truncate.

---

## Quality Bar

This should feel like a $4.99/month app that people happily pay for. Every interaction should feel intentional. Colors should pop against the dark background. The Keith Haring energy should make people smile when they open it. Bold, playful, alive — but the information architecture underneath is dead serious.

When completely finished, run this command to notify me:
openclaw system event --text "Done: Hot/Cold social dynamics app built — Reader + HUD modes with Keith Haring design" --mode now
