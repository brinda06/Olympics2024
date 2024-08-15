from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)

# Directory to save plots
PLOT_DIR = "static/plots"
if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

def save_plot(plot_func, filename):
    path = os.path.join(PLOT_DIR, filename)
    plot_func()
    plt.savefig(path)
    plt.close()

@app.route('/')
def index():
    # Load datasets
    athlete_bio_df = pd.read_csv('F:/CODE/olymics 2024/data/Olympic_Athlete_Bio.csv')
    medal_tally = pd.read_csv('F:/CODE/olymics 2024/data/Olympic_Games_Medal_Tally.csv')
    country_info = pd.read_csv('F:/CODE/olymics 2024/data/Olympics_Country.csv')
    athlete_event_results = pd.read_csv('F:/CODE/olymics 2024/data/Olympic_Athlete_Event_Results.csv')

    # 1. Male and Female Participation
    def plot_participation_by_gender():
        participation_by_gender = athlete_bio_df['sex'].value_counts().reset_index()
        participation_by_gender.columns = ['Gender', 'Number of Athletes']
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Gender', y='Number of Athletes', data=participation_by_gender)
        plt.title('Male and Female Participation in Olympics')
        plt.xlabel('Gender')
        plt.ylabel('Number of Athletes')

    save_plot(plot_participation_by_gender, 'participation_by_gender.png')

    # 2. Medals by Country in Each Continent
    continent_mapping = {
        'Africa': ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cameroon', 'Cape Verde', 'Central African Republic', 'Chad', 'Comoros', 'Congo'],
        'Asia': ['Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan', 'Brunei', 'Cambodia', 'China', 'Cyprus', 'Georgia', 'India', 'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 'Maldives', 'Mongolia', 'Myanmar', 'Nepal', 'North Korea', 'Oman', 'Pakistan', 'Palestine', 'Philippines', 'Qatar', 'Saudi Arabia', 'Singapore', 'South Korea', 'Sri Lanka', 'Syria', 'Tajikistan', 'Thailand', 'Timor-Leste', 'Turkmenistan', 'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen'],
        'Europe': ['Albania', 'Andorra', 'Armenia', 'Austria', 'Azerbaijan', 'Belarus', 'Belgium', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Georgia', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Israel', 'Italy', 'Kosovo', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'North Macedonia', 'Norway', 'Poland', 'Portugal', 'Romania', 'Russia', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Turkey', 'Ukraine', 'United Kingdom', 'Vatican City'],
        'North America': ['Antigua and Barbuda', 'Bahamas', 'Barbados', 'Belize', 'Canada', 'Costa Rica', 'Cuba', 'Dominica', 'Dominican Republic', 'El Salvador', 'Grenada', 'Guatemala', 'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Trinidad and Tobago', 'United States'],
        'Oceania': ['Australia', 'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Nauru', 'New Zealand', 'Palau', 'Papua New Guinea', 'Samoa', 'Solomon Islands', 'Tonga', 'Tuvalu', 'Vanuatu'],
        'South America': ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Guyana', 'Paraguay', 'Peru', 'Suriname', 'Uruguay', 'Venezuela']
    }

    country_info['Continent'] = country_info['country'].map(
        {country: continent for continent, countries in continent_mapping.items() for country in countries})

    medal_tally_with_continent = pd.merge(medal_tally, country_info, left_on='country_noc', right_on='noc')
    medals_by_continent_country = medal_tally_with_continent.groupby(['Continent', 'country_y'])['total'].sum().reset_index()

    continents = medals_by_continent_country['Continent'].unique()
    for continent in continents:
        def plot_medals_by_country_in_continent(continent=continent):
            plt.figure(figsize=(12, 6))
            continent_data = medals_by_continent_country[medals_by_continent_country['Continent'] == continent]
            sns.barplot(x='country_y', y='total', data=continent_data)
            plt.title(f'Medals by Country in {continent}')
            plt.xlabel('Country')
            plt.ylabel('Number of Medals')
            plt.xticks(rotation=90)
        
        save_plot(plot_medals_by_country_in_continent, f'medals_by_country_{continent.lower().replace(" ", "_")}.png')

    # 3. Age Distribution by Gender
    def plot_age_distribution_by_gender():
        athlete_bio_df['born'] = pd.to_datetime(athlete_bio_df['born'], errors='coerce')
        current_year = pd.Timestamp.now().year
        athlete_bio_df['age'] = current_year - athlete_bio_df['born'].dt.year
        plt.figure(figsize=(12, 6))
        sns.histplot(data=athlete_bio_df, x='age', hue='sex', multiple='stack', bins=30)
        plt.title('Age Distribution by Gender')
        plt.xlabel('Age')
        plt.ylabel('Number of Athletes')

    save_plot(plot_age_distribution_by_gender, 'age_distribution_by_gender.png')

    # 4. Top 5 Events for Men Based on Medal Count
    def plot_top_5_events_men():
        athlete_event_results_with_gender = pd.merge(athlete_event_results, athlete_bio_df[['athlete_id', 'sex']], on='athlete_id')
        medals_by_event_gender = athlete_event_results_with_gender.groupby(['event', 'sex'])['medal'].count().reset_index()
        top_5_events_men = medals_by_event_gender[medals_by_event_gender['sex'] == 'Male'].nlargest(5, 'medal')
        plt.figure(figsize=(12, 6))
        sns.barplot(x='event', y='medal', data=top_5_events_men)
        plt.title('Top 5 Events for Men Based on Medal Count')
        plt.xlabel('Event')
        plt.ylabel('Number of Medals')
        plt.xticks(rotation=90)

    save_plot(plot_top_5_events_men, 'top_5_events_men.png')

    # 5. Top 5 Events for Women Based on Medal Count
    def plot_top_5_events_women():
        athlete_event_results_with_gender = pd.merge(athlete_event_results, athlete_bio_df[['athlete_id', 'sex']], on='athlete_id')
        medals_by_event_gender = athlete_event_results_with_gender.groupby(['event', 'sex'])['medal'].count().reset_index()
        top_5_events_women = medals_by_event_gender[medals_by_event_gender['sex'] == 'Female'].nlargest(5, 'medal')
        plt.figure(figsize=(12, 6))
        sns.barplot(x='event', y='medal', data=top_5_events_women)
        plt.title('Top 5 Events for Women Based on Medal Count')
        plt.xlabel('Event')
        plt.ylabel('Number of Medals')
        plt.xticks(rotation=90)

    save_plot(plot_top_5_events_women, 'top_5_events_women.png')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
