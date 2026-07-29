import json
import os
import requests

TARGET_UID = "6395178860"  
DATA_FILE = "posts.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
}


def load_existing():
  if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      try:
        return json.load(f)
      except:
        return []
  return []


def save_posts(posts):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(posts, f, ensure_ascii=False, indent=2)


def fetch_weibo():
  url = f"https://m.weibo.cn/api/container/getIndex?type=uid&value={TARGET_UID}"
  res = requests.get(url, headers=HEADERS).json()

  containerid = None
  for tab in res.get("data", {}).get("tabsInfo", {}).get("tabs", []):
    if tab.get("tab_type") == "weibo":
      containerid = tab.get("containerid")
      break

  if not containerid:
    return []

  list_url = f"https://m.weibo.cn/api/container/getIndex?type=uid&value={TARGET_UID}&containerid={containerid}"
  list_res = requests.get(list_url, headers=HEADERS).json()
  cards = list_res.get("data", {}).get("cards", [])

  new_items = []
  for card in cards:
    if card.get("card_type") == 9:
      mblog = card.get("mblog", {})
      pics = [
          p.get("large", {}).get("url") for p in mblog.get("pics", []) if p
      ]
      new_items.append({
          "id": mblog.get("id"),
          "created_at": mblog.get("created_at"),
          "text": mblog.get("text"),
          "pics": pics,
      })
  return new_items


if __name__ == "__main__":
  existing = load_existing()
  existing_ids = {p["id"] for p in existing}

  latest = fetch_weibo()
  added = False

  for p in latest:
    if p["id"] not in existing_ids:
      existing.insert(0, p)  # 最新发布的排在前面
      added = True

  if added:
    save_posts(existing)
    print("发现新微博，已存库！")
  else:
    print("没有新微博。")
