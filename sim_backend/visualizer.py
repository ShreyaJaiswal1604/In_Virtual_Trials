import plotly.graph_objects as go

def plot_temperature(curve: dict) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=list(curve.keys()),
        y=[v["value"] for v in curve.values()],
        mode="lines+markers"
    ))
    fig.update_layout(
        title="Body Temperature Over Time",
        xaxis_title="Day",
        yaxis_title="Temperature (°C)"
    )
    return fig

def plot_activity_loss(loss: dict) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=list(loss.keys()),
        y=[v["value"] for v in loss.values()]
    ))
    fig.update_layout(
        title="Activity Loss Evaluation",
        xaxis_title="Metric",
        yaxis_title="Value"
    )
    return fig
