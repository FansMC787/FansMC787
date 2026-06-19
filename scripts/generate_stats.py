import os
import requests

def fetch_github_data(username, token):
    headers = {"Authorization": f"Bearer {token}"}
    graphql_query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection { totalCommitContributions }
        pullRequests { totalCount }
        issues { totalCount }
        followers { totalCount }
        repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          nodes {
            stargazerCount
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node { name }
              }
            }
          }
        }
      }
    }
    """
    try:
        response = requests.post("https://api.github.com/graphql", json={"query": graphql_query, "variables": {"login": username}}, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()["data"]["user"]
    except Exception as e:
        print(f"Fehler: {e}")
        return None

def generate_svg(data):
    commits, stars, prs, issues, repos, followers = 0, 0, 0, 0, 0, 0
    languages_agg = {}
    if data:
        commits = data["contributionsCollection"].get("totalCommitContributions", 0)
        prs = data["pullRequests"].get("totalCount", 0)
        issues = data["issues"].get("totalCount", 0)
        followers = data["followers"].get("totalCount", 0)
        repo_nodes = data["repositories"].get("nodes", [])
        repos = data["repositories"].get("totalCount", 0)
        for repo in repo_nodes:
            stars += repo.get("stargazerCount", 0)
            for edge in repo.get("languages", {}).get("edges", []):
                lang_name = edge["node"]["name"]
                languages_agg[lang_name] = languages_agg.get(lang_name, 0) + edge["size"]
    sorted_langs = sorted(languages_agg.items(), key=lambda x: x[1], reverse=True)[:6]
    total_size = sum(languages_agg.values()) if languages_agg else 1
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 360" width="100%" height="100%">
  <rect width="850" height="360" rx="14" fill="#0F0C1B" stroke="#2D2654" stroke-width="1.5" />
  <style>
    .label {{ font-family: sans-serif; font-size: 14px; fill: #A5A1B8; }}
    .val {{ font-family: sans-serif; font-size: 24px; fill: #00F2FE; font-weight: bold; }}
    .title {{ font-family: sans-serif; font-size: 16px; fill: #FFFFFF; font-weight: bold; }}
  </style>
  <g transform="translate(40, 40)">
    <text x="0" y="10" class="title" fill="#7D52FF">// STATISTIKEN</text>
    <g transform="translate(0, 45)"><text class="label">Gesamte Commits</text><text y="26" class="val">{commits}</text></g>
    <g transform="translate(180, 45)"><text class="label">Sterne erhalten</text><text y="26" class="val">{stars}</text></g>
    <g transform="translate(0, 125)"><text class="label">Pull Requests</text><text y="26" class="val">{prs}</text></g>
    <g transform="translate(180, 125)"><text class="label">Gelöste Issues</text><text y="26" class="val">{issues}</text></g>
    <g transform="translate(0, 205)"><text class="label">Repositories</text><text y="26" class="val">{repos}</text></g>
    <g transform="translate(180, 205)"><text class="label">Follower</text><text y="26" class="val">{followers}</text></g>
  </g>
  <line x1="425" y1="35" x2="425" y2="325" stroke="#2D2654" stroke-dasharray="4 4" />
  <g transform="translate(465, 40)">
    <text x="0" y="10" class="title" fill="#00F2FE">// SPRACHVERTEILUNG</text>
    <g transform="translate(0, 35)">"""
    for i, (name, size) in enumerate(sorted_langs):
        pct = (size / total_size) * 100
        y = i * 45
        color = "#7D52FF" if i % 2 == 0 else "#00F2FE"
        svg += f"""<g transform="translate(0, {y})">
          <text y="15" fill="#FFFFFF" font-family="sans-serif" font-size="13">{name}</text>
          <rect y="22" width="300" height="8" rx="4" fill="#2D2654"/>
          <rect y="22" width="{int(3 * pct)}" height="8" rx="4" fill="{color}"/>
          <text x="310" y="30" class="label" font-size="12">{pct:.1f}%</text>
        </g>"""
    svg += "</g></g></svg>"
    return svg

def main():
    token = os.getenv("GITHUB_TOKEN")
    data = fetch_github_data("FansMC787", token) if token else None
    with open("generated/github-stats.svg", "w", encoding="utf-8") as f:
        f.write(generate_svg(data))

if __name__ == "__main__":
    main()