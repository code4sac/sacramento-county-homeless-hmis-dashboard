# Flask app for HMIS dashboard

from flask import Flask, jsonify, render_template


import psycopg2
import pandas as pd 
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

url = os.environ['DATABASE_URL']

conn = psycopg2.connect(url, sslmode='require')


@app.route('/')
def home():
    
    return render_template('index.html')

# Add routes to pull table views
# Activity data
@app.route('/api')
def get_data():

    response = {'flow':{'yearly':{'in':{},
                                'out':{},
                                'active':{},
                                'distinct_active':{},
                                'distinct_in':{},
                                'distinct_out':{}},
                    'monthly':{'in':{},
                                'out':{},
                                'active':{}},
                    'top_5':{'2015':[],
                                '2016':[],
                                '2017':[],
                                '2018':[],
                                '2019':[],
                            None:[]}},
                'outcomes':{'yearly':{'exit_ph':{},
                                    'exit_all':{},
                                    'average':{},
                                    'percent_ph':{}
                                    },
                        'monthly':{'exit_ph':{},
                                    'exit_all':{},
                                    'percent_ph':{}}},
                'demo':{'age':{'2015':[],
                                '2016':[],
                                '2017':[],
                                '2018':[],
                                '2019':[],
                            None:[]},
                    'race':{'2015':[],
                                '2016':[],
                                '2017':[],
                                '2018':[],
                                '2019':[],
                            None: []},
                    'sex':{'2015':[],
                                '2016':[],
                                '2017':[],
                                '2018':[],
                                '2019':[],
                            None:[]}}
                    } 
                    
    with conn.cursor() as c:
        c.execute('Select * from yearly_flow')
        rs = c.fetchall()
        for r in rs:
            response['flow']['yearly']['in'][r[3]] = r[0]
            response['flow']['yearly']['out'][r[3]] = r[1]
            response['outcomes']['yearly']['exit_all'][r[3]] = r[1]
            response['outcomes']['yearly']['exit_ph'][r[3]] = r[4]
            response['outcomes']['yearly']['average'][r[3]] = int(r[5])
            response['flow']['yearly']['active'][r[3]] = r[2]
            response['outcomes']['yearly']['percent_ph'][r[3]]=int(r[6])
            response['flow']['yearly']['distinct_active'][r[3]] = r[7]
            response['flow']['yearly']['distinct_in'][r[3]] = r[8]
            response['flow']['yearly']['distinct_out'][r[3]] = r[9]
        c.execute('Select * from monthly_flow')
        rs = c.fetchall()
        for r in rs:
            response['flow']['monthly']['in'][r[3]] = r[0]
            response['flow']['monthly']['active'][r[3]] = r[2]
            response['flow']['monthly']['out'][r[3]] = r[1]
            response['outcomes']['monthly']['exit_all'][r[3]] = r[1]
            response['outcomes']['monthly']['exit_ph'][r[3]] = r[4]
            response['outcomes']['monthly']['percent_ph'][r[3]]=int(r[5])
        c.execute('Select * from demographics')
        rs = c.fetchall()
        for r in rs:
            response['demo']['age'][r[12]].append([r[7],r[8],r[9],r[10],r[11]])
            response['demo']['sex'][r[5]].append([r[3],r[4]])
            response['demo']['race'][r[2]].append([r[0],r[1]])
            response['flow']['top_5'][r[15]].append([r[13],r[14]])
            
    del response['demo']['age'][None]
    del response['demo']['sex'][None]
    del response['demo']['race'][None]
    del response['flow']['top_5'][None]
    
    return jsonify(response)



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
    app.run(debug=True)


