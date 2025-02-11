# 每月重新生成一次缓存
if __name__ == "__main__":
    gen = CombinationGenerator()
    gen.generate()

    with open("common_combinations.py", "w") as f:
        f.write("COMMON_CACHE = {\n")
        for k, v in gen.combinations.items():
            f.write(f"    {int(k)}: '{v[0]}',\n")
        f.write("}")