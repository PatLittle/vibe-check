import pandas as pd
from datetime import datetime
import os

# Source data from the provided URL
data_url = "https://open.canada.ca/data/dataset/2916fad5-ebcc-4c86-b0f3-4f619b29f412/resource/8353523a-8e4e-4cd0-a91e-b42abe2e6ee5/download/dataset-ratings-timeseries.csv"

df = pd.read_csv(data_url)

# Convert 'date' column to just the date
df['date'] = pd.to_datetime(df['date']).dt.date
# Group by date to summarize
daily_summary = df.groupby('date').agg(
    total_ratings=('rating_eval', 'count'),
    average_rating=('rating_eval', 'mean'),
    unique_datasets=('uuid', 'nunique')
).reset_index()

# Round average_rating to 2 decimals
daily_summary['average_rating'] = daily_summary['average_rating'].round(2)

# Add overall average and 30-day moving averages for total_ratings
daily_summary['overall_avg_total_ratings'] = daily_summary['total_ratings'].mean().round(2)
daily_summary['30_day_avg_total_ratings'] = daily_summary['total_ratings'].rolling(30, min_periods=1).mean().round(2)
daily_summary['percentile_total_ratings'] = daily_summary['total_ratings'].rank(pct=True).round(2)

# Add overall average and 30-day moving averages for average_rating
daily_summary['overall_avg_rating'] = daily_summary['average_rating'].mean().round(2)
daily_summary['30_day_avg_rating'] = daily_summary['average_rating'].rolling(30, min_periods=1).mean().round(2)
daily_summary['percentile_average_rating'] = daily_summary['average_rating'].rank(pct=True).round(2)

# Reorder columns to group total_ratings-related columns together
column_order = [
    'date',
    'total_ratings',
    'overall_avg_total_ratings',
    '30_day_avg_total_ratings',
    'percentile_total_ratings',
    'average_rating',
    'overall_avg_rating',
    '30_day_avg_rating',
    'percentile_average_rating',
    'unique_datasets'
]
daily_summary = daily_summary[column_order]

# Define volumetric and quality descriptors
volume_descriptors = [
    "dead quiet", "very quiet", "pretty quiet", "low-key", "somewhat active",
    "getting there", "busy", "buzzing", "very lively", "off the charts"
]
quality_descriptors = [
    "rock bottom", "not great", "below average", "a bit off", "about average",
    "decent", "solid", "great", "top notch", "absolutely stellar"
]

# Function to bin percentiles and assign descriptors
def get_descriptor(percentile, descriptors):
    bin_index = min(int(percentile * 10), 9)  # Ensure index is between 0 and 9
    return descriptors[bin_index]

# Add narrative summary column
daily_summary['narrative_summary'] = daily_summary.apply(
    lambda row: f"Yesterday was {get_descriptor(row['percentile_total_ratings'], volume_descriptors)} and the vibes were {get_descriptor(row['percentile_average_rating'], quality_descriptors)}",
    axis=1
)

# Output CSV file
output_file = "daily_summary.csv"

# Append to CSV file
if not os.path.exists(output_file):
    # If file doesn't exist, include headers
    daily_summary.to_csv(output_file, index=False, mode='w')
else:
    # Append without headers
    daily_summary.to_csv(output_file, index=False, header=False, mode='a')

print("Daily summary appended to", output_file)
print(daily_summary)
