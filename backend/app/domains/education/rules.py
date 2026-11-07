"""Education knowledge base - academic progression and support rules.

Thresholds mirror common Indian university regulations (75% attendance
requirement, 40% pass mark) and typical academic-advising practice.
"""

from app.domains.base import cond, rule

ON_TRACK, NEEDS_SUPPORT, AT_RISK = 0, 1, 2

RULES = [
    rule(
        "ED-01", "Minimum attendance requirement",
        "Attendance below the 75% requirement.",
        "Attendance",
        [cond("attendance", "lt", 75)],
        NEEDS_SUPPORT, "soft",
        "Attendance below configured threshold - meet the mentor and plan attendance recovery.",
        "Attendance requirement (≥ 75%): Passed.",
    ),
    rule(
        "ED-02", "Detention-level attendance",
        "Attendance below 60% risks detention from examinations.",
        "Attendance",
        [cond("attendance", "lt", 60)],
        AT_RISK, "hard",
        "Attendance is at detention level - immediate counselling and condonation process required.",
        "Attendance above detention level.",
    ),
    rule(
        "ED-03", "Assignment score below target",
        "Assignment score below 50/100.",
        "Coursework",
        [cond("assignment_score", "lt", 50)],
        NEEDS_SUPPORT, "soft",
        "Assignment score below target - provide additional learning resources and resubmission support.",
        "Assignment score meets target.",
    ),
    rule(
        "ED-04", "Mock test below target",
        "Mock test score below 40/100.",
        "Assessment",
        [cond("mock_test_score", "lt", 40)],
        NEEDS_SUPPORT, "soft",
        "Mock test score below target - recommend targeted practice tests.",
        "Mock test score meets target.",
    ),
    rule(
        "ED-05", "Previous exam below pass mark",
        "Previous exam score below the 40% pass mark.",
        "Assessment",
        [cond("previous_exam_score", "lt", 40)],
        NEEDS_SUPPORT, "soft",
        "Previous exam below pass mark - schedule remedial classes for weak topics.",
        "Previous exam above pass mark.",
    ),
    rule(
        "ED-06", "Consistent failure pattern",
        "Both previous exam and mock test below 35/100.",
        "Assessment",
        [cond("previous_exam_score", "lt", 35), cond("mock_test_score", "lt", 35)],
        AT_RISK, "hard",
        "Repeated failure pattern - assign a dedicated academic mentor and weekly monitoring.",
        "No consistent failure pattern.",
    ),
    rule(
        "ED-07", "Multiple backlogs",
        "Three or more pending backlogs.",
        "Progression",
        [cond("backlogs", "gte", 3)],
        AT_RISK, "hard",
        "Multiple backlogs - create a backlog-clearance plan with the department.",
        "Fewer than three backlogs.",
    ),
    rule(
        "ED-08", "Pending backlog",
        "One or two pending backlogs.",
        "Progression",
        [cond("backlogs", "gte", 1), cond("backlogs", "lt", 3)],
        NEEDS_SUPPORT, "soft",
        "Pending backlog - register for the supplementary examination.",
        "No pending backlogs.",
    ),
    rule(
        "ED-09", "Insufficient self-study",
        "Less than 1.5 hours of self-study per day.",
        "Study habits",
        [cond("study_hours", "lt", 1.5)],
        NEEDS_SUPPORT, "soft",
        "Build a structured daily study timetable (2+ hours).",
        "Self-study time adequate.",
    ),
]
