# Python Generators - Advanced Data Processing

## Project Overview

This project demonstrates advanced usage of Python generators for efficient handling of large datasets, batch processing, and memory-optimized computations. The implementation focuses on leveraging Python's `yield` keyword to create iterative data processing solutions that promote optimal resource utilization.

## Learning Objectives

- Master Python Generators for iterative data processing
- Handle Large Datasets with batch processing and lazy loading
- Simulate real-world data streaming scenarios
- Optimize performance using memory-efficient operations
- Integrate Python with SQL databases for dynamic data management

## Project Structure

```
python-generators-0x00/
├── seed.py                    # Database setup and data seeding
├── 0-stream_users.py         # Generator for streaming database rows
├── 1-batch_processing.py     # Batch processing with generators
├── 2-lazy_paginate.py        # Lazy pagination implementation
├── 4-stream_ages.py          # Memory-efficient aggregation
├── user_data.csv             # Sample data file
└── README.md                 # Project documentation
```

## Requirements

- Python 3.x
- MySQL Server
- mysql-connector-python package
- Understanding of generators and `yield` keyword
- Basic SQL and database knowledge

## Installation

1. Install required packages:
```bash
pip install mysql-connector-python
```

2. Set up MySQL database:
   - Ensure MySQL server is running
   - Update database credentials in `seed.py`

3. Create sample data file `user_data.csv` with columns: name, email, age

## Usage

### Task 0: Database Setup
```bash
python3 0-main.py
```

### Task 1: Stream Users
```bash
python3 1-main.py
```

### Task 2: Batch Processing
```bash
python3 2-main.py
```

### Task 3: Lazy Pagination
```bash
python3 3-main.py
```

### Task 4: Memory-Efficient Aggregation
```bash
python3 4-stream_ages.py
```

## Features

- **Database Integration**: Seamless MySQL integration with proper connection handling
- **Memory Efficiency**: Generators ensure minimal memory footprint for large datasets
- **Batch Processing**: Process data in configurable batch sizes
- **Lazy Loading**: Fetch data only when needed (pagination)
- **Real-time Streaming**: Stream data one record at a time
- **Aggregate Functions**: Calculate statistics without loading entire dataset

## Database Schema

### user_data Table
- `user_id`: Primary Key (UUID, Indexed)
- `name`: VARCHAR, NOT NULL
- `email`: VARCHAR, NOT NULL
- `age`: DECIMAL, NOT NULL

## Technical Implementation

Each task demonstrates specific generator patterns:

1. **Basic Streaming**: Single-row generator with database cursors
2. **Batch Processing**: Multi-record batching with filtering
3. **Pagination**: Offset-based lazy loading
4. **Aggregation**: Statistical calculations with generators

## Performance Benefits

- **Memory Efficient**: Process datasets larger than available RAM
- **Scalable**: Handle millions of records without performance degradation
- **Resource Optimized**: Minimal database connection overhead
- **Real-time Capable**: Stream processing for live data updates

## Author

Backend Software Engineering Student - ALX Program

## Repository

- **GitHub repository**: alx-backend-python
- **Directory**: python-generators-0x00