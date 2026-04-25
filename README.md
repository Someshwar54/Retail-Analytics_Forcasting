# 📊 Retail Analytics & Forecasting System

A high-performance, full-stack analytical platform designed to provide actionable insights for retail operations. This system combines state-of-the-art Machine Learning models (Prophet, LightGBM) with a modern, interactive dashboard to forecast revenue, identify sales drivers, and segment stores.

## 🚀 Key Features

*   **📈 Time-Series Forecasting**: Powered by **Meta Prophet**, providing accurate revenue predictions with confidence intervals.
    *   *AI-Powered Insights*: Automated summaries that compare filtered views to global averages and identify seasonal drivers.
*   **⚡ Sales Driver Analysis**: Leverages **LightGBM** and **SHAP** to identify the most significant factors impacting revenue (e.g., store ratings, discounts, payment methods).
*   **🎯 Store Segmentation**: Uses **K-Means Clustering** to categorize stores into performance tiers (Premium Performers, Growth Potential, etc.).
*   **🧠 Model Explainability**: Dedicated SHAP interpretation engine that classifies features into "Profit Boosters" and "Profit Reducers" with plain-English explanations.
*   **🔍 Global Filtering**: Real-time filtering by **Time Range**, **Store**, and **Category** across all analytical modules.
*   **📊 Dynamic Visualizations**: Interactive Plotly charts with a global "Chart Type Switcher" (Bar, Line, Column, Scatter, Pie) that mutates views instantly without re-fetching data.

## 🛠️ Technology Stack

### Backend
*   **Framework**: FastAPI (Python 3.10+)
*   **Machine Learning**:
    *   `prophet`: For additive time-series forecasting.
    *   `lightgbm`: For high-performance gradient boosting.
    *   `shap`: For model transparency and feature importance.
    *   `scikit-learn`: For store segmentation (K-Means).
*   **Database**: PostgreSQL with SQLAlchemy ORM.
*   **Caching**: In-memory dictionary-based caching for analytical results.

### Frontend
*   **Framework**: Next.js 14 (React, TypeScript, App Router)
*   **Styling**: TailwindCSS with a premium "Glassmorphism" aesthetic.
*   **Charts**: Plotly.js for interactive, publication-quality visualizations.
*   **Icons**: Lucide React.

## 🏗️ Architecture

The system follows a **Modular Strategy Pattern** for Machine Learning:
*   `AnalyticsService`: A central hub that orchestrates different analytical strategies.
*   **Decoupled Models**: ML models are isolated from API logic, allowing for easy updates or replacement of forecasting/driver engines.
*   **State Management**: Real-time filter state is synchronized across components using modern React patterns.

## 🏁 Getting Started

### Prerequisites
*   Python 3.10+
*   Node.js 18+
*   PostgreSQL

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## 📸 Preview
![Retail Analytics Preview](https://raw.githubusercontent.com/placeholder-path/retail-analytics-preview.webp)

---
*Developed as a high-performance solution for retail decision-makers.*
