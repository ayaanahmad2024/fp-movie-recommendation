import pandas as pd

def load_movie_data(file_path):
    """Load and clean the IMDB movie data."""
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("❌ File not found. Check the file path.")
        return None

    # Normalize Genre field: make sure each genre is separately searchable
    df['Genre'] = df['Genre'].fillna('').apply(lambda g: [genre.strip() for genre in g.split(',')])

    # Drop rows with missing important data
    df = df.dropna(subset=['Rating', 'Year', 'Runtime (Minutes)', 'Genre', 'Votes'])

    return df

def load_oscar_data(file_path):
    """Load the Oscar dataset from a CSV."""
    try:
        oscar_df = pd.read_csv(file_path)
    except FileNotFoundError:
        print("❌ Oscar data file not found.")
        return None

    # Clean the Oscar dataset if needed (e.g., strip extra spaces)
    oscar_df['film'] = oscar_df['film'].str.strip()
    return oscar_df


def get_user_preferences(df):
    """Prompt user for movie preferences"""

    # Get unique list of genres from all movies
    all_genres = sorted(set(genre for genre_list in df['Genre'] for genre in genre_list))

    # Get user preference for genre (and make sure they input a genre existing in dataset)
    while True:
        genre = input("What genre are you in the mood for? (Action, Drama, Comedy, etc.): ").title()
        if genre == "":
            genre = None  # user skipped
            break
        elif genre in all_genres:
            break
        else:
            while True:
                see_genres = input(
                    "❌ Invalid genre. Would you like to see the list of available genres? (y/n): ").strip().lower()
                if see_genres == "y":
                    print("🎭 Available genres:")
                    print(", ".join(all_genres))
                    break
                elif see_genres == "n":
                    print("Okay, try typing your genre again.\n")
                    break
                else:
                    print("❌ Invalid response. Please type 'y' or 'n'.")

    # Validate numeric inputs
    def get_float_input(prompt, min_val=0.0, max_val=10.0):
        while True:
            val = input(prompt).strip()
            if val == "":  # user skipped
                return None
            try:
                val = float(val)
                if min_val <= val <= max_val:
                    return val
                else:
                    print(f"❌ Enter a number between {min_val} and {max_val}.")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")

    def get_int_input(prompt, min_val=None, max_val=None):
        while True:
            val = input(prompt).strip()
            if val == "":  # user skipped
                return None
            try:
                val = int(val)
                if (min_val is None or val >= min_val) and (max_val is None or val <= max_val):
                    return val
                else:
                    print("❌ Input out of range.")
            except ValueError:
                print("❌ Invalid input. Please enter an integer.")

    print("\n🎯 Now enter your filter preferences: (remember you can hit 'Enter' to skip): ")
    min_rating = get_float_input("Minimum IMDb rating (0.0 to 10.0): ", 0.0, 10.0)

    while True:
        min_year = get_int_input("Earliest release year (minimum 2006):", 2006, 2016)
        max_year = get_int_input("Latest release year (maximum 2016):", 2006, 2016)
        if min_year is None or max_year is None or min_year <= max_year:
            break
        else:
            print("❌ Earliest year must be less than or equal to latest year.\n")

    max_runtime = get_int_input("Maximum runtime in minutes (e.g. 120):", 50)

    # Get actor input
    fav_actor = input("Is there any actor or actress you really want to see? (Press Enter to skip): ").strip().title()

    return {
        "genre": genre if genre else None,
        "min_rating": min_rating,
        "min_year": min_year,
        "max_year": max_year,
        "max_runtime": max_runtime,
        "fav_actor": fav_actor
    }

def filter_movies(df, prefs):
    # Start with a mask that includes everything
    mask = pd.Series([True] * len(df))

    # Apply filters only if preferences are provided
    if prefs['genre']:
        mask &= df['Genre'].apply(lambda genres: prefs['genre'] in genres)
    if prefs['min_rating'] is not None:
        mask &= df['Rating'] >= prefs['min_rating']
    if prefs['min_year'] is not None:
        mask &= df['Year'] >= prefs['min_year']
    if prefs['max_year'] is not None:
        mask &= df['Year'] <= prefs['max_year']
    if prefs['max_runtime'] is not None:
        mask &= df['Runtime (Minutes)'] <= prefs['max_runtime']

    filtered_df = df[mask].copy()

    if prefs.get('fav_actor'):
        # Create boolean mask where actor is found in the movie
        actor_mask = filtered_df['Actors'].str.contains(prefs['fav_actor'], case=False, na=False)

        if not actor_mask.any():
            print(f"👀 No matches found with actor '{prefs['fav_actor']}' in the filtered results.")

        # Sort: actor matches to top, then by rating and votes
        sorted_df = filtered_df.sort_values(
            by=['Actors', 'Rating', 'Votes'],
            ascending=[False, False, False],
            key=lambda col: actor_mask if col.name == 'Actors' else col
        )
    else:
        # Default sort: by IMDb rating and vote count
        sorted_df = filtered_df.sort_values(by=['Rating', 'Votes'], ascending=False)

    return sorted_df


def check_oscar_status(movie_title, oscar_df):
    """Check if a movie has been nominated or won an Oscar, and for which category."""
    if oscar_df is not None:
        # Check if movie is in the Oscar dataset and has a winner status
        matched_rows = oscar_df[oscar_df['film'].str.contains(movie_title, case=False, na=False)]

        if not matched_rows.empty:
            oscar_info = []
            for _, row in matched_rows.iterrows():
                category = row['category']  # category from the dataset
                winner = row['winner']
                status = "Winner" if str(winner).strip().lower() == 'true' else "Nominated"
                oscar_info.append(f"{status} for {category}")

            return oscar_info  # Return a list of Oscar categories and statuses
    return None


def show_recommendations(recommendations, oscar_df, fav_actor=None):
    """Print top movie recommendations, allowing user to swap out ones they've already seen"""

    # Let user know if no matches found
    if recommendations.empty:
        print("\n😔 Sorry, no movies matched your criteria.")
        return

    top_matches = recommendations[['Title', 'Genre', 'Year', 'Rating', 'Runtime (Minutes)', 'Actors']].reset_index(
        drop=True)

    display_limit = min(5, len(top_matches))  # Handle fewer than 5 matches
    display_indices = list(range(display_limit))
    next_index = display_limit

    while True:
        print("\n🎥 Top Movie Recommendations:")
        for i, idx in enumerate(display_indices):
            movie = top_matches.iloc[idx]
            oscar_info = check_oscar_status(movie['Title'], oscar_df)  # Oscar info
            oscar_note = ""
            if oscar_info:
                oscar_note = " | " + ", ".join(oscar_info)  # Join all Oscar nominations/wins
            actor_note = ""
            if fav_actor and fav_actor.lower() in movie['Actors'].lower():
                actor_note = f" (features {fav_actor})"
            print(
                f"{i + 1}. {movie['Title']} ({int(movie['Year'])}) | {movie['Genre']} | "
                f"{movie['Rating']}⭐ | {int(movie['Runtime (Minutes)'])} min{oscar_note}{actor_note}"
            )

        seen_input = input("\nHave you already seen any of these? (y/n): ").strip().lower()

        if seen_input == 'n':
            print("🍿 Enjoy your movie night!")
            break
        elif seen_input == 'y':
            seen_nums = input("Enter the number(s) of the movies you've seen (comma-separated, e.g. 2, 4): ")
            try:
                seen_indices = set()  # Use a set to avoid duplicates

                for num in seen_nums.split(','):
                    num = num.strip()
                    if not num.isdigit():
                        print(f"⚠️ '{num}' is not a valid number. Skipping.")
                        continue
                    val = int(num) - 1
                    if val < 0 or val >= len(display_indices):
                        print(f"⚠️ '{val + 1}' is not in the list of recommendations. Skipping.")
                        continue
                    seen_indices.add(val)

                for seen_idx in seen_indices:
                    if next_index < len(top_matches):
                        display_indices[seen_idx] = next_index
                        next_index += 1
                    else:
                        print(f"⚠️ No more new recommendations to replace movie #{seen_idx + 1}.")

                if not seen_indices:
                    print("⚠️ No valid selections were made.")
            except Exception as e:
                print("❌ Error processing your input. Please enter numbers like: 1, 3")

        else:
            print("❌ Please enter 'y' or 'n'.")

def main():
    movie_file_path = 'IMDB-Movie-Data.csv'  # Path to your movie details dataset
    oscar_file_path = 'oscar_data.csv'  # Path to your Oscar dataset

    movie_df = load_movie_data(movie_file_path)
    oscar_df = load_oscar_data(oscar_file_path)

    # Start project with instructions
    print('Welcome to movie recommender! 🎬✨\n')
    print("First, you'll go through a quick survey about your preferences. Feel free to click 'Enter' to skip\n")

    if movie_df is not None and oscar_df is not None:
        prefs = get_user_preferences(movie_df)
        recommendations = filter_movies(movie_df, prefs)
        show_recommendations(recommendations, oscar_df, prefs.get('fav_actor'))


if __name__ == '__main__':
    main()