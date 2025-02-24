import glob
import importlib.util
import os
from scraper_module.scraper_lib.runner import RunAllEngines
from scraper_module.scraper_lib.scraper_engine import ScraperEngine

def clean_output():
    # Remove any existing JSON output files to start fresh.
    for file in glob.glob("data_output/*.json"):
        os.remove(file)

EXCLUDE_ENGINES = {""} # For testing purposes

if __name__ == "__main__":
    clean_output()
    config_files = [
        file for file in glob.glob("configs/*.py")
        if os.path.basename(file).replace(".py", "") not in EXCLUDE_ENGINES
    ]

    engines = []
    for config_file in config_files:
        spec = importlib.util.spec_from_file_location(
            "config", config_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        engines.append(ScraperEngine(module.config))

    runner = RunAllEngines(engines=engines)
    runner.run_all()
    runner.save_all()