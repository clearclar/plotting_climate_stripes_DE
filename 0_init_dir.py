import os
import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        #logging.FileHandler("init_dir.log"),
        logging.StreamHandler()  # also show in console
    ]
)

def create_project_structure(base_dir, project_name):
    # Define folders and initial files
    project_slug = project_name.lower().replace(' ', '_')
    answer_project_slug = input(f"Using {project_slug} as project 'slug'? (y/n): ").strip().lower() == "y"
    if not answer_project_slug:
        new_project_slug = input("Enter project 'slug' name (short, lowercase, no spaces): ")

        if not new_project_slug.isidentifier():
            print(f"'{new_project_slug}' is not a valid Python identifier. Using 'myproject'.")
            project_slug = project_slug
        
        if new_project_slug.isidentifier():
            project_slug = new_project_slug

    folders = [
        "src",
        f"src/{project_slug}",
        "paper",
        "paper/images",
        "data",
        "data/raw",
        "data/processed",
        "data/external",
        "results",
        "results/figures",
        "results/tables",
        "notebooks"
    ]
    
    files = {
        ".gitignore":
        """
        # Python & uv
        .uv/
        __pycache__/
        *.pyc
        .ipynb_checkpoints/
        .pyc
        .env
        .venv

        # LaTeX
        *.aux
        *.bbl
        *.blg
        *.log
        *.out
        *.synctex.gz
        *.toc

        # Data (CRITICAL!)
        # Never commit large data files.
        # Commit a README in these folders explaining
        # *where* to get the data (e.g., a download URL).
        data/raw/
        data/processed/
        data/external/

        # OS & Other
        .DS_Store
        Thumbs.db
        """.strip(),

        "README.md": f"# {project_slug}\n\nProject description...",

        "pyproject.toml": f"""
        [project]
        name = "{project_slug}"
        version = "0.1.0"
        description = "This is a project"
        authors = [{{ name = "Clara Vydra", email = "clara@mainotter.de" }}]       
        readme = "README.md"
        license = {{ text = "CC-BY-NC-SA-4.0" }}
        requires-python = ">=3.11"
        dependencies = [
            "geopandas>=1.1.1",
            "hda>=2.34",
            "ipykernel>=7.1.0",
            "matplotlib>=3.10.7",
            "rioxarray>=0.19.0",
            "seaborn>=0.13.2",
            "xarray>=2025.10.1",
            "zarr>=3.1.3",
            "cdsapi>=0.7.7",
            "dask>=2025.10.0",
            "distributed>=2025.10.0",
            "folium>=0.20.0",
            "ipykernel>=7.1.0",
            "odc>=0.1.2",
            "odc-stac>=0.4.0",
        ]

        [project.optional-dependencies]
        dev = ["pytest"]
        """.strip(),

        "LICENSE": """
        Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License

        By exercising the Licensed Rights (defined below), You accept and agree to be bound by the terms and conditions of this Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International Public License ("Public License").

        Full license text: https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode

        You may not use the material for commercial purposes.
        If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.
        """.strip(),

        "paper/main.tex":r"""
        \documentclass[12pt, a4paper]{article}

        \usepackage[utf8]{inputenc}
        \usepackage{graphicx}
        \usepackage[margin=1in]{geometry}
        \usepackage{booktabs} % For nice tables
        \usepackage{hyperref} % For links

        % Point to the figures directory (one level up)
        \graphicspath{{../results/figures/}}

        \title{My Amazing Geospatial Analysis}
        \author{Your Name}
        \date{\today}

        \begin{document}

        \maketitle

        \section{Introduction}
        This is where the introduction goes.

        \section{Methods}
        We performed our analysis using Python.

        \section{Results}
        We created a map, see Figure \ref{fig:main_map}.

        \begin{figure}[h!]
            \centering
            % The \includegraphics command looks in the path
            % set by \graphicspath, so you just need the filename.
            % \includegraphics[width=\textwidth]{your_figure_name.png}
            \caption{The main map of our analysis.}
            \label{fig:main_map}
        \end{figure}

        \section{Conclusion}
        The results are conclusive.

        % \bibliographystyle{plain}
        % \bibliography{/Users/claravydra/Documents/03_Obsidian/Researchvault/PDFs/literature}

        \end{document}
        """
    }

    for folder in folders:
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
        logging.info(f"Created folder: {folder}")
    
    for file, content in files.items():
        logging.info("Creating boilerplate files ...")
        with open(os.path.join(base_dir, file), "w") as f:
            f.write(content)
        logging.info(f"Created file: {file}")

    # This makes 'src/project_slug' a package
    base_dir_path = Path(base_dir)
    (base_dir_path / f'src/{project_slug}/__init__.py').touch()
    # Create empty files as placeholders
    (base_dir_path / f'src/{project_slug}/data_processing.py').touch()
    (base_dir_path / f'src/{project_slug}/analysis.py').touch()
    (base_dir_path / f'src/{project_slug}/visualization.py').touch()
    
    logging.info("Project structure created successfully.")

def run_uv_setup(base_dir):
    logging.info("Setting up virtual environment using uv...")

    try:
        # Step 1: Create the virtual environment
        subprocess.run(["uv", "venv"], check=True, cwd=base_dir)

        # Step 2: Sync dependencies
        subprocess.run(["uv", "sync"], check=True, cwd=base_dir)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logging.error(f"Error during uv setup: {e}")
        sys.exit(1)

    print("Virtual environment setup complete.")

def git_setup(base_dir, project_name):
    subprocess.run(["git", "init"], cwd=base_dir)
    subprocess.run(["git", "add", "."], cwd=base_dir)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=base_dir)
    subprocess.run(["git", "branch", "-M", "main"], cwd=base_dir)
    subprocess.run(["git", "checkout", "-b", "dev"], cwd=base_dir)
    subprocess.run(["git", "add", "."], cwd=base_dir)
    subprocess.run(["git", "commit", "-m", "Create dev branch"], cwd=base_dir)
    logging.info(f"Project '{project_name}' has been set up at {base_dir}.")

def github_setup(base_dir, project_name, public):
    repo_name = input("Enter GitHub repository name (leave blank to use project name): ").strip()
    if repo_name == "":
        repo_name = project_name
    # install ghapi in uv environment
    # subprocess.run(["uv", "pip", "install", "ghapi"], check=True, cwd=base_dir)
    # authenticate through gh cli
    # token = ''
    # subprocess.run(["gh", "auth", "login", "--with-token"], input=token, text=True, check=True)
    subprocess.run(["gh", "auth", "login"])
    subprocess.run(["gh", "repo", "create", repo_name, "--source=.", "--public" if public else "--private"], cwd=base_dir)
    # Add remote origin
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=base_dir)
    subprocess.run(["git", "push", "-u", "origin", "dev"], cwd=base_dir)
    logging.info(f"GitHub repository '{repo_name}' created and linked successfully.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.realpath(__file__))
    project_name = os.path.basename(base_dir)
    logging.info('Local installation of uv and gh are necessary.')
    logging.info(f"Project name: {project_name}. Initializing project structure...")
    
    # subprocess.run([sys.executable, "-m", "pip", "install", "uv", "ghapi"])
    create_project_structure(base_dir, project_name)
    run_uv_setup(base_dir)

    logging.info("Activate uv environment with: '.venv/Scripts/activate' (Windows) or 'source .venv/bin/activate' (Linux/Mac). Then, run 2_init_git.py to initialize Git and GitHub repository.")

    GIT = input("Initialize Git repository? (y/n): ").strip().lower() == "y"
    GITHUB = input("Create and link GitHub repository? (y/n): ").strip().lower() == "y"
    public = input("Should the GitHub repository be public? (y/n): ").strip().lower() == "y"
    logging.info(f"Git initialization: {GIT}, GitHub repository creation: {GITHUB}, Public repo: {public}")

    if GIT:
        git_setup(base_dir, project_name)
    if GITHUB:
        logging.info("Creating and linking GitHub repository...")
        github_setup(base_dir, project_name, public)
        logging.info("GitHub repository setup complete.")

    # # This assumes your original script setup 'uv'
    # # Now, let's install the project you just created
    # print("\nRunning 'uv pip install -e .' to make your src code importable.")
    # try:
    #     # '-e' means "editable" mode.
    #     # It links your 'uv' env to your 'src' folder.
    #     # Changes in 'src' are instantly available to import.
    #     subprocess.run(["uv", "pip", "install", "-e", "."], check=True)
    #     print("✅ Project installed in editable mode.")
    #     print("\nTo get started:")
    #     print("1. Activate your environment: uv shell")
    #     print("2. Open a notebook in 'notebooks/'")
    #     print(f"3. In a cell, you can now run: import {project_slug}")
    # except Exception as e:
    #     print(f"\n⚠️ Could not auto-install project. Error: {e}")
    #     print("Run 'uv pip install -e .' manually after activating your environment.")