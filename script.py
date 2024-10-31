import requests
import csv
import time

# GitHub token and headers for authorization
headers = {
    "Authorization": "Bearer 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",
    "Accept": "application/vnd.github.v3+json"
}

def clean_company_name(company):
    if company:
        company = company.strip().lstrip('@').upper()
    return company if company is not None else ""

# Fetch all users in Hyderabad with over 50 followers, handling pagination
def fetchUsers():
    search_url = "https://api.github.com/search/users"
    params = {
        "q": "location:Hyderabad followers:>50",
        "type": "users",
        "per_page": 100  # Set to max limit per page
    }
    
    all_users = []
    page = 1
    with open('users.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            "login", "name", "company", "location", "email", "hireable",
            "bio", "public_repos", "followers", "following", "created_at"
        ])

        while True:
            params["page"] = page
            response = requests.get(search_url, headers=headers, params=params)
            
            # Check for successful response
            if response.status_code == 200:
                users_data = response.json().get('items', [])
                if not users_data:
                    break  # Exit loop if no more data

                for user in users_data:
                    user_details = requests.get(f"https://api.github.com/users/{user['login']}", headers=headers)
                    
                    if user_details.status_code == 200:
                        user_info = user_details.json()
                        writer.writerow([
                            user_info.get("login", ""),
                            user_info.get("name", ""),
                            clean_company_name(user_info.get("company")),
                            user_info.get("location", ""),
                            user_info.get("email", ""),
                            str(user_info.get("hireable", "")).lower() if user_info.get("hireable") is not None else "",
                            user_info.get("bio", ""),
                            user_info.get("public_repos", ""),
                            user_info.get("followers", ""),
                            user_info.get("following", ""),
                            user_info.get("created_at", "")
                        ])
                        all_users.append(user_info.get("login", ""))
                
                page += 1  # Go to the next page
                time.sleep(1)  # Rate limit safeguard (1 second delay between requests)
            else:
                print(f"Failed to retrieve users on page {page}: {response.status_code} - {response.text}")
                break

    print("User data successfully written to 'users.csv'")
    return all_users

# Fetch repositories for each user login obtained
def fetchRepos(users):
    with open('repositories.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            "login", "full_name", "created_at", "stargazers_count", 
            "watchers_count", "language", "has_projects", "has_wiki", "license_name"
        ])

        for user_login in users:
            page = 1
            while page <= 10:
                repos_url = f"https://api.github.com/users/{user_login}/repos"
                params = {"per_page": 50, "page": page}
                response = requests.get(repos_url, headers=headers, params=params)
                
                if response.status_code == 200:
                    repos = response.json()
                    if not repos:
                        break

                    for repo in repos:
                        writer.writerow([
                            user_login,
                            repo.get("full_name", ""),
                            repo.get("created_at", ""),
                            repo.get("stargazers_count", 0),
                            repo.get("watchers_count", 0),
                            repo.get("language", ""),
                            str(repo.get("has_projects", "")).lower(),
                            str(repo.get("has_wiki", "")).lower(),
                            repo.get("license", {}).get("key", "") if repo.get("license", {}) else ""
                        ])
                else:
                    print(f"Failed to retrieve repositories for {user_login}: {response.status_code} - {response.text}")
                    break
                page += 1

    print("Repository data successfully written to 'repositories.csv'")

# Main function to execute both data fetching functions
def main():
    users = fetchUsers()
    fetchRepos(users)

if __name__ == "__main__":
    main()
