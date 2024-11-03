create table if not exists users
(
    id            integer primary key autoincrement,
    username      text not null,
    register_date date not null,
    password      text not null,
    privilege     text not null check (privilege in ('admin', 'user'))
);

create table if not exists employees
(
    id           integer primary key autoincrement,
    name         text    not null,
    email        text    not null,
    recruited_at date    not null,
    position     text    not null,
    salary       real    not null check (salary > 0),
    department   integer not null
);

create table if not exists departments
(
    id     integer primary key autoincrement,
    name   text    not null,
    leader integer not null,
    foreign key (leader) references employees (id)
);

create table if not exists checkins
(
    id           integer primary key autoincrement,
    employee_id  integer not null,
    checkin_date date    not null,
    checkin_time time    not null,
    foreign key (employee_id) references employees (id)
);

create table if not exists applyoffs
(
    id                  integer primary key autoincrement,
    employee_id         integer not null,
    applyoff_date_start date    not null,
    applyoff_date_end   date    not null,
    applyoff_reason     text    not null,
    ended               text    not null check (ended in ('未销假', '已销假')),
    foreign key (employee_id) references employees (id)
);

