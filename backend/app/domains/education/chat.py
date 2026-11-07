"""Conversational lexicon for the education domain."""

KEYWORDS = [
    "student", "attendance", "exam", "marks", "assignment", "mock test", "study", "backlog", "backlogs", "grade",
    "semester", "pass", "fail", "academic", "class", "college", "school", "performance", "teacher", "course",
]
ALIASES = {
    "attendance": ["attendance", "attended"],
    "study_hours": ["study hours", "studies", "hours of study", "hours study", "hours a day", "hours per day", "hours/day", "study"],
    "assignment_score": ["assignment score", "assignment", "assignments", "coursework"],
    "previous_exam_score": ["previous exam", "last exam", "exam score", "previous exam score", "internal", "exam"],
    "mock_test_score": ["mock test", "mock", "mock test score", "practice test"],
    "backlogs": ["backlogs", "backlog", "arrears", "pending subjects", "failed subjects"],
}
OPTION_ALIASES = {
    "participation": {
        "Low": ["low participation", "rarely participates", "quiet", "passive", "disengaged"],
        "High": ["high participation", "active in class", "participates actively", "very engaged"],
        "Medium": ["medium participation", "average participation"],
    },
}
PATTERNS: list[tuple[str, list[str]]] = [(r"no\s+backlogs?", ["backlogs_zero"])]
KEY_FEATURES = ["attendance", "assignment_score", "previous_exam_score", "mock_test_score"]
EXAMPLES = [
    "Student with 65% attendance, assignment 45/100, previous exam 50, mock test 40, studies 2 hours a day",
    "Attendance 92%, assignment 84, exam 81, mock 78, no backlogs - how is this student doing?",
]
