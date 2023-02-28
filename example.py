from scraper import get_menu

def main():
    menu = get_menu(join_paragraphs="\n")
    
    import json
    with open("menu.json", "w") as f:
        f.write(json.dumps(menu, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()