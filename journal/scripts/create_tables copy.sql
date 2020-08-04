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
drop view if EXISTS view_consecutive;
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
    available bit default 1,
    constraint ck_current_value_table_ref check(current_value>=0)
);
GO


-- USER ROLE TABLE --
GO
CREATE TABLE user_role (
    id int primary key,
    name nvarchar(250) not null,
    description nvarchar(250) not null,
    active nvarchar(250),
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
    name nvarchar(250) not null,
    description nvarchar(250) not null,
    active nvarchar(250)
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
    name nvarchar(250) not null,
    active nvarchar(250) not null,
    user_role_id int FOREIGN KEY references user_role(id) on delete cascade not null,
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
    nickname nvarchar(250) not null,
    password nvarchar(500) not null,
    isAdmin nvarchar(250) not null,
    active nvarchar(250) not null,
    name nvarchar(250) not null,
    firstSurname nvarchar(250) not null,
    secondSurname nvarchar(250) not null,
    phone nvarchar(250) not null,
    signature nvarchar(300),
    photo nvarchar(300),
    degree_id int FOREIGN KEY references degree(id) on delete cascade not null,
    job_id int FOREIGN KEY references job(id) on delete cascade not null,
    constraint ck_id_person check (id >= 0),
    constraint unique_nickname unique(nickname),
    constraint unique_fullname_person unique(name, firstSurname, secondSurname)
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
    person_id int FOREIGN KEY REFERENCES person(id) on delete cascade not null,
    date_time nvarchar(250),
    table_name_id nvarchar(50) FOREIGN KEY REFERENCES table_ref(name) on delete cascade not null,
    description nvarchar(250) not null,
    summary nvarchar(2000) not null,
    constraint ck_id_error_log check (id >= 0),
    constraint unique_person_error_record unique(person_id,date_time,table_name_id),
    constraint pk_error_log PRIMARY KEY (id, table_name_id)
);
GO

-- Error Log Index --
GO
CREATE INDEX INDXERRLOG ON error_log(person_id);
GO

-- Activity Log Table --
GO
CREATE TABLE activity_log(
    id int,
    table_name_id nvarchar(50) FOREIGN KEY REFERENCES table_ref(name) on delete cascade not null,
    person_id int FOREIGN KEY REFERENCES person(id) on delete cascade not null,
    date_time nvarchar(250),
    description nvarchar(250) not null,
    constraint ck_id_activity_log check (id >= 0),
    constraint pk_activity_log PRIMARY KEY (id, table_name_id)
);
GO

-- Activity Log Index --
GO
CREATE INDEX INDXACTLOG ON activity_log(person_id);
GO

-- Equipment Table --
GO
CREATE TABLE equipment (
    id int PRIMARY KEY,
    name nvarchar(250) not null,
    brand nvarchar(250) not null,
    model nvarchar(250) not null,
    serial nvarchar(250) not null,
    active nvarchar(250),
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
    name nvarchar(250) not null,
    active nvarchar(250)
);
GO

-- Project Table --
GO
CREATE TABLE project(
    id int PRIMARY KEY,
    name nvarchar(250) not null,
    price nvarchar(250),
    journals nvarchar(250),
    active nvarchar(250),
    person_id int REFERENCES person(id) on delete cascade not null,
    branch_id int REFERENCES branch(id) on delete cascade not null,
    constraint ck_id_project check (id >= 0),
    constraint unique_name_project unique(name)
);
GO

-- Project Table Index --
GO
CREATE INDEX INDXPROJECT ON project(person_id, active);
GO

-- Experiment Table --
GO
CREATE Table experiment(
    id int PRIMARY KEY,
    name nvarchar(250) not null,
    date nvarchar(250),
    description nvarchar(2000) not null,
    main_objective nvarchar(3000) not null,
    active nvarchar(250),
    project_id int REFERENCES project(id) on delete cascade not null,
    experimenter_id int REFERENCES person(id) on delete no action,
    witness_id int REFERENCES person(id) on delete no action,
    constraint ck_id_experiment check (id >= 0),
    constraint unique_experiment UNIQUE(name, project_id)
);
GO

-- Experiment Table Index --
GO
CREATE INDEX INDXEXPERIMENT ON experiment(project_id, active);
GO

-- Experiment Equipment Table --
GO
CREATE TABLE experiment_equipment(
    experiment_id int FOREIGN KEY REFERENCES experiment(id) on delete cascade not null,
    equipment_id int FOREIGN KEY REFERENCES equipment(id) on delete cascade not null,
    active nvarchar(250)
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
    step nvarchar(250) not null,
    description nvarchar(1000) not null,
    experiment_id int REFERENCES experiment(id) on delete cascade not null,
    active nvarchar(250),
    constraint ck_id_methodology check (id >= 0)
);
GO

-- Methodology Table Index --
GO
CREATE INDEX INDXMETHODOLOGY ON methodology(experiment_id, active);
GO

-- Objective Table --
GO
CREATE Table objective(
    id int PRIMARY KEY,
    description nvarchar(250) not null,
    experiment_id int REFERENCES experiment(id) on delete cascade not null,
    active nvarchar(250),
    constraint ck_id_objective check (id >= 0)
);
GO

-- Objective Table Index --
GO
CREATE INDEX INDXOBJECTIVE ON objective(experiment_id, active);
GO

-- Experiment Image Table --
GO
CREATE Table experiment_image(
    id int PRIMARY KEY,
    photo nvarchar(300),
    active nvarchar(250),
    experiment_id int REFERENCES experiment(id) on delete cascade not null,
    constraint ck_id_experiment_image check (id >= 0)
);
GO

-- Experiment Image Index --
GO
CREATE INDEX INDXEXPIMG ON experiment_image(experiment_id, active);
GO

-- Code Table --
GO
CREATE Table code(
    id int IDENTITY(1,1) PRIMARY KEY,
    description nvarchar(250) unique not null,
    available nvarchar(250)
);
GO

-- Consecutive Table --
GO
CREATE Table consecutive(
    id int PRIMARY KEY,
    type_id int FOREIGN KEY REFERENCES code(id) on delete cascade unique not null,
    description nvarchar(250) not null,
    value nvarchar(250),
    prefix nvarchar(250),
    table_name_id nvarchar(50) FOREIGN KEY REFERENCES table_ref(name) on delete cascade unique not null,
    constraint ck_id_consecutive check (id >= 0)
);
GO


-- JOB View --
GO
CREATE VIEW view_job(
    id,
    code,
    name,
    role
) AS 
SELECT
    j.id,
    concat(coalesce(c.prefix, ''),j.id + COALESCE(c.value,0)),
    j.name,
    u.name
FROM 
    job j
    left join user_role u on j.user_role_id = u.id
    left join table_ref t on t.name = 'job'
    left join consecutive c on t.name = c.table_name_id
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
    left join consecutive c on t.name = c.table_name_id
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
    left join consecutive c on t.name = c.table_name_id
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
    left join consecutive c on t.name = c.table_name_id
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
    table_name,
    description,
    summary
) AS 
SELECT
    e.id,
    concat(coalesce(c.prefix, ''),e.id + COALESCE(c.value,0)),
    p.nickname,
    e.date_time,
    t.name,
    e.description,
    e.summary
FROM 
    error_log e
    left join person p on e.person_id = p.id
    left join table_ref t on t.name = e.table_name_id
    left join consecutive c on t.name = c.table_name_id
GO

-- Activity Log View --
GO
CREATE VIEW view_activity_log(
    id,
    code,
    table_name,
    person,
    date_time,
    description
) AS 
SELECT
    a.id,
    concat(coalesce(c.prefix, ''),a.id + COALESCE(c.value,0)),
    t.name,
    p.nickname,
    a.date_time,
    a.[description]
FROM 
    activity_log a
    left join person p on a.person_id = p.id
    left join table_ref t on t.name = a.table_name_id
    left join consecutive c on t.name = c.table_name_id
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
    withness,
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
    CONCAT(p.secondSurname,' ',p.firstSurname,', ',p.name),
    CONCAT(w.secondSurname,' ',w.firstSurname,', ',w.name),
    STRING_AGG(CONCAT('name: ', eq.name,'; model: ', eq.model,', serial:',eq.serial),' \n '),
    STRING_AGG(CONCAT('step: ',m.step,' description: ', m.description), ' \n '),
    STRING_AGG(o.description, ' \n ')
FROM 
    experiment e
    left join person p on e.experimenter_id = p.id
    left join person w on e.witness_id = w.id
    left join project pr on e.project_id = pr.id
    left join table_ref t on t.name = 'experiment'
    left join consecutive c on t.name = c.table_name_id
    left join experiment_equipment eq1 on e.id = eq1.experiment_id
    left join equipment eq on eq.id = eq1.equipment_id and eq.active = 1
    left join methodology m on e.id = m.experiment_id and m.active = 1
    left join objective o on o.experiment_id = e.id and o.active = 1
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
    CONCAT(w.secondSurname,' ',w.firstSurname,', ',w.name),
    CONCAT(p.secondSurname,' ',p.firstSurname,', ',p.name)
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
    CONCAT(p.secondSurname,' ',p.firstSurname,', ',p.name),
    b.name
FROM 
    project pr
    left join person p on pr.person_id = p.id
    left join table_ref t on t.name = 'project'
    left join consecutive c on t.name = c.table_name_id
    left join branch b on b.id = pr.branch_id
WHERE
    pr.active = 1
GO

-- -- Customer Order View --
-- GO
-- CREATE VIEW view_customer_order(
--     id,
--     project,
--     customer,
--     status
-- ) AS 
-- SELECT
--     pr.id,
--     pr.name,
--     co.customer_id,
--     co.status
-- FROM 
--     customer_order co
--     left join project pr on co.project_id = pr.id
--     left join table_ref t on t.name = 'customer_order'
--     left join consecutive c on t.name = c.table_name_id
-- GO

-- Person View --
GO
CREATE VIEW view_person(
    id,
    code,
    nickname,
    name,
    firstSurname,
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
    p.firstSurname,
    p.secondSurname,
    p.phone,
    p.signature,
    p.photo,
    d.name,
    j.name
FROM 
    person p
    left join degree d on d.id = p.degree_id
    left join job j on j.id = p.job_id
    left join table_ref t on t.name = 'person'
    left join consecutive c on t.name = c.table_name_id
WHERE
    p.active = 1
GO

-- Consecutive View --
GO
CREATE VIEW view_consecutive(
    id,
    type,
    description,
    value,
    prefix
) AS 
SELECT
    c.id,
    c2.description,
    c.description,
    c.value,
    c.prefix
FROM 
    consecutive c
    left join code c2 on c.type_id = c2.id
GO


-- Function to return max value

GO
CREATE OR ALTER FUNCTION maxInt(@valueA int, @valueB int)
returns INT
AS
BEGIN
    if @valueA > @valueB
        return @valueA
    return @valueB
END
GO

-- Procedure to get next available primary key for any table --
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

-- Procedure to reverse last available primary key for any table --
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

-- Procedure to update the number of journals in the project table --
GO
CREATE OR ALTER PROCEDURE updateJournalCount (@id int, @count int)
AS
BEGIN
    update project with (updlock)
    set journals = coalesce(journals,0) + @count
    where id = @id;
END
GO

-- -- Consecutive Trigger --
-- GO
-- CREATE OR ALTER TRIGGER consecutive_trigger ON consecutive
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'consecutive';
--     DECLARE @nextID int;
--     DECLARE @oldID int;
--     DECLARE @type int;
--     DECLARE @description varchar(100);
--     DECLARE @value int;
--     DECLARE @prefix nvarchar(50);
--     DECLARE @table_name NVARCHAR(50);
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 


--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @type, @description, @value, @prefix, @table_name
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into consecutive VALUES 
--             (@nextID, @type, @description, @value, @prefix, @table_name);
--             update table_ref set available=0 where name = @table_name;
--             update code set available=0 where id = @type;
--             FETCH NEXT FROM my_Cursor into @nextID, @type, @description, @value, @prefix, @table_name
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  

-- END;
-- GO

-- GO
-- CREATE OR ALTER TRIGGER consecutive_trigger_delete ON consecutive
-- after DELETE
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'consecutive';
--     DECLARE @nextID int;
--     DECLARE @oldID int;
--     DECLARE @type int;
--     DECLARE @description varchar(100);
--     DECLARE @value int;
--     DECLARE @prefix nvarchar(50);
--     DECLARE @table_name NVARCHAR(50);
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM DELETED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @type, @description, @value, @prefix, @table_name
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN
--             --EXEC reverseID @tableName = @table;
--             update table_ref set available=1 where name = @table_name;
--             update code set available=1 where id = @type;
--             FETCH NEXT FROM my_Cursor into @nextID, @type, @description, @value, @prefix, @table_name
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  

-- END;
-- GO
-- -- Branch Trigger --
-- GO
-- CREATE OR ALTER TRIGGER branch_trigger ON branch
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'branch';
--     DECLARE @nextID int;
--     DECLARE @name nvarchar(50);
--     DECLARE @active bit;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @name, @active
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into branch (id, name) VALUES 
--             (@nextID, @name);
--             FETCH NEXT FROM my_Cursor into @nextID, @name, @active
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  

-- END;
-- GO

-- -- User Roles Trigger --
-- GO
-- CREATE OR ALTER TRIGGER user_role_trigger ON user_role
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'user_role';
--     DECLARE @nextID int;
--     DECLARE @name nvarchar(50);
--     DECLARE @description nvarchar(100);
--     DECLARE @active bit;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @name, @description, @active
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into user_role (id, name, [description]) VALUES 
--             (@nextID, @name, @description);
--             FETCH NEXT FROM my_Cursor into @nextID, @name, @description, @active
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  

-- END;
-- GO

-- -- Jobs Trigger --
-- GO
-- CREATE OR ALTER TRIGGER job_trigger ON job
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'job';
--     DECLARE @nextID int;
--     DECLARE @name nvarchar(50);
--     DECLARE @active bit;
--     DECLARE @role int;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @name, @active, @role
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into job (id, name, user_role_id) VALUES 
--             (@nextID, @name, @role);
--             FETCH NEXT FROM my_Cursor into @nextID, @name, @active, @role
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  

-- END;
-- GO

-- -- Degree Trigger --
-- GO
-- CREATE OR ALTER TRIGGER degree_trigger ON degree
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'degree';
--     DECLARE @nextID int;
--     DECLARE @name nvarchar(50);
--     DECLARE @description nvarchar(50);
--     DECLARE @active bit;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @name, @description, @active
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into degree (id, name, description) VALUES 
--             (@nextID, @name, @description);
--             FETCH NEXT FROM my_Cursor into  @nextID, @name, @description, @active
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  

-- END;
-- GO

-- -- Person Trigger --
-- GO
-- CREATE OR ALTER TRIGGER person_trigger ON person
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'person';
--     DECLARE @nextID int;
--     DECLARE @nickname nvarchar(50);
--     DECLARE @password nvarchar(500);
--     DECLARE @isAdmin bit;
--     DECLARE @active bit;
--     DECLARE @name nvarchar(50);
--     DECLARE @firstSurname nvarchar(50);
--     DECLARE @secondSurname nvarchar(50);
--     DECLARE @phone int;
--     DECLARE @signature nvarchar(300);
--     DECLARE @photo nvarchar(300);
--     DECLARE @degree int;
--     DECLARE @job int;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     --Select * from inserted
--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @nickname, @password, @isAdmin, @active, @name, @firstSurname, @secondSurname, @phone, @signature, @photo, @degree, @job
--     --select @nextID, @nickname, @password, @isAdmin, @active, @name, @firstSurname, @secondSurname, @phone, @signature, @photo, @degree, @job
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into person (id, nickname, password, isAdmin, name, firstSurname, secondSurname, phone, signature, photo, degree_id, job_id) VALUES 
--             (@nextID, @nickname, @password, @isAdmin, @name, @firstSurname, @secondSurname, @phone, @signature, @photo, @degree, @job);
--             FETCH NEXT FROM my_Cursor into  @nextID, @nickname, @password, @isAdmin, @active, @name, @firstSurname, @secondSurname, @phone, @signature, @photo, @degree, @job
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  

-- END;
-- GO

-- -- Project Trigger --
-- GO
-- CREATE OR ALTER TRIGGER project_trigger ON project
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'project';
--     DECLARE @nextID int;
--     DECLARE @name varchar(50);
--     DECLARE @price float;
--     DECLARE @journals int;
--     DECLARE @active bit;
--     DECLARE @person int;
--     DECLARE @branch int;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @name, @price, @journals, @active, @person, @branch
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into project (id, name, price, journals, person_id, branch_id) VALUES 
--             (@nextID, @name, @price, @journals, @person, @branch);
--             FETCH NEXT FROM my_Cursor into  @nextID, @name, @price, @journals, @active, @person, @branch
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  
-- END;
-- GO

-- -- Experiment Insert Trigger --
-- GO
-- CREATE OR ALTER TRIGGER experiment_trigger ON experiment
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'experiment';
--     DECLARE @nextID int;
--     DECLARE @name nvarchar(50);
--     DECLARE @date date;
--     DECLARE @description nvarchar(2000);
--     DECLARE @main_objective nvarchar(3000);
--     DECLARE @active bit;
--     DECLARE @project int;
--     DECLARE @experimenter int;
--     DECLARE @witness int;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @name, @date, @description, @main_objective, @active, @project, @experimenter, @witness
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into experiment (id, name, date, description, main_objective, project_id, experimenter_id, witness_id) VALUES 
--             (@nextID, @name, @date, @description, @main_objective, @project, @experimenter, @witness);
--             FETCH NEXT FROM my_Cursor into  @nextID, @name, @date, @description, @main_objective, @active, @project, @experimenter, @witness
--             EXEC updateJournalCount @id = @project, @count = 1
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  
-- END;
-- GO

-- -- Project Trigger --
-- GO
-- CREATE OR ALTER TRIGGER project_trigger ON project
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'project';
--     DECLARE @nextID int;
--     DECLARE @name varchar(50);
--     DECLARE @price float;
--     DECLARE @journals int;
--     DECLARE @active bit;
--     DECLARE @person int;
--     DECLARE @branch int;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @name, @price, @journals, @active, @person, @branch
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into project (id, name, price, journals, person_id, branch_id) VALUES 
--             (@nextID, @name, @price, @journals, @person, @branch);
--             FETCH NEXT FROM my_Cursor into  @nextID, @name, @price, @journals, @active, @person, @branch
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  
-- END;
-- GO

-- -- Equipment Trigger --
-- GO
-- CREATE OR ALTER TRIGGER equipmment_trigger ON equipment
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'equipment';
--     DECLARE @nextID int;
--     DECLARE @name varchar(50);
--     DECLARE @brand varchar(50);
--     DECLARE @model varchar(50);
--     DECLARE @serial varchar(50);
--     DECLARE @active bit;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @name, @brand, @model, @serial, @active
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into equipment (id, name, brand, model, serial) VALUES 
--             (@nextID, @name, @brand, @model, @serial);
--             FETCH NEXT FROM my_Cursor into @nextID, @name, @brand, @model, @serial, @active
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  
-- END;
-- GO

-- -- Methodology Trigger --
-- GO
-- CREATE OR ALTER TRIGGER methodology_trigger ON methodology
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'methodology';
--     DECLARE @nextID int;
--     DECLARE @step int;
--     DECLARE @description nvarchar(1000);
--     DECLARE @experiment int;
--     DECLARE @active bit;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @step, @description, @experiment, @active
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into methodology (id, step, description, experiment_id) VALUES 
--             (@nextID, @step, @description, @experiment);
--             FETCH NEXT FROM my_Cursor into @nextID, @step, @description, @experiment, @active
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  
-- END;
-- GO

-- -- Objective Trigger --
-- GO
-- CREATE OR ALTER TRIGGER objective_trigger ON objective
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'objective';
--     DECLARE @nextID int;
--     DECLARE @description nvarchar(1000);
--     DECLARE @experiment int;
--     DECLARE @active bit;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @description, @experiment, @active
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into objective (id, description, experiment_id) VALUES 
--             (@nextID, @description, @experiment);
--             FETCH NEXT FROM my_Cursor into @nextID, @description, @experiment, @active
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  
-- END;
-- GO

-- -- Experiment Image Trigger --
-- GO
-- CREATE OR ALTER TRIGGER experiment_image_trigger ON experiment_image
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'experiment_image';
--     DECLARE @nextID int;
--     DECLARE @image nvarchar(300);
--     DECLARE @experiment int;
--     DECLARE @active bit;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @image, @active, @experiment
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into experiment_image (id, photo, experiment_id) VALUES 
--             (@nextID, @image, @experiment);
--             FETCH NEXT FROM my_Cursor into @nextID, @image, @active, @experiment
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  
-- END;
-- GO

-- -- Activiy Log Trigger --
-- GO
-- CREATE OR ALTER TRIGGER activity_log_trigger ON activity_log
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'activity_log';
--     DECLARE @nextID int;
--     DECLARE @tableNameID nvarchar(50);
--     DECLARE @personID int;
--     DECLARE @dateTime DATETIME;
--     DECLARE @description NVARCHAR(200);
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @tableNameID, @personID, @dateTime, @description
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into activity_log (id, table_name_id, person_id, [description]) VALUES 
--             (@nextID, @tableNameID, @personID, @description);
--             FETCH NEXT FROM my_Cursor into @nextID, @tableNameID, @personID, @dateTime, @description
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  
-- END;
-- GO

-- -- Activiy Log Trigger --
-- GO
-- CREATE OR ALTER TRIGGER error_log_trigger ON error_log
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'error_log';
--     DECLARE @nextID int;
--     DECLARE @tableNameID nvarchar(50);
--     DECLARE @personID int;
--     DECLARE @dateTime DATETIME;
--     DECLARE @description NVARCHAR(200);
--     DECLARE @summary NVARCHAR(2000);
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @personID, @dateTime, @tableNameID, @description, @summary
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into error_log (id, table_name_id, person_id, [description], summary) VALUES 
--             (@nextID, @tableNameID, @personID, @description, @summary);
--             FETCH NEXT FROM my_Cursor into @nextID, @personID, @dateTime, @tableNameID, @description, @summary
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  
-- END;
-- GO


-- Customer Trigger --
-- GO
-- CREATE OR ALTER TRIGGER customer_trigger ON customer
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'customer';
--     DECLARE @nextID int;
--     DECLARE @photo nvarchar(300);
--     DECLARE @active bit;
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @photo, @active
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into customer (id, photo, active) VALUES 
--             (@nextID, @photo, @active);
--             FETCH NEXT FROM my_Cursor into @nextID, @photo, @active
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  
-- END;
-- GO

-- Card Trigger --
-- GO
-- CREATE OR ALTER TRIGGER card_trigger ON card
-- INSTEAD OF INSERT
-- AS
-- BEGIN
--     DECLARE @table nvarchar(50) = 'card';
--     DECLARE @nextID int;
--     DECLARE @card_number bigint;
--     DECLARE @card_month int;
--     DECLARE @card_year int;
--     DECLARE @cvv int;
--     DECLARE @card_type bit;
--     DECLARE @active bit;
--     DECLARE @customer nvarchar(1000);
--     DECLARE my_Cursor CURSOR FOR SELECT * FROM INSERTED; 

--     OPEN my_Cursor;
--     FETCH NEXT FROM my_Cursor into @nextID, @card_number, @card_month, @card_year, @cvv, @card_type, @active, @customer
--     WHILE @@FETCH_STATUS = 0 
--         BEGIN  
--             EXEC @nextID = getNextID @tableName = @table;
--             insert into card (id, card_number, card_month, card_year, cvv, card_type, customer) VALUES 
--             (@nextID, @card_number, @card_month, @card_year, @cvv, @card_type, @customer);
--             FETCH NEXT FROM my_Cursor into @nextID, @card_number, @card_month, @card_year, @cvv, @card_type, @active, @customer
--         END
--     CLOSE my_Cursor  
--     DEALLOCATE my_Cursor  
-- END;
-- GO