import openpyxl
import csv

input_path = "/Users/apple/Downloads/shell/doc_85b68efca457_guatizi_订阅域名汇总.xlsx"
out_path = "/Users/apple/Downloads/shell/airports.csv"

wb = openpyxl.load_workbook(input_path, read_only=True)
ws = wb.active
sites = []

for row in ws.iter_rows(min_row=2, values_only=True):
    if len(row) < 4:
        continue
    name = str(row[2] or "").strip()
    url = str(row[3] or "").strip()
    if not url or not url.startswith("http"):
        continue
    panel_type = str(row[5] or "").strip().lower() if len(row) > 5 and row[5] else ""
    sites.append([name, url, panel_type, 0, "unknown"])

wb.close()

with open(out_path, mode="w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "url", "panel_type", "fail_count", "last_status"])
    writer.writerows(sites)

print(f"转换成功, 写入了 {len(sites)} 个站点到 {out_path}")
