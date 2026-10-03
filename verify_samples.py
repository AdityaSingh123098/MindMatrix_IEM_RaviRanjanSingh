import json
from analyzer import CommunicationGapAnalyzer

analyzer = CommunicationGapAnalyzer()
with open("data/sample_conversations.json", "r", encoding="utf-8") as f:
    samples = json.load(f)

for s in samples:
    print(f"==================================================")
    print(f"Sample: {s['name']} ({s['title']})")
    res = analyzer.analyze(s["conversation"])
    print(f"Health Score: {res['summary']['health_score']}% | Total Gaps: {len(res['gaps'])}")
    for g in res["gaps"]:
        print(f"  - [{g['type']}] {g['speaker']}: \"{g['message']}\"")
        print(f"    Evidence: {g['evidence']}")
print("==================================================")
