USE SCIENTIFIC_JOURNALS
GO

drop procedure if EXISTS getNextId;
drop procedure if EXISTS reverseId;
drop view if EXISTS view_job;
drop view if EXISTS view_role;
drop view if EXISTS view_degree;
drop view if EXISTS view_user_role;
drop view if EXISTS view_error_log;
drop view if EXISTS view_activity_log;
drop view if EXISTS view_branch;
drop view if EXISTS view_project;
drop view if EXISTS view_person;
drop view if EXISTS view_experiment;
drop view if EXISTS view_customer_order;
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
drop table if EXISTS activity_log;
drop table if EXISTS person;
drop table if EXISTS job;
drop table if EXISTS degree;
drop table if EXISTS user_role;
drop table if EXISTS table_ref;


-- Table Reference Table --
GO
CREATE Table table_ref(
    name nvarchar(50) PRIMARY KEY,
    description nvarchar(50) unique not null,
    current_value int default 0,
    isHidden bit default 0,
    constraint ck_current_value_table_ref check(current_value>=0)
);
GO


-- USER ROLE TABLE --
GO
CREATE TABLE user_role (
    id int primary key,
    name nvarchar(50) not null,
    description nvarchar (100) not null,
    active bit default 1,
    constraint ck_id_user_role check (id >= 0),
    constraint unique_name_user_role unique(name)
);
GO

-- User Role Index --
GO
CREATE INDEX INDXUSRROLE ON user_role(active);
GO

-- DEGREE TABLE --
GO
CREATE TABLE degree (
    id int primary key,
    name nvarchar (50) not null,
    description nvarchar (50) not null,
    active bit default 1,
    constraint ck_id_degree check (id >= 0)
);
GO

-- Degree Index --
GO
CREATE INDEX INDXDEGREE ON degree(active);
GO

-- JOB TABLE --
GO
CREATE TABLE job (
    id int primary key,
    name nvarchar(50) not null,
    description nvarchar(50) not null,
    active bit default 1 not null,
    user_role int FOREIGN KEY references user_role(id) on delete cascade not null,
    constraint ck_id_job check (id >= 0),
    constraint unique_name_job unique(name)
);
GO

-- Job Index --
GO
CREATE INDEX INDXJOB ON job(active);
GO

-- PERSON TABLE --

GO
CREATE TABLE person (
    id int primary key,
    nickname nvarchar(50) not null,
    password nvarchar(50) not null,
    active bit default 1 not null,
    name nvarchar(50) not null,
    first_surname nvarchar(50) not null,
    second_surname nvarchar(50) not null,
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

-- Person Index --
GO
CREATE INDEX INDXPERSON ON person(active);
GO

-- Error Log Table --
GO
CREATE TABLE error_log(
    id int,
    person int FOREIGN KEY REFERENCES person(id) on delete cascade not null,
    date_time datetime default CURRENT_TIMESTAMP,
    table_name nvarchar(50) FOREIGN KEY REFERENCES table_ref(name) on delete cascade not null,
    description nvarchar(200) not null,
    summary nvarchar(2000) not null,
    constraint ck_id_error_log check (id >= 0),
    constraint unique_person_error_record unique(person,date_time,table_name),
    constraint pk_error_log PRIMARY KEY (id, table_name)
);
GO

-- Error Log Index --
GO
CREATE INDEX INDXERRLOG ON error_log(person);
GO

-- Activity Log Table --
GO
CREATE TABLE activity_log(
    id int,
    table_name nvarchar(50) FOREIGN KEY REFERENCES table_ref(name) on delete cascade not null,
    person int FOREIGN KEY REFERENCES person(id) on delete cascade not null,
    date_time datetime default CURRENT_TIMESTAMP,
    description nvarchar(200) not null,
    constraint ck_id_activity_log check (id >= 0),
    constraint pk_activity_log PRIMARY KEY (id, table_name)
);
GO

-- Activity Log Index --
GO
CREATE INDEX INDXACTLOG ON activity_log(person);
GO

-- Equipment Table --
GO
CREATE TABLE equipment (
    id int PRIMARY KEY,
    name nvarchar(50) not null,
    brand nvarchar(50) not null,
    model nvarchar(50) not null,
    serial nvarchar(50) not null,
    active bit default 1,
    constraint ck_id_equipment check (id >= 0),
    constraint unique_equipment unique(name, brand, model, serial),
    constraint unique_equipment_serial unique(serial)
);
GO

-- Equipment Index --
GO
CREATE INDEX INDXEQUIPMENT ON equipment(active);
GO

-- Branch Table --
GO
CREATE TABLE branch(
    id int PRIMARY KEY,
    name nvarchar(50) not null,
    active bit default 1,
    constraint ck_id_branch check (id >= 0)
);
GO

-- EBranch Index --
GO
CREATE INDEX INDXBRANCH ON branch(active);
GO

-- Project Table --
GO
CREATE TABLE project(
    id int PRIMARY KEY,
    name nvarchar(50) not null,
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

-- Project Table Index --
GO
CREATE INDEX INDXPROJECT ON project(person, active);
GO

-- Experiment Table --
GO
CREATE Table experiment(
    id int PRIMARY KEY,
    name nvarchar(50) not null,
    date date default CURRENT_TIMESTAMP,
    description nvarchar(2000) not null,
    main_objective nvarchar(3000) not null,
    active bit default 1,
    project int REFERENCES project(id) on delete cascade not null,
    experimenter int REFERENCES person(id) on delete no action,
    constraint ck_id_experiment check (id >= 0)
);
GO

-- Experiment Table Index --
GO
CREATE INDEX INDXEXPERIMENT ON experiment(project, active);
GO

-- Experiment Equipment Table --
GO
CREATE TABLE experiment_equipment(
    experiment int FOREIGN KEY REFERENCES experiment(id) on delete cascade not null,
    equipment int FOREIGN KEY REFERENCES equipment(id) on delete cascade not null,
    active bit default 1
);
GO

-- Experiment Equipment Index --
GO
CREATE INDEX INDXEXPERIMENTEQUIPMENT ON experiment_equipment(active);
GO

-- Methodology Table --
GO
CREATE Table methodology(
    id int PRIMARY KEY,
    step nvarchar(50) not null,
    description nvarchar(50) not null,
    experiment int REFERENCES experiment(id) on delete cascade not null,
    active bit default 1,
    constraint ck_id_methodology check (id >= 0)
);
GO

-- Methodology Table Index --
GO
CREATE INDEX INDXMETHODOLOGY ON methodology(experiment, active);
GO

-- Objective Table --
GO
CREATE Table objective(
    id int PRIMARY KEY,
    description nvarchar(50) not null,
    experiment int REFERENCES experiment(id) on delete cascade not null,
    active bit default 1,
    constraint ck_id_objective check (id >= 0)
);
GO

-- Objective Table Index --
GO
CREATE INDEX INDXOBJECTIVE ON objective(experiment, active);
GO

-- Experiment Image Table --
GO
CREATE Table experiment_image(
    id int PRIMARY KEY,
    photo image,
    active bit default 1,
    experiment int REFERENCES experiment(id) on delete cascade not null,
    constraint ck_id_experiment_image check (id >= 0)
);
GO

-- Experiment Image Index --
GO
CREATE INDEX INDXEXPIMG ON experiment_image(experiment, active);
GO

-- Customer Table --
GO
CREATE Table customer (
    id int PRIMARY KEY,
    photo image,
    active bit default 1,
    constraint ck_id_customer check (id >= 0)
);
GO

-- Customer Index --
GO
CREATE INDEX INDCUSTOMER ON customer(active);
GO

-- Costumer Order Table --
GO
CREATE Table customer_order(
    id int PRIMARY KEY,
    date_time datetime default CURRENT_TIMESTAMP,
    project int FOREIGN KEY REFERENCES project(id) on delete cascade not null,
    customer int FOREIGN KEY REFERENCES customer(id) on delete cascade not null,
    status int default 0,
    constraint ck_id_customer_order check (id >= 0),
    constraint ck_customer_order_status check (status between -5 and 1)
);
GO

-- Customer Table Index --
GO
CREATE INDEX INDXCUSTOMERORDER ON customer_order(customer);
GO

-- Card Table --
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

-- Card Table Index --
GO
CREATE INDEX INDXCARD ON card(customer, active);
GO

-- Code Table --
GO
CREATE Table code(
    id int IDENTITY(1,1) PRIMARY KEY,
    description nvarchar(50) unique not null
);
GO

-- Consecutive Table --
GO
CREATE Table consecutive(
    id int PRIMARY KEY,
    type nvarchar(50) FOREIGN KEY REFERENCES code(description) on delete cascade unique not null,
    description nvarchar(100) not null,
    value int default 0,
    prefix nvarchar(50),
    table_name nvarchar(50) FOREIGN KEY REFERENCES table_ref(description) on delete cascade unique not null,
    constraint ck_id_consecutive check (id >= 0),
    constraint ck_value_consecutive check (value >= 0)
);
GO

-- JOB View --
GO
CREATE VIEW view_job(
    id,
    code,
    name,
    description,
    role
) AS 
SELECT
    j.id,
    concat(coalesce(c.prefix, ''),j.id + COALESCE(c.value,0)),
    j.name,
    j.description,
    u.name
FROM 
    job j
    left join user_role u on j.user_role = u.id
    left join table_ref t on t.name = 'job'
    left join consecutive c on t.name = c.table_name
WHERE 
    j.active = 1
GO

-- Branch View --
GO
CREATE VIEW view_branch(
    id,
    code,
    name
) AS 
SELECT
    b.id,
    concat(coalesce(c.prefix, ''),b.id + COALESCE(c.value,0)),
    b.name
FROM 
    branch b
    left join table_ref t on t.name = 'branch'
    left join consecutive c on t.name = c.table_name
WHERE 
    b.active = 1
GO

-- User Role View --
GO
CREATE VIEW view_user_role(
    id,
    code,
    name,
    description
) AS 
SELECT
    u.id,
    concat(coalesce(c.prefix, ''),u.id + COALESCE(c.value,0)),
    u.name,
    u.description
FROM 
    user_role u
    left join table_ref t on t.name = 'user_role'
    left join consecutive c on t.name = c.table_name
WHERE 
    u.active = 1
GO

-- Degree View --
GO
CREATE VIEW view_degree(
    id,
    code,
    name,
    description
) AS 
SELECT
    d.id,
    concat(coalesce(c.prefix, ''),d.id + COALESCE(c.value,0)),
    d.name,
    d.description
FROM 
    degree d
    left join table_ref t on t.name = 'degree'
    left join consecutive c on t.name = c.table_name
WHERE 
    d.active = 1
GO

-- Error Log View --
GO
CREATE VIEW view_error_log(
    id,
    code,
    person,
    date_time,
    description,
    summary
) AS 
SELECT
    e.id,
    concat(coalesce(c.prefix, ''),e.id + COALESCE(c.value,0)),
    p.nickname,
    e.date_time,
    e.description,
    e.summary
FROM 
    error_log e
    left join person p on e.person = p.name
    left join table_ref t on t.name = e.table_name
    left join consecutive c on t.name = c.table_name
GO

-- Activity Log View --
GO
CREATE VIEW view_activity_log(
    id,
    code,
    person,
    date_time,
    description
) AS 
SELECT
    a.id,
    concat(coalesce(c.prefix, ''),a.id + COALESCE(c.value,0)),
    p.nickname,
    a.date_time,
    a.[description]
FROM 
    activity_log a
    left join person p on a.person = p.name
    left join table_ref t on t.name = a.table_name
    left join consecutive c on t.name = c.table_name
GO

-- Experiment View --
GO
CREATE VIEW view_experiment(
    id,
    code,
    name,
    date,
    description,
    main_objective,
    project,
    experimenter,
    equipment,
    methodology,
    objective
) AS 
SELECT
    e.id,
    concat(coalesce(c.prefix, ''), e.id + COALESCE(c.value,0)),
    e.name,
    e.date,
    e.description,
    e.main_objective,
    pr.name,
    CONCAT(p.second_surname,' ',p.first_surname,', ',p.name),
    STRING_AGG(CONCAT('name: ', eq.name,'; model: ', eq.model,', serial:',eq.serial),'\n'),
    STRING_AGG(CONCAT('step: ',m.step,' description: ', m.description), '\n'),
    STRING_AGG(o.description, '\n')
FROM 
    experiment e
    left join person p on e.experimenter = p.name
    left join project pr on e.project = pr.id
    left join table_ref t on t.name = 'experiment'
    left join consecutive c on t.name = c.table_name
    left join experiment_equipment eq1 on e.id = eq1.experiment
    left join equipment eq on eq.id = eq1.equipment and eq.active = 1
    left join methodology m on e.id = m.experiment and m.active = 1
    left join objective o on o.experiment = e.id and o.active = 1
WHERE
    e.active = 1
GROUP BY
    e.id,
    concat(coalesce(c.prefix, ''), e.id + COALESCE(c.value,0)),
    e.name,
    e.date,
    e.description,
    e.main_objective,
    pr.name,
    CONCAT(p.second_surname,' ',p.first_surname,', ',p.name)
GO

-- Project View --
GO
CREATE VIEW view_project(
    id,
    code,
    name,
    price,
    journals,
    person,
    branch
) AS 
SELECT
    pr.id,
    concat(coalesce(c.prefix, ''),pr.id + COALESCE(c.value,0)),
    pr.name,
    pr.price,
    pr.journals,
    CONCAT(p.second_surname,' ',p.first_surname,', ',p.name),
    b.name
FROM 
    project pr
    left join person p on pr.person = p.name
    left join table_ref t on t.name = 'project'
    left join consecutive c on t.name = c.table_name
    left join branch b on b.id = pr.branch
WHERE
    pr.active = 1
GO

-- Customer Order View --
GO
CREATE VIEW view_customer_order(
    id,
    project,
    customer,
    status
) AS 
SELECT
    pr.id,
    pr.name,
    co.customer,
    co.status
FROM 
    customer_order co
    left join project pr on co.project = pr.id
    left join table_ref t on t.name = 'customer_order'
    left join consecutive c on t.name = c.table_name
GO

-- Person View --
GO
CREATE VIEW view_person(
    id,
    code,
    nickname,
    name,
    first_surname,
    secod_surname,
    phone,
    signature,
    photo,
    degree,
    job
) AS 
SELECT
    p.id,
    concat(coalesce(c.prefix, ''),p.id + COALESCE(c.value,0)),
    p.nickname,
    p.name,
    p.first_surname,
    p.second_surname,
    p.phone,
    p.signature,
    p.photo,
    d.name,
    j.name
FROM 
    person p
    left join degree d on d.id = p.degree
    left join job j on j.id = p.job
    left join table_ref t on t.name = 'person'
    left join consecutive c on t.name = c.table_name
GO

-- Function to get next available primary key for any table --
GO
CREATE OR ALTER PROCEDURE getNextID (@tableName nvarchar(50))
AS
BEGIN
    DECLARE @current_value int;

    update table_ref with (updlock)
    set 
    current_value = coalesce(current_value,0) + 1,
    @current_value = current_value
    where [name] = @tableName;
   
   	--select value = @current_value, name = @tableName
   	return @current_value
END
GO

-- Function to reverse last available primary key for any table --
GO
CREATE OR ALTER PROCEDURE reverseID (@tableName nvarchar(50))
AS
BEGIN
    DECLARE @current_value int;
    update table_ref with (updlock)
    set 
    current_value = current_value - 1
    where [name] = @tableName;
END
GO

-- Consecutive Trigger --
GO
CREATE OR ALTER TRIGGER consecutive_trigger ON consecutive
INSTEAD OF INSERT
AS
BEGIN
    DECLARE @table nvarchar(50) = 'consecutive';
    DECLARE @nextID int;
    DECLARE @oldID int;
    DECLARE @type varchar(50);
    DECLARE @description varchar(100);
    DECLARE @value int;
    DECLARE @prefix nvarchar(50);
    DECLARE @table_name NVARCHAR(50);
    DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

    select * from inserted
    OPEN my_Cursor;
    FETCH NEXT FROM my_Cursor into @nextID, @type, @description, @value, @prefix, @table_name
    WHILE @@FETCH_STATUS = 0 
        BEGIN  
            EXEC @nextID = getNextID @tableName = @table;
            select nextID = @oldID, newID = @nextID, type = @type
            insert into consecutive VALUES 
            (@nextID, @type, @description, @value, @prefix, @table_name);
            FETCH NEXT FROM my_Cursor into @nextID, @type, @description, @value, @prefix, @table_name
        END
    CLOSE my_Cursor  
    DEALLOCATE my_Cursor  

END;
GO



-- Populates table_ref --
GO
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
    ('activity_log','Bitacora',0),
    ('person','Usuarios',0),
    ('job','Puestos',0),
    ('degree','Nivel Academico',0),
    ('user_role','Roles',0);
GO

GO
Insert into code (description) values
    ('Proyectos'),
    ('Bitácoras Experimentales'),
    ('Roles'),
    ('Puestos'),
    ('Usuarios'),
    ('Bitácora'),
    ('Nivel Académico'),
    ('Ramas Científicas'),
    ('Errores');
GO

GO
Insert into consecutive (id, type, description, value, prefix, table_name) values
    (0, 'Proyectos','Test Description',100, 'PROY-','Proyectos')
    ,(1, 'Roles','Test Description',200, 'ROL-','Roles')
GO
