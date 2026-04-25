import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

class InteractiveCharts:
    """
    Decoupled visualization engine for generating Plotly-powered interactive charts.
    These charts can be serialized to JSON and served via FastAPI for frontend rendering.
    """
    
    @staticmethod
    def plot_forecast(historical_data: pd.DataFrame, forecast_data: pd.DataFrame, date_col: str, value_col: str) -> str:
        """
        Creates an interactive line chart showing historical data and future forecasts.
        """
        fig = go.Figure()

        # Historical data trace
        fig.add_trace(go.Scatter(
            x=historical_data[date_col],
            y=historical_data[value_col],
            mode='lines',
            name='Historical Revenue',
            line=dict(color='blue')
        ))

        # Forecast data trace
        fig.add_trace(go.Scatter(
            x=forecast_data[date_col],
            y=forecast_data['yhat'],
            mode='lines',
            name='Forecast',
            line=dict(color='orange', dash='dash')
        ))
        
        # Add confidence intervals if available
        if 'yhat_lower' in forecast_data.columns and 'yhat_upper' in forecast_data.columns:
            fig.add_trace(go.Scatter(
                x=pd.concat([forecast_data[date_col], forecast_data[date_col][::-1]]),
                y=pd.concat([forecast_data['yhat_upper'], forecast_data['yhat_lower'][::-1]]),
                fill='toself',
                fillcolor='rgba(255,165,0,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=False,
                name='Confidence Interval'
            ))

        fig.update_layout(
            title="Revenue Forecast",
            xaxis_title="Date",
            yaxis_title="Revenue",
            hovermode="x unified",
            template="plotly_white"
        )
        
        # Return as JSON string for frontend rendering
        return fig.to_json()

    @staticmethod
    def plot_clusters(df: pd.DataFrame, x_col: str, y_col: str, cluster_col: str) -> str:
        """
        Creates a scatter plot for store segmentation clusters.
        """
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=cluster_col,
            title="Store Performance Segmentation",
            labels={cluster_col: "Segment"},
            hover_data=df.columns,
            template="plotly_white"
        )
        return fig.to_json()

    @staticmethod
    def plot_feature_importance(importance_df: pd.DataFrame, feature_col: str, importance_val_col: str) -> str:
        """
        Creates a bar chart for feature importance (Drivers Analysis).
        """
        fig = px.bar(
            importance_df,
            x=importance_val_col,
            y=feature_col,
            orientation='h',
            title="Sales Drivers Importance",
            template="plotly_white"
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        return fig.to_json()
