# 🍜 Mai Shen Yun - Inventory Management Dashboard

A comprehensive, intelligent inventory management system built with Streamlit for restaurant operations. This dashboard provides real-time inventory tracking, predictive analytics, cost optimization, and actionable insights to streamline supply chain management.

![Dashboard](sample_dashboard.png)

## ✨ Features

### 📊 Executive Overview
- Real-time KPIs and metrics
- Critical inventory alerts
- Data quality monitoring
- Quick insights and recommendations
- System status dashboard

### 📦 Inventory Management
- Real-time inventory level tracking
- Stock status indicators (Low/Normal/Overstock)
- Automated reorder point calculations
- Interactive filtering and search
- Detailed inventory reports
- Downloadable CSV exports

### 📈 Advanced Analytics
- **Usage Trends**: Track ingredient consumption patterns over time
- **Seasonal Analysis**: Identify seasonal patterns with heatmaps
- **ABC Classification**: Prioritize inventory based on value
- **Correlation Analysis**: Discover relationships between ingredients
- Interactive visualizations with Plotly

### 🔮 Predictive Analytics
- Multiple forecasting methods:
  - Moving Average
  - Exponential Smoothing
  - Weighted Moving Average
  - Linear Regression
  - Ensemble (combines all methods)
- Demand forecasting
- Reorder date predictions
- What-if scenario analysis
- Forecast accuracy metrics (MAE, MAPE, RMSE)

### 💰 Cost Analysis & Optimization
- Cost breakdown by ingredient and category
- Economic Order Quantity (EOQ) analysis
- Spending trend analysis
- Waste & spoilage estimation
- ROI calculator for improvements
- Cost-saving recommendations

## 🛠️ Technology Stack

- **Framework**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly, Altair
- **Forecasting**: Prophet, scikit-learn, statsmodels
- **File Handling**: openpyxl (Excel), CSV

## 📁 Project Structure

```
mai-shen-yun/
├── app.py                          # Main dashboard entry point
├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── config.toml                # Streamlit configuration
├── data/
│   ├── raw/                       # Raw data files
│   │   ├── MSY Data - Ingredient.csv
│   │   ├── MSY Data - Shipment.csv
│   │   └── *_Data_Matrix.xlsx    # Monthly data
│   └── processed/                 # Processed data (generated)
├── src/
│   ├── data_loader.py            # Data loading and validation
│   ├── data_processor.py         # Data cleaning and transformation
│   ├── analytics.py              # Analytics functions
│   ├── predictions.py            # Forecasting models
│   └── visualizations.py         # Chart components
└── pages/                         # Multi-page app
    ├── 1_📊_Overview.py          # Executive dashboard
    ├── 2_📦_Inventory.py         # Inventory tracking
    ├── 3_📈_Analytics.py         # Trend analysis
    ├── 4_🔮_Predictions.py       # Forecasting
    └── 5_💰_Cost_Analysis.py     # Cost optimization
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/mai-shen-yun.git
   cd mai-shen-yun
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare your data**
   - Place your data files in the `data/raw/` directory
   - Required files:
     - `MSY Data - Ingredient.csv` (menu items and ingredient quantities)
     - `MSY Data - Shipment.csv` (shipment frequencies and quantities)
     - Monthly data matrices (Excel files)

4. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

5. **Access the dashboard**
   - Open your browser and navigate to `http://localhost:8501`

## 📊 Data Format

### Ingredient Data (MSY Data - Ingredient.csv)

```csv
Item name,braised beef used (g),Braised Chicken(g),Braised Pork(g),Egg(count),Rice(g),...
Beef Tossed Ramen,140,,,0.5,,1
Beef Fried Rice,100,,,1,350
...
```

### Shipment Data (MSY Data - Shipment.csv)

```csv
Ingredient,Quantity per shipment,Unit of shipment,Number of shipments,frequency
Beef,40,lbs,3,weekly
Chicken,40,lbs,2,weekly
...
```

### Monthly Data (Excel files)

Excel files containing monthly sales or usage data. Format should match the ingredient data structure.

## 🎯 Key Algorithms

### Inventory Optimization

**Reorder Point Calculation**
```
Reorder Point = (Lead Time × Average Daily Usage) + Safety Stock
```

**Economic Order Quantity (EOQ)**
```
EOQ = √((2 × Annual Demand × Ordering Cost) / Holding Cost)
```

**Safety Stock**
```
Safety Stock = (Max Daily Usage × Max Lead Time) - (Avg Daily Usage × Avg Lead Time)
```

### Forecasting Methods

1. **Moving Average**: Simple average of recent periods
2. **Exponential Smoothing**: Weighted average favoring recent data
3. **Weighted Moving Average**: Customizable weights for different periods
4. **Linear Regression**: Trend-based prediction
5. **Ensemble**: Combines multiple methods for robust forecasts

### ABC Classification

- **A items**: Top 20% (80% of value) - Tight control
- **B items**: Next 30% (15% of value) - Moderate control
- **C items**: Remaining 50% (5% of value) - Simple controls

## 📖 Usage Guide

### Navigation

Use the sidebar to navigate between different pages:

1. **📊 Overview**: Start here for a high-level summary
2. **📦 Inventory**: Monitor and manage stock levels
3. **📈 Analytics**: Explore trends and patterns
4. **🔮 Predictions**: View forecasts and reorder schedules
5. **💰 Cost Analysis**: Optimize spending and reduce costs

### Filtering and Search

- Use sidebar filters to focus on specific data segments
- Search bars allow quick ingredient lookup
- Date ranges can be adjusted for time-based analysis

### Exporting Data

- Download buttons are available on most pages
- Exports are in CSV format for easy analysis in Excel
- Reports include all filtered data

### Interpreting Alerts

- 🔴 **Red/Critical**: Immediate action required (low stock)
- 🟡 **Yellow/Warning**: Monitor closely (overstock, approaching reorder)
- 🟢 **Green/Normal**: Stock levels are healthy

## 🔧 Customization

### Adjusting Thresholds

Edit `src/data_processor.py` to modify:
- Reorder point calculations
- Safety stock multipliers
- Overstock thresholds

### Adding New Visualizations

Add new chart functions to `src/visualizations.py`:

```python
def plot_custom_chart(self, df: pd.DataFrame) -> go.Figure:
    # Your custom Plotly chart
    fig = go.Figure(...)
    return fig
```

### Custom Forecasting Models

Extend `src/predictions.py` with new forecasting methods:

```python
def custom_forecast(self, data: pd.Series, periods: int) -> pd.Series:
    # Your forecasting logic
    forecast = ...
    return forecast
```

## 📈 Performance Optimization

- **Caching**: Streamlit's `@st.cache_data` decorator is used extensively
- **Data Loading**: Files are loaded once and cached
- **Lazy Loading**: Pages load data only when accessed
- **Efficient Processing**: Pandas vectorized operations for speed

## 🐛 Troubleshooting

### Common Issues

1. **Module not found errors**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

2. **Data files not loading**
   - Check file paths in `data/raw/`
   - Verify file formats (CSV encoding, Excel version)

3. **Visualization not displaying**
   - Clear cache: Click menu → Clear cache
   - Refresh browser

4. **Performance issues**
   - Reduce forecast periods
   - Limit data to recent months
   - Close unused browser tabs

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 Future Enhancements

- [ ] Database integration (PostgreSQL/MySQL)
- [ ] User authentication and role-based access
- [ ] Email alerts for critical stock levels
- [ ] Mobile-responsive design
- [ ] Integration with POS systems
- [ ] Supplier management module
- [ ] Recipe cost calculator
- [ ] Multi-location support
- [ ] Advanced ML models (LSTM, ARIMA)
- [ ] Real-time data streaming

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Visualizations powered by [Plotly](https://plotly.com/)
- Forecasting using [Prophet](https://facebook.github.io/prophet/) and [scikit-learn](https://scikit-learn.org/)

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Email: support@maishenyu n.com
- Documentation: [Wiki](https://github.com/yourusername/mai-shen-yun/wiki)

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐

---

**Built with ❤️ for efficient restaurant inventory management**

Last Updated: 2025-11-08
Version: 1.0.0
