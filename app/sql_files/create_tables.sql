CREATE DATABASE SCIENTIFIC_JOURNALS
GO

USE SCIENTIFIC_JOURNALS
Go 

drop table if EXISTS equipment;
drop table if EXISTS experiment;
drop table if EXISTS project;
drop table if EXISTS error_log;
drop table if EXISTS person;
drop table if EXISTS job;
drop table if EXISTS degree;
drop table if EXISTS user_role;


CREATE TABLE user_role (
    id int primary key,
    name varchar(50) not null,
    description varchar (100) not null,
    active bit default 1,
    constraint ck_id_user_role check (id >= 0),
    constraint unique_name_user_role unique(name)
)


CREATE TABLE degree (
    id int primary key,
    name varchar (50) not null,
    description varchar (50) not null,
    active bit default 1,
    constraint ck_id_degree check (id >= 0)
)


CREATE TABLE job (
    id int primary key,
    name varchar(50) not null,
    description varchar(50) not null,
    active bit default 1 not null,
    user_role int FOREIGN KEY references user_role(id) on delete cascade not null,
    constraint ck_id_job check (id >= 0),
    constraint unique_name_job unique(name)
)

CREATE TABLE person (
    id int primary key,
    nickname varchar(50) not null,
    password varchar(50) not null,
    active bit default 1 not null,
    name varchar(50) not null,
    first_surname varchar(50) not null,
    second_surname varchar(50) not null,
    phone int not null,
    signature image,
    photo image,
    degree int FOREIGN KEY references degree(id) on delete cascade not null,
    job int FOREIGN KEY references job(id) on delete cascade not null,
    constraint ck_id_person check (id >= 0),
    constraint unique_nickname unique(nickname),
    constraint unique_fullname_person unique(name, first_surname, second_surname),
    constraint unique_phone_person unique(phone)
)

CREATE TABLE error_log(
    id int primary key,
    person int FOREIGN KEY REFERENCES person(id) on delete cascade not null,
    date_time datetime default CURRENT_TIMESTAMP,
    table_name varchar(50) not null,
    description varchar(200) not null,
    summary varchar(2000) not null,
    constraint ck_id_error_log check (id >= 0),
    constraint unique_person_error_record unique(person,date_time,table_name)
)

CREATE TABLE equipment (
    id int PRIMARY KEY,
    name varchar(50) not null,
    brand varchar(50) not null,
    model varchar(50) not null,
    serial varchar(50) not null,
    active bit default 1,
    constraint ck_id_equipment check (id >= 0),
    constraint unique_equipment unique(name, brand, model, serial),
    constraint unique_equipment_serial unique(serial)
)

CREATE TABLE project(
    id int PRIMARY KEY,
    name varchar(50) not null,
    price float default 0,
    journals int default 0,
    active bit default 1,
    person int REFERENCES person(id) on delete cascade not null,
    constraint ck_id_project check (id >= 0),
    constraint ck_price_project check (price >= 0),
    constraint ck_journals_project check (journals >= 0),
    constraint unique_name_project unique(name)
)

CREATE Table experiment(
    id int PRIMARY KEY,
    name VARCHAR(50) not null,
    date date default CURRENT_TIMESTAMP,
    description varchar(2000) not null,
    main_objective varchar(3000) not null,
    project int REFERENCES project(id) on delete cascade not null,
    constraint ck_id_experiment check (id >= 0)
)
