# Flask app for HMIS dashboard

from flask import Flask, jsonify, render_template


import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static')



url = os.environ['DATABASE_URL']

conn = psycopg2.connect(url, sslmode='require')



@app.route('/')
def home():
    return render_template('index.html')

#volume route
@app.route('/api/volume/<project_type>')
def get_volume_date(project_type):
    if ("'" in project_type) or (";" in project_type):
        return jsonify({'Message':'Table Dropped'})
    response = {'in':{},
                'in_dist':{},
                'out':{},
                'out_dist':{},
                'active':{},
                'active_dist':{}
    }
    if project_type == 'All':
        fill = 'volume_total'
    else:
        fill = '''volume_total_programs WHERE "project_type_group" = '{}' '''.format(project_type)
    sql = '''
    SELECT * from {} 
    '''.format(fill)
    with conn.cursor() as c:
        c.execute(sql)
        rs = c.fetchall()
        for r in rs:
            response['in'][r[0]] = r[3]
            response['in_dist'][r[0]] = r[4]
            response['out'][r[0]] = r[5]
            response['out_dist'][r[0]] = r[6]
            response['active'][r[0]] = r[1]
            response['active_dist'][r[0]] = r[2]

    return jsonify(response)


@app.route('/api/outcomes')
def get_outcomes_data():
    response = []
    with conn.cursor() as c:
        c.execute('''
        SELECT * FROM outcomes_sum_monthly
        ''')
        response.append(c.fetchall())
        
        c.execute('''
        SELECT * FROM outcomes_sum_yearly
        ''')
        response.append(c.fetchall())

    return jsonify(response)


@app.route('/api/demo/<year>/<project_type>')
def get_demo_data(year, project_type):
    if ("'" in project_type) or (";" in project_type):
        return jsonify({'Message':'Table Dropped'})
    if ("'" in year) or (";" in year):
        return jsonify({'Message':'Table Dropped'})
    response = {'age':{},
                    'race':{},
                    'sex':{}}
    if (year == "All") and (project_type != "All"):
        with conn.cursor() as c:
            c.execute('''
            select "Project_Type", "Age", sum("Num_Clients")
            from age_prog
            where "Project_Type" like '%{}%'
            group by "Project_Type","Age"
            '''.format(project_type))
            rs = c.fetchall()
            for r in rs:
                response['age'][r[1]] = int(r[2])
            c.execute('''
            select "Project_Type", "Race", sum("num_people_enroll")
            from yearly_race
            where "Project_Type" like '%{}%'
            group by "Project_Type","Race"
            '''.format(project_type))
            rs = c.fetchall()
            for r in rs:
                response['race'][r[1]] = int(r[2])
            c.execute('''
            select "Project_Type", "Gender", sum("num_people_enroll")
            from yearly_gender
            where "Project_Type" like '%{}%'
            group by "Project_Type","Gender"
            '''.format(project_type))
            rs = c.fetchall()
            for r in rs:
                response['sex'][r[1]] = int(r[2])

    if (year == "All") and (project_type == "All"):
        with conn.cursor() as c:
            c.execute('''
            select "Age", sum("Num_Clients") from age_no_prog
            group by "Age"
            ''')
            rs = c.fetchall()
            for r in rs:
                response['age'][r[0]] = int(r[1])
            c.execute('''
            select "Race",sum("num_people_enroll") from race_no_prog
            group by "Race"
            ''')
            rs = c.fetchall()
            for r in rs:
                response['race'][r[0]] = int(r[1])
            c.execute('''
            select "Gender",sum("num_people_enroll") from gender_no_prog
            group by "Gender"
            ''')
            rs = c.fetchall()
            for r in rs:
                response['sex'][r[0]] = int(r[1])

    if (project_type == 'All') and (year != "All"):
        with conn.cursor() as c:
            c.execute('''SELECT * FROM age_no_prog where "Date" = '{}' '''.format(year))
            rs = c.fetchall()
            for r in rs:
                response['age'][r[1]] = r[2] 
            c.execute('''SELECT * FROM gender_no_prog where "date" = '{}' '''.format(year))
            rs = c.fetchall()
            for r in rs:
                response['sex'][r[1]] = r[2]
            c.execute('''SELECT * FROM race_no_prog where "date" = '{}' '''.format(year))
            rs = c.fetchall()
            for r in rs:
                response['race'][r[1]] = r[2]

    else:
        with conn.cursor() as c:
            c.execute('''SELECT * FROM age_prog where "Date" = '{}' and "Project_Type" = '{}' '''.format(year, project_type))
            rs = c.fetchall()
            for r in rs:
                response['age'][r[2]] = r[3] 
            c.execute('''SELECT * FROM yearly_gender where "date" = '{}' and "Project_Type" = '{}' '''.format(year, project_type))
            rs = c.fetchall()
            for r in rs:
                response['sex'][r[2]] = r[3]
            c.execute('''SELECT * FROM yearly_race where "date" = '{}' and "Project_Type" = '{}' '''.format(year, project_type))
            rs = c.fetchall()
            for r in rs:
                response['race'][r[2]] = r[3]

        
    return response

@app.route('/api/source')
def get_source():
    responce = {}
    responce['clients'] = pd.read_sql('Select * from clients', con=conn).to_json(orient='split', index=False)
    responce['assessment'] = pd.read_sql('Select * from assessment', con=conn).to_json(orient='split', index=False)
    responce['programs'] = pd.read_sql('Select * from programs', con=conn).to_json(orient='split', index=False)
    responce['enrollment'] = pd.read_sql('Select * from enrollment', con=conn).to_json(orient='split', index=False)
    responce['exit_screen'] = pd.read_sql('Select * from exit_screen', con=conn).to_json(orient='split', index=False)
    responce['destinations'] = pd.read_sql('Select * from destinations', con=conn).to_json(orient='split', index=False)
   
    return jsonify(responce)

# Demographic data

if __name__ == "__main__":
    app.run(debug=False)



