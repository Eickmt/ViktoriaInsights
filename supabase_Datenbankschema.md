create table public.dim_date (
  date_key integer not null,
  full_date date not null,
  year smallint not null,
  month_nr smallint not null,
  month_name character varying(10) null,
  quarter smallint not null,
  week_nr smallint not null,
  weekday_nr smallint not null,
  weekday_name character varying(10) null,
  is_weekend boolean not null default false,
  constraint dim_date_pkey primary key (date_key),
  constraint dim_date_full_date_key unique (full_date)
) TABLESPACE pg_default;


create table public.dim_penalty_type (
  penalty_type_key serial not null,
  description text null,
  default_amount_eur numeric(6, 2) null,
  constraint dim_penalty_type_pkey primary key (penalty_type_key)
) TABLESPACE pg_default;

create table public.dim_player (
  player_key serial not null,
  name character varying(80) not null,
  birthday date null,
  join_date date null,
  active_flag boolean null default true,
  created_at timestamp without time zone null default now(),
  "Rolle" text null,
  constraint dim_player_pkey primary key (player_key),
  constraint dim_player_name_key unique (name)
) TABLESPACE pg_default;

create table public.fact_penalty (
  penalty_id serial not null,
  date_key integer null,
  player_key integer null,
  penalty_type_key integer null,
  amount_eur numeric(6, 2) not null,
  penalty_cnt smallint not null default 1,
  created_at timestamp without time zone null default now(),
  source_penalty_id integer null,
  note text null,
  constraint fact_penalty_pkey primary key (penalty_id),
  constraint fact_penalty_source_penalty_id_key unique (source_penalty_id),
  constraint fact_penalty_date_key_fkey foreign KEY (date_key) references dim_date (date_key),
  constraint fact_penalty_penalty_type_key_fkey foreign KEY (penalty_type_key) references dim_penalty_type (penalty_type_key),
  constraint fact_penalty_player_key_fkey foreign KEY (player_key) references dim_player (player_key),
  constraint fact_penalty_amount_eur_check check ((amount_eur >= (0)::numeric))
) TABLESPACE pg_default;

create table public.fact_training_win (
  date_key integer not null,
  player_key integer not null,
  played_cnt smallint not null default 1,
  win_cnt smallint not null default 0,
  constraint fact_training_win_pkey primary key (date_key, player_key),
  constraint fact_training_win_date_key_fkey foreign KEY (date_key) references dim_date (date_key),
  constraint fact_training_win_player_key_fkey foreign KEY (player_key) references dim_player (player_key)
) TABLESPACE pg_default;

create table public.team_standings (
  standing_id serial not null,
  team_name varchar(100) not null,
  season varchar(10) not null, -- z.B. "2425"
  match_day integer null,
  position integer not null,
  games_played integer not null,
  wins integer not null,
  draws integer not null,
  losses integer not null,
  goals_for integer not null,
  goals_against integer not null,
  goal_difference integer not null,
  points integer not null,
  scraped_at timestamp with time zone not null default now(),
  constraint team_standings_pkey primary key (standing_id)
) TABLESPACE pg_default;

create table public.events (
  match_id text null,
  source_url text null,
  minute integer null,
  phase text null,
  type text null,
  team_side text null,
  player_primary text null,
  player_id text null,
  player_in text null,
  player_id_in text null,
  player_out text null,
  player_id_out text null,
  score_home integer null,
  score_away integer null,
  detail text null,
  raw text null
) TABLESPACE pg_default;

create table public.lineups (
  match_id text null,
  source_url text null,
  team_side text null,
  team_name text null,
  role text null,
  number integer null,
  name text null,
  player_id text null,
  is_captain boolean null,
  is_goalkeeper boolean null
) TABLESPACE pg_default;

create table public.matches (
  match_id text null,
  source_url text null,
  competition text null,
  season text null,
  match_date date null,
  home_team text null,
  away_team text null,
  score_home integer null,
  score_away integer null
) TABLESPACE pg_default;