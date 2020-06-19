USE SCIENTIFIC_JOURNALS
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

-- Populates code table --
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

-- Populates consecutive table --
GO
Insert into consecutive (type_id, description, value, prefix, table_name_id) values
    ( 1,'Consecutivo, pertenece a los proyectos',0, 'PRO-','project')
    ,( 2,'Consecutivo, pertenece a las Bitácoras de los Experimentos',0, 'BEXP-','experiment')
    ,( 3,'Consecutivo, pertenece a los roles',12, 'ROL-','user_role')
    ,( 8,'Consecutivo, pertenece a las Ramas Cintíficas',8, 'RAMC-','branch')
    ,( 4,'Consecutivo, pertenece a los Puestos',4, 'PU-','job')
    ,( 7,'Consecutivo, pertenece al Nivel Académico',6, 'NIAC-','degree')
    ,( 6,'Consecutivo, pertenece a la Bitácora de Seguridad', 0, 'BIT-','activity_log')
    -- ,( 9,'Consecutivo, pertenece a los Errores en el sistema', 0, 'ERR-','error_log')
    -- ,( 5,'Consecutivo, pertenece a los Usuarios de la Aplicación',1, 'USU-','person')
GO

-- Populate branch table --
GO
Insert into branch (name) values 
    ('Nanotechnología')
    ,('Química')
    ,('Biología')
    ,('Física')
    ,('Odontología')
    ,('Mecánica')
    ,('Eléctrica')
    ,('Mecatrónica')
GO

-- Populate user role table --
GO
Insert into user_role (name, description) values
    ('Lider de Equipo', 'Se encarga de Liderar los Equipos de Investigación')
    ,('Investigador', 'Se encarga de generar los diversos experimentos y/o procesos de investigacion')
    ,('Director', 'Se encarga de Liderar los proyectos y el laboratorio')
    ,('Asistente de laboratorio', 'Se encarga de ayudar a los investigadores de laboratorio')
    ,('Analista', 'Se encarga de predecir los diversos parámetros que son contenidos en el experimento')
    ,('Consultor', 'Se encarga de probar y autorizar los resultados otorgados')
    ,('Técnico', 'Se encarga de mantener el equpo del laboratorio siempre al marjen')
    ,('Encargado de laboratorio', 'Vela por la seguridad del laboratorio')
    ,('Limpieza', 'Se encarga de desinfectar los diversos equipos y utencilios del laboratorio')
GO

-- Populate Jobs table --
GO
insert into job (name, user_role_id) VALUES
    ('Directior de Laboratorio', 2)
    ,('Investigador de Primer Grado', 1)
    ,('Investigador de Segundo Grado', 4)
    ,('Conserje', 8)
GO

-- Populate Degree Table --
GO
insert into degree (name, description) VALUES
    ('Educación Secundaria', 'Bachillerato en educación media')
    ,('Diplomado', 'Grado de una institucion de educacion superior')
    ,('Profesorado', 'Grado de una institucion de educacion superior')
    ,('Técnico', 'Grado de una institucion de educacion superior')
    ,('Bachiller Universitario', 'Grado de una institucion de educacion superior')
    ,('Licenciatura', 'Grado de una institucion de educacion superior')
    ,('Especialidad', 'Grado de una institucion de educacion superior')
    ,('Maestria', 'Grado de una institucion de educacion superior')
    ,('Doctorado', 'Grado de una institucion de educacion superior')
GO

-- Populate Person Table --
GO
insert into person (nickname, password, isAdmin, name,  first_surname, second_surname, phone, degree_id, job_id) values
    ('chris','123', 1, 'Christian', 'Hardin', 'Rodriguez', 22222222, 4, 0)
    ,('dean','123', 1, 'Dean', 'Fernandez', 'Bryant', 22222223, 4, 1)
    ,('jose','123', 0, 'Jose', 'Moya', 'Porras', 22222224, 4, 2)
GO

-- Populate Project Table --
GO
insert into project (name, price, person_id, branch_id) values
    ('Project A', 10.0, 0, 0)
    ,('Project B', 15.5, 1, 1)
    ,('Project C', 21, 2, 2)
GO

-- Populate Experiment Table --
GO
insert into experiment (name, [description], main_objective, project_id, experimenter_id, witness_id) values
    ('Experiment A', 'Foo', 'Foo', 0, 0, 2)
    ,('Experiment B', 'Bar', 'Bar', 0, 1, 2)
GO

-- Populate Experiment Table --
GO
insert into equipment (name, brand, model, serial) values
    ('Macbook Pro 16', 'Apple', 'Macbook Pro', 'A1')
    ,('Macbook Pro 13', 'Apple', 'Macbook Pro', 'A2')
    ,('Arduino Uno', 'Arduino', 'Uno', 'A3')
GO

-- Populate Experiment Equipment Table --
GO
insert into experiment_equipment (experiment_id, equipment_id) values
    (0,0)
    ,(0,2)
    ,(1,1)
    ,(1,2)
GO

-- Populate Methodology Table --
GO
insert into methodology (step,description, experiment_id) values
    (1, 'Step A', 0)
    ,(2, 'Step B', 0)
    ,(3, 'Step C',0)
GO

-- Populate Objective Table --
GO
insert into objective (description, experiment_id) values
    ('Goal A', 0)
    ,('Goal B', 0)
    ,('Goal C',0)
GO

