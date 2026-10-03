
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from collections import defaultdict


class CommunicationGapAnalyzer:
  

    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
        "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
        "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
        "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
        "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
        "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
        "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
        "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
        "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
        "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
        "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "shan't",
        "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
        "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
        "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
        "they've", "this", "those", "through", "to", "too", "under", "until", "up",
        "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
        "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
        "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
        "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
        "yourself", "yourselves", "ok", "okay", "yeah", "yes", "sure", "thanks", "hello", "hi"
    }

    REQUEST_PATTERNS = [
        r"(?:can|could)\s+you\s+(?:please\s+)?(?:send|share|provide|give|upload|forward|email|link)",
        r"please\s+(?:send|share|provide|give|upload|forward|email|link)",
        r"kindly\s+(?:share|send|provide|give|upload)",
        r"(?:can|could)\s+someone\s+(?:please\s+)?(?:provide|share|send|give|help\s+with)",
        r"i\s+need\s+(?:someone\s+to\s+|you\s+to\s+)?(?:send|share|provide|give|look\s+at)",
        r"any\s+update\s+on",
        r"reminder\s+to\s+(?:send|share|provide)",
    ]

    CLARIFICATION_PATTERNS = [
        r"\bwhat\s+do\s+you\s+mean\b",
        r"\bcan\s+you\s+clarify\b",
        r"\bcould\s+you\s+clarify\b",
        r"\bplease\s+explain\b",
        r"\bcan\s+you\s+explain\b",
        r"\bwhich\s+one\b",
        r"\bwhat\s+exactly\b",
        r"\bi\s+don't\s+understand\b",
        r"\bi\s+do\s+not\s+understand\b",
        r"\bcould\s+you\s+elaborate\b",
        r"\bcan\s+you\s+elaborate\b",
        r"\bnot\s+clear\b",
        r"\bwhat\s+does\s+(?:that|this)\s+mean\b",
        r"\bcan\s+you\s+rephrase\b",
        r"\bi('m|\s+am)\s+confused\b",
    ]

    TOPIC_INTRO_PATTERNS = [
        r"\babout\s+(?:the\s+)?([a-zA-Z0-9_\-\s]{3,30}?)(?:\?|\.|\,|$)",
        r"\bregarding\s+(?:the\s+)?([a-zA-Z0-9_\-\s]{3,30}?)(?:\?|\.|\,|$)",
        r"\bdiscuss\s+(?:the\s+)?([a-zA-Z0-9_\-\s]{3,30}?)(?:\?|\.|\,|$)",
        r"\bissue\s+with\s+(?:the\s+)?([a-zA-Z0-9_\-\s]{3,30}?)(?:\?|\.|\,|$)",
        r"\bupdate\s+on\s+(?:the\s+)?([a-zA-Z0-9_\-\s]{3,30}?)(?:\?|\.|\,|$)",
        r"\bdecide\s+on\s+(?:the\s+)?([a-zA-Z0-9_\-\s]{3,30}?)(?:\?|\.|\,|$)",
        r"\bstatus\s+of\s+(?:the\s+)?([a-zA-Z0-9_\-\s]{3,30}?)(?:\?|\.|\,|$)",
        r"\bwhat\s+about\s+(?:the\s+)?([a-zA-Z0-9_\-\s]{3,30}?)(?:\?|\.|\,|$)",
    ]

    RESOLUTION_KEYWORDS = {
        "fixed", "resolved", "done", "completed", "approved", "agreed", "decided",
        "scheduled", "merged", "shipped", "sent", "attached", "updated", "finalized",
        "closed", "settled", "taken care of", "sorted"
    }

    TIME_INDICATORS = {
        "today", "tomorrow", "tonight", "yesterday", "monday", "tuesday",
        "wednesday", "thursday", "friday", "saturday", "sunday", "noon", "midnight",
        "morning", "afternoon", "evening", "o'clock"
    }

    def __init__(self):
        self.request_regexes = [re.compile(p, re.IGNORECASE) for p in self.REQUEST_PATTERNS]
        self.clarification_regexes = [re.compile(p, re.IGNORECASE) for p in self.CLARIFICATION_PATTERNS]
        self.topic_regexes = [re.compile(p, re.IGNORECASE) for p in self.TOPIC_INTRO_PATTERNS]

    def parse_conversation(self, raw_text: str) -> List[Dict[str, Any]]:
        """
        Parses multi-line chat text into structured messages.
        Supports standard formats:
          Speaker: Message
          [Time] Speaker: Message
          Speaker (Time): Message
        """
        if not raw_text or not raw_text.strip():
            return []

        lines = raw_text.strip().split("\n")
        messages = []
        msg_id = 1

        patterns = [
            # [10:30 AM] Speaker: Message
            re.compile(r"^\[(?:\d{1,2}:\d{2}(?::\d{2})?(?:\s*[APap][Mm])?|\d{4}-\d{2}-\d{2}[^\]]*)\]\s*([^:]+):\s*(.*)$"),
            # Speaker (10:30 AM): Message
            re.compile(r"^([^\(:]+)\s*\([^)]*\):\s*(.*)$"),
            # Speaker: Message
            re.compile(r"^([^:]+):\s*(.*)$")
        ]

        current_msg = None

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            matched = False
            for pat in patterns:
                m = pat.match(line_str)
                if m:
                    speaker = m.group(1).strip()
                    content = m.group(2).strip()
                    current_msg = {
                        "id": msg_id,
                        "speaker": speaker,
                        "message": content,
                        "raw": line_str,
                        "has_gap": False,
                        "gap_types": []
                    }
                    messages.append(current_msg)
                    msg_id += 1
                    matched = True
                    break

            if not matched:
                if current_msg:
                    current_msg["message"] += " " + line_str
                    current_msg["raw"] += "\n" + line_str
                else:
                    current_msg = {
                        "id": msg_id,
                        "speaker": "Unknown",
                        "message": line_str,
                        "raw": line_str,
                        "has_gap": False,
                        "gap_types": []
                    }
                    messages.append(current_msg)
                    msg_id += 1

        return messages

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful alphanumeric tokens excluding common stopwords."""
        words = re.findall(r"\b[a-zA-Z0-9_\-']+\b", text.lower())
        return {w for w in words if w not in self.STOPWORDS and len(w) > 2}

    def _is_question(self, text: str) -> bool:
        """Determines if a text contains an interrogative question."""
        text_clean = text.strip()
        if "?" in text_clean:
            return True
        interrogative_starts = (
            "who ", "what ", "when ", "where ", "why ", "how ", "which ",
            "can you ", "could you ", "would you ", "will you ", "is there ",
            "are there ", "do you ", "does anyone ", "has anyone ", "have you "
        )
        return text_clean.lower().startswith(interrogative_starts)

    def _is_request(self, text: str) -> bool:
        return any(regex.search(text) for regex in self.request_regexes)

    def _extract_request_subject(self, text: str) -> str:
        for regex in self.request_regexes:
            match = regex.search(text)
            if match:
                remainder = text[match.end():].strip().rstrip(".?!")
                clean_remainder = re.sub(r"^(?:the|a|an|me|us)\s+", "", remainder, flags=re.IGNORECASE)
                words = [w for w in self._extract_keywords(clean_remainder) if w not in {"please", "thanks"}]
                if words:
                    return " ".join(words[:4])
                return clean_remainder[:30]
        kw = list(self._extract_keywords(text))
        return " ".join(kw[:3]) if kw else "request"

    def _is_clarification_request(self, text: str) -> bool:
        return any(regex.search(text) for regex in self.clarification_regexes)

    def _is_direct_answer(self, question_text: str, response_text: str, question_speaker: str, response_speaker: str) -> Tuple[bool, str]:
       
        q_lower = question_text.lower()
        r_lower = response_text.lower()

        if question_speaker.lower() in r_lower:
            return True, f"Explicitly addressed {question_speaker}"

        if "when" in q_lower or "what time" in q_lower or "which time" in q_lower:
            time_pat = r"\b(?:\d{1,2}:\d{2}(?:\s*(?:am|pm))?|\d{1,2}\s*(?:am|pm|o'clock)|at\s+\d{1,2}(?::\d{2})?)\b"
            has_time_digits = bool(re.search(time_pat, r_lower))
            has_time_words = bool(any(tw in r_lower.split() for tw in self.TIME_INDICATORS))
            if has_time_digits or has_time_words:
                return True, "Contains time-specific answer details"

        if "where" in q_lower:
            loc_cues = ["in ", "at ", "room", "link", "drive", "folder", "repo", "slack", "teams", "meet", "zoom", "office"]
            if any(cue in r_lower for cue in loc_cues):
                return True, "Contains location or access details"

        # Check binary / confirmation answering for "is", "can", "are", "do", "will"
        binary_starts = ("can", "could", "is", "are", "do", "does", "did", "will", "would", "has", "have", "should")
        is_binary_q = any(q_lower.startswith(b + " ") for b in binary_starts)
        if is_binary_q:
            affirmations = {"yes", "yeah", "yep", "sure", "no", "nope", "i will", "done", "will do", "okay", "ok", "working on it", "can't", "cannot"}
            r_tokens = set(re.findall(r"\b\w+\b", r_lower))
            if affirmations.intersection(r_tokens):
                return True, "Contains direct confirmation or affirmation"

        # Check keyword overlap between question and response
        q_keywords = self._extract_keywords(question_text)
        r_keywords = self._extract_keywords(response_text)

        overlap = q_keywords.intersection(r_keywords)
        if overlap:
            return True, f"Shares key subject terms: {', '.join(overlap)}"

        return False, "No topical or contextual alignment"

    def detect_unanswered_questions(self, messages: List[Dict[str, Any]], exclude_ids: Optional[Set[int]] = None) -> List[Dict[str, Any]]:
       
        gaps = []
        if exclude_ids is None:
            exclude_ids = set()

        for i, msg in enumerate(messages):
            if msg["id"] in exclude_ids:
                continue

            # Clarification requests are handled by detect_repeated_clarifications
            if self._is_clarification_request(msg["message"]):
                continue

            if not self._is_question(msg["message"]):
                continue

            speaker = msg["speaker"]
            q_text = msg["message"]

            subsequent_msgs = messages[i + 1:]

            if not subsequent_msgs:
                gaps.append({
                    "type": "Unanswered Question",
                    "speaker": speaker,
                    "message": q_text,
                    "message_id": msg["id"],
                    "evidence": "Question remained unanswered at the conclusion of the conversation."
                })
                msg["has_gap"] = True
                msg["gap_types"].append("Unanswered Question")
                continue

            answered = False
            unrelated_replies = []

            for sub in subsequent_msgs:
                if sub["speaker"].lower() == speaker.lower():
                    # Same speaker continuing monologue or repeating
                    continue

                is_answer, reason = self._is_direct_answer(q_text, sub["message"], speaker, sub["speaker"])
                if is_answer:
                    answered = True
                    break
                else:
                    unrelated_replies.append(f"{sub['speaker']}: '{sub['message']}'")

            if not answered:
                if unrelated_replies:
                    sample_replies = "; ".join(unrelated_replies[:2])
                    evidence_text = f"Question received no direct response. Subsequent responses shifted topics without addressing it (e.g., {sample_replies})."
                else:
                    evidence_text = "Question received no direct response from other participants."

                gaps.append({
                    "type": "Unanswered Question",
                    "speaker": speaker,
                    "message": q_text,
                    "message_id": msg["id"],
                    "evidence": evidence_text
                })
                msg["has_gap"] = True
                msg["gap_types"].append("Unanswered Question")

        return gaps

    def detect_repeated_requests(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rule B: Repeated Requests
        Detect requests (e.g. 'Can you send...', 'Please send...') that
        are repeated multiple times without resolution or fulfillment.
        """
        gaps = []
        recorded_requests = []

        for msg in messages:
            text = msg["message"]
            if self._is_request(text):
                subject = self._extract_request_subject(text)
                recorded_requests.append({
                    "id": msg["id"],
                    "speaker": msg["speaker"],
                    "message": text,
                    "subject": subject,
                    "keywords": self._extract_keywords(text)
                })

        # Find repeated requests
        matched_pairs = []
        for i in range(len(recorded_requests)):
            req_a = recorded_requests[i]
            for j in range(i + 1, len(recorded_requests)):
                req_b = recorded_requests[j]

                # Check if subject overlaps or keywords match significantly
                kw_overlap = req_a["keywords"].intersection(req_b["keywords"])
                subject_match = (
                    req_a["subject"] and req_b["subject"] and
                    (req_a["subject"] in req_b["subject"] or req_b["subject"] in req_a["subject"])
                )

                if subject_match or len(kw_overlap) >= 2 or (len(kw_overlap) >= 1 and req_a["speaker"] == req_b["speaker"]):
                    # Check if there was an intervening resolution message
                    intervening_resolved = False
                    start_id = req_a["id"]
                    end_id = req_b["id"]

                    for m in messages:
                        if start_id < m["id"] < end_id:
                            m_keywords = self._extract_keywords(m["message"])
                            if any(res in m["message"].lower() for res in self.RESOLUTION_KEYWORDS):
                                # If the resolution also refers to the item or provides it
                                if kw_overlap.intersection(m_keywords) or "sent" in m["message"].lower() or "here" in m["message"].lower():
                                    intervening_resolved = True
                                    break

                    if not intervening_resolved:
                        matched_pairs.append((req_a, req_b))

        # Build gap records for repeated requests
        reported_ids = set()
        for first_req, second_req in matched_pairs:
            if second_req["id"] not in reported_ids:
                reported_ids.add(second_req["id"])

                subject_display = second_req["subject"] or "the requested item"
                evidence = (
                    f"Request repeated without resolution. Originally requested in Message #{first_req['id']} "
                    f"by {first_req['speaker']}, and repeated in Message #{second_req['id']} by {second_req['speaker']} "
                    f"due to lack of fulfillment."
                )

                gaps.append({
                    "type": "Repeated Request",
                    "speaker": second_req["speaker"],
                    "message": second_req["message"],
                    "message_id": second_req["id"],
                    "evidence": evidence
                })

                # Mark gap on second request
                for m in messages:
                    if m["id"] == second_req["id"]:
                        m["has_gap"] = True
                        m["gap_types"].append("Repeated Request")

        return gaps

    def detect_repeated_clarifications(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rule C: Repeated Clarification Requests
        Detect phrases expressing confusion or asking for clarification
        (e.g., 'What do you mean?', 'Can you clarify?') occurring repeatedly.
        """
        gaps = []
        clarifications = []

        for msg in messages:
            if self._is_clarification_request(msg["message"]):
                clarifications.append(msg)

        if len(clarifications) >= 2:
            # Report each subsequent clarification or the cluster
            for idx, c_msg in enumerate(clarifications[1:], start=2):
                prev_speakers = {c["speaker"] for c in clarifications[:idx-1]}
                evidence = (
                    f"Multiple clarification requests detected ({idx} occurrences). "
                    f"Message #{c_msg['id']} asks for clarification again ('{c_msg['message']}'), "
                    f"indicating unresolved confusion in the discussion."
                )
                gaps.append({
                    "type": "Repeated Clarification",
                    "speaker": c_msg["speaker"],
                    "message": c_msg["message"],
                    "message_id": c_msg["id"],
                    "evidence": evidence
                })
                c_msg["has_gap"] = True
                c_msg["gap_types"].append("Repeated Clarification")

        return gaps

    def detect_unresolved_topics(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rule D: Unresolved Topics
        Detects topics or action items introduced (e.g., 'about X', 'regarding X', 'update on X')
        where no confirmation, decision, or conclusion was reached before the conversation ended.
        """
        gaps = []
        topics_introduced = []

        for msg in messages:
            text = msg["message"]
            for regex in self.topic_regexes:
                match = regex.search(text)
                if match:
                    raw_topic = match.group(1).strip()
                    # Clean punctuation
                    clean_topic = re.sub(r"[^\w\s\-]", "", raw_topic).strip()
                    topic_words = [w for w in clean_topic.split() if w.lower() not in self.STOPWORDS]
                    if topic_words:
                        topics_introduced.append({
                            "topic": " ".join(topic_words),
                            "msg": msg
                        })

        for item in topics_introduced:
            topic_str = item["topic"]
            msg = item["msg"]
            topic_kw = set(topic_str.lower().split())

            # Check messages after this topic intro for resolution
            has_resolution = False
            for post_msg in messages[msg["id"]:]:
                post_text = post_msg["message"].lower()
                # Check for resolution words
                if any(res in post_text for res in self.RESOLUTION_KEYWORDS):
                    # Check if resolution links to the topic
                    post_kw = self._extract_keywords(post_text)
                    if topic_kw.intersection(post_kw) or len(topic_kw) == 0:
                        has_resolution = True
                        break

            if not has_resolution:
                gaps.append({
                    "type": "Unresolved Topic",
                    "speaker": msg["speaker"],
                    "message": msg["message"],
                    "message_id": msg["id"],
                    "evidence": f"Topic '{topic_str}' was introduced but no resolution, decision, or concluding follow-up was found in the conversation."
                })
                msg["has_gap"] = True
                msg["gap_types"].append("Unresolved Topic")

        return gaps

    def analyze(self, raw_conversation: str) -> Dict[str, Any]:
        """
        Executes full communication gap analysis on raw conversation text.
        Returns standard JSON-compliant results along with conversation metadata.
        """
        messages = self.parse_conversation(raw_conversation)

        if not messages:
            return {
                "gaps": [],
                "summary": {
                    "total_messages": 0,
                    "total_participants": 0,
                    "participants": [],
                    "total_gaps": 0,
                    "health_score": 100,
                    "gap_breakdown": {}
                },
                "messages": []
            }

        # Run detection rules
        repeated_request_gaps = self.detect_repeated_requests(messages)
        repeated_ids = {g.get("message_id") for g in repeated_request_gaps}

        unanswered_gaps = self.detect_unanswered_questions(messages, exclude_ids=repeated_ids)
        repeated_clarification_gaps = self.detect_repeated_clarifications(messages)
        unresolved_topic_gaps = self.detect_unresolved_topics(messages)

        # Combine all gaps
        all_gaps = unanswered_gaps + repeated_request_gaps + repeated_clarification_gaps + unresolved_topic_gaps

        # De-duplicate if same message flagged with identical gap type
        unique_gaps = []
        seen = set()
        for gap in all_gaps:
            key = (gap["type"], gap["speaker"], gap["message"], gap.get("message_id"))
            if key not in seen:
                seen.add(key)
                unique_gaps.append(gap)

        # Participants
        participants = sorted(list({m["speaker"] for m in messages if m["speaker"] != "Unknown"}))

        # Gap breakdown
        breakdown = defaultdict(int)
        for g in unique_gaps:
            breakdown[g["type"]] += 1

        # Health score (100 is pristine, drops with more gaps)
        total_msgs = len(messages)
        gap_count = len(unique_gaps)
        deduction = min(100, gap_count * 20)
        health_score = max(0, 100 - deduction)

        return {
            "gaps": unique_gaps,
            "summary": {
                "total_messages": total_msgs,
                "total_participants": len(participants),
                "participants": participants,
                "total_gaps": gap_count,
                "health_score": health_score,
                "gap_breakdown": dict(breakdown)
            },
            "messages": messages
        }
