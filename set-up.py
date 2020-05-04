
import subprocess
import sys


### FOLLOWING LINES WILL INSTALL NEEDED PACKAGES ONTO YOUR COMPUTER
### THEN REST OF CODE WILL RUN AND SET UP YOUR LOCAL POSTGRES DATABASE
### THE DB CONNECTION STRING SHOULD BE MADE IN YOUR LOCAL ".env" FILE 

# def install_package(package):
#     subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# def install_req(path):
#     subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", path])

# install_package('setuptools')
# install_req('requirements.txt')


from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np




load_dotenv()

database_url = os.environ['DATABASE_URL']

engine = create_engine(database_url)

con = engine.connect()

with engine.connect() as c:
    sql = '''
    DROP TABLE IF EXISTS Clients CASCADE;


CREATE TABLE Clients(
"Race" VARCHAR,
"Ethnicity" VARCHAR,
"Gender" VARCHAR,
"Vet_Status" VARCHAR,
"Vet_Discharge_Status" VARCHAR,
"Created_Date" DATE,
"Updated_Date" DATE,
"Birth_Date" DATE,
"Client_Id" BIGINT PRIMARY KEY
);

DROP TABLE IF EXISTS Assessment CASCADE;

CREATE TABLE Assessment (
"Client_Id" BIGINT,
"Assessment_Id" BIGINT PRIMARY KEY,
"Assessment_Type" VARCHAR,
"Assessment_Score" INT,
"Assessment_Date" DATE,
FOREIGN KEY ("Client_Id") REFERENCES Clients("Client_Id")
);


DROP TABLE IF EXISTS Programs CASCADE;

CREATE TABLE Programs (
"Program_Id" INT PRIMARY KEY,
"Agency_Id" INT,
"Program_Name" VARCHAR, 
"Program_Start" DATE,
"Program_End" DATE,
"Continuum" INT,
"Project_Type" VARCHAR,
"Target_Pop" VARCHAR,
"Housing_Type" VARCHAR,
"Added_Date" DATE,
"Updated_Date" DATE
);

DROP TABLE IF EXISTS Enrollment CASCADE;

CREATE TABLE Enrollment (
"Client_Id" BIGINT,
"Enrollment_Id" BIGINT PRIMARY KEY,
"Household_Id" BIGINT,
"Program_Id" INT,
"Added_Date" DATE,
"Housing_Status" VARCHAR,
"LOS_Prior" VARCHAR,
"Entry Screen Times Homeless in the Past Three Years" VARCHAR,
"Entry Screen Total Months Homeless in Past Three Years" VARCHAR,
"Zip" INT,
"Chronic_Homeless" VARCHAR,
"Prior_Residence" VARCHAR,
"Last_Grade_Completed" VARCHAR,
-- FOREIGN KEY ("Program_Id") REFERENCES Programs("Program_Id"), -program table missing programs
FOREIGN KEY ("Client_Id") REFERENCES Clients("Client_Id")
);

DROP TABLE IF EXISTS Exit_Screen CASCADE; 

CREATE TABLE Exit_Screen (
"Client_Id" BIGINT,
"Enrollment_Id" BIGINT,
"Exit_Destination" VARCHAR,
"Exit_Reason" VARCHAR, 
"Exit_Date" DATE,
FOREIGN KEY ("Client_Id") REFERENCES Clients("Client_Id"),
FOREIGN KEY ("Enrollment_Id") REFERENCES Enrollment("Enrollment_Id")
);

DROP TABLE IF EXISTS Destinations CASCADE;

CREATE TABLE Destinations(
"Destination_Code" INT,
"Exit_Destination" VARCHAR PRIMARY KEY
);

DROP TABLE IF EXISTS yearly_race;
create table yearly_race
(Date text,
"Project_Type" varchar,
"Race" varchar,
num_people_enroll bigint);

DROP TABLE IF EXISTS race_no_prog;

create table race_no_prog
(Date text,
"Race" varchar,
num_people_enroll bigint);
    
DROP TABLE IF EXISTS age_no_prog;

create table age_no_prog
("Date" text,
"Age" int,
"Num_Clients" bigint); 

DROP TABLE IF EXISTS age_prog;

create table age_prog
("Date" text,
"Project_Type" varchar,
"Age" int,
"Num_Clients" bigint);


DROP TABLE IF EXISTS gender_no_prog;

create table gender_no_prog
(Date text,
"Gender" varchar,
num_people_enroll bigint);   

DROP TABLE IF EXISTS yearly_gender;

create table yearly_gender
(Date text,
"Project_Type" varchar,
"Gender" varchar,
num_people_enroll bigint);
    '''
    c.execute(sql)



assessment = pd.read_csv(r"data/Sacramento_County_-_Assessment_Table_2019-09-05T0401_pTq3TT.csv")
client = pd.read_csv(r"data/Sacramento_County_-_Client_Table_2019-09-05T0101_Kky8n7.csv")
exit = pd.read_csv(r"data/Sacramento_County_-_Exit_Table_2019-09-01T0601_FDwNWs.csv")
enrollment = pd.read_csv(r"data/Sacramento_County_-_Enrollment_Table_2019-09-05T0131_KptDcM.csv")
project = pd.read_csv(r"data/Sacramento_County_-_Project_Table_2019-09-05T0200_DdZb5N.csv")
destination = pd.read_csv(r"data/exit_destinations.csv")

# Eliminate spaces in column names
for i in assessment.columns:
    assessment.rename(columns = {
        i:str(i).replace(' ', '_')
    }, inplace=True)
    
# Rename columns for consistency    
assessment.rename(columns={
    'Personal_ID': 'Client_Id',
    "Assessment_ID":'Assessment_Id'
}, inplace=True)



# Reformat numbers with , dividers
assessment['Client_Id'] = assessment['Client_Id'].str.replace(',', '')

# Drop unneeded column
assessment.drop(columns=['Unnamed:_0'], inplace=True)

client.rename(columns={
    'Clients Race': 'Race',
    'Clients Ethnicity':'Ethnicity',
    'Clients Gender': 'Gender',
    'Clients Veteran Status':'Vet_Status',
    'Clients Discharge Status': 'Vet_Discharge_Status',
    'Clients Date Created Date': 'Created_Date',
    'Clients Date Updated': 'Updated_Date',
    'Birth_Date_d':'Birth_Date',
    'Personal_Id_d':'Client_Id'
},inplace=True)

client['Client_Id'] = client['Client_Id'].str.replace(',', '')

project.rename(columns={
    'Program Id': 'Program_Id',
    'Agency Id': 'Agency_Id',
    'Name': 'Program_Name',
    'Availability Start Date':'Program_Start',
    'Availability End Date': 'Program_End',
    'Continuum Project': 'Continuum',
    'Project Type Code': 'Project_Type',
    'Housing Type':'Housing_Type',
    'Added Date':'Added_Date',
    'Last Updated Date':'Updated_Date',
    'Target Population':'Target_Pop'
}, inplace=True)

# Drop columns labelled as unimportant in source documentation
project.drop(columns=['Unnamed: 0','Affiliated Project Ids','Affiliated with a Residential Project', 'Tracking Method',
                     'Victim Service Provider'], inplace=True)


for i in exit.columns:
    if i == 'Project Exit Date':
        exit.rename(columns={
            i:'Exit_Date'
        }, inplace=True)
        continue
    exit.rename(columns={
        i:str(i).replace(' ', '_')
    }, inplace=True)



exit.rename(columns={
    'Personal_ID':'Client_Id'
}, inplace=True)



# Reformat numbers with , dividers
exit['Client_Id'] = exit['Client_Id'].str.replace(',', '')
exit['Enrollment_Id'] = exit['Enrollment_Id'].str.replace(',', '')

# Drop record with bad year
exit.drop(exit[exit['Exit_Date'] == '2918-08-07'].index, inplace = True) 


enrollment.rename(columns={
    'Personal ID':'Client_Id',
    'Enrollment Id': 'Enrollment_Id',
    'Household ID': 'Household_Id',
    'Enrollments Project Id': 'Program_Id',
    'Entry Screen Added Date':'Added_Date',
    'Entry Screen Housing Status':'Housing_Status',
    'Entry Screen Length of Stay in Prior Living Situation':'LOS_Prior',
    'Entry Screen Zip Code':'Zip',
    'Entry Screen Chronic Homeless at Project Start':'Chronic_Homeless',
    'Entry Screen Residence Prior to Project Entry':'Prior_Residence',
    'Entry Screen Last Grade Completed':'Last_Grade_Completed'
}, inplace=True)


# Drop columns lablled as unimportant in source documentation
enrollment.drop(columns=['Unnamed: 0',
                        'Entry Screen Client Became Enrolled in PATH (Yes / No)',
                        'Entry Screen Reason not Enrolled','Entry Screen City','Entry Screen State'
                        ], inplace=True)

enrollment['Enrollment_Id'] = enrollment['Enrollment_Id'].str.replace(',', '')


exit.drop(exit[exit['Client_Id'] == '455040993'].index, inplace = True) 
exit.drop(exit[exit['Client_Id'] == '3834035492'].index, inplace = True)


# Load cleaned up data to database tables - can take some time
client.to_sql(name="clients", if_exists='append', index=False, con=con, method='multi')
assessment.to_sql(name="assessment", if_exists='append', index=False, con=con, method='multi')
project.to_sql(name="programs", if_exists='append', index=False, con=con, method='multi') 
enrollment.to_sql(name="enrollment",if_exists="append", index=False, con=con, method='multi')
exit.to_sql(name="exit_screen",if_exists="append", index=False, con=con, method='multi')
destination.to_sql(name="destinations", if_exists='append', index=False, con=con, method='multi')





with engine.connect() as c:
    sql = '''
    ALTER TABLE Exit_Screen
ADD COLUMN ES_Id bigserial PRIMARY KEY;

alter table Programs
add column "Project_Type_Group" varchar;
update programs
set "Project_Type_Group" = 'Permanent Housing'
where "Project_Type" in ('PH - Housing with Services (no disability required)',
						'PH - Housing Only',
						'PH - Permanent Supportive Housing (disability required)');
update programs
set "Project_Type_Group" = 'Rapid Re-Housing'
where "Project_Type" = 'PH - Rapid Re-Housing';
update programs
set "Project_Type_Group" = 'Emergency Shelter' where "Project_Type" = 'Emergency Shelter';
update programs
set "Project_Type_Group" = 'Street Outreach' where "Project_Type" = 'Street Outreach';
update programs
set "Project_Type_Group" = 'Transitional Housing' where "Project_Type" = 'Transitional Housing';
update programs
set "Project_Type_Group" = 'Other' where "Project_Type" in ('Day Shelter',
														  'Coordinated Assessment',
														  'Homeless Prevention',
														  'Other',
														  'Services Only',
														  'RETIRED (HPRP)');
    '''
    c.execute(sql)


# Table for number of active clients per month 
# Number active = those enrolled in a program without
# an exit date before the end of the queried time period
# Client Id may be represented more than once - each enrollment counted


dates = ['2015','2016','2017','2018','2019']

sql_create = '''
DROP TABLE IF EXISTS num_active_monthly CASCADE;
drop table if exists volume_active_programs cascade;
drop table if exists volume_active cascade;
CREATE TABLE volume_active_programs (
Year VARCHAR,
Num_Active BIGINT,
Distinct_Active BIGINT,
Project_Type_Group VARCHAR
);

CREATE TABLE volume_active (
Year VARCHAR,
Num_Active BIGINT,
Distinct_Active BIGINT
);
'''
with engine.connect() as c:
    c.execute(sql_create)
    
sql_update_programs = '''
INSERT INTO volume_active_programs
SELECT '{0}' as "Year",
count(a."Client_Id") as "Num_Active",
count(distinct a."Client_Id") as "Distinct_Active",
c."Project_Type_Group" as "Project_Type_Group"
FROM enrollment a
LEFT JOIN exit_screen b
ON a."Enrollment_Id" = b."Enrollment_Id"
left join programs c 
on a."Program_Id" = c."Program_Id"
WHERE TO_CHAR(a."Added_Date",'YYYY') <= '{0}'
AND (b."Exit_Date" > '{0}-01-01' or b."Exit_Date" is null)
AND a."Added_Date" <> '2014-01-01'
group by "Project_Type_Group","Year"
	order by "Project_Type_Group", "Year"
'''
sql_update = '''
INSERT INTO volume_active
SELECT '{0}' as "Year",
count(a."Client_Id") as "Num_Active",
count(distinct a."Client_Id") as "Distinct_Active"
FROM enrollment a
LEFT JOIN exit_screen b
ON a."Enrollment_Id" = b."Enrollment_Id"
WHERE TO_CHAR(a."Added_Date",'YYYY') <= '{0}'
AND (b."Exit_Date" > '{0}-01-01' or b."Exit_Date" is null)
AND a."Added_Date" <> '2014-01-01'
'''

for date in dates:
    print(date)
    with engine.connect() as c:
            c.execute(sql_update.format(date))
            c.execute(sql_update_programs.format(date))




with engine.connect() as c:
    sql = '''
DROP VIEW IF EXISTS monthly_in;
DROP VIEW IF EXISTS monthly_out;
DROP VIEW if exists yearly_in;
drop view if exists yearly_out;
drop view if exists volume_in;
drop view if exists volume_out;
drop view if exists volume_in_programs;
drop view if exists volume_out_programs;
drop view if exists volume_out_monthly;

create view volume_in_programs as
SELECT to_char(a."Added_Date", 'YYYY') as "Year",
count(a."Client_Id") as "Num_in",
count(distinct a."Client_Id") as "Num_in_distinct",
c."Project_Type_Group" as "Project_Type_Group"
FROM enrollment a
left join programs c 
on a."Program_Id" = c."Program_Id"
where to_char(a."Added_Date", 'YYYY') > '2014'
group by "Year","Project_Type_Group"
order by "Year","Project_Type_Group";


create view volume_out_programs as
SELECT to_char(b."Exit_Date", 'YYYY') as "Year",
count(a."Client_Id") as "Num_out",
count(distinct a."Client_Id") as "Num_out_distinct",
c."Project_Type_Group" as "Project_Type_Group"
FROM enrollment a
left join exit_screen b 
on a."Enrollment_Id" = b."Enrollment_Id"
left join programs c 
on a."Program_Id" = c."Program_Id"
where to_char(b."Exit_Date", 'YYYY') > '2014'
group by "Year","Project_Type_Group"
order by "Year","Project_Type_Group";

create view volume_in as 
SELECT to_char(a."Added_Date", 'YYYY') as "Year",
count(a."Client_Id") as "Num_in",
count(distinct a."Client_Id") as "Num_in_distinct"
FROM enrollment a
where to_char(a."Added_Date", 'YYYY') > '2014'
group by "Year"
order by "Year";

create view volume_out as 
SELECT to_char(b."Exit_Date", 'YYYY') as "Year",
count(a."Client_Id") as "Num_out",
count(distinct a."Client_Id") as "Num_out_distinct"
FROM enrollment a
left join exit_screen b 
on a."Enrollment_Id" = b."Enrollment_Id"
where to_char(b."Exit_Date", 'YYYY') > '2014'
group by "Year"
order by "Year";


create view volume_out_monthly as 
SELECT to_char(b."Exit_Date", 'YYYY') as "Year",
to_char(b."Exit_Date",'YYYY-mm') as "Month",
count(a."Client_Id") as "Num_out",
count(distinct a."Client_Id") as "Num_out_distinct"
FROM enrollment a
left join exit_screen b 
on a."Enrollment_Id" = b."Enrollment_Id"
where to_char(b."Exit_Date", 'YYYY') > '2014'
and to_char(b."Exit_Date", 'YYYY-mm') < '2019-08'
group by "Year", "Month"
order by "Year", "Month";


drop table if exists volume_total;
drop table if exists volume_total_programs;

select a."year", a."num_active", a."distinct_active",
b."Num_in", b."Num_in_distinct",
c."Num_out", c."Num_out_distinct", a."project_type_group"
into volume_total_programs
from volume_active_programs as a
left join volume_in_programs b
on a."year" = b."Year" and a."project_type_group" = b."Project_Type_Group"
left join volume_out_programs c
on a."year" = c."Year" and a."project_type_group" = c."Project_Type_Group";


create index indx_project_group 
on volume_total_programs using btree
(project_type_group, year);

select a."year", a."num_active", a."distinct_active",
b."Num_in", b."Num_in_distinct",
c."Num_out", c."Num_out_distinct"
into volume_total
from volume_active as a
left join volume_in b
on a."year" = b."Year"
left join volume_out c
on a."year" = c."Year";





    '''
    c.execute(sql)




# # Create demographic tables
with engine.connect()as c:
    sql = '''
UPDATE clients
SET "Race" = 'Unknown'
WHERE "Race" IN ('Client Refused', 'Data Not Collected',
'Client doesn''t Know')
OR"Race" IS NULL;


UPDATE clients
SET "Gender" = 'Unknown'
WHERE "Gender" IN ('Client doesn''t know', 'Client refused',
'Data not collected')
OR "Gender" IS NULL;



'''
    c.execute(sql)





# Table for % to permanent housing at program exit
sql_create = '''
DROP TABLE IF EXISTS num_to_PH CASCADE;
CREATE TABLE num_to_PH (
Month_Exit VARCHAR PRIMARY KEY,
Num_PH BIGINT,
Num_Exit BIGINT
);
'''
with engine.connect() as c:
     c.execute(sql_create)

dates = pd.date_range(start='1/01/2015',periods=12*5,freq='M')

sql_update = '''
INSERT INTO num_to_PH VALUES
('{0}',
(SELECT COUNT (DISTINCT e."Client_Id") 
FROM exit_screen e
LEFT JOIN destinations d
ON e."Exit_Destination" = d."Exit_Destination"
WHERE d."Destination_Code" = 1 
AND to_char(e."Exit_Date", 'YYYY-mm') <= '{0}'
AND e."Exit_Date" > '{0}-01'),
(SELECT COUNT (DISTINCT e."Client_Id") 
FROM exit_screen e
LEFT JOIN destinations d
ON e."Exit_Destination" = d."Exit_Destination"
WHERE to_char(e."Exit_Date", 'YYYY-mm') <= '{0}'
AND e."Exit_Date" > '{0}-01'));
'''

for date in dates:
    date = date.strftime('%Y-%m')
    with engine.connect() as c:
        c.execute(sql_update.format(date))



# Create views for number to permanent housing at exit yearly and all exits yearly
with engine.connect() as c:
    sql = '''
DROP VIEW IF EXISTS yearly_to_ph CASCADE;

CREATE VIEW yearly_to_ph AS
SELECT to_char(e."Exit_Date", 'YYYY') date, 
COUNT(e."Client_Id") Num_exit
FROM exit_screen e
LEFT JOIN destinations d
ON e."Exit_Destination" = d."Exit_Destination"
WHERE d."Destination_Code" = 1 
AND to_char(e."Exit_Date", 'YYYY') > '2014'
GROUP BY to_char(e."Exit_Date", 'YYYY')
ORDER BY to_char(e."Exit_Date", 'YYYY') DESC;

DROP VIEW IF EXISTS yearly_total_exit CASCADE;
CREATE VIEW yearly_total_exit AS
SELECT TO_CHAR(e."Exit_Date", 'YYYY') DATE, 
COUNT(e."Client_Id") Num_exit
FROM exit_screen e
WHERE TO_CHAR(e."Exit_Date", 'YYYY') > '2014'
GROUP BY TO_CHAR(e."Exit_Date", 'YYYY')
ORDER BY TO_CHAR(e."Exit_Date", 'YYYY') DESC;
    '''
    c.execute(sql)



# # Create view for number of unique individuals to programs per year where the client was homeless on entry
# from sqlalchemy import text
# sql_homeless = text('''
# DROP VIEW IF EXISTS yearly_enroll_homeless CASCADE;

# CREATE VIEW yearly_enroll_homeless AS
# SELECT DISTINCT TO_CHAR("Added_Date", 'YYYY') "Date",
# COUNT(distinct "Client_Id") "Num_Homeless"
# FROM enrollment
# WHERE ("Housing_Status" LIKE '%Category 1%' OR
# "Prior_Residence" = 'Emergency Shelter, including hotel/motel paid for with voucher'
# OR "Prior_Residence" = 'Hospital or other residential non-psychiatric medical facility'
# OR "Prior_Residence" = 'Place not meant for habitation'
# OR "Prior_Residence" = 'Psychiatric hospital or other psychiatric facility'
# OR "Prior_Residence" = 'Transitional housing for homeless persons')
# AND TO_CHAR("Added_Date", 'YYYY') > '2014'
# GROUP BY "Date"
# ORDER BY "Date" DESC;
# ''')


# with engine.connect() as connection:
#     connection.execute(sql_homeless)




# View for average days from exit for those who exit to permanent housing and started in
# transitional housing or shelter to permanent housing

with engine.connect() as c:
    sql = '''
DROP VIEW IF EXISTS avg_to_PH CASCADE;

CREATE VIEW avg_to_PH AS 
SELECT DISTINCT TO_CHAR(a."Added_Date", 'YYYY') "Date",
AVG(b."Exit_Date"::date - a."Added_Date"::date) "Avg_Time_to_PH",
COUNT(distinct a."Client_Id")
FROM enrollment a
LEFT JOIN exit_screen b
ON a."Enrollment_Id" = b."Enrollment_Id"
LEFT JOIN destinations d
ON b."Exit_Destination" = d."Exit_Destination"
LEFT JOIN programs p
ON a."Program_Id" = p."Program_Id"
WHERE TO_CHAR(a."Added_Date", 'YYYY') > '2014'
AND d."Destination_Code" = 1
AND (p."Project_Type" = 'Transitional Housing'
OR p."Project_Type" = 'Day Shelter'
OR p."Project_Type" = 'Emergency Shelter'
OR p."Project_Type"='Street Outreach')
GROUP BY "Date"
'''
    c.execute(sql)


# Views for % to permanent housing
with engine.connect() as c:
    sql = '''
DROP VIEW IF EXISTS percent_ph_yr CASCADE;

CREATE VIEW percent_ph_yr AS
SELECT p."date" "Date", 
(CAST(p."num_exit" AS FLOAT)/
    CAST(a."num_exit" AS FLOAT)*100) "Percent"
FROM yearly_to_ph p
LEFT JOIN yearly_total_exit a 
ON a."date" = p."date"; 

DROP VIEW IF EXISTS percent_ph_mo CASCADE;

CREATE VIEW percent_ph_mo AS
SELECT "month_exit" "Date", 
(CAST("num_ph" AS FLOAT)/
    CAST(NULLIF("num_exit",0) AS FLOAT)*100) "Percent"
FROM num_to_ph; 
'''
    c.execute(sql)



# with engine.connect() as c:
#     sql= '''
# ALTER TABLE num_active_yearly
# ADD COLUMN total_act BIGINT;
# UPDATE num_active_yearly 
# SET "total_act" = "null_act" + "num_act";

# ALTER TABLE num_active_monthly
# ADD COLUMN total_act BIGINT;
# UPDATE num_active_monthly
# SET "total_act" = "null_act" + "num_act";
# '''
#     c.execute(sql)



# #Pandas manipulation for quartiles needed for age box plot
# sql = 'SELECT * FROM yearly_age'
# con = engine.connect()
# age = pd.read_sql(sql=sql, con=con)
# for index,row in age.iterrows():
#     if row[1] >= 100:
#         age.drop([index], inplace=True)
        
# years = ['2015','2016','2017','2018','2019']
# age_stats = {}
# for year in years:
#     age_stats[year] = age.loc[age.Date == year].describe().T.values

# age_df = pd.DataFrame(columns=['Count','Mean','std','Min','lower','median','upper','max','date'])
# counter = 0
# for key in age_stats:
#     age_df.loc[counter] = np.append(age_stats[key][0],key)
#     counter += 1
    
# age_df.to_sql(name='yearly_age_table', if_exists='replace',index=False, con=con)


# # Changed selecting from yearly age language due to new column names 

with engine.connect() as c:
    sql= '''
DROP TABLE if exists monthly_flow;
DROP TABLE if exists outcomes_sum_monthly; 
SELECT 
B."Num_out",B."Month",
D."num_ph", 
E."Percent"::int
INTO outcomes_sum_monthly
FROM volume_out_monthly B 
FULL JOIN num_to_ph D on D."month_exit" = B."Month"
FULL JOIN percent_ph_mo E ON E."Date" = D."month_exit"
ORDER BY "Month";

DROP TABLE if exists yearly_flow;
drop table if exists outcomes_sum_yearly;
SELECT 
E."Avg_Time_to_PH"::int, 
F."Percent"::int, F."Date"
INTO outcomes_sum_yearly
FROM avg_to_ph E 
FULL JOIN percent_ph_yr F ON F."Date"= E."Date"
order by "Date";

DELETE FROM outcomes_sum_monthly
where "Num_out" is null;
    '''
    c.execute(sql)


# # Make projection for end of 2019 data for comparison in yearly activity chart
# # Simple approach  just using means of previous corresponding months of data for in and out
# # Projections for active is tricker to get, so just assumes 5% growth in active participants based on 2018 growth

# # Monthly table data manipulation 
# con = engine.connect()
# sql = 'SELECT * FROM monthly_flow'
# monthly = pd.read_sql(sql=sql,con=con)
# replace_dates = ['2019-09','2019-10','2019-11','2019-12']
# monthly['month'] = monthly['act_date'].apply(lambda x : str(x).split('-')[1])
# monthly.set_index(monthly.act_date, inplace=True)
# for date in replace_dates:
#     monthly.loc[date,'num_in'] = int(monthly.loc[monthly.month==date.split('-')[1],'num_in'].mean())
#     monthly.loc[date,'num_out'] = int(monthly.loc[monthly.month==date.split('-')[1],'num_out'].mean())
#     monthly.loc[date,'total_act'] = int(monthly.loc[monthly.month==date.split('-')[1],'total_act'].mean())
#     monthly.loc[date,'num_ph'] = int(monthly.loc[monthly.month==date.split('-')[1],'num_ph'].mean())
#     monthly.loc[date,'Percent'] = (monthly.loc[date,'num_ph'] / monthly.loc[date,'num_out'])*100
#     monthly.loc[date,'act_date'] = date
    

# monthly.reset_index(drop=True, inplace=True)
# monthly['date'] = pd.to_datetime(monthly['act_date'])
# monthly.sort_values('date', inplace=True, ascending=False)

# # Yearly flow data table manipulation 
# sql = 'SELECT * FROM yearly_flow'
# yearly = pd.read_sql(sql=sql,con=con)
# yearly.loc[yearly.act_date=='2019','num_in'] = monthly.loc[monthly.date.dt.year==2019,'num_in'].sum()
# yearly.loc[yearly.act_date=='2019','num_out'] = monthly.loc[monthly.date.dt.year==2019,'num_out'].sum()
# yearly.loc[yearly.act_date=='2019','total_act'] = 22001 

# # Write manuipulated dataframes back to db 
# yearly.to_sql(name='yearly_flow', con=con, if_exists='replace', index=False)
# # Drop created columns needed for making predictions for last months of 2019 
# monthly.drop(columns=['date', 'month'], inplace=True)
# monthly.to_sql(name='monthly_flow', con=con, if_exists='replace', index=False)


# from sqlalchemy import text
from sqlalchemy.orm.session import sessionmaker

Session = sessionmaker()
sess = Session(bind=con)
sql = '''
DO $$
DECLARE
	rec RECORD;
BEGIN
	FOR rec IN 
		(SELECT DISTINCT to_char("Added_Date", 'YYYY') as yearvar FROM enrollment
		WHERE to_char("Added_Date", 'YYYY') > '2014')
		LOOP 
			INSERT INTO yearly_race
			SELECT rec.yearvar::text as Date,
			p."Project_Type_Group" as "Project_Type",
			c."Race", 
			COUNT(distinct e."Client_Id") Num_People_Enroll
			FROM enrollment e
			LEFT JOIN clients c
			ON e."Client_Id" = c."Client_Id"
			left join programs p
			on e."Program_Id" = p."Program_Id"
			left join exit_screen ex on ex."Enrollment_Id" = e."Enrollment_Id"
			WHERE e."Added_Date" <> '2014-01-01'
			AND TO_CHAR(e."Added_Date", 'YYYY') <= rec.yearvar::text
			and (ex."Exit_Date" > cast((rec.yearvar::text || '-01-01') as date)
				OR ex."Exit_Date" IS NULL)
			GROUP BY date, p."Project_Type_Group", c."Race"
			ORDER BY date, p."Project_Type_Group";

			INSERT INTO race_no_prog
			SELECT rec.yearvar::text as Date,
			c."Race", 
			COUNT(distinct e."Client_Id") Num_People_Enroll
			FROM enrollment e
			LEFT JOIN clients c
			ON e."Client_Id" = c."Client_Id"
			left join exit_screen ex on ex."Enrollment_Id" = e."Enrollment_Id"
			WHERE e."Added_Date" <> '2014-01-01'
			AND TO_CHAR(e."Added_Date", 'YYYY') <= rec.yearvar::text
			and (ex."Exit_Date" > cast((rec.yearvar::text || '-01-01') as date)
				OR ex."Exit_Date" IS NULL)
			GROUP BY date, c."Race"
			ORDER BY date,c."Race";
			
			INSERT INTO gender_no_prog
			SELECT rec.yearvar::text as Date, 
			c."Gender", 
			COUNT(distinct e."Client_Id") Num_People_Enroll
			FROM enrollment e
			LEFT JOIN clients c
			ON e."Client_Id" = c."Client_Id"
			left join exit_screen ex
			on e."Enrollment_Id" = ex."Enrollment_Id"
			WHERE e."Added_Date" <> '2014-01-01'
			AND TO_CHAR(e."Added_Date", 'YYYY') <= rec.yearvar::text
			and (ex."Exit_Date" > cast((rec.yearvar::text || '-01-01') as date)
				OR ex."Exit_Date" IS NULL)
			GROUP BY date, c."Gender"
			ORDER BY date, 
			c."Gender";
			
			insert into yearly_gender
			SELECT rec.yearvar::text as Date,
			p."Project_Type_Group" as "Project_Type",
			c."Gender", 
			COUNT(distinct e."Client_Id") Num_People_Enroll
			FROM enrollment e
			LEFT JOIN clients c
			ON e."Client_Id" = c."Client_Id"
			left join programs p
			on e."Program_Id" = p."Program_Id"
			left join exit_screen ex
			on e."Enrollment_Id" = ex."Enrollment_Id"
			WHERE e."Added_Date" <> '2014-01-01'
			AND TO_CHAR(e."Added_Date", 'YYYY') <= rec.yearvar::text
			and (ex."Exit_Date" > cast((rec.yearvar::text || '-01-01') as date)
				OR ex."Exit_Date" IS NULL)
			GROUP BY date, p."Project_Type_Group", c."Gender"
			ORDER BY date, p."Project_Type_Group", c."Gender";
			
			insert into age_prog
			 (with t as (
				SELECT rec.yearvar::text as "Date",
				(to_char(MAX(e."Added_Date") OVER(
							PARTITION BY e."Client_Id"
									),
		 'YYYY')::int - to_char(c."Birth_Date",'YYYY')::int)  "Age",
				 p."Project_Type_Group" as "Project_Type",
				 e."Client_Id"
				FROM enrollment e
				LEFT JOIN 
				clients c 
				ON e."Client_Id" = c."Client_Id"
				left join programs p
				on e."Program_Id" = p."Program_Id"
				left join exit_screen ex on ex."Enrollment_Id" = e."Enrollment_Id"
				WHERE e."Added_Date" <> '2014-01-01'
				AND TO_CHAR(e."Added_Date", 'YYYY') <= rec.yearvar::text
				and (ex."Exit_Date" > cast((rec.yearvar::text || '-01-01') as date) 
					 or ex."Exit_Date" is null)
				and c."Birth_Date" is not null
				ORDER BY "Date", "Project_Type", "Age"
				)
			select rec.yearvar::text as "Date", "Project_Type", 
			  "Age", count(distinct "Client_Id") as "Num_Clients" 
			  from t
			Where "Age" < 100
			group by "Date", "Project_Type", "Age"
			order by "Date", "Project_Type");
			
			insert into age_no_prog
			 (with t as (
				SELECT rec.yearvar::text as "Date",
				(to_char(MAX(e."Added_Date") OVER(
							PARTITION BY e."Client_Id"
									),
		 'YYYY')::int - to_char(c."Birth_Date",'YYYY')::int)  "Age",
				 c."Client_Id"
				FROM enrollment e
				LEFT JOIN 
				clients c 
				ON e."Client_Id" = c."Client_Id"
				left join exit_screen ex on ex."Enrollment_Id" = e."Enrollment_Id"
				WHERE e."Added_Date" <> '2014-01-01'
				AND TO_CHAR(e."Added_Date", 'YYYY') <= rec.yearvar::text
				and (ex."Exit_Date" > cast((rec.yearvar::text || '-01-01') as date) 
					 or ex."Exit_Date" is null)
				and c."Birth_Date" is not null
				ORDER BY "Date", "Age"
				)
			select rec.yearvar::text as "Date", 
			  "Age", count(distinct "Client_Id") as "Num_Clients" 
			  from t
			where "Age" < 100
			group by "Date","Age"
			order by "Date","Age");
		END LOOP;
END;$$ LANGUAGE 'plpgsql';

'''

sess.execute(sql)
sess.commit()