import os
import urllib.request
import json
import ssl

token = "os.environ.get("SHOPIFY_ACCESS_TOKEN", "")"
shop_url = "https://divyaprabhafoods.myshopify.com"
blog_id = 97942077654

ctx = ssl.create_default_context()

# Test 1: REST API with published: true and future published_at
payload_rest = {
    "article": {
        "title": "TEST SCHEDULE REST API",
        "author": "Baa & The DivyaPrabha Culinary Team",
        "tags": "Heritage Recipes",
        "body_html": "<p>Test schedule content</p>",
        "published": True,
        "published_at": "2026-08-15T09:00:00+05:30"
    }
}

url = f"{shop_url}/admin/api/2024-04/blogs/{blog_id}/articles.json"
data_bytes = json.dumps(payload_rest).encode("utf-8")
req = urllib.request.Request(url, data=data_bytes, headers={
    "X-Shopify-Access-Token": token,
    "Content-Type": "application/json"
})

try:
    with urllib.request.urlopen(req, context=ctx) as resp:
        res = json.loads(resp.read().decode())
        art = res.get("article", {})
        print("REST API Result:")
        print(f"ID: {art.get('id')}")
        print(f"published_at: {art.get('published_at')}")
except Exception as e:
    print("REST Error:", e)

# Test 2: GraphQL API articleCreate
gql_query = """
mutation articleCreate($article: ArticleCreateInput!) {
  articleCreate(article: $article) {
    article {
      id
      title
      publishedAt
    }
    userErrors {
      field
      message
    }
  }
}
"""

gql_variables = {
  "article": {
    "blogId": f"gid://shopify/Blog/{blog_id}",
    "title": "TEST SCHEDULE GRAPHQL API",
    "bodyHtml": "<p>Test schedule graphql content</p>",
    "author": { "name": "Baa & The DivyaPrabha Culinary Team" },
    "tags": ["Heritage Recipes"],
    "publishedAt": "2026-08-15T12:00:00+05:30"
  }
}

url_gql = f"{shop_url}/admin/api/2024-04/graphql.json"
data_gql = json.dumps({"query": gql_query, "variables": gql_variables}).encode("utf-8")
req_gql = urllib.request.Request(url_gql, data=data_gql, headers={
    "X-Shopify-Access-Token": token,
    "Content-Type": "application/json"
})

try:
    with urllib.request.urlopen(req_gql, context=ctx) as resp:
        res_gql = json.loads(resp.read().decode())
        print("\nGraphQL API Result:")
        print(json.dumps(res_gql, indent=2))
except Exception as e:
    print("GraphQL Error:", e)
