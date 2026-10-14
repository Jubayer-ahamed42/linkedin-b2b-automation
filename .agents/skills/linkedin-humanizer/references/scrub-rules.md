# LinkedIn Humanizer — Scrub Rules (Regex & Detection Logic)

## Forensic Markers (Immediate Elimination)
```python
FORENSIC_PATTERNS = [
    r"\boaicite\b",
    r"\bcontentReference\b",
    r"\bturn\d+search\d+\b",
    r"\battached_file\b",
    r"As of my (last update|knowledge cutoff)[^.]*\.",
    r"\[Your Name\]|\[Your Company\]|\[Insert [^]]+\]",
]
```

## Cliché & Reveal Bridges (Direct Replacement)
```python
REVEAL_BRIDGES = [
    (r"(?im)^The (result|outcome|lesson|catch|truth)\?\s*", ""),
    (r"(?im)^Plot twist:\s*", ""),
    (r"(?im)^Here'?s (the thing|what happened|the secret)[:.]\s*", ""),
]
```

## 2026 High-Frequency AI Vocabulary (Density Scored)
```python
AI_VOCABULARY = [
    "delve", "tapestry", "revolutionize", "game-changer", "game changer",
    "furthermore", "it is important to note", "leverage", "streamline",
    "foster", "robust", "comprehensive", "landscape", "holistic",
    "multifaceted", "seamless", "synergy", "paradigm", "testament"
]
```
