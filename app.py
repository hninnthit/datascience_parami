import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Colors
st.markdown("""
    <style>
    .stApp {
        background-color: #a9cfb0;  /* light green background */
    }
    </style>
""", unsafe_allow_html=True)

def load_data(filename):
    return pd.read_csv(filename)
df = load_data("films.csv")  

# --- Normalize column names ---
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# --- App Title ---
st.title("Film Dataset Visualization")
st.write("Explore your film dataset with interactive filters and charts.")

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")

# Filter by main_genre with "All" option
if 'main_genre' in df.columns:
    main_genres = df['main_genre'].dropna().unique().tolist()
    main_genres.sort()
    main_genres.insert(0, "All")
    selected_main_genre = st.sidebar.selectbox("Select Genre", main_genres)
    if selected_main_genre == "All":
        df_filtered = df.copy()
    else:
        df_filtered = df[df['main_genre'] == selected_main_genre]
else:
    df_filtered = df.copy()

# Filter by year
if 'year' in df.columns:
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    selected_year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))
    df_filtered = df_filtered[
        (df_filtered['year'] >= selected_year_range[0]) &
        (df_filtered['year'] <= selected_year_range[1])
    ]
# Debug: show filtered data
st.write("Filtered Data Preview:", df_filtered.head())
st.write("Number of rows after filter:", len(df_filtered))

def clean_censor(x):
    if pd.isna(x):
        return "Unknown"
    x = x.strip().upper()
    if x in ["U", "G"]:
        return "All Ages"
    elif x in ["UA", "PG", "PG-13"]:
        return "Parental Guidance"
    elif x in ["A", "R"]:
        return "Adults Only"
    else:
        return "Unknown"

df_filtered['censor_group'] = df_filtered['censor'].apply(clean_censor)

# --- Chart 1: Top 10 Highest Rated Movies ---
if 'rating' in df_filtered.columns and 'movie_title' in df_filtered.columns and len(df_filtered) > 0:
    st.subheader("Top 10 Highest Rated Movies")
    top10 = df_filtered.nlargest(10, 'rating')
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(x='rating', y='movie_title', data=top10, ax=ax, color='skyblue')
    ax.set_xlabel("Rating")
    ax.set_ylabel("Movie Title")
    st.pyplot(fig)

# --- Chart 2: Average Rating by Year ---
if 'year' in df_filtered.columns and 'rating' in df_filtered.columns and len(df_filtered) > 0:
    st.subheader("Average Rating by Year (Interactive)")
    year_avg = df_filtered.groupby('year')['rating'].mean().reset_index()
    fig = px.line(
        year_avg,
        x='year',
        y='rating',
        markers=True,
        title="Average Rating by Year",
        labels={'year':'Year', 'rating':'Average Rating'},
        hover_data={'year':True, 'rating':':.2f'},
        color_discrete_sequence=['skyblue']
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Chart 3: Runtime Distribution ---
if 'runtime_(mins)' in df_filtered.columns and len(df_filtered) > 0:
    st.subheader("Runtime Distribution")
    fig3, ax3 = plt.subplots(figsize=(8,5))
    ax3.hist(df_filtered['runtime_(mins)'].dropna(), bins=25, color='skyblue', edgecolor='black')
    ax3.set_xlabel("Runtime (minutes)")
    ax3.set_ylabel("Number of Movies")
    st.pyplot(fig3)

# --- Chart 4: Interactive Total Gross vs Rating ---
if (
    'rating' in df_filtered.columns
    and 'total_gross' in df_filtered.columns
    and len(df_filtered) > 0
):
    st.subheader("Total Gross by Rating (Interactive)")

    # Step 1: Convert total_gross to numeric (millions USD)
    def parse_gross(x):
        try:
            x = str(x)
            x = x.replace("$", "").replace("M", "").replace(",", "").strip()
            return float(x)
        except:
            return None

    df_filtered['total_gross_millions'] = df_filtered['total_gross'].apply(parse_gross)

    # Step 2: Remove rows where gross is missing
    df_plot = df_filtered.dropna(subset=['total_gross_millions'])

    # Step 3: Round values for readability
    df_plot['total_gross_millions'] = df_plot['total_gross_millions'].round(1)

    # Step 4: Create interactive scatter plot
    fig = px.scatter(
        df_plot,
        x="rating",
        y="total_gross_millions",
        hover_name="movie_title",
        labels={
            "rating": "Rating",
            "total_gross_millions": "Total Gross (Millions USD)"
        },
        title="Total Gross by Rating",
        color_discrete_sequence=["skyblue"]
    )

    st.plotly_chart(fig, use_container_width=True)


# --- Chart 5: Rating Distribution by Censor Group (Interactive) ---
if 'censor_group' in df_filtered.columns and 'rating' in df_filtered.columns and len(df_filtered) > 0:
    st.subheader("Rating Distribution by Censor Group")

    import plotly.express as px

    fig = px.box(
        df_filtered,
        x="censor_group",
        y="rating",
        points="outliers",  # show only outliers for clarity
        color_discrete_sequence=["skyblue"],
        labels={
            "censor_group": "Censor Group",
            "rating": "Rating"
        },
        title="Rating Distribution by Censor Group"
    )

    st.plotly_chart(fig, use_container_width=True)
