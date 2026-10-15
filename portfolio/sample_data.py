"""Hardcoded client stories used by the Client Stories page.

While the Project model is not yet migrated to the story schema, the stories
page renders the entries below whenever the database has no published Project
rows. As soon as real projects are added via the admin, the queryset takes
over and this module is no longer touched at request time.

Story schema
------------
Every entry in SAMPLE_PROJECTS has the same keys:

    title         Client / project name. Also used to build the page anchor.
    image_prefix  Stem shared by all of the story's images (see below).
    client_type   Industry label shown as a badge.
    tagline       One-line, value-driven hook. Shown in the hero carousel.
    description   Plain-text paragraph shown under the tagline in the hero
                  carousel: what the client does, in a sentence or two.
    problem       The "before" picture, in the client's own terms.
    solution      What was built, described by what it changed for them.
    benefits      List of 'Lead phrase: explanation' strings. The text before
                  the first ': ' is rendered bold as the benefit's headline.

The verbal side (title, tagline, problem, solution, benefits) is subjective
and value-driven. The visual side (the images) is the actual screens, views,
buttons and dashboards.

Images
------
Images live in static/images/clientstories/ and are found from image_prefix:

    {image_prefix}-Splash.jpg    Hero carousel image (1200x630 works well).
    {image_prefix}-1.jpg         Screenshots for the story's carousel and
    {image_prefix}-2.jpg         full-screen zoom. Numbered from 1 with no
    ...                          gaps: the first missing number ends the list.

The hero fades the splash in from the left, underneath the text, so keep the
left ~25% of the splash artwork as background rather than important content.

Notes on quoting: strings below are double-quoted so apostrophes (Thompson's,
couldn't) can be written naturally.
"""

SAMPLE_PROJECTS = [
    {
        "title": "Thompson's Steel Fabricators Ltd",
        "description": "Thompson's Steel Fabricators Ltd - Custom gates, fences, window bars, awnings, and ornate welded fixtures for residential and commercial properties.",
        "image_prefix": "Thompson_s_Steel_Fabricators_OS",
        "client_type": "Construction and Trades",
        "tagline": "Forging a System That Scales",
        "problem": "Thompson's was growing fast. Leads were coming in daily from Facebook, Instagram, and TikTok, plus on-site solicitation at active construction sites. But the back-office couldn't keep up. Quotes were being calculated by hand and sent via WhatsApp, job details lived in notebooks and phone calls, costs were tracked from memory, and project photos and videos were scattered across his phone gallery. With more jobs running at once, he was losing time searching for information, under-pricing complex ornate work, and missing follow-ups.",
        "solution": "We implemented a holistic, custom data management system that acts as the single source of truth for the entire business. From the moment a lead messages the page or is added from a construction site, to the final installation photo, everything now flows through one system. No more switching between WhatsApp, gallery, notepad, and calculator.",
        "benefits": [
            "True Job Profitability Tracking: Every job automatically tracks estimated vs. actual costs for steel, consumables, labor, transport, and subcontractors. He now knows his exact profit margin per gate, not just per month.",
            "Professional Quotes in Minutes, Not Hours: The system can now handle over 90% of the job estimates immediately at the site with just a few clicks, saving everyone time.",
            "Complete Customer & Site History: Every customer record shows all past quotes, jobs, payments, addresses, and gate measurements. Repeat customers and referrals are handled in seconds with accurate history.",
            "True Operations Management: Mr Thompson can see all his resources, whether it's his workers, inventory or cash, at a glance and on the go at any time of the day.",
        ],
    },
    {
        "title": "Ken Yee's Life Training Gym",
        "description": "Ken Yee's Life Training Gym - Martial arts and self-defense school, certified CPR training provider, and tactical training partner for security firms.",
        "image_prefix": "Life_Training_Gym_OS",
        "client_type": "Education and Training",
        "tagline": "Stronger Students. Sharper Systems",
        "problem": "Ken Yee runs a high-discipline, high-volume operation. Students don't train as individuals, they train in tight-knit batches who are scheduled, tested, and spar together. On top of that, he runs separate batches for CPR certification and security firm contracts, plus promotional events and grading events. Everything was manual. Attendance was on paper sheets, student progress and belt levels were in his head and in notebooks, fee tracking was separate, and staff had no way to log what happened in a class unless they called him. When a student started missing classes or falling behind on technique or fitness standards, he only noticed weeks later. Parents had to be chased down individually, and revenue from three very different program types was impossible to reconcile.",
        "solution": "We built a centralized gym management OS around how he actually teaches: by batch. The main dashboard now centers on what matters most each day: the upcoming class and event schedule. He can create and manage regular classes, special grading sessions, CPR workshops, and promotional events from one calendar. Students are grouped into batches, staff log in with their own accounts to take attendance, log incident notes and progress flags, and contact parents directly from the student file. All progress, attendance, and fee timelines are at his fingertips, so intervention happens early, not after a student quits.",
        "benefits": [
            "Early Intervention for At-Risk Students: The system automatically flags students with dropping attendance, missed assessments, or instructor progress concerns. Ken can see exactly who is falling behind standard and intervene before they drop out.",
            "True Batch Management: Batches are the core unit, not individual bookings. Each batch has its own roster, sparring group, schedule, lead instructor, and progression timeline. Moving a batch's schedule updates everyone at once.",
            "Staff Accountability & Mobile Attendance: Staff have their own logins to take attendance on their phone/tablet during class, log notes on student progress or incidents, record hours worked, and message parents. No more paper sheets to hand in.",
            "Linked Attendance, Progress & Fees: Student profile shows belt level, techniques passed, attendance rate, outstanding fees, and parent/guardian contact in one place. Fees are tied to batch enrollment, so non-payment is visible at roll call.",
            "Clear Financials Across All Programs: A dedicated financials section separates revenue and expenses for martial arts tuition, CPR courses, and security firm contracts, giving him true profitability per program line.",
        ],
    },
]
