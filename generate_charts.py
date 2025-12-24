"""
Business Analytics Chart Generator for Temirci.az Marketplace
Generates business-focused visualizations for stakeholder presentations
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set style for professional business charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Load data
df = pd.read_csv('temirci_listings.csv')

# Data preprocessing
df['date_posted'] = pd.to_datetime(df['date_posted'])
df['year'] = df['date_posted'].dt.year
df['month'] = df['date_posted'].dt.to_period('M')
df['year_month'] = df['date_posted'].dt.strftime('%Y-%m')

# Extract numeric price values
df['price_numeric'] = df['price'].str.extract(r'(\d+)').astype(float)

print("Generating business analytics charts...")
print(f"Total listings analyzed: {len(df)}")

# ============================================
# Chart 1: Market Composition by Category
# ============================================
plt.figure(figsize=(14, 7))
category_counts = df['category'].value_counts()
colors = sns.color_palette("husl", len(category_counts))
bars = plt.barh(category_counts.index, category_counts.values, color=colors)
plt.xlabel('Number of Listings', fontsize=12, fontweight='bold')
plt.ylabel('Service Category', fontsize=12, fontweight='bold')
plt.title('Market Composition: Active Listings by Service Category', fontsize=14, fontweight='bold', pad=20)
for i, bar in enumerate(bars):
    width = bar.get_width()
    percentage = (width / len(df)) * 100
    plt.text(width, bar.get_y() + bar.get_height()/2,
             f' {int(width)} ({percentage:.1f}%)',
             va='center', fontweight='bold')
plt.tight_layout()
plt.savefig('charts/01_market_composition_by_category.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 1: Market Composition by Category")

# ============================================
# Chart 2: Average Engagement by Category
# ============================================
plt.figure(figsize=(14, 7))
avg_views = df.groupby('category')['views'].mean().sort_values(ascending=True)
colors = sns.color_palette("rocket", len(avg_views))
bars = plt.barh(avg_views.index, avg_views.values, color=colors)
plt.xlabel('Average Views per Listing', fontsize=12, fontweight='bold')
plt.ylabel('Service Category', fontsize=12, fontweight='bold')
plt.title('Customer Engagement: Average Views by Service Category', fontsize=14, fontweight='bold', pad=20)
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width, bar.get_y() + bar.get_height()/2,
             f' {int(width):,} views',
             va='center', fontweight='bold')
plt.tight_layout()
plt.savefig('charts/02_average_engagement_by_category.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 2: Average Engagement by Category")

# ============================================
# Chart 3: Geographic Market Distribution
# ============================================
plt.figure(figsize=(12, 6))
city_counts = df['city'].value_counts().head(10)
colors = sns.color_palette("viridis", len(city_counts))
bars = plt.bar(range(len(city_counts)), city_counts.values, color=colors)
plt.xlabel('City', fontsize=12, fontweight='bold')
plt.ylabel('Number of Active Listings', fontsize=12, fontweight='bold')
plt.title('Geographic Distribution: Service Provider Concentration by City', fontsize=14, fontweight='bold', pad=20)
plt.xticks(range(len(city_counts)), city_counts.index, rotation=45, ha='right')
for i, bar in enumerate(bars):
    height = bar.get_height()
    percentage = (height / len(df)) * 100
    plt.text(bar.get_x() + bar.get_width()/2, height,
             f'{int(height)}\n({percentage:.1f}%)',
             ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig('charts/03_geographic_market_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 3: Geographic Market Distribution")

# ============================================
# Chart 4: Platform Growth Over Time
# ============================================
plt.figure(figsize=(14, 7))
yearly_listings = df.groupby('year').size()
plt.plot(yearly_listings.index, yearly_listings.values, marker='o', linewidth=3, markersize=10, color='#2E86AB')
plt.fill_between(yearly_listings.index, yearly_listings.values, alpha=0.3, color='#2E86AB')
plt.xlabel('Year', fontsize=12, fontweight='bold')
plt.ylabel('New Listings Posted', fontsize=12, fontweight='bold')
plt.title('Platform Growth: Annual Listing Activity Trend', fontsize=14, fontweight='bold', pad=20)
plt.grid(True, alpha=0.3)
for x, y in zip(yearly_listings.index, yearly_listings.values):
    plt.text(x, y + 2, str(int(y)), ha='center', va='bottom', fontweight='bold', fontsize=11)
plt.tight_layout()
plt.savefig('charts/04_platform_growth_over_time.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 4: Platform Growth Over Time")

# ============================================
# Chart 5: Pricing Analysis by Top Categories
# ============================================
plt.figure(figsize=(14, 7))
top_categories = df['category'].value_counts().head(6).index
df_top = df[df['category'].isin(top_categories) & df['price_numeric'].notna()]
category_prices = df_top.groupby('category')['price_numeric'].agg(['mean', 'median']).sort_values('mean', ascending=False)

x = np.arange(len(category_prices))
width = 0.35
bars1 = plt.bar(x - width/2, category_prices['mean'], width, label='Average Price', color='#A23B72')
bars2 = plt.bar(x + width/2, category_prices['median'], width, label='Median Price', color='#F18F01')

plt.xlabel('Service Category', fontsize=12, fontweight='bold')
plt.ylabel('Price (AZN)', fontsize=12, fontweight='bold')
plt.title('Pricing Strategy: Average vs Median Prices in Top Service Categories', fontsize=14, fontweight='bold', pad=20)
plt.xticks(x, category_prices.index, rotation=45, ha='right')
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3, axis='y')

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height,
                 f'{int(height)} AZN',
                 ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/05_pricing_analysis_top_categories.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 5: Pricing Analysis by Top Categories")

# ============================================
# Chart 6: Engagement Distribution
# ============================================
plt.figure(figsize=(12, 6))
bins = [0, 1000, 2000, 3000, 5000, 10000, 30000]
labels = ['0-1K', '1K-2K', '2K-3K', '3K-5K', '5K-10K', '10K+']
df['view_range'] = pd.cut(df['views'], bins=bins, labels=labels, include_lowest=True)
view_distribution = df['view_range'].value_counts().sort_index()

colors = sns.color_palette("coolwarm", len(view_distribution))
bars = plt.bar(range(len(view_distribution)), view_distribution.values, color=colors)
plt.xlabel('View Range', fontsize=12, fontweight='bold')
plt.ylabel('Number of Listings', fontsize=12, fontweight='bold')
plt.title('Engagement Distribution: Listings by View Count Range', fontsize=14, fontweight='bold', pad=20)
plt.xticks(range(len(view_distribution)), view_distribution.index, rotation=0)

for i, bar in enumerate(bars):
    height = bar.get_height()
    percentage = (height / len(df)) * 100
    plt.text(bar.get_x() + bar.get_width()/2, height,
             f'{int(height)}\n({percentage:.1f}%)',
             ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/06_engagement_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 6: Engagement Distribution")

# ============================================
# Chart 7: Monthly Activity Trends
# ============================================
plt.figure(figsize=(16, 7))
monthly_activity = df.groupby('year_month').size().reset_index(name='count')
monthly_activity = monthly_activity.sort_values('year_month')

plt.plot(range(len(monthly_activity)), monthly_activity['count'],
         marker='o', linewidth=2, markersize=6, color='#06A77D')
plt.fill_between(range(len(monthly_activity)), monthly_activity['count'], alpha=0.2, color='#06A77D')
plt.xlabel('Month', fontsize=12, fontweight='bold')
plt.ylabel('New Listings', fontsize=12, fontweight='bold')
plt.title('Activity Trends: Monthly Listing Volume Over Time', fontsize=14, fontweight='bold', pad=20)
plt.xticks(range(0, len(monthly_activity), 6),
           monthly_activity['year_month'].iloc[::6], rotation=45, ha='right')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('charts/07_monthly_activity_trends.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 7: Monthly Activity Trends")

# ============================================
# Chart 8: Top Performing Listings
# ============================================
plt.figure(figsize=(14, 8))
top_listings = df.nlargest(15, 'views')[['title', 'views', 'category']].copy()
top_listings['short_title'] = top_listings['title'].str[:50] + '...'

colors_map = {cat: color for cat, color in zip(df['category'].unique(),
              sns.color_palette("Set2", len(df['category'].unique())))}
bar_colors = [colors_map[cat] for cat in top_listings['category']]

bars = plt.barh(range(len(top_listings)), top_listings['views'], color=bar_colors)
plt.yticks(range(len(top_listings)), top_listings['short_title'], fontsize=9)
plt.xlabel('Total Views', fontsize=12, fontweight='bold')
plt.ylabel('Listing', fontsize=12, fontweight='bold')
plt.title('Top Performers: 15 Most-Viewed Service Listings', fontsize=14, fontweight='bold', pad=20)

for i, bar in enumerate(bars):
    width = bar.get_width()
    category = top_listings.iloc[i]['category']
    plt.text(width, bar.get_y() + bar.get_height()/2,
             f' {int(width):,} views | {category}',
             va='center', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/08_top_performing_listings.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 8: Top Performing Listings")

# ============================================
# Chart 9: Category Performance Matrix
# ============================================
plt.figure(figsize=(14, 7))
category_stats = df.groupby('category').agg({
    'views': 'sum',
    'ad_id': 'count'
}).rename(columns={'ad_id': 'listings'})
category_stats['avg_views'] = df.groupby('category')['views'].mean()

top_cats = category_stats.nlargest(8, 'views')
x = np.arange(len(top_cats))
width = 0.35

fig, ax1 = plt.subplots(figsize=(14, 7))
color1 = '#E63946'
ax1.bar(x - width/2, top_cats['views']/1000, width, label='Total Views (thousands)', color=color1, alpha=0.7)
ax1.set_xlabel('Service Category', fontsize=12, fontweight='bold')
ax1.set_ylabel('Total Views (thousands)', fontsize=12, fontweight='bold', color=color1)
ax1.tick_params(axis='y', labelcolor=color1)
ax1.set_xticks(x)
ax1.set_xticklabels(top_cats.index, rotation=45, ha='right')

ax2 = ax1.twinx()
color2 = '#457B9D'
ax2.bar(x + width/2, top_cats['listings'], width, label='Number of Listings', color=color2, alpha=0.7)
ax2.set_ylabel('Number of Listings', fontsize=12, fontweight='bold', color=color2)
ax2.tick_params(axis='y', labelcolor=color2)

plt.title('Category Performance Matrix: Total Engagement vs Market Supply', fontsize=14, fontweight='bold', pad=20)
fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9), fontsize=11)
plt.tight_layout()
plt.savefig('charts/09_category_performance_matrix.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 9: Category Performance Matrix")

# ============================================
# Chart 10: Market Concentration Analysis
# ============================================
plt.figure(figsize=(12, 6))
baku_vs_others = pd.DataFrame({
    'Location': ['Baku (Capital)', 'Other Cities'],
    'Listings': [
        len(df[df['city'] == 'Bakı']),
        len(df[df['city'] != 'Bakı'])
    ]
})

colors = ['#FF6B6B', '#4ECDC4']
bars = plt.bar(baku_vs_others['Location'], baku_vs_others['Listings'], color=colors)
plt.ylabel('Number of Active Listings', fontsize=12, fontweight='bold')
plt.title('Market Concentration: Capital vs Regional Distribution', fontsize=14, fontweight='bold', pad=20)

for i, bar in enumerate(bars):
    height = bar.get_height()
    percentage = (height / len(df)) * 100
    plt.text(bar.get_x() + bar.get_width()/2, height,
             f'{int(height)}\n({percentage:.1f}%)',
             ha='center', va='bottom', fontweight='bold', fontsize=12)

plt.tight_layout()
plt.savefig('charts/10_market_concentration_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Chart 10: Market Concentration Analysis")

print("\n" + "="*60)
print("All business analytics charts generated successfully!")
print("Charts saved in: ./charts/")
print("="*60)
