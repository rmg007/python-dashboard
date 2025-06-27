# Permit Dashboard

A scalable Dash dashboard for visualizing permit data with real-time filtering capabilities and customizable layouts.

## Features

- **Interactive Visualizations**: Time series charts, status distribution, and data tables
- **Drag-and-Drop Interface**: Customize your dashboard layout by dragging and resizing components
- **Persistent Layouts**: Your dashboard layout is saved automatically and restored on your next visit
- **Responsive Design**: Works on desktop and tablet devices
- **Real-time Filtering**: Filter data by year, month, and department

## Project Structure

```
permit_dashboard/
├── app.py                 # Main application entry point
├── config.py             # Configuration settings
├── data/                 # Database and data files
│   └── app.db           # SQLite database
├── db/                   # Database related code
│   ├── connection.py    # Database connection and utilities
│   ├── migrations/      # Database migration scripts
│   └── queries.py       # SQL queries and data access
├── layout/               # Layout components
│   ├── base.py          # Main layout structure
│   └── sidebar.py       # Sidebar component
├── components/           # Reusable UI components
│   ├── kpis.py          # KPI cards component
│   ├── charts.py        # Chart components
│   ├── datatable.py     # Data table component
│   ├── draggable.py     # Draggable grid component
│   └── placeholders.py  # Placeholder components
├── callbacks/           # Dash callbacks
│   ├── kpi_callbacks.py
│   ├── visual_callbacks.py
│   └── layout_callbacks.py
├── tests/               # Test files
│   └── test_layout_logic.py
└── requirements.txt     # Python dependencies
│   └── placeholders.py
├── assets/
│   └── custom.css
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd permit-dashboard
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python -c "from db.connection import init_db; init_db()"
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://127.0.0.1:8050/`

## Usage

### Dashboard Navigation
- Use the sidebar filters to filter the dashboard data by year, month, or department
- The dashboard will update automatically when filters change

### Customizing Layout
- **Drag and Drop**: Click and hold on any dashboard component to move it
- **Resize**: Drag the bottom-right corner of any component to resize it
- **Save Layout**: Click the "Save Layout" button to save your current layout
- **Reset Layout**: Click the "Reset Layout" button to restore the default layout

### Layout Persistence
- Your dashboard layout is automatically saved to the database
- The layout will be restored the next time you visit the dashboard
- Each user gets their own personalized layout

## Development

The application uses a modular architecture where:
- Layout components are in the `layout/` directory
- UI components are in the `components/` directory
- Database operations are in the `db/` directory
- Custom styles can be added in `assets/custom.css`

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run tests with coverage report
pytest --cov=./ tests/
```

### Code Style

This project uses:
- Black for code formatting
- Flake8 for linting
- isort for import sorting
- mypy for type checking

Run the following commands before committing:
```bash
black .
isort .
flake8
mypy .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Dash](https://dash.plotly.com/) and [Plotly](https://plotly.com/)
- UI components from [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)
- Drag and drop functionality with [dash-draggable](https://github.com/pb111/dash-draggable)
