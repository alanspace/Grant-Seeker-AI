import os
import streamlit as st
import sys
import site
import shutil

def human(n):
    for u in ['B', 'KB', 'MB', 'GB', 'TB']:
        if n < 1024.0:
            return f"{n:.2f} {u}"
        n /= 1024.0
    return f"{n:.2f} PB"

def dir_size(path):
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total

def show_diagnostics():
    st.title("App Diagnostics")
    
    st.header("1. Repository Footprint")
    root = os.getcwd()  # repo root as checked out in the container
    st.write(f"**Current Working Directory:** `{root}`")
    
    # Compute repo size
    repo_bytes = dir_size(root)
    st.metric(label="Repo Files Size", value=human(repo_bytes))

    st.divider()

    st.header("2. Installed Packages (site-packages)")
    site_paths = site.getsitepackages() if hasattr(site, 'getsitepackages') else [sys.prefix]
    st.write("Checking paths:", site_paths)
    
    pkgs_size = sum(dir_size(p) for p in site_paths if os.path.exists(p))
    st.metric(label="Total Installed Packages Size", value=human(pkgs_size))

    st.divider()

    st.header("3. Top 20 Largest Files in Repo")
    items = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                items.append((os.path.getsize(fp), fp))
            except OSError:
                pass
    items.sort(reverse=True)
    
    top_files = [{"Size": human(size), "Path": path} for size, path in items[:20]]
    st.table(top_files)

    st.divider()

    st.header("4. Full Container Disk Usage")
    try:
        total, used, free = shutil.disk_usage('/')
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Space", human(total))
        col2.metric("Used Space", human(used))
        col3.metric("Free Space", human(free))
    except Exception as e:
        st.error(f"Could not get disk usage: {e}")

if __name__ == "__main__":
    show_diagnostics()
