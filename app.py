import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import dash
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

markdown_text = '''
The gender wage gap has been an issue discussed for centuries. According to [The Pew Research Center](https://www.pewresearch.org/fact-tank/2021/05/25/gender-pay-gap-facts/), women were making 36 cents less than their male counterparts in 1980. Fastforward 40 years and the gender wage gap is still an issue. The Pew Research Center has found that the gender wage gap has stabilized for the last 15 years and women now make about 16 cents less (another way to think about it is that women make 84% of men's salaries). That's much less compared to back in 1980, but still a significant and clear difference between the genders. A lot of reasearch has gone into why the gender wage gap exists. [Robin Bleiweis](https://www.americanprogress.org/article/quick-facts-gender-wage-gap/) mentions many possible reasons. For example, differences in industries or jobs worked, differences in experience, differences in hours worked, and discrimination are all factors that contribute to the gender wage gap. Although women have made great strides in combating many of these areas, The Pew Research Center concludes that "women as a whole continue to be overrepresented in lower-paying occupations relative to their share of the workforce". Thus the problem continues. 

To further explore the gender wage gap we use data from the 2019 General Social Survey (GSS).  Since 1972, this survey has been collecting information "on contemporary American society in order to monitor and explain trends in opinions, attitudes and behaviors" according to the [National Opinion Research Center](http://www.gss.norc.org/About-The-GSS). The National Opinion Research Center explains that the GSS collects data from the contemporary American through face-to-face interviews at the University of Chicago every other year. Some relevant variables of special interest that the GSS collects include the respondent's personal annual income, their occupational prestige score, their socioeconomic status, their years of education, and of course their demographic data - including sex. We know that all these variables impact the gender wage gap, but by how much and to what extent? 
'''

gss_display = gss_clean.groupby('sex').agg({'income':'mean',
                                            'job_prestige':'mean',
                                            'socioeconomic_index': 'mean',
                                            'education':'mean'})

# use more presentabnle column names
gss_display = gss_display.rename({'sex':'Sex',
                                   'income':'Avg. Income',
                                   'job_prestige':'Avg. Occupational Prestige',
                                   'socioeconomic_index':'Avg. Socioeconomic Index',
                                   'education':'Avg. Years of Education'}, axis=1)

# round to 2 decimal places
gss_display = round(gss_display, 2)
gss_display = gss_display.reset_index().rename({'sex':'Gender'}, axis=1)
table = ff.create_table(gss_display)

gss_plot = gss_clean.groupby(['sex', 'male_breadwinner']).size()
gss_plot = gss_plot.reset_index()
gss_plot = gss_plot.rename({0:'count'}, axis=1)
gss_plot

fig_bar = px.bar(gss_plot, x='male_breadwinner', y='count', color='sex', 
            labels={'male_breadwinner':'Level of Agreement', 'count':'Number of people'},
            barmode = 'group', text= 'count')
fig_bar.update_layout(showlegend=True)
fig_bar.update(layout=dict(title=dict(x=0.5)))


fig_scatter = px.scatter(gss_clean, x='job_prestige', y='income', 
                 color = 'sex', 
                 labels={'job_prestige':'Occupational Prestige', 
                         'income':'Income'},
                 hover_data=['education', 'socioeconomic_index'],
                 trendline="ols")
fig_scatter.update(layout=dict(title=dict(x=0.5)))

fig_box = px.box(gss_clean, x='sex', y = 'income',
                   labels={'sex':'', 'income':'Annual Income'})
fig_box.update(layout=dict())

fig_box2 = px.box(gss_clean, x='sex', y = 'job_prestige',
                   labels={'sex':'', 'job_prestige':'Occupational Prestige'})
fig_box2.update(layout=dict())

gss_new = gss_clean[['income','sex','job_prestige']]

# break job_presitge into six categories with equally sized ranges
gss_new['job_prestige_levels'] = pd.cut(gss_new['job_prestige'], 6, labels=["very low", "low", "medium low", "medium high", "high", "very high"])
gss_new.job_prestige_levels.unique()

# drop all rows with any missing values
gss_new = gss_new.dropna()

gss_new['job_prestige_levels'] = gss_new['job_prestige_levels'].astype('category')
gss_new['job_prestige_levels'] = gss_new['job_prestige_levels'].cat.reorder_categories(["very low", "low", "medium low", "medium high", "high", "very high"])

# create a facet grid
fig_grid = px.box(gss_new, x='sex', y = 'income',
            labels={'sex':'', 'income':'Income'},
            facet_col = 'job_prestige_levels',facet_col_wrap=2)

fig_grid.update(layout=dict(title=dict(x=0.5)))
fig_grid.for_each_annotation(lambda a: a.update(text=a.text.replace("job_prestige_levels=", "")))

ft_columns = ['satjob','relationship','male_breadwinner','men_bettersuited','child_suffer','men_overwork'] 
cat_columns = ['sex', 'region', 'education'] 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app2 = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app2.server

app2.layout = html.Div([

    html.Div([
        html.H1(children="Exploring the Gender Wage Gap with Data from the 2019 Gender Social Survey"),
        dcc.Markdown(markdown_text), 
    ], className='side_bar'),

    html.Div([
        html.Div([
            
            html.Div([
                html.H2("Comparing Male versus Female Responses"),
                dcc.Graph(figure=table)
            ], className='box', style={'margin': '10px', 'padding-top':'15px', 'padding-bottom':'15px'}),

            html.Div([
                html.Div([

                    html.Div([
            
                        html.H3("x-axis feature"),
                        dcc.Dropdown(id='x-axis',
                                    options=[{'label': i, 'value': i} for i in ft_columns],
                                    value='male_breadwinner'),
                        
                        html.H3("colors"),
                        dcc.Dropdown(id='color',
                                    options=[{'label': i, 'value': i} for i in cat_columns],
                                    value='sex')
                    ]),

                    html.Div([   
                       html.H2("Level of Agreement towards Male Breadwinners by Sex"),
                       dcc.Graph(id="graph")
                    ], className='box', style={'padding-bottom':'15px'}),


                    html.Div([
                        html.H2("Job Prestige vs. Income by Sex"),
                        dcc.Graph(figure=fig_scatter),
                    ], ),
               

                ], className='box'),


                html.Div([
                     html.Div([

                        html.Div([
                            html.H2("Distribution of Income by Sex"),
                            dcc.Graph(figure=fig_box),

                        ], className='box'),

                        html.Div([
                            html.H2("Distribution of Job Prestige by Sex"),
                            dcc.Graph(figure=fig_box2),
                        ], className='box'),

                     ]),     
       
                ], style={'width': '60%'}),           
            ], className='row'),
            
                    
        html.Div([ 
            html.H2("Distribution of Income by Sex for each Job Prestige Level"),
            dcc.Graph(figure=fig_grid)  
        ], className='box', style={'margin': '10px', 'padding-top':'15px', 'padding-bottom':'15px'}), 
        ], className='main'),

    ]),
    
])

@app2.callback(Output(component_id="graph",component_property="figure"), 
             [Input(component_id='x-axis',component_property="value"),
              Input(component_id='color',component_property="value")])

def make_figure(x, color):

    gss_plot = gss_clean.groupby([color, x]).size()
    gss_plot = gss_plot.reset_index()
    gss_plot = gss_plot.rename({0:'count'}, axis=1)

    return px.bar(gss_plot, x=x, y='count', color=color, 
            labels={x:'Level of Agreement', 'count':'Number of people'},
            barmode = 'group', text= 'count')
    
    
# run/create dashboard
if __name__ == '__main__':
    app2.run_server(debug=True)
