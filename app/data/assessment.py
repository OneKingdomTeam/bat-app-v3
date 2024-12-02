from app.data.init import curs


# -------------------------------
#   CRUDs
# -------------------------------


curs.execute("""create table if not exists assessments(
    assessment_id integer primary key,
    assessment_name text,
    owner_id text references user( user_id ),
    last_edit text,
    last_editor text references user( user_id ),
    )""")


curs.execute("""create table if not exists assessments_questions(
    assessment_question_id integer PRIMARY KEY,
    assessment_id integer references assessments( assessment_id ),
    assessment_qc_id references assessments_q_categories( assessment_qc_id ),
    question text,
    question_description text,
    question_order integer,
    option_yes text,
    option_mid text,
    option_no text)""")


curs.execute("""create table if not exists assessments_answers(
    answer_id integer PRIMARY KEY,
    assessment_id integer references assessments( assessment_id ),
    assessment_question_id integer references assessments_questions( assessment_question_id ),
    answer_option text,
    answer_description text
    )""")

curs.execute("""create table if not exists assessments_q_categories(
    assessment_qc_id integer primary key,
    assessment_qc_name text,
    assessment_qc_order integer
    )""")
