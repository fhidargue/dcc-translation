def sanitize_usd_name(name):
    return name.split("|")[-1].replace(":", "_").replace("|", "_").replace(" ", "_")
