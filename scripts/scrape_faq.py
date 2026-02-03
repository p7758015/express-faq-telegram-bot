from app.scraping import fetch_faq_page, parse_faq_html, save_faq_items


def main() -> None:
    html = fetch_faq_page()
    items = parse_faq_html(html)
    print(f"Parsed {len(items)} FAQ items")
    save_faq_items(items)


if __name__ == "__main__":
    main()
