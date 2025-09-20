-- Table to persist generated daily facts and example questions
create table if not exists daily_generated_content (
    id bigserial primary key,
    content_date date not null,
    content_type text not null check (content_type in ('example_question', 'daily_fact')),
    position smallint not null check (position between 1 and 10),
    question_text text,
    answer_text text,
    source_model text,
    raw_payload jsonb,
    created_at timestamptz not null default now(),
    unique (content_date, content_type, position)
);

create index if not exists idx_daily_generated_content_date_type
    on daily_generated_content (content_date desc, content_type);
