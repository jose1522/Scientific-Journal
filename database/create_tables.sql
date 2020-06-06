CREATE DATABASE SCIENTIFIC_JOURNALS
GO

USE SCIENTIFIC_JOURNALS
Go

drop procedure if EXISTS getNextId;
drop table if EXISTS customer_order;
drop table if EXISTS consecutive;
drop table if EXISTS code;
drop table if EXISTS card;
drop table if EXISTS customer;
drop table if EXISTS methodology;
drop table if EXISTS objective;
drop table if EXISTS experiment_image;
drop table if EXISTS experiment_equipment;
drop table if EXISTS equipment;
drop table if EXISTS experiment;
drop table if EXISTS project;
drop table if EXISTS branch;
drop table if EXISTS error_log;
drop table if EXISTS person;
drop table if EXISTS job;
drop table if EXISTS degree;
drop table if EXISTS user_role;
drop table if EXISTS table_ref;

GO
CREATE TABLE user_role (
    id int primary key,
    name varchar(50) not null,
    description varchar (100) not null,
    active bit default 1,
    constraint ck_id_user_role check (id >= 0),
    constraint unique_name_user_role unique(name)
);
GO

GO
CREATE TABLE degree (
    id int primary key,
    name varchar (50) not null,
    description varchar (50) not null,
    active bit default 1,
    constraint ck_id_degree check (id >= 0)
);
GO

GO
CREATE TABLE job (
    id int primary key,
    name varchar(50) not null,
    description varchar(50) not null,
    active bit default 1 not null,
    user_role int FOREIGN KEY references user_role(id) on delete cascade not null,
    constraint ck_id_job check (id >= 0),
    constraint unique_name_job unique(name)
);
GO

GO
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
);
GO

GO
CREATE TABLE error_log(
    id int primary key,
    person int FOREIGN KEY REFERENCES person(id) on delete cascade not null,
    date_time datetime default CURRENT_TIMESTAMP,
    table_name varchar(50) not null,
    description varchar(200) not null,
    summary varchar(2000) not null,
    constraint ck_id_error_log check (id >= 0),
    constraint unique_person_error_record unique(person,date_time,table_name)
);
GO

GO
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
);
GO

GO
CREATE TABLE branch(
    id int PRIMARY KEY,
    name varchar(50) not null,
    active bit default 1,
    constraint ck_id_branch check (id >= 0)
);
GO

GO
CREATE TABLE project(
    id int PRIMARY KEY,
    name varchar(50) not null,
    price float default 0,
    journals int default 0,
    active bit default 1,
    person int REFERENCES person(id) on delete cascade not null,
    branch int REFERENCES branch(id) on delete cascade not null,
    constraint ck_id_project check (id >= 0),
    constraint ck_price_project check (price >= 0),
    constraint ck_journals_project check (journals >= 0),
    constraint unique_name_project unique(name)
);
GO


GO
CREATE Table experiment(
    id int PRIMARY KEY,
    name VARCHAR(50) not null,
    date date default CURRENT_TIMESTAMP,
    description varchar(2000) not null,
    main_objective varchar(3000) not null,
    active bit default 1,
    project int REFERENCES project(id) on delete cascade not null,
    experimenter int REFERENCES person(id) on delete no action,
    constraint ck_id_experiment check (id >= 0)
);
GO


GO
CREATE TABLE experiment_equipment(
    experiment int FOREIGN KEY REFERENCES experiment(id) on delete cascade not null,
    equipment int FOREIGN KEY REFERENCES equipment(id) on delete cascade not null,
    active bit default 1
);
GO

GO
CREATE Table methodology(
    id int PRIMARY KEY,
    step varchar(50) not null,
    description varchar(50) not null,
    experiment int REFERENCES experiment(id) on delete cascade not null,
    active bit default 1,
    constraint ck_id_methodology check (id >= 0)
);
GO

GO
CREATE Table objective(
    id int PRIMARY KEY,
    description varchar(50) not null,
    experiment int REFERENCES experiment(id) on delete cascade not null,
    active bit default 1,
    constraint ck_id_objective check (id >= 0)
);
GO

GO
CREATE Table experiment_image(
    id int PRIMARY KEY,
    photo image,
    active bit default 1,
    experiment int REFERENCES experiment(id) on delete cascade not null,
    constraint ck_id_experiment_image check (id >= 0)
);
GO

GO
CREATE Table customer (
    id int PRIMARY KEY,
    photo image,
    active bit default 1,
    constraint ck_id_customer check (id >= 0)
);
GO

GO
CREATE Table customer_order(
    id int PRIMARY KEY,
    project int FOREIGN KEY REFERENCES project(id) on delete cascade not null,
    customer int FOREIGN KEY REFERENCES customer(id) on delete cascade not null,
    status int default 0,
    constraint ck_id_customer_order check (id >= 0),
    constraint ck_customer_order_status check (status between -5 and 1)
);
GO

GO
CREATE Table card (
    id int PRIMARY KEY,
    card_number bigint not null,
    card_month int not null,
    card_year int not null,
    cvv int not null,
    card_type bit not null,
    active bit default 1 not null,
    customer int FOREIGN KEY REFERENCES customer(id) on delete cascade not null,
    constraint ck_id_card check (id >= 0),
    constraint ck_id_month check (card_month between 1 and 12),
    constraint ck_id_year check (card_year >= 2018)
);
GO

GO
CREATE Table table_ref(
    name varchar(50) PRIMARY KEY,
    description varchar(50) unique not null,
    current_value int default 0,
    isHidden bit default 0,
    constraint ck_current_value_table_ref check(current_value>=0)
);
GO

GO
CREATE Table code(
    id int IDENTITY(1,1) PRIMARY KEY,
    description varchar(50) unique not null
);
GO

GO
CREATE Table consecutive(
    id int PRIMARY KEY,
    type varchar(50) FOREIGN KEY REFERENCES code(description) on delete cascade unique not null,
    description varchar(100) not null,
    value int default 0,
    prefix varchar(50),
    table_name varchar(50) FOREIGN KEY REFERENCES table_ref(name) on delete cascade unique not null,
    constraint ck_id_consecutive check (id >= 0),
    constraint ck_value_consecutive check (value >= 0)
);
GO

-- Populates table_ref --
insert into table_ref(name, description, isHidden) values 
    ('customer_order','Pedidos',1),
    ('consecutive','Consecutivos',1),
    ('card','Tarjetas',1),
    ('customer','Clientes',1),
    ('methodology','Metodologias',1),
    ('objective','Objetivos',1),
    ('experiment_image','Imagenes Experimento',1),
    ('experiment_equipment','Equipo Experimento',1),
    ('equipment','Equipo',1),
    ('experiment','Bitacoras Experimentos',0),
    ('project','Proyectos',0),
    ('branch','Ramas Cientificas',0),
    ('error_log','Errores',0),
    ('person','Usuarios',0),
    ('job','Puestos',0),
    ('degree','Nivel Academico',0),
    ('user_role','Roles',0);

-- Function to get next available primary key for any table --
GO
CREATE PROCEDURE getNextID (@tableName varchar(10))
AS
BEGIN
    DECLARE @current_value int;

    update table_ref with (updlock)
    set 
    @current_value = current_value,
    current_value = current_value + 1
    where name = @tableName;

    return @current_value;
END
Go

