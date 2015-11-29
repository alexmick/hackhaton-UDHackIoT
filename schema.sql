drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null
);

drop table if exists button_press;
CREATE TABLE button_press (
  carriage integer not null,
  seat_number integer not null,
  pressed_at text NOT NULL,
  is_reset integer DEFAULT 0
);
