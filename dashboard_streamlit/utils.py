import plotly.graph_objects as go
import plotly.express as px

from config import *


threshold_choices = {
    'Risque optimal': round(DEF_THRESHOLD, 2),
    'Risque modéré': round(DEF_THRESHOLD + 0.1, 2),
    'Risque élevé': round(DEF_THRESHOLD + 0.2, 2),
    '': 0
}


def gauge_plot(probability, threshold):
    value = round(probability, 2) * 100
    percent = 0.15
    steps = [([0, max(0, threshold - percent)], (14, 67, 123)),
             ([threshold - percent, max(threshold - percent, threshold)], (71, 149, 196)),
             ([threshold, max(threshold, threshold + percent)], (224, 120, 95)),
             ([threshold + percent, max(threshold + percent, 1)], (135, 10, 36))]

    fig = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=value,
        mode="gauge+number+delta",
        title={'text': f""},
        delta={'reference': threshold * 100,
               'increasing': {'color': "rgb(135, 10, 36)"},
               'decreasing': {'color': "rgb(14, 67, 123)"}},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "forestgreen"},
               'steps': [{'range': [step[0][0] * 100, step[0][1] * 100], 'color': f'rgb{str(step[1])}'}
                         for step in steps if step[0][0] != step[0][1]],
               'threshold': {'line': {'color': "black", 'width': 8}, 'thickness': 0.75, 'value': threshold * 100}}))

    return fig


def feature_boxplot(data, feature, value, customer_id):
    fig = px.box(data, x=feature)
    fig.add_vline(x=value,
                  line_color="rgb(135, 10, 36)",
                  line_width=4,
                  annotation_text=f'Client #{customer_id}',
                  annotation_bgcolor="rgb(135, 10, 36)")

    fig.update_layout({
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)'
    })
    fig.layout.yaxis.color = 'black'
    fig.layout.xaxis.color = 'black'
    fig.update_xaxes(color='black')
    fig.update_yaxes(color='black')

    return fig
    
    
def convert_choice_to_threshold(choice):
    
    return threshold_choices[choice]
        

def convert_threshold_to_choice(threshold):
    
    return {v: k for k, v in threshold_choices.items()}[threshold]