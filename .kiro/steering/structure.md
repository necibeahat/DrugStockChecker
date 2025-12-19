# Project Structure

## Root Directory
```
├── .venv/                 # Python virtual environment
├── .git/                  # Git version control
├── .kiro/                 # Kiro IDE configuration and steering
└── data/                  # All data files and datasets
```

## Data Organization

### `/data/`
Primary data storage with source-based organization:

- **`Navlin News/`**: Pharmaceutical news data
  - `als_news_all.json` - Complete news dataset
  - `als_news_details_page_*.json` - Paginated detailed news records (001-009)
  
- **Drug shortage files**: Root-level shortage data
  - `drug_shortage_combined_*.json` - Timestamped combined shortage data

## Data File Conventions

### Naming Patterns
- **News data**: `als_news_*` prefix for neurology/ALS related content
- **Shortage data**: `drug_shortage_combined_YYYYMMDD_HHMMSS.json` with timestamp
- **Paginated files**: Sequential numbering with zero-padding (001, 002, etc.)

### File Organization Rules
- Source-specific subdirectories for different data providers
- Timestamped files for tracking data collection runs
- Separate summary and detailed data files
- Consistent JSON structure across all data files

## Key Data Fields
- **Geographic**: `countries`, `country_codes`, `regions`
- **Classification**: `therapeutic_areas`, `indications`, `keywords`
- **Temporal**: `date`, `scraped_at`, `date_reported`
- **Identification**: `id`, `product_name`, `ingredient`