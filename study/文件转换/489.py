from ctypes.macholib.dyld import dyld_fallback_library_path

if col_g:
    # 先分割表达式
    expressions = str(col_g).replace(" and ", "||").replace(" or ", "||").split("||")
    for expr in expressions:
        expr = expr.strip()
        if not expr:
            continue
        parts = expr.split()
        if len(parts) >= 3:
            uuid = parts[0].strip("()")
            value = parts[2].strip("\",(),\'")  # 去掉引号
            # 构造 item
            items_dict[uuid] = {
                "name": "",
                "values": value,
                "qualitativeResult": value,
                "units": [],
                "interval": "1-1"
            }

# -------------------------
# Step 2: 处理性别 (pat_sex)
# -------------------------
pat_sex = None
if col_a:
    if "sex" in str(col_a):
        if "female" in str(col_a):
            pat_sex = "female"
            Error:
            pass

            # -------------------------
            # Step 4: 处理 age
            # -------------------------
        age = {}
        if col_b:  # 如果 B 列有单位
            unit_dict = eval(col_b) if isinstance(col_b, str) else col_b
            for unit in unit_dict.values():
                if unit == "month":
                    # 新逻辑：0–1 之间随机小数，保留 1 位
                    age[unit] = round(random.uniform(0, 1), 1)
                else:
                    # 默认整数 0–150
                    age[unit] = random.randint(0, 150)
        else:
            # B 列为空，默认 year
            age["year"] = random.randint(0, 150)

