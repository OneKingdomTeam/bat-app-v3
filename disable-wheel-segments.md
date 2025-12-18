We are gonna be modifying the functionality of this repository in following way. I need to allow for
the coaches and admins to be able to disable segments of the wheel for the teams. Let's say that
some teams might not use all the toolings so some segments might not be relevant for them.

I need you to keep the current main function that generates the wheel: @app/service/assessment.py
prepare_wheel_context() since the interactivity of the coloring is based around that. Analyze the
way how the wheel is rendered and suggest smoothest way how to add option to disable the segment of
the wheel.

There are also functions that creates the paging for the next and previous button and we need to
make sure that those skip the disabled segments while paging.

In database structure you want to look at @app/data/assessment.py specifically table calle assessments_questions_cateogires:

curs.execute(
    """create table if not exists assessments_questions_categories(
    category_id integer primary key,
    assessment_id text references assessments( assessment_id ),
    category_name text,
    category_order integer
    )"""
)

Which basically is the source of truth when it comes to PER ASSESSMENTS categories.
Here it would be the easiest to add enabled = T / F or 1 / 0 and use that data while generating
the wheel for the front end. 

I would suggest that the easierst way for visual representation would be to add some check to the svg wheel files
that verifies if the segments should be disabled.

Segments should be possible to disable at any point, probably after the creation of the assessment.
Answers should be stored even when disabled just inaccessible.
Only Admins and Coaches should be able to manage enabled / disabled segments.

!! All imports of modules and classes happens at the beginning of the document

