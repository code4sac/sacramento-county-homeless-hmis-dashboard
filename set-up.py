import subprocess
import sys



def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def install_req(path):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", path])


#MacOS install might need setuptools installed first, hence the install package then install requirements.txt

#FOLLOWING LINES WILL INSTALL ALL THE REQUIRED PACKAGES ONTO YOUR LOCAL MACHINE
# YOU WILL NEED TO MANUALLY INSTALL POSTGRESQL LOCALLY TO HAVE THIS CODE RUN
install_package('setuptools')
install_req('requirements.txt')


from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np


###### FOLLOWING LINE WILL ONLY WORK ONCE YOU"VE CREATED A LOCAL .ENV FILE LIKE THE EXAMPLE IN GITHUB REPO
###### SETS UP THIS PROJECT TO HAVE THE CONNECTION STRING FOR YOUR LOCAL POSTGRESQL DATABASE
####################################
load_dotenv()
###############################



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
    '''
    c.execute(sql)


# Table for number of active clients per month 
# Number active = those enrolled in a program without
# an exit date before the end of the queried time period
# Client Id may be represented more than once - each enrollment counted

dates = pd.date_range(start='1/01/2015',periods=12*5,freq='M')

sql_create = '''
DROP TABLE IF EXISTS num_active_monthly CASCADE;
CREATE TABLE num_active_monthly (
Act_Date VARCHAR PRIMARY KEY,
Num_Act BIGINT,
Null_Act BIGINT
)
'''
with engine.connect() as c:
    c.execute(sql_create)
    
sql_update = '''
INSERT INTO num_active_monthly VALUES
('{0}',
(SELECT COUNT(a."Client_Id")
FROM enrollment a
LEFT JOIN exit_screen b
ON a."Enrollment_Id" = b."Enrollment_Id"
WHERE TO_CHAR(a."Added_Date",'YYYY-mm') <= '{0}'
AND b."Exit_Date" > '{0}-01'),
(SELECT COUNT(a."Client_Id")
FROM enrollment a
LEFT JOIN exit_screen b
ON a."Enrollment_Id" = b."Enrollment_Id"
WHERE TO_CHAR(a."Added_Date",'YYYY-mm') <= '{0}'
AND b."Exit_Date" IS NULL))
'''

for date in dates:
    date = date.strftime('%Y-%m')
    with engine.connect() as c:
            c.execute(sql_update.format(date))


# Table for number of active clients per year
# Clients who were exclusively active (entered before year start, exited after)

dates_y = ['2015','2016','2017','2018','2019']

sql_create = '''
DROP TABLE IF EXISTS num_active_yearly CASCADE;
CREATE TABLE num_active_yearly (
Act_Date VARCHAR PRIMARY KEY,
Num_Act BIGINT,
Null_Act BIGINT
);
'''
with engine.connect() as c:
    c.execute(sql_create)
    
sql_update = '''
INSERT INTO num_active_yearly VALUES
('{0}',
(SELECT COUNT(a."Client_Id")
FROM enrollment a
LEFT JOIN exit_screen b
ON a."Enrollment_Id" = b."Enrollment_Id"
WHERE TO_CHAR(a."Added_Date",'YYYY') <= '{0}'
AND b."Exit_Date" > '{0}-01-01'),
(SELECT COUNT(a."Client_Id")
FROM enrollment a
LEFT JOIN exit_screen b
ON a."Enrollment_Id" = b."Enrollment_Id"
WHERE TO_CHAR(a."Added_Date",'YYYY') <= '{0}'
AND b."Exit_Date" is null));
'''

for date in dates_y:
    with engine.connect() as c:
        c.execute(sql_update.format(date))



with engine.connect() as c:
    sql = '''
    DROP VIEW IF EXISTS monthly_in CASCADE;
    
    CREATE VIEW monthly_in AS
    SELECT TO_CHAR(e."Added_Date", 'YYYY-mm'), COUNT(e."Client_Id") Num_in
    FROM enrollment e
    WHERE TO_CHAR(e."Added_Date", 'YYYY') > '2014'
    GROUP BY TO_CHAR(e."Added_Date", 'YYYY-mm')
    ORDER BY TO_CHAR(e."Added_Date", 'YYYY-mm') DESC;
    
    DROP VIEW IF EXISTS monthly_out CASCADE;
    
    CREATE VIEW monthly_out as
    SELECT TO_CHAR(e."Exit_Date", 'YYYY-mm'), COUNT(e."Client_Id") Num_out
    FROM exit_screen e
    WHERE TO_CHAR(e."Exit_Date", 'YYYY') > '2014'
    GROUP BY TO_CHAR(e."Exit_Date", 'YYYY-mm')
    ORDER BY TO_CHAR(e."Exit_Date", 'YYYY-mm') DESC;
    
    DROP VIEW IF EXISTS yearly_in CASCADE;
    
    CREATE VIEW yearly_in as
    SELECT TO_CHAR(e."Added_Date", 'YYYY') date, COUNT(e."Client_Id") Num_in
    FROM enrollment e
    WHERE TO_CHAR(e."Added_Date", 'YYYY') > '2014'
    GROUP BY TO_CHAR(e."Added_Date", 'YYYY')
    ORDER BY TO_CHAR(e."Added_Date", 'YYYY') DESC;
    
    DROP VIEW IF EXISTS yearly_out CASCADE;
    
    CREATE VIEW yearly_out as
    SELECT TO_CHAR(e."Exit_Date", 'YYYY'), COUNT(e."Client_Id") Num_out
    FROM exit_screen e
    WHERE TO_CHAR(e."Exit_Date", 'YYYY') > '2014'
    GROUP BY TO_CHAR(e."Exit_Date", 'YYYY')
    ORDER BY TO_CHAR(e."Exit_Date", 'YYYY') DESC;
    '''
    c.execute(sql)



# Create table for top 5 programs by enrollment by year
dates_y = ['2015','2016','2017','2018','2019']

sql_create = '''
DROP TABLE IF EXISTS top_5_programs CASCADE;
CREATE TABLE top_5_programs(
"Date" VARCHAR(5),
"Program" VARCHAR(100),
"Num_Enroll" BIGINT);
'''
with engine.connect() as c:
    c.execute(sql_create)
    
sql_update = '''
INSERT INTO top_5_programs

SELECT TO_CHAR(e."Added_Date",'YYYY') "Date", p."Program_Name", COUNT(e."Enrollment_Id")"Num_Enroll"
FROM enrollment e
LEFT JOIN programs p
ON p."Program_Id" = e."Program_Id"
WHERE TO_CHAR(e."Added_Date",'YYYY') = '{0}'
GROUP BY TO_CHAR(e."Added_Date",'YYYY'), p."Program_Name" 
ORDER BY COUNT(e."Enrollment_Id") DESC LIMIT 5;
'''

for date in dates_y:
    with engine.connect() as c:
        c.execute(sql_update.format(date))


# Create demographic tables
with engine.connect()as c:
    sql = '''
UPDATE clients
SET "Race" = 'Unknown'
WHERE "Race" IN ('Client Refused', 'Data Not Collected',
'Client doesn''t Know')
OR"Race" IS NULL;

DROP VIEW IF EXISTS yearly_race CASCADE;

CREATE VIEW yearly_race AS
SELECT TO_CHAR(e."Added_Date",'YYYY') Date, c."Race", COUNT(distinct e."Client_Id") Num_People_Enroll
FROM enrollment e
LEFT JOIN clients c
ON e."Client_Id" = c."Client_Id"
WHERE TO_CHAR(e."Added_Date",'YYYY') > '2014'
GROUP BY TO_CHAR(e."Added_Date",'YYYY'), c."Race"
ORDER BY TO_CHAR(e."Added_Date",'YYYY'), COUNT(e."Enrollment_Id");

UPDATE clients
SET "Gender" = 'Unknown'
WHERE "Gender" IN ('Client doesn''t know', 'Client refused',
'Data not collected')
OR "Gender" IS NULL;

DROP VIEW IF EXISTS yearly_gender CASCADE;

CREATE VIEW yearly_gender AS
SELECT TO_CHAR(e."Added_Date",'YYYY') Date, c."Gender", COUNT(distinct e."Client_Id") Num_People_Enroll
FROM enrollment e
LEFT JOIN clients c
ON e."Client_Id" = c."Client_Id"
WHERE TO_CHAR(e."Added_Date",'YYYY') > '2014'
GROUP BY TO_CHAR(e."Added_Date",'YYYY'), c."Gender"
ORDER BY TO_CHAR(e."Added_Date",'YYYY'), COUNT(distinct e."Client_Id");


DROP VIEW IF EXISTS yearly_age;
CREATE VIEW yearly_age AS
SELECT TO_CHAR(e."Added_Date",'YYYY') "Date",
((e."Added_Date"::date - c."Birth_Date"::date)/365) "Age"
FROM enrollment e
LEFT JOIN 
clients c 
ON e."Client_Id" = c."Client_Id"
WHERE TO_CHAR(e."Added_Date",'YYYY') > '2014'
and c."Birth_Date" is not null
ORDER BY "Date", "Age";
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



# Create view for number of unique individuals to programs per year where the client was homeless on entry
from sqlalchemy import text
sql_homeless = text('''
DROP VIEW IF EXISTS yearly_enroll_homeless CASCADE;

CREATE VIEW yearly_enroll_homeless AS
SELECT DISTINCT TO_CHAR("Added_Date", 'YYYY') "Date",
COUNT(distinct "Client_Id") "Num_Homeless"
FROM enrollment
WHERE ("Housing_Status" LIKE '%Category 1%' OR
"Prior_Residence" = 'Emergency Shelter, including hotel/motel paid for with voucher'
OR "Prior_Residence" = 'Hospital or other residential non-psychiatric medical facility'
OR "Prior_Residence" = 'Place not meant for habitation'
OR "Prior_Residence" = 'Psychiatric hospital or other psychiatric facility'
OR "Prior_Residence" = 'Transitional housing for homeless persons')
AND TO_CHAR("Added_Date", 'YYYY') > '2014'
GROUP BY "Date"
ORDER BY "Date" DESC;
''')


with engine.connect() as connection:
    connection.execute(sql_homeless)




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



with engine.connect() as c:
    sql= '''
ALTER TABLE num_active_yearly
ADD COLUMN total_act BIGINT;
UPDATE num_active_yearly 
SET "total_act" = "null_act" + "num_act";

ALTER TABLE num_active_monthly
ADD COLUMN total_act BIGINT;
UPDATE num_active_monthly
SET "total_act" = "null_act" + "num_act";
'''
    c.execute(sql)



#Pandas manipulation for quartiles needed for age box plot
sql = 'SELECT * FROM yearly_age'
con = engine.connect()
age = pd.read_sql(sql=sql, con=con)
for index,row in age.iterrows():
    if row[1] >= 100:
        age.drop([index], inplace=True)
        
years = ['2015','2016','2017','2018','2019']
age_stats = {}
for year in years:
    age_stats[year] = age.loc[age.Date == year].describe().T.values

age_df = pd.DataFrame(columns=['Count','Mean','std','Min','lower','median','upper','max','date'])
counter = 0
for key in age_stats:
    age_df.loc[counter] = np.append(age_stats[key][0],key)
    counter += 1
    
age_df.to_sql(name='yearly_age_table', if_exists='replace',index=False, con=con)


# Changed selecting from yearly age language due to new column names 

with engine.connect() as c:
    sql= '''
DROP TABLE if exists monthly_flow;
SELECT A."num_in", 
B."num_out",
C."total_act", C."act_date",
D."num_ph", 
E."Percent" 
INTO monthly_flow
FROM monthly_in A FULL JOIN monthly_out B ON A."to_char" = B."to_char"
FULL JOIN num_active_monthly C on A."to_char" = C."act_date"
FULL JOIN num_to_ph D on D."month_exit" = A."to_char"
FULL JOIN percent_ph_mo E ON E."Date" = D."month_exit"
WHERE A."num_in" IS NOT NULL
ORDER BY "act_date" DESC;

DROP TABLE if exists yearly_flow;
SELECT A."num_in", 
B."num_out",
C."total_act", C."act_date",
D."num_exit",
E."Avg_Time_to_PH", 
F."Percent"
INTO yearly_flow
FROM yearly_in A FULL JOIN yearly_out B ON A."date" = B."to_char"
FULL JOIN num_active_yearly C ON A."date" = C."act_date"
FULL JOIN yearly_to_ph D ON A."date" = D."date"
FULL JOIN avg_to_ph E ON E."Date" = A."date"
FULL JOIN percent_ph_yr F ON F."Date"=A."date"
ORDER BY "act_date" DESC;

DROP TABLE if exists demographics;
WITH race AS
(
SELECT ROW_NUMBER() OVER(ORDER BY "date") AS ROWNUM, * FROM yearly_race
),
gender AS
(
SELECT ROW_NUMBER() OVER (ORDER BY "date") AS ROWNUM, * FROM yearly_gender
),
age as 
(
SELECT ROW_NUMBER() OVER (ORDER BY "date") AS ROWNUM, * FROM yearly_age_table
),
progs as 
(
SELECT ROW_NUMBER() OVER (ORDER BY "Date") AS ROWNUM, * FROM top_5_programs
)
SELECT 
A."Race", A."num_people_enroll" race_enroll, A."date" RDate,
B."Gender", B."num_people_enroll" gender_enroll, B."date" GDate,
D."Count", D."Min", D."lower",D."median",D."upper", D."max", D."date" ADate,
E."Program", E."Num_Enroll" prog_enroll, E."Date" PDate
INTO demographics 
FROM race A 
FULL JOIN gender B ON A.ROWNUM = B.ROWNUM
FULL JOIN age D on A.ROWNUM = D.ROWNUM
FULL JOIN progs E on A.ROWNUM = E.ROWNUM;
    '''
    c.execute(sql)


# Make projection for end of 2019 data for comparison in yearly activity chart
# Simple approach  just using means of previous corresponding months of data for in and out
# Projections for active is tricker to get, so just assumes 5% growth in active participants based on 2018 growth

# Monthly table data manipulation 
con = engine.connect()
sql = 'SELECT * FROM monthly_flow'
monthly = pd.read_sql(sql=sql,con=con)
replace_dates = ['2019-09','2019-10','2019-11','2019-12']
monthly['month'] = monthly['act_date'].apply(lambda x : str(x).split('-')[1])
monthly.set_index(monthly.act_date, inplace=True)
for date in replace_dates:
    monthly.loc[date,'num_in'] = int(monthly.loc[monthly.month==date.split('-')[1],'num_in'].mean())
    monthly.loc[date,'num_out'] = int(monthly.loc[monthly.month==date.split('-')[1],'num_out'].mean())
    monthly.loc[date,'total_act'] = int(monthly.loc[monthly.month==date.split('-')[1],'total_act'].mean())
    monthly.loc[date,'num_ph'] = int(monthly.loc[monthly.month==date.split('-')[1],'num_ph'].mean())
    monthly.loc[date,'Percent'] = (monthly.loc[date,'num_ph'] / monthly.loc[date,'num_out'])*100
    monthly.loc[date,'act_date'] = date
    

monthly.reset_index(drop=True, inplace=True)
monthly['date'] = pd.to_datetime(monthly['act_date'])
monthly.sort_values('date', inplace=True, ascending=False)

# Yearly flow data table manipulation 
sql = 'SELECT * FROM yearly_flow'
yearly = pd.read_sql(sql=sql,con=con)
yearly.loc[yearly.act_date=='2019','num_in'] = monthly.loc[monthly.date.dt.year==2019,'num_in'].sum()
yearly.loc[yearly.act_date=='2019','num_out'] = monthly.loc[monthly.date.dt.year==2019,'num_out'].sum()
yearly.loc[yearly.act_date=='2019','total_act'] = 22001 

# Write manuipulated dataframes back to db 
yearly.to_sql(name='yearly_flow', con=con, if_exists='replace', index=False)
# Drop created columns needed for making predictions for last months of 2019 
monthly.drop(columns=['date', 'month'], inplace=True)
monthly.to_sql(name='monthly_flow', con=con, if_exists='replace', index=False)