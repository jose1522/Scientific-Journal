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
Insert into consecutive (type, description, value, prefix, table_name) values
    ( 'Proyectos','Consecutivo, pertenece a los proyectos',0, 'PRO-','project')
    ,( 'Bitácoras Experimentales','Consecutivo, pertenece a las Bitácoras de los Experimentos',0, 'BEXP-','experiment')
    ,( 'Roles','Consecutivo, pertenece a los roles',12, 'ROL-','user_role')
    ,( 'Ramas Científicas','Consecutivo, pertenece a las Ramas Cintíficas',8, 'RAMC-','branch')
    ,( 'Puestos','Consecutivo, pertenece a los Puestos',4, 'PU-','job')
    ,( 'Nivel Académico','Consecutivo, pertenece al Nivel Académico',6, 'NIAC-','degree')
    ,( 'Bitácora','Consecutivo, pertenece a la Bitácora de Seguridad', 0, 'BIT-','activity_log')
    ,( 'Errores','Consecutivo, pertenece a los Errores en el sistema', 0, 'ERR-','error_log')
    ,( 'Usuarios','Consecutivo, pertenece a los Usuarios de la Aplicación',1, 'USU-','person')
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
insert into job (name, user_role) VALUES
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