---
# puerto-rico-elections-platform-lkz5
title: Translate Step Content in All Chapters
status: completed
type: bug
priority: high
created_at: 2026-01-20T10:00:59Z
updated_at: 2026-01-20T10:00:59Z
---

The scrollytelling step content (narrative text boxes) in all 12 chapters is hardcoded in English. While headers, conclusions, and UI elements use the bilingual translation object, the Step components contain hardcoded English text.

## Problem
Each chapter has 10-12 Step components with narrative content like:
- Step titles (h3 elements)
- Paragraph content (p elements)
- Emphasis text, highlights, and stats

These need to be moved into the `t` translation object with both `en` and `es` versions.

## Chapters to Update
1. exodus
2. turnout
3. shrinking
4. plebiscites
5. referendum-2020
6. geography
7. fortaleza
8. battlegrounds
9. precincts
10. senate
11. house
12. future

## Checklist
- [x] exodus - Add step content to translation object
- [x] turnout - Add step content to translation object
- [x] shrinking - Add step content to translation object
- [x] plebiscites - Add step content to translation object
- [x] referendum-2020 - Add step content to translation object
- [x] geography - Add step content to translation object
- [x] fortaleza - Add step content to translation object
- [x] battlegrounds - Add step content to translation object
- [x] precincts - Add step content to translation object
- [x] senate - Add step content to translation object
- [x] house - Add step content to translation object
- [x] future - Add step content to translation object